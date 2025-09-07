# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SmartTemplateDocumentIntegration(models.Model):
    _name = 'smart.template.document.integration'
    _description = 'Smart Template Document Integration'
    _rec_name = 'name'
    
    # Basic fields
    name = fields.Char(string='Integration Name', required=True)
    description = fields.Text(string='Description')
    is_active = fields.Boolean(string='Active', default=True)
    
    # Methods (will be implemented later)
    def integrate_with_documents(self):
        """Integrate templates with document module"""
        pass
