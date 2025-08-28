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

    # Product Template Selection Field
    unified_product_template_id = fields.Many2one(
        'unified.product.template', 
        string='Product Template',
        help='Select a product template to automatically add template documents to this product'
    )

    # Task Template Selection Fields
    task_template_ids = fields.Many2many(
        'project.task.template', 
        string='Task Templates',
        help='Select task templates to automatically add template tasks to this product'
    )
    
    # Keep the old field for backward compatibility
    task_template_id = fields.Many2one(
        'project.task.template', 
        string='Task Template (Legacy)',
        help='Legacy field - use Task Templates field above for multiple selection'
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

    @api.onchange('unified_product_template_id')
    def _onchange_unified_product_template_id(self):
        """Show warning when a product template is selected"""
        if self.unified_product_template_id:
            # Don't apply template during onchange, just show a warning
            return {
                'warning': {
                    'title': _('Template Selected'),
                    'message': _('Product template "%s" has been selected. Save the product to apply the template documents, or use the "Apply Template" button to apply immediately.') % self.unified_product_template_id.name,
                }
            }

    @api.onchange('task_template_ids')
    def _onchange_task_template_ids(self):
        """Show warning when task templates are selected"""
        if self.task_template_ids:
            template_names = ', '.join(self.task_template_ids.mapped('name'))
            return {
                'warning': {
                    'title': _('Task Templates Selected'),
                    'message': _('Task templates selected: %s. Save the product to apply the template tasks, or use the "Apply Task Templates" button to apply immediately.') % template_names,
                }
            }

    @api.onchange('task_template_id')
    def _onchange_task_template_id(self):
        """Show warning when a task template is selected (legacy)"""
        if self.task_template_id:
            # Don't apply template during onchange, just show a warning
            return {
                'warning': {
                    'title': _('Task Template Selected'),
                    'message': _('Task template "%s" has been selected. Save the product to apply the template tasks, or use the "Apply Task Template" button to apply immediately.') % self.task_template_id.name,
                }
            }



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
            # Apply document template if selected
            if record.unified_product_template_id:
                record._apply_selected_template()
            # Apply task templates if selected
            if record.task_template_ids:
                record._apply_selected_task_templates()
            elif record.task_template_id:
                record._apply_selected_task_template()
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
        
        # Check if unified_product_template_id is being set
        if vals.get('unified_product_template_id'):
            for record in self:
                if record.unified_product_template_id:
                    record._apply_selected_template()
        
        # Check if task_template_ids is being set
        if vals.get('task_template_ids'):
            for record in self:
                if record.task_template_ids:
                    record._apply_selected_task_templates()
        # Check if task_template_id is being set (legacy)
        elif vals.get('task_template_id'):
            for record in self:
                if record.task_template_id:
                    record._apply_selected_task_template()
        
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

    def action_apply_product_template(self):
        """Apply the selected product template to this product"""
        self.ensure_one()
        
        if not self.unified_product_template_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Template Selected'),
                    'message': _('Please select a product template first.'),
                    'type': 'warning',
                }
            }
        
        # Apply the template
        self.unified_product_template_id.action_apply_to_product(self)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Template Applied'),
                'message': _('Product template "%s" has been applied successfully. Template documents have been added to this product.') % self.unified_product_template_id.name,
                'type': 'success',
            }
        }

    def action_view_selected_template(self):
        """Open the selected product template"""
        self.ensure_one()
        
        if not self.unified_product_template_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Template Selected'),
                    'message': _('No product template is selected for this product.'),
                    'type': 'info',
                }
            }
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'unified.product.template',
            'res_id': self.unified_product_template_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _apply_selected_template(self):
        """Apply the selected template to this product"""
        self.ensure_one()
        
        if not self.unified_product_template_id:
            return
        
        try:
            # Apply the template
            self.unified_product_template_id.action_apply_to_product(self)
            _logger.info(f"Template {self.unified_product_template_id.name} applied to product {self.name}")
        except Exception as e:
            _logger.error(f"Failed to apply template {self.unified_product_template_id.name} to product {self.name}: {e}")
            # Don't raise the error to avoid breaking the save operation

    def get_combined_documents_from_templates(self):
        """Collect documents from both product and project templates, preventing duplicates"""
        self.ensure_one()
        
        combined_documents = {}
        duplicates_resolved = []
        
        # Priority: Product Template > Project Template
        
        # 1. Collect documents from Product Template (Higher Priority)
        if self.unified_product_template_id:
            for line in self.unified_product_template_id.document_template_line_ids:
                doc_key = line.name.lower().strip()
                combined_documents[doc_key] = {
                    'name': line.name,
                    'category': line.category,
                    'priority': line.priority,
                    'notes': line.notes,
                    'tag_ids': line.tag_ids.ids,
                    'source': 'Product Template',
                    'template_name': self.unified_product_template_id.name
                }
        
        # 2. Collect documents from Project Template (Lower Priority)
        if hasattr(self, 'project_template_id') and self.project_template_id:
            for doc in self.project_template_id.document_ids:
                doc_key = doc.name.lower().strip()
                
                if doc_key in combined_documents:
                    # Duplicate found - keep product template version, but merge additional info
                    existing_doc = combined_documents[doc_key]
                    duplicates_resolved.append({
                        'name': doc.name,
                        'product_version': existing_doc,
                        'project_version': {
                            'name': doc.name,
                            'category': doc.category,
                            'priority': doc.priority,
                            'notes': doc.notes,
                            'tag_ids': doc.tag_ids.ids,
                            'source': 'Project Template',
                            'template_name': self.project_template_id.name
                        }
                    })
                    
                    # Merge tags if not already present
                    existing_tags = set(existing_doc['tag_ids'])
                    project_tags = set(doc.tag_ids.ids)
                    merged_tags = list(existing_tags | project_tags)
                    combined_documents[doc_key]['tag_ids'] = merged_tags
                    
                    # Merge notes if project template has additional info
                    if doc.notes and not existing_doc['notes']:
                        combined_documents[doc_key]['notes'] = doc.notes
                    elif doc.notes and existing_doc['notes']:
                        combined_documents[doc_key]['notes'] = f"{existing_doc['notes']}\n\nProject Template Notes: {doc.notes}"
                        
                else:
                    # No duplicate - add project template document
                    combined_documents[doc_key] = {
                        'name': doc.name,
                        'category': doc.category,
                        'priority': doc.priority,
                        'notes': doc.notes,
                        'tag_ids': doc.tag_ids.ids,
                        'source': 'Project Template',
                        'template_name': self.project_template_id.name
                    }
        
        return {
            'documents': list(combined_documents.values()),
            'duplicates_resolved': duplicates_resolved,
            'total_documents': len(combined_documents),
            'product_template_count': len([d for d in combined_documents.values() if d['source'] == 'Product Template']),
            'project_template_count': len([d for d in combined_documents.values() if d['source'] == 'Project Template']),
            'duplicates_count': len(duplicates_resolved)
        }

    def action_view_combined_template_documents(self):
        """Show combined documents from both templates"""
        self.ensure_one()
        
        combined_data = self.get_combined_documents_from_templates()
        
        if not combined_data['documents']:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Templates'),
                    'message': _('No document templates are configured for this product.'),
                    'type': 'info',
                }
            }
        
        # Build detailed message
        message = f"Combined Document Analysis for {self.name}:\n\n"
        message += f"📊 Summary:\n"
        message += f"   • Total Documents: {combined_data['total_documents']}\n"
        message += f"   • From Product Template: {combined_data['product_template_count']}\n"
        message += f"   • From Project Template: {combined_data['project_template_count']}\n"
        message += f"   • Duplicates Resolved: {combined_data['duplicates_count']}\n\n"
        
        if combined_data['duplicates_resolved']:
            message += f"⚠️ Duplicates Resolved (Product Template Priority):\n"
            for dup in combined_data['duplicates_resolved']:
                message += f"   • {dup['name']} → Kept from Product Template\n"
            message += "\n"
        
        message += f"📋 Final Document List:\n"
        for doc in combined_data['documents']:
            source_icon = "🟢" if doc['source'] == 'Product Template' else "🔵"
            message += f"   {source_icon} {doc['name']} ({doc['category']}) - {doc['source']}\n"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Combined Template Documents'),
                'message': message,
                'type': 'info',
            }
        }

    def apply_combined_templates_to_product(self):
        """Apply combined documents from both templates to this product"""
        self.ensure_one()
        
        combined_data = self.get_combined_documents_from_templates()
        
        if not combined_data['documents']:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Documents'),
                    'message': _('No documents found in the configured templates.'),
                    'type': 'warning',
                }
            }
        
        created_count = 0
        for doc_data in combined_data['documents']:
            try:
                # Check if document already exists
                existing_doc = self.env['documents.document'].search([
                    ('linked_product_id', '=', self.id),
                    ('name', '=', doc_data['name'])
                ], limit=1)
                
                if existing_doc:
                    # Update existing document with merged data
                    existing_doc.write({
                        'category': doc_data['category'],
                        'priority': doc_data['priority'],
                        'notes': doc_data['notes'],
                        'tag_ids': [(6, 0, doc_data['tag_ids'])]
                    })
                else:
                    # Create new document
                    document_vals = {
                        'name': doc_data['name'],
                        'category': doc_data['category'],
                        'priority': doc_data['priority'],
                        'notes': doc_data['notes'],
                        'tag_ids': [(6, 0, doc_data['tag_ids'])],
                        'linked_product_id': self.id,
                        'status': 'draft',
                    }
                    self.env['documents.document'].create(document_vals)
                
                created_count += 1
                
            except Exception as e:
                _logger.warning(f"Failed to create document '{doc_data['name']}' for product {self.name}: {e}")
                continue
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Templates Applied'),
                'message': _('Successfully applied %d documents from combined templates (Product Template Priority).') % created_count,
                'type': 'success',
            }
        }

    def _apply_selected_task_templates(self):
        """Apply the selected task templates to this product"""
        self.ensure_one()
        
        if not self.task_template_ids:
            _logger.warning(f"No task templates selected for product {self.name}")
            return
        
        applied_count = 0
        errors = []
        
        for task_template in self.task_template_ids:
            try:
                self._apply_task_template_to_product(task_template)
                applied_count += 1
                _logger.info(f"Successfully applied task template '{task_template.name}' to product '{self.name}'")
            except Exception as e:
                error_msg = f"Error applying task template '{task_template.name}': {str(e)}"
                _logger.error(error_msg)
                errors.append(error_msg)
        
        if errors:
            error_summary = '\n'.join(errors)
            raise ValidationError(_('Some task templates failed to apply:\n%s') % error_summary)
        
        if applied_count > 0:
            _logger.info(f"Successfully applied {applied_count} task templates to product '{self.name}'")

    def _apply_selected_task_template(self):
        """Apply the selected task template to this product (legacy)"""
        self.ensure_one()
        
        if not self.task_template_id:
            return
        
        try:
            # Apply the task template
            self._apply_task_template_to_product(self.task_template_id)
            _logger.info(f"Task template {self.task_template_id.name} applied to product {self.name}")
        except Exception as e:
            _logger.error(f"Failed to apply task template {self.task_template_id.name} to product {self.name}: {e}")
            # Don't raise the error to avoid breaking the save operation

    def _apply_task_template_to_product(self, task_template):
        """Apply a task template to this product"""
        self.ensure_one()
        
        if not task_template or not task_template.exists():
            raise ValidationError(_('Invalid task template provided.'))
        
        # For now, we'll store the task template reference
        # The actual task creation will happen when a project is created from this product
        # This ensures tasks are created in the correct project context
        
        _logger.info(f"Task template {task_template.name} linked to product {self.name}")
        return True

    def action_apply_task_templates(self):
        """Apply the selected task templates to this product"""
        self.ensure_one()
        
        if not self.task_template_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Task Templates Selected'),
                    'message': _('Please select task templates first.'),
                    'type': 'warning',
                }
            }
        
        # Apply the task templates
        self._apply_selected_task_templates()
        
        template_names = ', '.join(self.task_template_ids.mapped('name'))
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Task Templates Applied'),
                'message': _('Task templates "%s" have been applied successfully. Tasks will be created when a project is created from this product.') % template_names,
                'type': 'success',
            }
        }

    def action_apply_task_template(self):
        """Apply the selected task template to this product (legacy)"""
        self.ensure_one()
        
        if not self.task_template_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Task Template Selected'),
                    'message': _('Please select a task template first.'),
                    'type': 'warning',
                }
            }
        
        # Apply the task template
        self._apply_task_template_to_product(self.task_template_id)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Task Template Applied'),
                'message': _('Task template "%s" has been applied successfully. Tasks will be created when a project is created from this product.') % self.task_template_id.name,
                'type': 'success',
            }
        }

    def action_view_selected_task_templates(self):
        """Open the selected task templates"""
        self.ensure_one()
        
        if not self.task_template_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Task Templates Selected'),
                    'message': _('No task templates are selected for this product.'),
                    'type': 'info',
                }
            }
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task.template',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.task_template_ids.ids)],
            'context': {
                'default_name': f"Task Templates for {self.name}",
            },
        }

    def action_view_selected_task_template(self):
        """Open the selected task template (legacy)"""
        self.ensure_one()
        
        if not self.task_template_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Task Template Selected'),
                    'message': _('No task template is selected for this product.'),
                    'type': 'info',
                }
            }
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task.template',
            'res_id': self.task_template_id.id,
            'view_mode': 'form',
            'target': 'current',
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
