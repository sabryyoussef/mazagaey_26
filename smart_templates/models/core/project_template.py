# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


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
    
    # Template relationships (restored - all models now exist)
    task_template_ids = fields.Many2many(
        'smart.task.template',
        string='Task Templates'
    )
    document_template_ids = fields.Many2many(
        'smart.document.template',
        string='Document Templates'
    )
    checkpoint_template_ids = fields.Many2many(
        'smart.checkpoint.template',
        string='Checkpoint Templates'
    )
    milestone_template_ids = fields.Many2many(
        'smart.milestone.template',
        string='Milestone Templates'
    )
    
    # Smart features
    suggestion_level = fields.Selection([
        ('passive', 'Passive'),
        ('active', 'Active'),
        ('smart', 'Smart')
    ], string='Suggestion Level', default='active')
    
    # Computed fields (restored)
    total_templates = fields.Integer(
        string='Total Related Templates',
        compute='_compute_total_templates'
    )
    
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
    
    @api.depends('task_template_ids', 'document_template_ids', 
                 'checkpoint_template_ids', 'milestone_template_ids')
    def _compute_total_templates(self):
        for record in self:
            record.total_templates = (
                len(record.task_template_ids) +
                len(record.document_template_ids) +
                len(record.checkpoint_template_ids) +
                len(record.milestone_template_ids)
            )
    
    @api.depends('task_template_ids', 'document_template_ids',
                 'checkpoint_template_ids', 'milestone_template_ids')
    def _compute_compatibility_score(self):
        for record in self:
            # Simple compatibility scoring based on template count and types
            score = 0.0
            if record.task_template_ids:
                score += 0.3
            if record.document_template_ids:
                score += 0.2
            if record.checkpoint_template_ids:
                score += 0.3
            if record.milestone_template_ids:
                score += 0.2
            record.compatibility_score = min(score, 1.0)
    
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
    
    def get_smart_suggestions(self, context=None, limit=5):
        """Get smart template suggestions using the suggestion engine"""
        try:
            suggestion_engine = self.env['smart.template.suggestion.engine']
            
            # Prepare context
            suggestion_context = context or {}
            suggestion_context.update({
                'template_type': 'project',
                'project_type': self.template_type,
                'complexity_level': self.complexity_level,
                'user_id': self.env.user.id,
            })
            
            # Get suggestions
            suggestions = suggestion_engine.get_suggestions(
                context=suggestion_context,
                limit=limit,
                user_id=self.env.user.id
            )
            
            # If called from button, show results in a dialog
            if self.env.context.get('from_button'):
                return self._show_suggestions_dialog(suggestions)
            
            return suggestions
            
        except Exception as e:
            _logger.error(f"Error getting smart suggestions: {str(e)}")
            if self.env.context.get('from_button'):
                return self._show_error_dialog(f"Error getting suggestions: {str(e)}")
            return []
    
    def check_template_compatibility(self, template_ids=None):
        """Check compatibility with other templates"""
        try:
            suggestion_engine = self.env['smart.template.suggestion.engine']
            
            # If called from button, get related template IDs
            if self.env.context.get('from_button') and not template_ids:
                template_ids = []
                if self.task_template_ids:
                    template_ids.extend(self.task_template_ids.ids)
                if self.document_template_ids:
                    template_ids.extend(self.document_template_ids.ids)
                if self.checkpoint_template_ids:
                    template_ids.extend(self.checkpoint_template_ids.ids)
                if self.milestone_template_ids:
                    template_ids.extend(self.milestone_template_ids.ids)
            
            # Include current template in compatibility check
            all_template_ids = [self.id] + (template_ids or [])
            
            compatibility_result = suggestion_engine.check_template_compatibility(
                template_ids=all_template_ids,
                context={
                    'project_type': self.template_type,
                    'complexity_level': self.complexity_level,
                }
            )
            
            # If called from button, show results in a dialog
            if self.env.context.get('from_button'):
                return self._show_compatibility_dialog(compatibility_result)
            
            return compatibility_result
            
        except Exception as e:
            _logger.error(f"Error checking template compatibility: {str(e)}")
            error_result = {
                'compatible': False,
                'warnings': [f"Error checking compatibility: {str(e)}"],
                'conflicts': [],
                'suggestions': [],
                'compatibility_score': 0.0
            }
            
            if self.env.context.get('from_button'):
                return self._show_compatibility_dialog(error_result)
            
            return error_result
    
    def learn_from_usage(self, action='applied'):
        """Learn from user actions to improve suggestions"""
        try:
            suggestion_engine = self.env['smart.template.suggestion.engine']
            
            suggestion_engine.learn_from_user_action(
                template_id=self.id,
                action=action,
                user_id=self.env.user.id,
                context={
                    'template_type': 'project',
                    'project_type': self.template_type,
                    'complexity_level': self.complexity_level,
                }
            )
            
        except Exception as e:
            _logger.error(f"Error learning from usage: {str(e)}")
    
    def apply_template_with_suggestions(self):
        """Apply template and get suggestions for related templates"""
        # Learn from this action
        self.learn_from_usage('applied')
        
        # Get suggestions for related templates
        suggestions = self.get_smart_suggestions(limit=3)
        
        # Apply the template
        result = self.apply_template()
        
        # Add suggestions to context
        if isinstance(result, dict) and 'context' in result:
            result['context']['suggestions'] = suggestions
        
        return result
    
    def _show_suggestions_dialog(self, suggestions):
        """Show suggestions in a dialog"""
        message = f"<h3>Smart Suggestions for '{self.name}'</h3><br/>"
        
        if not suggestions:
            message += "<p>No suggestions available at this time.</p>"
        else:
            message += "<ul>"
            for suggestion in suggestions:
                template = suggestion.get('template')
                score = suggestion.get('score', 0.0)
                if template:
                    message += f"<li><strong>{template.name}</strong> (Score: {score:.2f})</li>"
            message += "</ul>"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Smart Suggestions',
                'message': message,
                'type': 'success',
                'sticky': True,
            }
        }
    
    def _show_compatibility_dialog(self, compatibility_result):
        """Show compatibility results in a dialog"""
        message = f"<h3>Compatibility Analysis for '{self.name}'</h3><br/>"
        
        # Compatibility status
        status = "✅ Compatible" if compatibility_result.get('compatible', False) else "❌ Not Compatible"
        message += f"<p><strong>Status:</strong> {status}</p>"
        
        # Compatibility score
        score = compatibility_result.get('compatibility_score', 0.0)
        message += f"<p><strong>Compatibility Score:</strong> {score:.2f}</p>"
        
        # Conflicts
        conflicts = compatibility_result.get('conflicts', [])
        if conflicts:
            message += "<p><strong>Conflicts:</strong></p><ul>"
            for conflict in conflicts:
                message += f"<li>{conflict}</li>"
            message += "</ul>"
        
        # Warnings
        warnings = compatibility_result.get('warnings', [])
        if warnings:
            message += "<p><strong>Warnings:</strong></p><ul>"
            for warning in warnings:
                message += f"<li>{warning}</li>"
            message += "</ul>"
        
        # Suggestions
        suggestions = compatibility_result.get('suggestions', [])
        if suggestions:
            message += "<p><strong>Suggestions:</strong></p><ul>"
            for suggestion in suggestions:
                message += f"<li>{suggestion}</li>"
            message += "</ul>"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Compatibility Analysis',
                'message': message,
                'type': 'info',
                'sticky': True,
            }
        }
    
    def _show_error_dialog(self, error_message):
        """Show error in a dialog"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Error',
                'message': f"<p>{error_message}</p>",
                'type': 'danger',
                'sticky': True,
            }
        }