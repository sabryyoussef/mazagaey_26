# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SmartTaskTemplate(models.Model):
    _name = 'smart.task.template'
    _description = 'Smart Task Template'
    _rec_name = 'name'
    
    # Core fields
    name = fields.Char(string='Template Name', required=True)
    description = fields.Text(string='Description')
    is_active = fields.Boolean(string='Active', default=True)
    
    # Task-specific fields
    task_type = fields.Selection([
        ('development', 'Development'),
        ('testing', 'Testing'),
        ('documentation', 'Documentation'),
        ('review', 'Review'),
        ('deployment', 'Deployment'),
        ('maintenance', 'Maintenance'),
        ('analysis', 'Analysis'),
        ('design', 'Design'),
        ('other', 'Other')
    ], string='Task Type', default='development', required=True)
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Very High')
    ], string='Priority', default='1', required=True)
    
    complexity_level = fields.Selection([
        ('simple', 'Simple'),
        ('medium', 'Medium'),
        ('complex', 'Complex')
    ], string='Complexity Level', default='medium', required=True)
    
    estimated_hours = fields.Float(string='Estimated Hours', digits=(16, 2))
    estimated_days = fields.Float(string='Estimated Days', digits=(16, 2))
    
    # Task requirements
    required_skills = fields.Text(string='Required Skills')
    prerequisites = fields.Text(string='Prerequisites')
    deliverables = fields.Text(string='Expected Deliverables')
    
    # Task workflow
    workflow_stage = fields.Selection([
        ('planning', 'Planning'),
        ('in_progress', 'In Progress'),
        ('review', 'Review'),
        ('testing', 'Testing'),
        ('completed', 'Completed')
    ], string='Workflow Stage', default='planning')
    
    # Smart features
    suggestion_level = fields.Selection([
        ('passive', 'Passive'),
        ('active', 'Active'),
        ('smart', 'Smart')
    ], string='Suggestion Level', default='active')
    
    auto_assign = fields.Boolean(string='Auto Assign', default=False)
    auto_schedule = fields.Boolean(string='Auto Schedule', default=False)
    
    # Usage statistics
    usage_count = fields.Integer(string='Usage Count', default=0)
    last_used = fields.Datetime(string='Last Used')
    
    # Template relationships
    project_template_ids = fields.Many2many(
        'smart.project.template',
        string='Project Templates'
    )
    
    # Computed fields
    total_projects = fields.Integer(
        string='Total Related Projects',
        compute='_compute_total_projects'
    )
    
    @api.depends('project_template_ids')
    def _compute_total_projects(self):
        for record in self:
            record.total_projects = len(record.project_template_ids)
    
    # Methods
    def apply_template(self):
        """Apply this template to create a new task"""
        # Update usage statistics
        self.update_usage()
        
        # This will be implemented to create actual tasks
        return {
            'type': 'ir.actions.act_window',
            'name': f'Create Task from {self.name}',
            'res_model': 'project.task',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name': self.name,
                'default_description': self.description,
                'default_priority': self.priority,
                'template_id': self.id
            }
        }
    
    def update_usage(self):
        """Update usage statistics"""
        self.usage_count += 1
        self.last_used = fields.Datetime.now()
    
    def get_suggestions(self):
        """Get suggested related templates based on task type and complexity"""
        domain = [
            ('task_type', '=', self.task_type),
            ('complexity_level', '=', self.complexity_level),
            ('id', '!=', self.id)
        ]
        return self.search(domain, limit=5)
    
    def view_related_projects(self):
        """View projects that use this task template"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Projects using {self.name}',
            'res_model': 'smart.project.template',
            'view_mode': 'list,form',
            'domain': [('task_template_ids', 'in', [self.id])],
            'context': {'search_default_active': 1}
        }
