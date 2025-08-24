# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProjectChecklistTemplateLine(models.Model):
    _name = 'project.checklist.template.line'
    _description = 'Project Checklist Template Line'
    _order = 'sequence'

    template_id = fields.Many2one('project.document.template', string='Template', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', default=10)
    
    name = fields.Char('Checklist Item', required=True)
    description = fields.Text('Description')
    is_required = fields.Boolean('Required', default=True)
