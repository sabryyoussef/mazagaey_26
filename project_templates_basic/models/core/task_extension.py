# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ProjectTask(models.Model):
    _inherit = 'project.task'

    # Template tracking fields
    is_generated_from_template = fields.Boolean(
        string='Generated from Template',
        default=False,
        help='Indicates if this task was generated from a task template'
    )
    
    source_task_template_id = fields.Many2one(
        'project.task.template',
        string='Source Task Template',
        help='The task template that was used to generate this task'
    )
    
    template_generation_date = fields.Datetime(
        string='Template Generation Date',
        help='Date when this task was generated from template'
    )
    
    template_context_data = fields.Text(
        string='Template Context Data',
        help='Context data used when generating this task from template'
    )
