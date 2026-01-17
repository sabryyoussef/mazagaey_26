# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SmartTemplatePreferences(models.Model):
    _name = 'smart.template.preferences'
    _description = 'Smart Template Preferences'
    _rec_name = 'name'
    
    # Basic fields
    name = fields.Char(string='Preference Name', required=True)
    description = fields.Text(string='Description')
    is_active = fields.Boolean(string='Active', default=True)
    
    # Methods (will be implemented later)
    def apply_preferences(self):
        """Apply these preferences to templates"""
        pass
