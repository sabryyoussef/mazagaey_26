# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SmartProjectTemplate(models.Model):
    _name = 'smart.project.template'
    _description = 'Smart Project Template'
    _rec_name = 'name'
    
    # Core fields
    name = fields.Char(string='Template Name', required=True)
    description = fields.Text(string='Description')
    is_active = fields.Boolean(string='Active', default=True)
    
    # Template metadata
    template_type = fields.Selection([
        ('basic', 'Basic Project'),
        ('advanced', 'Advanced Project'),
        ('enterprise', 'Enterprise Project')
    ], string='Template Type', default='basic', required=True)
    
    complexity_level = fields.Selection([
        ('simple', 'Simple'),
        ('medium', 'Medium'),
        ('complex', 'Complex')
    ], string='Complexity Level', default='medium', required=True)
    
    estimated_duration = fields.Integer(string='Estimated Duration (Days)')
    required_skills = fields.Text(string='Required Skills')
    
    # Template relationships (commented out until models are created)
    # task_template_ids = fields.Many2many(
    #     'smart.task.template',
    #     string='Task Templates'
    # )
    # document_template_ids = fields.Many2many(
    #     'smart.document.template',
    #     string='Document Templates'
    # )
    # checkpoint_template_ids = fields.Many2many(
    #     'smart.checkpoint.template',
    #     string='Checkpoint Templates'
    # )
    # milestone_template_ids = fields.Many2many(
    #     'smart.milestone.template',
    #     string='Milestone Templates'
    # )
    
    # Smart features
    suggestion_level = fields.Selection([
        ('passive', 'Passive'),
        ('active', 'Active'),
        ('smart', 'Smart')
    ], string='Suggestion Level', default='active')
    
    compatibility_score = fields.Float(
        string='Compatibility Score',
        compute='_compute_compatibility_score',
        store=True
    )
    
    usage_count = fields.Integer(
        string='Usage Count',
        default=0
    )
    
    last_used = fields.Datetime(string='Last Used')
    
    # Computed fields (commented out until template relationships are created)
    # total_templates = fields.Integer(
    #     string='Total Related Templates',
    #     compute='_compute_total_templates'
    # )
    
    # @api.depends('task_template_ids', 'document_template_ids', 
    #              'checkpoint_template_ids', 'milestone_template_ids')
    # def _compute_total_templates(self):
    #     for record in self:
    #         record.total_templates = (
    #             len(record.task_template_ids) +
    #             len(record.document_template_ids) +
    #             len(record.checkpoint_template_ids) +
    #             len(record.milestone_template_ids)
    #         )
    
    # @api.depends('task_template_ids', 'document_template_ids',
    #              'checkpoint_template_ids', 'milestone_template_ids')
    # def _compute_compatibility_score(self):
    #     for record in self:
    #         # Simple compatibility scoring based on template count and types
    #         score = 0.0
    #         if record.task_template_ids:
    #             score += 0.3
    #         if record.document_template_ids:
    #             score += 0.2
    #         if record.checkpoint_template_ids:
    #             score += 0.3
    #         if record.milestone_template_ids:
    #             score += 0.2
    #         record.compatibility_score = min(score, 1.0)
    
    # Methods
    def apply_template(self):
        """Apply this template to create a new project"""
        # Update usage statistics
        self.update_usage()
        # This will be implemented to create actual projects
        return {
            'type': 'ir.actions.act_window',
            'name': 'Apply Template',
            'res_model': 'project.project',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name': f'Project from {self.name}',
                'template_id': self.id,
            }
        }
    
    def get_suggestions(self):
        """Get suggested related templates based on user preferences"""
        # This will integrate with the suggestion engine
        suggestions = self.env['smart.template.user.preferences'].get_user_preferences()
        return {
            'suggestion_level': suggestions.suggestion_level,
            'trigger_behavior': suggestions.trigger_behavior,
        }
    
    def update_usage(self):
        """Update usage statistics"""
        self.usage_count += 1
        self.last_used = fields.Datetime.now()
    
    def action_view_related_templates(self):
        """View all related templates in a single view"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Related Templates for {self.name}',
            'res_model': 'smart.project.template',
            'view_mode': 'list,form',
            'domain': [('id', 'in', [
                self.id,
                *self.task_template_ids.ids,
                *self.document_template_ids.ids,
                *self.checkpoint_template_ids.ids,
                *self.milestone_template_ids.ids,
            ])],
            'context': {'default_project_template_id': self.id},
        }