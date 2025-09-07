# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TemplateSuggestionWizard(models.TransientModel):
    _name = 'template.suggestion.wizard'
    _description = 'Template Suggestion Wizard'
    _rec_name = 'name'
    
    # Basic fields
    name = fields.Char(string='Wizard Name', required=True)
    description = fields.Text(string='Description')
    
    # Methods (will be implemented later)
    def action_suggest_templates(self):
        """Suggest templates based on context"""
        pass
    
    def action_apply_suggestions(self):
        """Apply suggested templates"""
        pass
