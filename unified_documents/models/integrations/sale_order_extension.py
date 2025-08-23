# -*- coding: utf-8 -*-
import logging
from odoo import models, api, fields, _

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        """Override to create projects for workflow products and copy documents"""
        res = super().action_confirm()
        self._create_projects_from_workflow_products()
        return res

    def _create_projects_from_workflow_products(self):
        """Create projects for products with workflow service tracking and copy documents"""
        for order in self:
            try:
                _logger.info(f"Processing order {order.name} for workflow products")
                
                # Find products with workflow service tracking
                workflow_products = order.order_line.mapped('product_id').filtered(
                    lambda p: p.service_tracking in ['project_only', 'task_new_project', 'task_global_project']
                )
                
                if not workflow_products:
                    _logger.info(f"No workflow products found in order {order.name}")
                    continue
                
                _logger.info(f"Found {len(workflow_products)} workflow products in order {order.name}")
                
                # Check if project already exists for this order
                existing_projects = self.env['project.project'].search([
                    ('sale_line_id.order_id', '=', order.id)
                ])
                
                if existing_projects:
                    projects = existing_projects
                    _logger.info(f"Using existing project(s) for order {order.name}")
                else:
                    # Create project
                    project_vals = {
                        "name": f"{order.name} - {order.partner_id.name}",
                        "sale_line_id": order.order_line[0].id if order.order_line else False,
                        "user_id": order.user_id.id,
                        "partner_id": order.partner_id.id,
                    }
                    
                    project = self.env["project.project"].create(project_vals)
                    projects = project
                    _logger.info(f"Created new project {project.name} for order {order.name}")
                
                # Create tasks from templates and copy documents for each project
                for project in projects:
                    try:
                        _logger.info(f"Creating tasks from templates for project {project.name}")
                        self._create_tasks_from_templates(project, workflow_products)
                    except Exception as task_error:
                        _logger.error(f"Error creating tasks for project {project.name}: {task_error}")
                        continue
                    
                    # Copy documents from product templates to project
                    try:
                        _logger.info(f"Copying documents from products to project {project.name}")
                        self._copy_documents_from_products_to_project(project, workflow_products)
                    except Exception as doc_error:
                        _logger.error(f"Error copying documents for project {project.name}: {doc_error}")
                        continue
                    
            except Exception as e:
                _logger.error(f"Error processing order {order.name}: {e}")
                continue

    def _check_existing_task(self, project, template_name):
        """Check if a task with the same name already exists in the project"""
        existing_task = self.env['project.task'].search([
            ('name', '=', template_name),
            ('project_id', '=', project.id)
        ], limit=1)
        
        if existing_task:
            _logger.info(f"Task '{template_name}' already exists in project '{project.name}' (ID: {existing_task.id})")
            return existing_task
        return False

    def _create_tasks_from_templates(self, project, workflow_products):
        """Create tasks from product task templates with duplicate prevention"""
        for product in workflow_products:
            _logger.info(f"Processing product {product.name} for task templates")
            
            # Check if product has task templates (from project_templates_basic)
            if hasattr(product, 'task_template_ids') and product.task_template_ids:
                _logger.info(f"Found {len(product.task_template_ids)} task templates for product {product.name}")
                
                for template in product.task_template_ids:
                    try:
                        _logger.info(f"Processing template: {template.name}")
                        
                        # Check for existing task with same name
                        existing_task = self._check_existing_task(project, template.name)
                        
                        if existing_task:
                            _logger.info(f"Task '{template.name}' already exists, skipping creation")
                            continue
                        
                        # Create task from template
                        task_vals = {
                            'name': template.name,
                            'description': template.description or '',
                            'project_id': project.id,
                            'user_ids': [(6, 0, template.user_ids.ids)] if template.user_ids else False,
                            'allocated_hours': template.planned_hours or 0.0,
                            'priority': template.priority or '0',
                            'tag_ids': [(6, 0, template.tag_ids.ids)] if template.tag_ids else False,
                        }
                        
                        task = self.env['project.task'].create(task_vals)
                        _logger.info(f"Created task '{task.name}' from template '{template.name}'")
                        
                        # Copy documents from project to task if project has documents
                        if hasattr(project, 'document_ids') and project.document_ids:
                            try:
                                self._copy_documents_from_project_to_task(task, project)
                                _logger.info(f"Copied documents from project to task '{task.name}'")
                            except Exception as doc_error:
                                _logger.warning(f"Failed to copy documents to task '{task.name}': {doc_error}")
                        else:
                            _logger.info(f"Skipping document copy for existing task '{task.name}' - already has documents")
                        
                    except Exception as e:
                        _logger.error(f"Error processing template {template.name}: {e}")
                        continue
            else:
                _logger.info(f"No task templates found for product {product.name}")

    def _copy_documents_from_products_to_project(self, project, workflow_products):
        """Copy documents from products to project using unified_documents model"""
        _logger.info(f"Copying documents from products to project {project.name}")
        
        # Deduplication set for this project
        copied_docs = set()
        total_copied = 0
        
        for product in workflow_products:
            _logger.info(f"Processing product {product.name} for document copying")
            
            if hasattr(product, 'document_ids') and product.document_ids:
                _logger.info(f"Found {len(product.document_ids)} documents for product {product.name}")
                
                for doc in product.document_ids:
                    # Create unique key for deduplication
                    doc_key = (project.id, doc.name, doc.category)
                    
                    if doc_key not in copied_docs:
                        copied_docs.add(doc_key)
                        try:
                            # Create copy of document linked to project
                            new_doc_vals = {
                                'name': f"{doc.name} - {project.name}",
                                'category': doc.category or 'reference',
                                'status': doc.status or 'draft',
                                'priority': doc.priority or '1',
                                'description': doc.description or '',
                                'notes': doc.notes or '',
                                'tag_ids': [(6, 0, doc.tag_ids.ids)] if doc.tag_ids else False,
                                'res_model': 'project.project',
                                'res_id': project.id,
                                'linked_project_id': project.id,  # CRITICAL for document list
                                'linked_product_id': product.id,  # Keep reference to original
                            }
                            
                            # Copy attachment if exists and is valid
                            if doc.attachment_id and doc.attachment_id.exists():
                                new_doc_vals['attachment_id'] = doc.attachment_id.id
                            
                            # Create document with error handling
                            new_doc = self.env['documents.document'].sudo().create(new_doc_vals)
                            total_copied += 1
                            _logger.info(f"Copied document '{doc.name}' to project '{project.name}'")
                            
                        except Exception as e:
                            _logger.warning(f"Failed to copy document '{doc.name}': {e}")
                            continue
                    else:
                        _logger.info(f"Skipping duplicate document: {doc.name}")
            else:
                _logger.info(f"No documents found for product {product.name}")
        
        # Invalidate cache to ensure project.document_ids is updated
        if total_copied > 0:
            project.invalidate_cache(['document_ids', 'document_count', 'required_document_count', 'deliverable_document_count', 'reference_document_count', 'compliance_document_count'])
            _logger.info(f"Invalidated cache for project {project.name} after copying {total_copied} documents")

    def _copy_documents_from_project_to_task(self, task, project):
        """Copy documents from project to task using unified_documents model"""
        _logger.info(f"Copying documents from project {project.name} to task {task.name}")
        
        # Deduplication set for this task
        copied_docs = set()
        
        for doc in project.document_ids:
            # Create unique key for deduplication
            doc_key = (task.id, doc.name, doc.category)
            
            if doc_key not in copied_docs:
                copied_docs.add(doc_key)
                try:
                    new_doc_vals = {
                        'name': f"{doc.name} - {task.name}",
                        'category': doc.category,
                        'status': doc.status,
                        'priority': doc.priority,
                        'description': doc.description,
                        'notes': doc.notes,
                        'tag_ids': [(6, 0, doc.tag_ids.ids)] if doc.tag_ids else False,
                        'res_model': 'project.task',
                        'res_id': task.id,
                        'linked_task_id': task.id,  # Link to task
                        'linked_project_id': project.id,  # Keep project reference
                    }
                    
                    # Copy attachment if exists
                    if doc.attachment_id and doc.attachment_id.exists():
                        new_doc_vals['attachment_id'] = doc.attachment_id.id
                    
                    self.env['documents.document'].create(new_doc_vals)
                    _logger.info(f"Copied document '{doc.name}' to task '{task.name}'")
                    
                except Exception as e:
                    _logger.warning(f"Failed to copy document '{doc.name}' to task: {e}")
                    continue
            else:
                _logger.info(f"Skipping duplicate document: {doc.name}")

    def action_copy_documents_to_projects(self):
        """Directly copy documents from products to their respective projects for all order lines"""
        self.ensure_one()
        copied_count = 0
        failed_count = 0
        total_documents = 0
        
        # First, count total documents to copy
        for line in self.order_line:
            if line.product_id and line.product_id.document_ids and line.project_id:
                total_documents += len(line.product_id.document_ids)
        
        if total_documents == 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Documents to Copy'),
                    'message': _('No documents found in products linked to this sales order.'),
                    'type': 'info',
                }
            }
        
        # Now copy documents
        for line in self.order_line:
            if line.product_id and line.product_id.document_ids and line.project_id:
                try:
                    # Use the direct copy method from sale order line
                    copied = line._direct_copy_documents_to_project(line.project_id)
                    if copied:  # This returns True/False, not a count
                        copied_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    _logger.warning(f"Failed to copy documents for line {line.name}: {e}")
                    failed_count += 1
        
        # Prepare result message
        if copied_count > 0:
            message = f"Successfully copied documents for {copied_count} order line(s)"
            if failed_count > 0:
                message += f". Failed for {failed_count} line(s)"
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Documents Copied'),
                    'message': message,
                    'type': 'success' if failed_count == 0 else 'warning',
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Copy Failed'),
                    'message': _('Failed to copy documents. Please check if projects are created and products have documents.'),
                    'type': 'error',
                }
            }
