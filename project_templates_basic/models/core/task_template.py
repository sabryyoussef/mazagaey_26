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
