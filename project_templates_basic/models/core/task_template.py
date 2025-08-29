# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class ProjectTaskTemplate(models.Model):
    _name = 'project.task.template'
    _description = 'Project Task Template'
    _order = 'sequence, name'

    # Basic Information
    name = fields.Char('Task Name', required=True)
    description = fields.Text('Description')
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)

    # Template Configuration
    template_type = fields.Selection([
        ('document_based', 'Document-Based'),
        ('progress_tracking', 'Progress Tracking'),
        ('milestone', 'Milestone'),
        ('custom', 'Custom')
    ], string='Template Type', required=True, default='document_based')

    # Document Classification
    document_category = fields.Selection([
        ('required', 'Required'),
        ('deliverable', 'Deliverable'),
        ('reference', 'Reference'),
        ('compliance', 'Compliance'),
        ('all', 'All Documents')
    ], string='Document Category', default='all')

    # Task Configuration
    task_name_pattern = fields.Char('Task Name Pattern', 
        help='Pattern for task names. Use {category}, {count}, {project} as placeholders')
    task_description_pattern = fields.Text('Task Description Pattern',
        help='Pattern for task descriptions. Use {category}, {count}, {project} as placeholders')
    estimated_hours = fields.Float('Estimated Hours', default=1.0)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Critical')
    ], string='Priority', default='1')

    # Dependencies
    prerequisite_task_ids = fields.Many2many('project.task.template', 
        'task_template_prerequisite_rel', 'task_id', 'prerequisite_id',
        string='Prerequisite Tasks')

    # Template Integration
    milestone_template_ids = fields.Many2many(
        'project.milestone.template', 
        'task_template_milestone_rel',
        'task_template_id', 'milestone_template_id',
        string='Milestone Templates',
        help='Select milestone templates to associate with this task template'
    )
    
    # Document Template Integration
    document_template_ids = fields.Many2many(
        'project.document.template',
        'task_template_document_rel',
        'task_template_id', 'document_template_id',
        string='Document Templates',
        help='Select document templates to associate with this task template'
    )
    
    # Checkpoint Template Integration
    checkpoint_template_ids = fields.Many2many(
        'project.checkpoint.template',
        'task_template_checkpoint_rel',
        'task_template_id', 'checkpoint_template_id',
        string='Checkpoint Templates',
        help='Select checkpoint templates to associate with this task template'
    )

    # Usage Tracking
    usage_count = fields.Integer('Usage Count', compute='_compute_usage_count', store=True)

    @api.depends()
    def _compute_usage_count(self):
        """Compute how many times this template has been used"""
        for template in self:
            # Count usage in task generation records
            usage_count = self.env['project.task.template.usage'].search_count([
                ('task_template_id', '=', template.id)
            ])
            template.usage_count = usage_count

    def get_task_name(self, context_data=None):
        """Generate task name based on pattern and context"""
        if not self.task_name_pattern:
            return self.name
        
        if not context_data:
            context_data = {}
        
        # Default placeholders
        placeholders = {
            'category': context_data.get('category', 'Documents'),
            'count': context_data.get('count', 0),
            'project': context_data.get('project_name', 'Project'),
            'template': self.name
        }
        
        # Replace placeholders in pattern
        task_name = self.task_name_pattern
        for key, value in placeholders.items():
            task_name = task_name.replace(f'{{{key}}}', str(value))
        
        return task_name

    def get_task_description(self, context_data=None):
        """Generate task description based on pattern and context"""
        if not self.task_description_pattern:
            return self.description or ''
        
        if not context_data:
            context_data = {}
        
        # Default placeholders
        placeholders = {
            'category': context_data.get('category', 'Documents'),
            'count': context_data.get('count', 0),
            'project': context_data.get('project_name', 'Project'),
            'template': self.name,
            'description': self.description or ''
        }
        
        # Replace placeholders in pattern
        task_description = self.task_description_pattern
        for key, value in placeholders.items():
            task_description = task_description.replace(f'{{{key}}}', str(value))
        
        return task_description

    def action_view_usage(self):
        """View usage history of this template"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Template Usage History'),
            'res_model': 'project.task.template.usage',
            'view_mode': 'list,form',
            'domain': [('task_template_id', '=', self.id)],
            'context': {'default_task_template_id': self.id},
        }

    def action_create_task_from_template(self):
        """Create a task from this template"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Task from Template'),
            'res_model': 'project.task',
            'view_mode': 'form',
            'context': {
                'default_name': self.get_task_name(),
                'default_description': self.get_task_description(),
                'default_priority': self.priority,
                'default_allocated_hours': self.estimated_hours,
            },
            'target': 'new',
        }
    
    def apply_to_task(self, task, product=None, project=None):
        """Apply this task template to an existing task, including documents from multiple sources"""
        self.ensure_one()
        
        # Update task with template data
        task.write({
            'name': self.get_task_name(),
            'description': self.get_task_description(),
            'priority': self.priority,
            'allocated_hours': self.estimated_hours,
        })
        
        # Collect documents from multiple sources
        documents_to_create = []
        
        # 1. Documents from Product (if product is provided)
        if product and hasattr(product, 'document_ids') and product.document_ids:
            for doc in product.document_ids:
                if self._should_include_product_document(doc):
                    documents_to_create.append({
                        'name': doc.name,
                        'category': doc.category or 'reference',
                        'priority': doc.priority or '1',
                        'notes': doc.notes or '',
                        'res_model': 'project.task',
                        'res_id': task.id,
                        'linked_project_id': project.id if project else False,
                        'status': 'draft',
                        'tag_ids': [(6, 0, doc.tag_ids.ids)] if doc.tag_ids else False,
                        'source': 'product',
                        'source_document_id': doc.id,
                    })
        
        # 2. Documents from Document Templates
        if self.document_template_ids:
            for doc_template in self.document_template_ids:
                documents_to_create.extend(self._create_documents_from_template(doc_template, task, project))
        
        # 3. Create all documents
        if 'documents.document' in self.env:
            for doc_vals in documents_to_create:
                # Add source tracking fields if they exist
                if hasattr(self.env['documents.document'], 'source'):
                    # Source tracking fields are already included in doc_vals
                    pass
                else:
                    # Remove source tracking fields if they don't exist
                    doc_vals.pop('source', None)
                    doc_vals.pop('source_document_id', None)
                    doc_vals.pop('source_template_id', None)
                    doc_vals.pop('template_line_id', None)
                
                self.env['documents.document'].create(doc_vals)
        else:
            _logger.warning("documents.document model not available, skipping document creation")
        
        # 4. Create checklist items from document templates
        if self.document_template_ids:
            for doc_template in self.document_template_ids:
                self._create_checklist_from_template(doc_template, task)
        
        # 5. Create checkpoints from checkpoint templates
        if self.checkpoint_template_ids:
            for checkpoint_template in self.checkpoint_template_ids:
                self._create_checkpoints_from_template(checkpoint_template, task, project)
        
        # 6. Record usage
        self._record_template_usage(task, product, project)
        
        return True
    
    def _should_include_product_document(self, product_doc):
        """Determine if a product document should be included based on task template settings"""
        # If document category is 'all', include all documents
        if self.document_category == 'all':
            return True
        
        # If document category matches, include the document
        if product_doc.category == self.document_category:
            return True
        
        # For document-based templates, include documents
        if self.template_type == 'document_based':
            return True
        
        return False
    
    def _create_documents_from_template(self, doc_template, task, project):
        """Create documents from a document template"""
        documents = []
        
        for line in doc_template.document_template_line_ids:
            documents.append({
                'name': line.name,
                'category': line.category,
                'priority': line.priority,
                'notes': line.notes or '',
                'res_model': 'project.task',
                'res_id': task.id,
                'linked_project_id': project.id if project else False,
                'status': 'draft',
                'tag_ids': [(6, 0, line.tag_ids.ids)] if line.tag_ids else False,
                'source': 'template',
                'source_template_id': doc_template.id,
                'template_line_id': line.id,
            })
        
        return documents
    
    def _create_checklist_from_template(self, doc_template, task):
        """Create checklist items from a document template"""
        # Check if the checklist model exists
        if 'project.checklist.item' not in self.env:
            _logger.warning("project.checklist.item model not available, skipping checklist creation")
            return
        
        for line in doc_template.checklist_template_line_ids:
            checklist_vals = {
                'name': line.name,
                'description': line.description or '',
                'task_id': task.id,
                'sequence': line.sequence,
                'is_required': line.is_required,
            }
            
            # Add source tracking fields if they exist
            if hasattr(self.env['project.checklist.item'], 'source'):
                checklist_vals.update({
                    'source': 'template',
                    'source_template_id': doc_template.id,
                    'template_line_id': line.id,
                })
            
            self.env['project.checklist.item'].create(checklist_vals)
    
    def _create_checkpoints_from_template(self, checkpoint_template, task, project):
        """Create checkpoints from a checkpoint template"""
        # Check if the checkpoint model exists
        if 'project.task.checkpoint' not in self.env:
            _logger.warning("project.task.checkpoint model not available, skipping checkpoint creation")
            return
        
        # Create the main checkpoint
        checkpoint_vals = {
            'name': checkpoint_template.name,
            'description': checkpoint_template.description or '',
            'task_id': task.id,
            'project_id': project.id if project else False,
            'sequence': checkpoint_template.sequence,
            'is_required': checkpoint_template.is_required,
            'checkpoint_type': checkpoint_template.checkpoint_type,
            'status': 'pending',
        }
        
        checkpoint = self.env['project.task.checkpoint'].create(checkpoint_vals)
        
        # Create checklist items for this checkpoint if they exist
        if hasattr(checkpoint_template, 'checklist_template_line_ids') and checkpoint_template.checklist_template_line_ids:
            for line in checkpoint_template.checklist_template_line_ids:
                checklist_vals = {
                    'name': line.name,
                    'description': line.description or '',
                    'checkpoint_id': checkpoint.id,
                    'sequence': line.sequence,
                    'is_required': line.is_required,
                }
                
                # Check if checkpoint checklist model exists
                if 'project.checkpoint.checklist.item' in self.env:
                    self.env['project.checkpoint.checklist.item'].create(checklist_vals)
                else:
                    _logger.warning("project.checkpoint.checklist.item model not available, skipping checkpoint checklist creation")
    
    def _record_template_usage(self, task, product, project):
        """Record that this template was used"""
        usage_vals = {
            'task_template_id': self.id,
            'task_id': task.id,
            'applied_by': self.env.user.id,
        }
        
        if product:
            usage_vals['project_template_id'] = product.project_template_id.id if hasattr(product, 'project_template_id') else False
        
        if project:
            usage_vals['project_id'] = project.id
        
        if 'project.task.template.usage' in self.env:
            self.env['project.task.template.usage'].create(usage_vals)
        else:
            _logger.warning("project.task.template.usage model not available, skipping usage recording")



    def action_view_milestone_templates(self):
        """Open the selected milestone templates"""
        self.ensure_one()
        
        if not self.milestone_template_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Milestone Templates Selected'),
                    'message': _('No milestone templates are selected for this task template.'),
                    'type': 'info',
                }
            }
        
        return {
            'name': _('Milestone Templates - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'project.milestone.template',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.milestone_template_ids.ids)],
            'context': {
                'default_name': f"Milestone Templates for {self.name}",
            },
        }



    def action_create_milestone_template(self):
        """Create a new milestone template for this task template"""
        self.ensure_one()
        
        return {
            'name': _('Create Milestone Template - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'project.milestone.template',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name': f"{self.name} - Milestone Template",
                'default_description': f"Milestone template for {self.name} task template",
            },
        }
    
    def action_view_document_templates(self):
        """Open the selected document templates"""
        self.ensure_one()
        
        if not self.document_template_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Document Templates Selected'),
                    'message': _('No document templates are selected for this task template.'),
                    'type': 'info',
                }
            }
        
        return {
            'name': _('Document Templates - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'project.document.template',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.document_template_ids.ids)],
            'context': {
                'default_name': f"Document Templates for {self.name}",
            },
        }
    
    def action_create_document_template(self):
        """Create a new document template for this task template"""
        self.ensure_one()
        
        return {
            'name': _('Create Document Template - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'project.document.template',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name': f"{self.name} - Document Template",
                'default_description': f"Document template for {self.name} task template",
                'default_template_type': 'document_based',
            },
        }
    
    def action_view_checkpoint_templates(self):
        """Open the selected checkpoint templates"""
        self.ensure_one()
        
        if not self.checkpoint_template_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Checkpoint Templates Selected'),
                    'message': _('No checkpoint templates are selected for this task template.'),
                    'type': 'info',
                }
            }
        
        return {
            'name': _('Checkpoint Templates - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'project.checkpoint.template',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.checkpoint_template_ids.ids)],
            'context': {
                'default_name': f"Checkpoint Templates for {self.name}",
            },
        }
    
    def action_create_checkpoint_template(self):
        """Create a new checkpoint template for this task template"""
        self.ensure_one()
        
        return {
            'name': _('Create Checkpoint Template - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'project.checkpoint.template',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name': f"{self.name} - Checkpoint Template",
                'default_description': f"Checkpoint template for {self.name} task template",
            },
        }


class ProjectTaskTemplateUsage(models.Model):
    _name = 'project.task.template.usage'
    _description = 'Project Task Template Usage'
    _order = 'create_date desc'

    task_template_id = fields.Many2one('project.task.template', string='Task Template', required=True)
    project_template_id = fields.Many2one('project.project', string='Project Template')
    project_id = fields.Many2one('project.project', string='Project')
    task_id = fields.Many2one('project.task', string='Generated Task')
    applied_by = fields.Many2one('res.users', string='Applied By', default=lambda self: self.env.user)
    applied_date = fields.Datetime('Applied Date', default=fields.Datetime.now)
    
    # Context information
    document_category = fields.Selection([
        ('required', 'Required'),
        ('deliverable', 'Deliverable'),
        ('reference', 'Reference'),
        ('compliance', 'Compliance'),
        ('all', 'All Documents')
    ], string='Document Category')
    document_count = fields.Integer('Document Count')
    project_name = fields.Char('Project Name')

    def name_get(self):
        """Custom name display"""
        result = []
        for record in self:
            name = f"{record.task_template_id.name} - {record.project_name or 'Unknown Project'}"
            result.append((record.id, name))
        return result
