# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProjectTaskCheckpoint(models.Model):
    _name = 'project.task.checkpoint'
    _description = 'Project Task Checkpoint'
    _order = 'sequence, id'

    name = fields.Char(
        string='Checkpoint Name',
        required=True,
        help='Name of the checkpoint'
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of the checkpoint'
    )
    
    task_id = fields.Many2one(
        'project.task',
        string='Task',
        required=False,
        ondelete='cascade',
        help='Task this checkpoint belongs to'
    )
    
    milestone_id = fields.Many2one(
        'project.milestone',
        string='Milestone',
        required=False,
        ondelete='cascade',
        help='Milestone this checkpoint belongs to'
    )
    
    tag_ids = fields.Many2many(
        'project.task.checkpoint.tag',
        'checkpoint_tag_rel',
        'checkpoint_id',
        'tag_id',
        string='Tags',
        help='Tags for categorizing this checkpoint'
    )
    
    is_reached = fields.Boolean(
        string='Reached',
        default=False,
        help='Whether this checkpoint has been reached'
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
    
    @api.onchange('is_reached')
    def _onchange_is_reached(self):
        """Handle checkpoint reached state change"""
        for checkpoint in self:
            if checkpoint.task_id:
                # Existing single checkpoint logic
                if checkpoint.is_reached and checkpoint.auto_advance_stage and checkpoint.target_stage_id:
                    checkpoint.task_id.stage_id = checkpoint.target_stage_id.id
                
                # New template rule evaluation
                checkpoint.task_id._evaluate_checkpoint_rules()
            
            # Milestone auto-advancement logic (works for both checking and unchecking)
            if checkpoint.milestone_id:
                checkpoint.milestone_id._advance_milestone_on_checkpoint(checkpoint)
