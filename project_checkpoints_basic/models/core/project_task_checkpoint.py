# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


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
    
    # Compliance Integration
    compliance_project_id = fields.Many2one(
        'project.project',
        string='Compliance Project',
        required=False,
        ondelete='cascade',
        help='Compliance project this checkpoint belongs to'
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
    
    reached_on = fields.Date(
        string='Reached On',
        help='Date when this checkpoint was reached'
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
    
    # Checklist Items for this checkpoint
    checklist_item_ids = fields.One2many(
        'project.checkpoint.checklist.item',
        'checkpoint_id',
        string='Checklist Items',
        help='Checklist items for this specific checkpoint'
    )
    
    # Checklist statistics
    checklist_total_count = fields.Integer(
        string='Total Checklist Items',
        compute='_compute_checklist_stats',
        store=True,
        help='Total number of checklist items for this checkpoint'
    )
    
    checklist_completed_count = fields.Integer(
        string='Completed Checklist Items',
        compute='_compute_checklist_stats',
        store=True,
        help='Number of completed checklist items'
    )
    
    checklist_completion_percentage = fields.Float(
        string='Checklist Completion %',
        compute='_compute_checklist_stats',
        store=True,
        help='Percentage of checklist items completed'
    )
    
    # Enhanced Checkpoint Management - Visibility Conditions
    visibility_condition = fields.Text(
        string='Visibility Condition',
        help='Python expression to determine checkpoint visibility. Use task_id, milestone_id, and other fields.'
    )
    
    is_visible = fields.Boolean(
        string='Is Visible',
        compute='_compute_visibility',
        store=True,
        help='Whether this checkpoint is currently visible based on conditions'
    )
    
    visibility_depends_on = fields.Many2many(
        'project.task.checkpoint',
        'checkpoint_visibility_rel',
        'checkpoint_id',
        'depends_on_id',
        string='Visibility Depends On',
        help='Checkpoints that affect this checkpoint\'s visibility'
    )
    
    # Enhanced Checkpoint Management - Dependency Management
    prerequisite_ids = fields.Many2many(
        'project.task.checkpoint',
        'checkpoint_prerequisite_rel',
        'checkpoint_id',
        'prerequisite_id',
        string='Prerequisites',
        help='Checkpoints that must be completed before this one'
    )
    
    dependency_type = fields.Selection([
        ('all', 'All Prerequisites'),
        ('any', 'Any Prerequisite'),
        ('none', 'No Dependencies')
    ], string='Dependency Type', default='none')
    
    can_start = fields.Boolean(
        string='Can Start',
        compute='_compute_can_start',
        store=True,
        help='Whether this checkpoint can be started based on prerequisites'
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
    
    @api.depends('visibility_condition', 'task_id', 'milestone_id', 'visibility_depends_on')
    def _compute_visibility(self):
        """Compute checkpoint visibility based on conditions"""
        for checkpoint in self:
            if checkpoint.visibility_condition:
                try:
                    # Safe evaluation of visibility condition
                    checkpoint.is_visible = self._evaluate_condition(
                        checkpoint.visibility_condition, checkpoint
                    )
                except Exception as e:
                    # Log error and default to visible
                    _logger.warning(f"Visibility condition error for checkpoint {checkpoint.name}: {e}")
                    checkpoint.is_visible = True
            else:
                checkpoint.is_visible = True
    
    def _evaluate_condition(self, condition, checkpoint):
        """Safely evaluate visibility condition"""
        try:
            # Create a safe evaluation context
            context = {
                'checkpoint': checkpoint,
                'task_id': checkpoint.task_id,
                'milestone_id': checkpoint.milestone_id,
                'project_id': checkpoint.task_id.project_id if checkpoint.task_id else None,
                'user_id': checkpoint.task_id.user_id if checkpoint.task_id else None,
                'stage_id': checkpoint.task_id.stage_id if checkpoint.task_id else None,
                'datetime': fields.Datetime,
                'date': fields.Date,
                'now': fields.Datetime.now,
                'today': fields.Date.today,
            }
            
            # Add visibility dependencies to context
            if checkpoint.visibility_depends_on:
                context['visibility_depends_on'] = checkpoint.visibility_depends_on
                context['depends_on_reached'] = all(cp.is_reached for cp in checkpoint.visibility_depends_on)
            
            # Evaluate the condition safely
            result = eval(condition, {"__builtins__": {}}, context)
            return bool(result)
            
        except Exception as e:
            _logger.error(f"Error evaluating visibility condition '{condition}' for checkpoint {checkpoint.name}: {e}")
            return True  # Default to visible on error
    
    @api.depends('prerequisite_ids.is_reached', 'dependency_type')
    def _compute_can_start(self):
        """Compute whether checkpoint can be started based on prerequisites"""
        for checkpoint in self:
            if checkpoint.dependency_type == 'none':
                checkpoint.can_start = True
            elif checkpoint.dependency_type == 'all':
                checkpoint.can_start = all(
                    prereq.is_reached for prereq in checkpoint.prerequisite_ids
                ) if checkpoint.prerequisite_ids else True
            elif checkpoint.dependency_type == 'any':
                checkpoint.can_start = any(
                    prereq.is_reached for prereq in checkpoint.prerequisite_ids
                ) if checkpoint.prerequisite_ids else True
            else:
                checkpoint.can_start = True
    
    @api.depends('checklist_item_ids', 'checklist_item_ids.is_completed')
    def _compute_checklist_stats(self):
        """Compute checklist statistics for this checkpoint"""
        for checkpoint in self:
            total_items = len(checkpoint.checklist_item_ids)
            completed_items = len(checkpoint.checklist_item_ids.filtered(lambda item: item.is_completed))
            
            checkpoint.checklist_total_count = total_items
            checkpoint.checklist_completed_count = completed_items
            
            if total_items > 0:
                checkpoint.checklist_completion_percentage = (completed_items / total_items) * 100
            else:
                checkpoint.checklist_completion_percentage = 0.0
