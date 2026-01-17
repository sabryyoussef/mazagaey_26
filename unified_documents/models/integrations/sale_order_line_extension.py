# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Add a field to track if documents need to be copied
    documents_copied = fields.Boolean(
        string='Documents Copied',
        default=False,
        help='Indicates if documents have been copied to the project'
    )

    def _timesheet_create_project(self):
        """Override to automatically copy documents and create processing tasks when project is created"""
        # Call the original method to create the project
        project = super()._timesheet_create_project()
        
        # Copy documents and create processing tasks
        if self.product_id and self.product_id.document_ids:
            # Copy documents first
            self._copy_product_documents_to_project(project)
            self.documents_copied = True
            
            # Create document processing tasks for each category
            self._create_document_processing_tasks(project)
            
            _logger.info(f"Project {project.name} created with documents and processing tasks")
        
        return project

    def copy_documents_to_project(self):
        """Manual method to copy documents to project"""
        self.ensure_one()
        
        if not self.project_id or not self.product_id or not self.product_id.document_ids:
            return False
        
        try:
            self._copy_product_documents_to_project(self.project_id)
            self.documents_copied = True
            _logger.info(f"Successfully copied documents from product {self.product_id.name} to project {self.project_id.name}")
            return True
        except Exception as e:
            _logger.warning(f"Failed to copy documents from product {self.product_id.name} to project {self.project_id.name}: {e}")
            return False

    def _copy_product_documents_to_project(self, project):
        """Copy documents from product to project"""
        self.ensure_one()
        
        if not self.product_id or not self.product_id.document_ids:
            return
        
        # Use the document service to copy documents
        try:
            document_service = self.env['unified.document.service']
            if hasattr(document_service, 'copy_product_documents_to_project'):
                result = document_service.copy_product_documents_to_project(project, self.product_id)
                _logger.info(f"Document service copied documents: {result}")
            else:
                # Fallback: direct copy if service is not available
                self._direct_copy_documents_to_project(project)
        except Exception as e:
            _logger.warning(f"Document service failed, using fallback: {e}")
            self._direct_copy_documents_to_project(project)

    def _direct_copy_documents_to_project(self, project):
        """Direct copy of documents from product to project (fallback method)"""
        self.ensure_one()
        
        if not self.product_id or not self.product_id.document_ids:
            return
        
        copied_count = 0
        for doc in self.product_id.document_ids:
            try:
                # Create a copy of the document linked to the project
                new_doc_vals = {
                    'name': f"{doc.name} - {project.name}",
                    'category': doc.category or 'reference',  # Provide default category
                    'status': doc.status or 'draft',  # Provide default status
                    'priority': doc.priority or '1',  # Provide default priority
                    'description': doc.description or '',
                    'notes': doc.notes or '',
                    'tag_ids': [(6, 0, doc.tag_ids.ids)] if doc.tag_ids else False,
                    'res_model': 'project.project',
                    'res_id': project.id,
                    'linked_product_id': self.product_id.id,  # Keep reference to original product
                }
                
                # Copy attachment if exists and is valid
                if doc.attachment_id and doc.attachment_id.exists():
                    new_doc_vals['attachment_id'] = doc.attachment_id.id
                
                # Create document with error handling
                new_doc = self.env['documents.document'].sudo().create(new_doc_vals)
                copied_count += 1
                
                _logger.info(f"Copied document '{doc.name}' to project '{project.name}'")
                
            except Exception as e:
                _logger.warning(f"Failed to copy document '{doc.name}': {e}")
                continue  # Continue with next document
        
        _logger.info(f"Direct copy completed: {copied_count} documents copied to project {project.name}")

    def _timesheet_create_task(self, project):
        """Override to ensure documents are copied when task is created"""
        # Call the original method to create the task
        task = super()._timesheet_create_task(project)
        
        # Mark that documents need to be copied if not already done
        if project and not self.documents_copied and self.product_id and self.product_id.document_ids:
            self.documents_copied = False
            _logger.info(f"Task created for project {project.name}, documents will be copied later")
        
        return task

    @api.model
    def copy_pending_documents(self):
        """Cron job to copy documents for sale order lines that need it"""
        pending_lines = self.search([
            ('documents_copied', '=', False),
            ('project_id', '!=', False),
            ('product_id.document_ids', '!=', False)
        ])
        
        copied_count = 0
        for line in pending_lines:
            if line.copy_documents_to_project():
                copied_count += 1
        
        _logger.info(f"Cron job copied documents for {copied_count} sale order lines")
        return copied_count

    def _create_document_processing_tasks(self, project):
        """Create document processing tasks for each document category"""
        self.ensure_one()
        
        if not self.product_id or not self.product_id.document_ids:
            return []
        
        # Get unique document categories from the product
        categories = list(set(self.product_id.document_ids.mapped('category')))
        categories = [cat for cat in categories if cat]  # Remove empty categories
        
        if not categories:
            _logger.warning(f"No valid document categories found for product {self.product_id.name}")
            return []
        
        created_tasks = []
        
        for category in categories:
            # Get documents for this category
            category_docs = self.product_id.document_ids.filtered(lambda d: d.category == category)
            
            if not category_docs:
                continue
                
            # Create main category task
            main_task = self._create_category_main_task(project, category, category_docs)
            created_tasks.append(main_task)
            
            # Create subtasks for each document in this category
            for doc in category_docs:
                subtask = self._create_document_subtask(main_task, doc, project)
                created_tasks.append(subtask)
        
        _logger.info(f"Created {len(created_tasks)} document processing tasks for project {project.name}")
        return created_tasks

    def _create_category_main_task(self, project, category, category_docs):
        """Create main task for a document category"""
        self.ensure_one()
        
        # Format category name for display
        category_display = category.replace('_', ' ').title()
        
        # Get or create tag for this category
        tag_name = f'Document-{category}'
        existing_tag = self.env['project.tags'].search([('name', '=', tag_name)], limit=1)
        if existing_tag:
            tag_ids = [(4, existing_tag.id)]
        else:
            tag_ids = [(0, 0, {'name': tag_name, 'color': self._get_category_color(category)})]
        
        # Create main category task
        main_task_vals = {
            'name': f'{category_display} Documents Processing',
            'project_id': project.id,
            'description': f'Process all {category_display.lower()} documents for {self.product_id.name}\n\nDocuments in this category:\n' + 
                          '\n'.join([f'• {doc.name}' for doc in category_docs]),
            'priority': '1',  # Normal priority
            'user_ids': [(6, 0, [project.user_id.id])] if project.user_id else False,
            'tag_ids': tag_ids
        }
        
        # Set higher priority for required and compliance documents
        if category in ['required', 'compliance']:
            main_task_vals['priority'] = '1'  # High priority
        
        main_task = self.env['project.task'].create(main_task_vals)
        
        _logger.info(f"Created main task '{main_task.name}' for category '{category}'")
        return main_task

    def _create_document_subtask(self, parent_task, document, project):
        """Create subtask for individual document processing"""
        self.ensure_one()
        
        # Create subtask for document processing
        subtask_vals = {
            'name': f'Process: {document.name}',
            'parent_id': parent_task.id,
            'project_id': project.id,
            'document_id': document.id,  # Link to the document
            'description': f'Process document: {document.name}\n\nDocument Details:\n'
                          f'• Category: {document.category}\n'
                          f'• Priority: {document.priority}\n'
                          f'• Status: {document.status}\n'
                          f'• Notes: {document.notes or "No notes"}',
            'priority': document.priority or '1',
            'user_ids': [(6, 0, [project.user_id.id])] if project.user_id else False,
        }
        
        # Set due date based on document category
        if document.category == 'required':
            subtask_vals['date_deadline'] = fields.Date.add(fields.Date.today(), days=7)
        elif document.category == 'compliance':
            subtask_vals['date_deadline'] = fields.Date.add(fields.Date.today(), days=10)
        elif document.category == 'deliverable':
            subtask_vals['date_deadline'] = fields.Date.add(fields.Date.today(), days=14)
        
        subtask = self.env['project.task'].create(subtask_vals)
        
        # Create document processing checkpoints for this subtask
        self._create_document_checkpoints(subtask, document)
        
        # Create approval request if needed for critical document types
        if document.category in ['required', 'compliance']:
            self._create_approval_request(subtask, document)
        
        _logger.info(f"Created subtask '{subtask.name}' for document '{document.name}'")
        return subtask

    def _create_document_checkpoints(self, task, document):
        """Create checkpoints for document processing stages"""
        self.ensure_one()
        
        # Check if project_task_checkpoints module is available
        if 'project.task.checkpoint' not in self.env:
            _logger.warning("project_task_checkpoints module not available, skipping checkpoint creation")
            return []
        
        # Define checkpoint stages for document processing
        checkpoint_stages = [
            {
                'name': f'Upload {document.name}',
                'sequence': 10,
                'stage': 'upload',
                'notes': f'Document "{document.name}" has been uploaded to the system and verified for format and completeness.',
                'checklist_items': [
                    'Document file uploaded successfully',
                    'Document format verified (PDF, DOC, etc.)',
                    'Document size within acceptable limits',
                    'Document content is readable and complete'
                ]
            },
            {
                'name': f'Review {document.name}',
                'sequence': 20,
                'stage': 'review',
                'notes': f'Document "{document.name}" has been reviewed by the team for content accuracy and compliance.',
                'checklist_items': [
                    'Document content reviewed by team member',
                    'Technical accuracy verified',
                    'Compliance requirements checked',
                    'Stakeholder feedback incorporated'
                ]
            },
            {
                'name': f'Approve {document.name}',
                'sequence': 30,
                'stage': 'approve',
                'notes': f'Document "{document.name}" has been approved by authorized personnel through the approval workflow.',
                'checklist_items': [
                    'Approval request submitted',
                    'Approval workflow completed',
                    'All approvers have signed off',
                    'Approval documentation recorded'
                ]
            },
            {
                'name': f'Deliver {document.name}',
                'sequence': 40,
                'stage': 'deliver',
                'notes': f'Document "{document.name}" has been delivered to the client or stakeholder and receipt confirmed.',
                'checklist_items': [
                    'Final document version prepared',
                    'Document sent to client/stakeholder',
                    'Delivery receipt confirmed',
                    'Document archived for future reference'
                ]
            }
        ]
        
        created_checkpoints = []
        
        try:
            for stage in checkpoint_stages:
                # Create checkpoint
                checkpoint_vals = {
                    'name': stage['name'],
                    'sequence': stage['sequence'],
                    'task_id': task.id,
                    'notes': stage['notes'],
                    'auto_advance_stage': True,
                }
                
                checkpoint = self.env['project.task.checkpoint'].create(checkpoint_vals)
                created_checkpoints.append(checkpoint)
                
                # Create checklist items for this checkpoint if the model exists
                if 'project.checkpoint.checklist.item' in self.env:
                    for i, item_text in enumerate(stage['checklist_items']):
                        self.env['project.checkpoint.checklist.item'].create({
                            'name': item_text,
                            'checkpoint_id': checkpoint.id,
                            'sequence': i + 1,
                        })
                
                _logger.info(f"Created checkpoint '{checkpoint.name}' for task '{task.name}'")
        
        except Exception as e:
            _logger.warning(f"Failed to create checkpoints for task {task.name}: {e}")
        
        return created_checkpoints

    def _create_approval_request(self, task, document):
        """Create approval request for document processing (if approvals module is available)"""
        self.ensure_one()
        
        # Check if approvals module is available
        if 'approval.request' not in self.env:
            _logger.info("Approvals module not available, skipping approval request creation")
            return False
        
        try:
            # Get or create document approval category
            category = self._get_or_create_approval_category(document.category)
            
            if not category:
                _logger.warning(f"Could not create approval category for document {document.name}")
                return False
            
            # Create approval request
            approval_vals = {
                'name': f'Approve {document.name}',
                'category_id': category.id,
                'request_owner_id': task.user_ids[0].id if task.user_ids else self.env.user.id,
                'reference': f'Task: {task.name} | Document: {document.name} | Project: {task.project_id.name}',
                'date_start': fields.Date.today(),
                'date_end': fields.Date.add(fields.Date.today(), days=7),
                'request_status': 'pending',
            }
            
            approval_request = self.env['approval.request'].create(approval_vals)
            
            # Link approval to task (if task has approval_request_id field)
            if hasattr(task, 'approval_request_id'):
                task.write({'approval_request_id': approval_request.id})
            
            _logger.info(f"Created approval request '{approval_request.name}' for task '{task.name}'")
            return approval_request
            
        except Exception as e:
            _logger.warning(f"Failed to create approval request for task {task.name}: {e}")
            return False

    def _get_or_create_approval_category(self, document_category):
        """Get or create approval category for document type"""
        self.ensure_one()
        
        try:
            if 'approval.category' not in self.env:
                return False
            
            # Map document categories to approval category names
            category_mapping = {
                'required': 'Required Document Approval',
                'compliance': 'Compliance Document Approval',
                'deliverable': 'Deliverable Document Approval',
                'reference': 'Reference Document Approval'
            }
            
            category_name = category_mapping.get(document_category, 'Document Approval')
            
            # Search for existing category
            category = self.env['approval.category'].search([
                ('name', '=', category_name)
            ], limit=1)
            
            if not category:
                # Create new approval category
                category_vals = {
                    'name': category_name,
                    'description': f'Approval workflow for {document_category} documents',
                    'approval_minimum': 1,
                    'has_product': False,
                    'has_reference': True,
                    'has_date': True,
                    'has_period': False,
                    'has_quantity': False,
                    'has_amount': False,
                    'has_tax': False,
                    'has_partner': False,
                    'has_payment_method': False,
                    'has_location': False,
                    'has_delivery_address': False,
                }
                
                category = self.env['approval.category'].create(category_vals)
                _logger.info(f"Created new approval category '{category_name}'")
            
            return category
            
        except Exception as e:
            _logger.warning(f"Failed to get/create approval category for {document_category}: {e}")
            return False

    def _get_category_color(self, category):
        """Get color code for document category tags"""
        color_mapping = {
            'required': 1,      # Red
            'compliance': 2,    # Orange  
            'deliverable': 3,   # Yellow
            'reference': 4,     # Blue
        }
        return color_mapping.get(category, 0)  # Default to no color
