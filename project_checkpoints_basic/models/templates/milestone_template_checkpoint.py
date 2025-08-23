# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProjectMilestoneTemplateCheckpoint(models.Model):
    _name = 'project.milestone.template.checkpoint'
    _description = 'Milestone Template Checkpoint Definition'
    _order = 'sequence, id'

    template_id = fields.Many2one(
        'project.milestone.template',
        string='Template',
        required=True,
        ondelete='cascade',
        help='Milestone template this checkpoint belongs to'
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of the checkpoint within the milestone'
    )
    
    name = fields.Char(
        string='Checkpoint Name',
        required=True,
        help='Name of the checkpoint'
    )
    
    tag_ids = fields.Many2many(
        'project.task.checkpoint.tag',
        'milestone_template_checkpoint_tag_rel',
        'checkpoint_id',
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
        help='Stage to advance to when this checkpoint is reached'
    )
    
    notes = fields.Text(
        string='Notes',
        help='Additional notes about this checkpoint'
    )
