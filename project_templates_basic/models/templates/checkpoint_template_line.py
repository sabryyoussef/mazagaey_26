# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProjectCheckpointTemplateLine(models.Model):
    _name = 'project.checkpoint.template.line'
    _description = 'Project Checkpoint Template Line'
    _order = 'sequence'

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
        'project.checkpoint.template',
        string='Template',
        required=True,
        ondelete='cascade'
    )
    
    # Note: Tag and stage functionality handled by project_checkpoints_basic module
    # This template module focuses only on template definition
    
    auto_advance_stage = fields.Boolean(
        string='Auto Advance Stage',
        default=True,
        help='Automatically advance task stage when this checkpoint is reached'
    )
    
    notes = fields.Text(
        string='Notes',
        help='Additional notes for this checkpoint'
    )
