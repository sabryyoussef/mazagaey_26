# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SmartCheckpointTemplate(models.Model):
    _name = 'smart.checkpoint.template'
    _description = 'Smart Checkpoint Template'
    _rec_name = 'name'
    
    # Basic fields
    name = fields.Char(string='Template Name', required=True)
    description = fields.Text(string='Description')
    is_active = fields.Boolean(string='Active', default=True)
    
    # Template relationships (will be implemented later)
    project_template_ids = fields.Many2many(
        'smart.project.template',
        string='Project Templates'
    )
    
    # Methods (will be implemented later)
    def apply_template(self):
        """Apply this template to create a new checkpoint"""
        pass
