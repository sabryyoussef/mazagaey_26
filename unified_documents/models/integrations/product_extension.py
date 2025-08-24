# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Document relationships (One2many fields)
    document_ids = fields.One2many(
        'documents.document', 'linked_product_id',
        string='Documents'
    )
    required_document_ids = fields.One2many(
        'documents.document', 'linked_product_id',
        domain=[('category', '=', 'required')],
        string='Required Documents'
    )
    deliverable_document_ids = fields.One2many(
        'documents.document', 'linked_product_id',
        domain=[('category', '=', 'deliverable')],
        string='Deliverable Documents'
    )

    # Document count fields
    document_count = fields.Integer(
        compute='_compute_document_counts', 
        store=True,
        string='Total Documents'
    )
    required_document_count = fields.Integer(
        compute='_compute_document_counts', 
        store=True,
        string='Required Document Count'
    )
    deliverable_document_count = fields.Integer(
        compute='_compute_document_counts', 
        store=True,
        string='Deliverable Document Count'
    )

    # Temporary fields for document creation
    new_document_name = fields.Char('Document Name')
    new_document_category = fields.Selection([
        ('required', 'Required'),
        ('deliverable', 'Deliverable'),
        ('reference', 'Reference'),
        ('compliance', 'Compliance')
    ], string='Category', default='required')
    new_document_priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Critical')
    ], string='Priority', default='1')
    new_document_status = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('verified', 'Verified'),
        ('delivered', 'Delivered'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')
    new_document_expiry_date = fields.Date('Expiry Date')
    new_document_notes = fields.Text('Notes')
    new_document_tag_ids = fields.Many2many('documents.tag', string='Document Tags')
    
    # Project Template fields (using existing project_template_id from sale_project)
    create_project_template = fields.Boolean(
        string='Auto-Create Project Template',
        default=False,
        help='Automatically create a project template when service tracking is set to Project and Task'
    )
    
    project_template_name = fields.Char(
        string='Project Template Name',
        help='Custom name for the project template (optional)'
    )
    
    # Task template count
    task_template_count = fields.Integer(
        string='Task Template Count',
        compute='_compute_task_template_count',
        store=True,
        help='Number of task templates for this product'
    )
    

    


    @api.depends('document_ids', 'required_document_ids', 'deliverable_document_ids')
    def _compute_document_counts(self):
        """Compute document counts for products"""
        for product in self:
            # Use the direct One2many relationship
            documents = product.document_ids
            required_docs = product.required_document_ids
            deliverable_docs = product.deliverable_document_ids
            

            
            product.document_count = len(documents)
            product.required_document_count = len(required_docs)
            product.deliverable_document_count = len(deliverable_docs)

    @api.depends('project_template_id.task_ids')
    def _compute_task_template_count(self):
        """Compute task template count for products"""
        for product in self:
            if hasattr(product, 'project_template_id') and product.project_template_id:
                product.task_template_count = len(product.project_template_id.task_ids)
            else:
                product.task_template_count = 0



    def _invalidate_document_fields(self):
        """Invalidate all document-related computed fields"""
        self._invalidate_cache(['document_count', 'required_document_count', 'deliverable_document_count'])

    def action_view_documents(self):
        """Open documents view for this product"""
        self.ensure_one()
        return {
            'name': _('Product Documents'),
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'list,form',
            'domain': [
                ('linked_product_id', '=', self.id)
            ],
            'context': {
                'default_linked_product_id': self.id,
            },
        }

    def action_create_document(self):
        """Create a new document record for this product"""
        self.ensure_one()
        
        if not self.new_document_name:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Missing Information'),
                    'message': _('Please enter a document name.'),
                    'type': 'warning',
                }
            }
        
        # Get or create product folder (optional)
        product_folder = self.env['documents.document']._get_product_folder(self)
        
        # Create the document record
        document_vals = {
            'name': self.new_document_name,
            'category': self.new_document_category,
            'priority': self.new_document_priority,
            'status': self.new_document_status,
            'expiry_date': self.new_document_expiry_date,
            'notes': self.new_document_notes,
            'tag_ids': [(6, 0, self.new_document_tag_ids.ids)] if self.new_document_tag_ids else False,
            'linked_product_id': self.id,
        }
        
        # Add folder_id only if folder was created successfully
        if product_folder:
            document_vals['folder_id'] = product_folder.id
        
        new_document = self.env['documents.document'].create(document_vals)
        
        # Clear the temporary fields
        self.write({
            'new_document_name': False,
            'new_document_category': 'required',
            'new_document_priority': '1',
            'new_document_status': 'draft',
            'new_document_expiry_date': False,
            'new_document_notes': False,
            'new_document_tag_ids': [(5, 0, 0)],
        })
        
        # Refresh the document counts
        self._invalidate_cache(['document_count', 'required_document_count', 'deliverable_document_count'])
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Document Created'),
                'message': _('Document "%s" has been created. Use the Upload button to add the file.') % new_document.name,
                'type': 'success',
            }
        }

    def action_refresh_documents(self):
        """Refresh the document list and counts"""
        self.ensure_one()
        
        # Force recomputation of One2many fields
        self._invalidate_cache(['document_ids', 'required_document_ids', 'deliverable_document_ids'])
        
        # Also force recomputation of count fields
        self._invalidate_document_fields()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Documents Refreshed'),
                'message': _('Document list has been refreshed.'),
                'type': 'success',
            }
        }

    def action_fix_document_tags(self):
        """Fix existing documents that might not have tag_ids field properly initialized"""
        self.ensure_one()
        documents = self.env['documents.document'].search([
            ('res_model', '=', 'product.template'),
            ('res_id', '=', self.id),
            ('active', '=', True)
        ])
        
        fixed_count = 0
        for doc in documents:
            # Force recomputation of tag_ids field
            doc._invalidate_cache(['tag_ids'])
            fixed_count += 1
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Tags Fixed'),
                'message': _('Fixed tag display for %d documents.') % fixed_count,
                'type': 'success',
            }
        }

    def action_copy_documents_to_project(self):
        """Open wizard to copy documents from this product to a project"""
        self.ensure_one()
        
        return {
            'name': _('Copy Documents to Project'),
            'type': 'ir.actions.act_window',
            'res_model': 'copy.documents.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_source_model': 'product.template',
                'default_source_id': self.id,
            }
        }

    def action_view_required_documents(self):
        """Open required documents view for this product"""
        self.ensure_one()
        return {
            'name': _('Required Documents - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'list,form',
            'domain': [
                ('linked_product_id', '=', self.id),
                ('category', '=', 'required')
            ],
            'context': {
                'default_linked_product_id': self.id,
                'default_category': 'required',
            },
        }

    def action_view_deliverable_documents(self):
        """Open deliverable documents view for this product"""
        self.ensure_one()
        return {
            'name': _('Deliverable Documents - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'list,form',
            'domain': [
                ('linked_product_id', '=', self.id),
                ('category', '=', 'deliverable')
            ],
            'context': {
                'default_linked_product_id': self.id,
                'default_category': 'deliverable',
            },
        }

    def action_upload_product_document(self):
        """Upload a new document for this product"""
        self.ensure_one()
        return {
            'name': _('Upload Document for %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_linked_product_id': self.id,
                'default_name': 'New Document',
                'default_category': 'required',
                'form_view_initial_mode': 'edit',
            }
        }

    def action_copy_documents_to_project(self):
        """Copy documents from this product to a project"""
        self.ensure_one()
        
        # Check if we have a target project in context
        target_project_id = self.env.context.get('default_target_project_id')
        if not target_project_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Target Project'),
                    'message': _('Please select a target project first.'),
                    'type': 'warning',
                }
            }
        
        return {
            'name': _('Copy Documents from %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'copy.documents.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_source_model': 'product.template',
                'default_source_id': self.id,
                'default_source_product_id': self.id,
                'default_target_model': 'project.project',
                'default_target_id': target_project_id,
                'default_target_project_id': target_project_id,
            }
        }

    # Project Template Methods
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.service_tracking == 'task_in_project' and record.create_project_template:
                record._create_product_project_template()
        return records

    def write(self, vals):
        result = super().write(vals)
        
        # Check if service_tracking is being set to task_in_project
        if vals.get('service_tracking') == 'task_in_project':
            for record in self:
                if record.create_project_template and not (hasattr(record, 'project_template_id') and record.project_template_id):
                    record._create_product_project_template()
        
        # Check if create_project_template is being set to True
        if vals.get('create_project_template'):
            for record in self:
                if record.service_tracking == 'task_in_project' and not (hasattr(record, 'project_template_id') and record.project_template_id):
                    record._create_product_project_template()
        
        # Check if project_template_id is being set and copy documents automatically
        if vals.get('project_template_id'):
            for record in self:
                if record.project_template_id:
                    # Use a safer approach - only copy if the product doesn't already have documents
                    if not record.document_ids:
                        record._copy_documents_from_project_template()
        
        return result

    def _create_product_project_template(self):
        """Create a project template specific to this product"""
        self.ensure_one()
        
        # Use custom name or default name
        if self.project_template_name:
            template_name = self.project_template_name
        else:
            # Generate a more descriptive default name
            template_name = f"{self.name} - Service Project Template"
        
        # Create project template (using existing project.project model)
        template_vals = {
            'name': template_name,
            'description': f"Auto-generated project template for {self.name}",
            'is_template': True,  # Mark as template so it appears in Project Templates menu
            'template_category': 'general',  # Default category
            'template_description': f"Auto-generated project template for {self.name} service",
            'estimated_duration': 15,  # Default estimated duration
            'complexity_level': 'medium',  # Default complexity
        }
        
        # Add timesheet fields if available (hr_timesheet module)
        if 'allow_timesheets' in self.env['project.project']._fields:
            template_vals['allow_timesheets'] = True
        if 'allow_billable' in self.env['project.project']._fields:
            template_vals['allow_billable'] = True
        
        project_template = self.env['project.project'].create(template_vals)
        
        # Create default tasks for this product
        default_tasks = [
            {
                'name': f'{self.name} - Setup',
                'description': f'Initial setup for {self.name} project',
                'sequence': 10,
                'priority': '1',
            },
            {
                'name': f'{self.name} - Requirements',
                'description': f'Requirements gathering for {self.name}',
                'sequence': 20,
                'priority': '1',
            },
            {
                'name': f'{self.name} - Development',
                'description': f'Core development for {self.name}',
                'sequence': 30,
                'priority': '0',
            },
            {
                'name': f'{self.name} - Testing',
                'description': f'Testing and QA for {self.name}',
                'sequence': 40,
                'priority': '1',
            },
            {
                'name': f'{self.name} - Delivery',
                'description': f'Final delivery of {self.name}',
                'sequence': 50,
                'priority': '1',
            },
        ]
        
        # Create tasks with dependencies
        previous_task = None
        for task_data in default_tasks:
            task_vals = {
                'name': task_data['name'],
                'description': task_data['description'],
                'sequence': task_data['sequence'],
                'priority': task_data['priority'],
                'project_id': project_template.id,
            }
            
            task = self.env['project.task'].create(task_vals)
            
            # Set dependencies (each task depends on the previous one)
            if previous_task:
                task.depend_on_ids = [(4, previous_task.id)]
            
            previous_task = task
        
        # Link the template to the product
        if hasattr(self, 'project_template_id'):
            self.project_template_id = project_template.id
        
        return project_template

    def action_view_project_template(self):
        """Open the project template"""
        self.ensure_one()
        if hasattr(self, 'project_template_id') and self.project_template_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.project',
                'res_id': self.project_template_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return False

    def action_create_custom_project_template(self):
        """Manually create a custom project template"""
        self.ensure_one()
        
        # Check if user wants to set a custom name
        if not self.project_template_name:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Custom Name Required'),
                    'message': _('Please enter a custom project template name before creating the template.'),
                    'type': 'warning',
                }
            }
        
        project_template = self._create_product_project_template()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Project Template Created'),
                'message': _('Project template "%s" has been created successfully and is now available in the Project Templates menu.') % project_template.name,
                'type': 'success',
            }
        }

    def action_edit_project_template(self):
        """Edit the existing project template"""
        self.ensure_one()
        if hasattr(self, 'project_template_id') and self.project_template_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.project',
                'res_id': self.project_template_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return False

    def action_create_project_with_documents(self):
        """Create project template with document-based tasks"""
        self.ensure_one()
        
        if not self.document_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Documents'),
                    'message': _('This product has no documents to create tasks from.'),
                    'type': 'warning',
                }
            }
        
        # Create project template without default tasks
        if self.project_template_name:
            template_name = self.project_template_name
        else:
            template_name = f"{self.name} - Document-Based Project Template"
        template_vals = {
            'name': template_name,
            'description': f"Auto-generated project template for {self.name} with document-based tasks",
            'is_template': True,  # Mark as template so it appears in Project Templates menu
            'template_category': 'general',  # Default category
            'template_description': f"Auto-generated project template for {self.name} with document-based tasks",
            'estimated_duration': 15,  # Default estimated duration
            'complexity_level': 'medium',  # Default complexity
        }
        
        # Add timesheet fields if available (hr_timesheet module)
        if 'allow_timesheets' in self.env['project.project']._fields:
            template_vals['allow_timesheets'] = True
        if 'allow_billable' in self.env['project.project']._fields:
            template_vals['allow_billable'] = True
        
        template = self.env['project.project'].create(template_vals)
        
        # Link the template to the product
        if hasattr(self, 'project_template_id'):
            self.project_template_id = template.id
        
        # Create tasks based on documents
        created_tasks = []
        for doc in self.document_ids:
            task_vals = {
                'name': f"{doc.name} - Task",
                'description': f"Task based on document: {doc.name}",
                'sequence': doc.id * 10,  # Use document ID for sequence
                'priority': '1' if doc.category == 'required' else '0',
                'project_id': template.id,
            }
            
            task = self.env['project.task'].create(task_vals)
            created_tasks.append(task)
        
        # Copy documents from product to project template
        try:
            document_service = self.env['unified.document.service']
            copied_docs = document_service.copy_product_documents_to_project(template, self)
            _logger.info(f"Copied {len(copied_docs.get('required', []))} required and {len(copied_docs.get('deliverable', []))} deliverable documents to project template")
        except Exception as e:
            _logger.warning(f"Failed to copy documents to project template: {e}")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Project Template Created'),
                'message': _('Project template created with %d document-based tasks and documents copied.') % len(created_tasks),
                'type': 'success',
            }
        }

    def action_view_task_templates(self):
        """Open tasks view for this product's project template"""
        self.ensure_one()
        if hasattr(self, 'project_template_id') and self.project_template_id:
            return {
                'name': _('Tasks - %s') % self.name,
                'type': 'ir.actions.act_window',
                'res_model': 'project.task',
                'view_mode': 'list,form',
                'domain': [
                    ('project_id', '=', self.project_template_id.id)
                ],
                'context': {
                    'default_project_id': self.project_template_id.id,
                },
            }
        return False

    def action_create_task_template(self):
        """Create a new task for this product's project template"""
        self.ensure_one()
        if not hasattr(self, 'project_template_id') or not self.project_template_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Project Template'),
                    'message': _('Please create a project template first.'),
                    'type': 'warning',
                }
            }
        
        return {
            'name': _('Create Task'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_project_id': self.project_template_id.id,
            },
        }

    def action_test_document_copy(self):
        """Test method to simulate document copying when project is created"""
        self.ensure_one()
        
        if not self.document_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Documents'),
                    'message': _('This product has no documents to test copying.'),
                    'type': 'warning',
                }
            }
        
        # Create a test project to simulate the process
        test_project_vals = {
            'name': f"TEST - {self.name} - Document Copy Test",
            'description': f"Test project to verify document copying from {self.name}",
        }
        
        # Add timesheet fields if available
        if 'allow_timesheets' in self.env['project.project']._fields:
            test_project_vals['allow_timesheets'] = True
        if 'allow_billable' in self.env['project.project']._fields:
            test_project_vals['allow_billable'] = True
        
        test_project = self.env['project.project'].create(test_project_vals)
        
        # Test the document copying logic using the safer approach
        try:
            # Use the same logic as in sale_order_line_extension but with better error handling
            copied_count = 0
            for doc in self.document_ids:
                try:
                    # Create a copy of the document linked to the project
                    new_doc_vals = {
                        'name': f"{doc.name} - {test_project.name}",
                        'category': doc.category or 'reference',  # Provide default category
                        'status': doc.status or 'draft',  # Provide default status
                        'priority': doc.priority or '1',  # Provide default priority
                        'description': doc.description or '',
                        'notes': doc.notes or '',
                        'tag_ids': [(6, 0, doc.tag_ids.ids)] if doc.tag_ids else False,
                        'res_model': 'project.project',
                        'res_id': test_project.id,
                        'linked_product_id': self.id,  # Keep reference to original product
                    }
                    
                    # Copy attachment if exists and is valid
                    if doc.attachment_id and doc.attachment_id.exists():
                        new_doc_vals['attachment_id'] = doc.attachment_id.id
                    
                    # Create document with sudo to avoid permission issues
                    new_doc = self.env['documents.document'].sudo().create(new_doc_vals)
                    copied_count += 1
                    
                except Exception as e:
                    _logger.warning(f"Failed to copy document '{doc.name}': {e}")
                    continue  # Continue with next document
            
            # Open the test project to show the results
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.project',
                'res_id': test_project.id,
                'view_mode': 'form',
                'target': 'current',
                'context': {},
            }
            
        except Exception as e:
            _logger.error(f"Test document copy failed: {e}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Test Failed'),
                    'message': _('Document copy test failed: %s') % str(e),
                    'type': 'danger',
                }
            }

    def _copy_documents_from_project_template(self):
        """Copy documents from the selected project template to this product"""
        self.ensure_one()
        
        if not self.project_template_id:
            return False
        
        project_template = self.project_template_id
        
        # Check if project template has documents
        if not hasattr(project_template, 'document_ids') or not project_template.document_ids:
            _logger.info(f"Project template {project_template.name} has no documents to copy")
            return False
        
        # Use a safer approach with try-catch and transaction handling
        try:
            copied_count = 0
            for doc in project_template.document_ids:
                try:
                    # Create a copy of the document linked to the product
                    new_doc_vals = {
                        'name': f"{doc.name} - {self.name}",
                        'category': doc.category or 'reference',
                        'status': doc.status or 'draft',
                        'priority': doc.priority or '1',
                        'description': doc.description or '',
                        'notes': doc.notes or '',
                        'tag_ids': [(6, 0, doc.tag_ids.ids)] if doc.tag_ids else False,
                        'linked_product_id': self.id,  # Link to this product
                        'res_model': 'product.template',
                        'res_id': self.id,
                    }
                    
                    # Copy attachment if exists and is valid
                    if doc.attachment_id and doc.attachment_id.exists():
                        new_doc_vals['attachment_id'] = doc.attachment_id.id
                    
                    # Create document with sudo to avoid permission issues
                    new_doc = self.env['documents.document'].sudo().create(new_doc_vals)
                    copied_count += 1
                    
                    _logger.info(f"Copied document '{doc.name}' from project template '{project_template.name}' to product '{self.name}'")
                    
                except Exception as e:
                    _logger.warning(f"Failed to copy document '{doc.name}' from project template: {e}")
                    continue
            
            # Invalidate cache to ensure product.document_ids is updated
            if copied_count > 0:
                self.invalidate_cache(['document_ids', 'document_count', 'required_document_count', 'deliverable_document_count'])
                _logger.info(f"Invalidated cache for product {self.name} after copying {copied_count} documents from project template")
            
            _logger.info(f"Project template copy completed: {copied_count} documents copied from template {project_template.name} to product {self.name}")
            return copied_count > 0
            
        except Exception as e:
            _logger.error(f"Failed to copy documents from project template: {e}")
            return False

    def action_copy_documents_from_project_template(self):
        """Manual action to copy documents from project template to product"""
        self.ensure_one()
        
        if not self.project_template_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Project Template'),
                    'message': _('Please select a project template first.'),
                    'type': 'warning',
                }
            }
        
        # Use a safer approach with transaction handling
        try:
            copied = self._copy_documents_from_project_template()
            
            if copied:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Documents Copied'),
                        'message': _('Documents have been copied from the project template to this product successfully.'),
                        'type': 'success',
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('No Documents Copied'),
                        'message': _('No documents were copied. The project template may not have any documents.'),
                        'type': 'info',
                    }
                }
        except Exception as e:
            _logger.error(f"Error in action_copy_documents_from_project_template: {e}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('An error occurred while copying documents. Please try again.'),
                    'type': 'error',
                }
            }
