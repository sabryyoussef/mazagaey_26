# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProjectTaskCheckpointTemplateLine(models.Model):
    _name = 'project.task.checkpoint.template.line'
    _description = 'Task Checkpoint Template Line'
    _order = 'sequence, id'

    name = fields.Char(
        string='Checkpoint Name',
        required=True,
        help='Name of the checkpoint'
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of the checkpoint in the template'
    )
    
    template_id = fields.Many2one(
        'project.task.checkpoint.template',
        string='Template',
        required=True,
        ondelete='cascade'
    )
    
    tag_ids = fields.Many2many(
        'project.task.checkpoint.tag',
        'checkpoint_template_line_tag_rel',
        'template_line_id',
        'tag_id',
        string='Tags',
        help='Tags for categorizing this checkpoint'
    )
    
    auto_advance_stage = fields.Boolean(
        string='Auto Advance Stage',
        default=True,
        help='Automatically advance task stage when this checkpoint is reached'
    )
    
    target_stage_id = fields.Many2one(
        'project.task.type',
        string='Target Stage',
        help='Target stage to advance to when checkpoint is reached'
    )
    
    notes = fields.Text(
        string='Notes',
        help='Additional notes for this checkpoint'
    )
