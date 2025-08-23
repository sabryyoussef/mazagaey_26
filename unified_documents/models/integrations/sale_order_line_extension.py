# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
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
        """Override to automatically copy documents when project is created"""
        # Call the original method to create the project
        project = super()._timesheet_create_project()
        
        # Automatically copy documents immediately when project is created
        if project and self.product_id and self.product_id.document_ids:
            try:
                # Copy documents immediately
                self._copy_product_documents_to_project(project)
                self.documents_copied = True
                _logger.info(f"Automatically copied documents from product {self.product_id.name} to project {project.name}")
                
                # Create document category tasks after documents are copied
                try:
                    created_tasks = project.create_document_category_tasks()
                    _logger.info(f"Created {len(created_tasks)} document category tasks for project {project.name}")
                except Exception as e:
                    _logger.warning(f"Failed to create document category tasks for project {project.name}: {e}")
                    
            except Exception as e:
                _logger.warning(f"Failed to copy documents from product {self.product_id.name} to project {project.name}: {e}")
        
        return project

    def copy_documents_to_project(self):
        """Copy documents from product to project"""
        self.ensure_one()
        
        if not self.project_id:
            _logger.warning(f"No project found for sale order line {self.name}")
            return False
        
        if not self.product_id or not self.product_id.document_ids:
            _logger.info(f"No documents found for product {self.product_id.name if self.product_id else 'None'}")
            return False
        
        # Use the document service to copy documents
        try:
            document_service = self.env['unified.document.service']
            if hasattr(document_service, 'copy_product_documents_to_project'):
                result = document_service.copy_product_documents_to_project(self.project_id, self.product_id)
                _logger.info(f"Document service copied documents: {result}")
                return bool(result)  # Return True if documents were copied
            else:
                # Fallback: direct copy if service is not available
                return self._direct_copy_documents_to_project(self.project_id)
        except Exception as e:
            _logger.warning(f"Document service failed, using fallback: {e}")
            return self._direct_copy_documents_to_project(self.project_id)

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
            return False
        
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
                    'linked_project_id': project.id,  # CRITICAL: Link to project for document list
                    # Remove linked_product_id to avoid foreign key constraint issues
                    # 'linked_product_id': self.product_id.id,  # Keep reference to original product
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
        
        # Invalidate cache to ensure project.document_ids is updated
        if copied_count > 0:
            project.invalidate_cache(['document_ids', 'document_count', 'required_document_count', 'deliverable_document_count', 'reference_document_count', 'compliance_document_count'])
            _logger.info(f"Invalidated cache for project {project.name} after copying {copied_count} documents")
        
        _logger.info(f"Direct copy completed: {copied_count} documents copied to project {project.name}")
        return copied_count > 0  # Return True if any documents were copied

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
                
                # Create document category tasks after documents are copied
                if line.project_id:
                    try:
                        created_tasks = line.project_id.create_document_category_tasks()
                        _logger.info(f"Cron job created {len(created_tasks)} document category tasks for project {line.project_id.name}")
                    except Exception as e:
                        _logger.warning(f"Cron job failed to create document category tasks for project {line.project_id.name}: {e}")
        
        _logger.info(f"Cron job copied documents for {copied_count} sale order lines")
        return copied_count
