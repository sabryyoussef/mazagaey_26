# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProjectDocumentTemplateLine(models.Model):
    _name = 'project.document.template.line'
    _description = 'Project Document Template Line'
    _order = 'sequence'

    template_id = fields.Many2one('project.document.template', string='Template', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', default=10)
    
    name = fields.Char('Document Name', required=True)
    description = fields.Text('Description')
    category = fields.Selection([
        ('required', 'Required'),
        ('deliverable', 'Deliverable'),
        ('reference', 'Reference'),
        ('compliance', 'Compliance')
    ], string='Category', required=True, default='required')
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Critical')
    ], string='Priority', default='1')
    
    notes = fields.Text('Notes')
    tag_ids = fields.Many2many('documents.tag', string='Document Tags')
