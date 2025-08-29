# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ChecklistItemExtension(models.Model):
    _inherit = 'project.checklist.item'
    
    # Source tracking fields
    source = fields.Selection([
        ('template', 'Template'),
        ('manual', 'Manual'),
    ], string='Checklist Source', default='manual', help='Source of this checklist item')
    
    source_template_id = fields.Many2one(
        'project.document.template', 
        string='Source Template', 
        help='Document template this checklist item was created from'
    )
    
    template_line_id = fields.Many2one(
        'project.checklist.template.line',
        string='Template Line',
        help='Specific template line this checklist item was created from'
    )
