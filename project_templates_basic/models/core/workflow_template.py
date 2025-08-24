# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class WorkflowTemplate(models.Model):
    _name = 'workflow.template'
    _description = 'Workflow Template'
    _order = 'create_date desc'

    # Basic Information
    name = fields.Char('Workflow Name', required=True)
    description = fields.Text('Description')
    active = fields.Boolean('Active', default=True)
    
    # Product Template Information
    product_name = fields.Char('Product Template Name', required=True)
    product_description = fields.Text('Product Description')
    product_category_id = fields.Many2one('product.category', string='Product Category')
    product_type = fields.Selection([
        ('service', 'Service'),
        ('product', 'Product'),
        ('consu', 'Consumable')
    ], string='Product Type', default='service', required=True)
    
    # Product Template Selection
    use_existing_product = fields.Boolean('Use Existing Product Template', default=False)
    existing_product_template_id = fields.Many2one('product.template', string='Select Existing Product Template')
    
    # Project Template Information
    project_name = fields.Char('Project Template Name', required=True)
    project_description = fields.Text('Project Description')
    project_duration = fields.Integer('Estimated Duration (Days)', default=30)
    project_complexity = fields.Selection([
        ('simple', 'Simple'),
        ('medium', 'Medium'),
        ('complex', 'Complex')
    ], string='Project Complexity', default='medium')
    
    # Project Template Selection
    use_existing_project = fields.Boolean('Use Existing Project Template', default=False)
    existing_project_template_id = fields.Many2one('project.project', string='Select Existing Project Template', domain="[('is_template', '=', True)]")
    
    # Task Generation Configuration
    auto_generate_tasks = fields.Boolean('Auto-Generate Tasks', default=True)
    task_generation_strategy = fields.Selection([
        ('document_based', 'Document-Based'),
        ('progress_tracking', 'Progress Tracking'),
        ('milestone', 'Milestone-Based'),
        ('custom', 'Custom')
    ], string='Task Generation Strategy', default='document_based')
    
    # Related Records
    product_template_id = fields.Many2one('product.template', string='Product Template')
    project_template_id = fields.Many2one('project.project', string='Project Template')
    task_template_ids = fields.Many2many('project.task.template', string='Task Templates')
    checkpoint_template_ids = fields.Many2many('project.checkpoint.template', string='Checkpoint Templates')
    
    # Checkpoint Template Selection
    use_existing_checkpoints = fields.Boolean('Use Existing Checkpoint Templates', default=False)
    selected_checkpoint_template_ids = fields.Many2many('project.checkpoint.template', relation='workflow_template_selected_checkpoint_rel', string='Select Existing Checkpoint Templates')
    
    # Task Template Selection
    use_existing_tasks = fields.Boolean('Use Existing Task Templates', default=False)
    selected_task_template_ids = fields.Many2many('project.task.template', relation='workflow_template_selected_task_rel', string='Select Existing Task Templates')
    
    # Statistics
    task_template_count = fields.Integer('Task Templates', compute='_compute_counts', store=True)
    checkpoint_template_count = fields.Integer('Checkpoint Templates', compute='_compute_counts', store=True)
    
    # Tracking
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
    create_date = fields.Datetime('Created Date', default=fields.Datetime.now)
    
    @api.depends('task_template_ids', 'checkpoint_template_ids')
    def _compute_counts(self):
        for template in self:
            template.task_template_count = len(template.task_template_ids)
            template.checkpoint_template_count = len(template.checkpoint_template_ids)

    @api.onchange('use_existing_product', 'existing_product_template_id')
    def _onchange_existing_product(self):
        """Update fields when existing product template is selected"""
        if self.use_existing_product and self.existing_product_template_id:
            self.product_name = self.existing_product_template_id.name
            self.product_description = self.existing_product_template_id.description or ''
            self.product_category_id = self.existing_product_template_id.categ_id
            self.product_type = self.existing_product_template_id.type
            self.product_template_id = self.existing_product_template_id
        elif not self.use_existing_product:
            # Clear the existing product template selection
            self.existing_product_template_id = False

    @api.onchange('use_existing_project', 'existing_project_template_id')
    def _onchange_existing_project(self):
        """Update fields when existing project template is selected"""
        if self.use_existing_project and self.existing_project_template_id:
            self.project_name = self.existing_project_template_id.name
            self.project_description = self.existing_project_template_id.description or ''
            self.project_template_id = self.existing_project_template_id
        elif not self.use_existing_project:
            # Clear the existing project template selection
            self.existing_project_template_id = False

    @api.onchange('use_existing_checkpoints', 'selected_checkpoint_template_ids')
    def _onchange_existing_checkpoints(self):
        """Update fields when existing checkpoint templates are selected"""
        if self.use_existing_checkpoints and self.selected_checkpoint_template_ids:
            self.checkpoint_template_ids = [(6, 0, self.selected_checkpoint_template_ids.ids)]
        elif not self.use_existing_checkpoints:
            # Clear the existing checkpoint template selection
            self.selected_checkpoint_template_ids = [(5, 0, 0)]

    @api.onchange('use_existing_tasks', 'selected_task_template_ids')
    def _onchange_existing_tasks(self):
        """Update fields when existing task templates are selected"""
        if self.use_existing_tasks and self.selected_task_template_ids:
            self.task_template_ids = [(6, 0, self.selected_task_template_ids.ids)]
        elif not self.use_existing_tasks:
            # Clear the existing task template selection
            self.selected_task_template_ids = [(5, 0, 0)]
    
    def action_view_product_template(self):
        """Open the related product template"""
        self.ensure_one()
        if self.product_template_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'product.template',
                'res_id': self.product_template_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return False

    def action_view_product_templates(self):
        """Open product templates list view"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'list,form',
            'target': 'new',
            'context': {
                'default_type': 'service',
                'search_default_service': 1,
            }
        }

    def action_create_product_template(self):
        """Open product template creation form"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_type': 'service',
                'default_name': self.product_name or 'New Product Template',
                'default_description': self.product_description or '',
                'default_categ_id': self.product_category_id.id if self.product_category_id else False,
            }
        }
    
    def action_view_project_template(self):
        """Open the related project template"""
        self.ensure_one()
        if self.project_template_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.project',
                'res_id': self.project_template_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return False

    def action_view_project_templates(self):
        """Open project templates list view"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'view_mode': 'list,form',
            'target': 'new',
            'domain': [('is_template', '=', True)],
            'context': {
                'default_is_template': True,
                'search_default_templates': 1,
            }
        }

    def action_create_project_template(self):
        """Open project template creation form"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_is_template': True,
                'default_name': self.project_name or 'New Project Template',
                'default_description': self.project_description or '',
                'default_use_documents': False,
            }
        }
    
    def action_view_task_templates(self):
        """Open the related task templates"""
        self.ensure_one()
        if self.task_template_ids:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.task.template',
                'view_mode': 'list,form',
                'domain': [('id', 'in', self.task_template_ids.ids)],
                'target': 'current',
            }
        return False

    def action_view_all_task_templates(self):
        """Open task templates list view"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task.template',
            'view_mode': 'list,form',
            'target': 'new',
            'context': {
                'search_default_active': 1,
            }
        }

    def action_create_task_template(self):
        """Open task template creation form"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task.template',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_template_type': 'document_based',
                'default_document_category': 'required',
                'default_priority': 1,
                'default_estimated_hours': 1.0,
            }
        }

    def action_view_checkpoint_templates(self):
        """Open the related checkpoint templates"""
        self.ensure_one()
        if self.checkpoint_template_ids:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.checkpoint.template',
                'view_mode': 'list,form',
                'domain': [('id', 'in', self.checkpoint_template_ids.ids)],
                'target': 'current',
            }
        return False

    def action_view_all_checkpoint_templates(self):
        """Open checkpoint templates list view"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.checkpoint.template',
            'view_mode': 'list,form',
            'target': 'new',
            'context': {
                'search_default_active': 1,
            }
        }

    def action_create_checkpoint_template(self):
        """Open checkpoint template creation form"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.checkpoint.template',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_checkpoint_type': 'milestone',
                'default_is_mandatory': True,
                'default_estimated_days': 1,
            }
        }
    
    def action_create_from_template(self):
        """Create a new workflow from this template"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'workflow.template.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_product_name': self.product_name,
                'default_product_type': self.product_type,
                'default_product_category': self.product_category_id.id,
                'default_product_description': self.product_description,
                'default_project_name': self.project_name,
                'default_project_description': self.project_description,
                'default_project_duration': self.project_duration,
                'default_project_complexity': self.project_complexity,
                'default_auto_generate_tasks': self.auto_generate_tasks,
                'default_task_generation_strategy': self.task_generation_strategy,
            }
        }
