# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SmartTemplateProjectIntegration(models.Model):
    _name = 'smart.template.project.integration'
    _description = 'Smart Template Project Integration'
    _rec_name = 'name'
    
    # Basic fields
    name = fields.Char(string='Integration Name', required=True)
    description = fields.Text(string='Description')
    is_active = fields.Boolean(string='Active', default=True)
    
    # Methods (will be implemented later)
    def integrate_with_project(self):
        """Integrate templates with project module"""
        pass
