# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProjectTemplateUsage(models.Model):
    _name = 'project.template.usage'
    _description = 'Project Template Usage History'
    _order = 'create_date desc'

    template_id = fields.Many2one('project.document.template', string='Template', required=True)
    res_model = fields.Char('Resource Model', required=True)
    res_id = fields.Integer('Resource ID', required=True)
    applied_by = fields.Many2one('res.users', string='Applied By', required=True)
    applied_date = fields.Datetime('Applied Date', default=fields.Datetime.now)
    
    # Statistics
    documents_created = fields.Integer('Documents Created', compute='_compute_statistics', store=True)
    checklist_items_created = fields.Integer('Checklist Items Created', compute='_compute_statistics', store=True)
    
    @api.depends('template_id', 'res_model', 'res_id')
    def _compute_statistics(self):
        for usage in self:
            if usage.template_id and usage.res_model and usage.res_id:
                usage.documents_created = len(usage.template_id.document_template_line_ids)
                usage.checklist_items_created = len(usage.template_id.checklist_template_line_ids)
            else:
                usage.documents_created = 0
                usage.checklist_items_created = 0
