# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProjectMilestone(models.Model):
    _inherit = 'project.milestone'

    checkpoint_ids = fields.One2many(
        'project.task.checkpoint',
        'milestone_id',
        string='Checkpoints',
        help='Checkpoints for this milestone'
    )
    
    # Computed fields for checkpoint statistics
    checkpoint_count = fields.Integer(
        string='Total Checkpoints',
        compute='_compute_checkpoint_counts',
        store=False,
        help='Total number of checkpoints for this milestone'
    )
    
    completed_checkpoint_count = fields.Integer(
        string='Completed Checkpoints',
        compute='_compute_checkpoint_counts',
        store=False,
        help='Number of completed checkpoints'
    )
    
    checkpoint_progress = fields.Float(
        string='Checkpoint Progress',
        compute='_compute_checkpoint_counts',
        store=False,
        help='Progress percentage of completed checkpoints'
    )
    
    @api.depends('checkpoint_ids', 'checkpoint_ids.is_reached')
    def _compute_checkpoint_counts(self):
        """Compute checkpoint counts and progress"""
        for milestone in self:
            total_checkpoints = len(milestone.checkpoint_ids)
            completed_checkpoints = len(milestone.checkpoint_ids.filtered(lambda c: c.is_reached))
            
            milestone.checkpoint_count = total_checkpoints
            milestone.completed_checkpoint_count = completed_checkpoints
            
            if total_checkpoints > 0:
                milestone.checkpoint_progress = (completed_checkpoints / total_checkpoints) * 100
            else:
                milestone.checkpoint_progress = 0.0
    
    def _advance_milestone_on_checkpoint(self, checkpoint):
        """Mark milestone as reached when all checkpoints are reached"""
        if all(self.checkpoint_ids.mapped('is_reached')):
            if not self.is_reached:
                self.is_reached = True
                return True
        else:
            # If not all checkpoints are reached, milestone should not be reached
            if self.is_reached:
                self.is_reached = False
                return True
        return False
    
    def write(self, vals):
        """Override write to handle checkpoint milestone advancement"""
        result = super().write(vals)
        
        # Check if any checkpoints were marked as reached
        if 'checkpoint_ids' in vals:
            for milestone in self:
                for checkpoint in milestone.checkpoint_ids:
                    if checkpoint.is_reached:
                        milestone._advance_milestone_on_checkpoint(checkpoint)
        
        return result
    
    def apply_milestone_template(self, template):
        """Apply milestone template to create milestone with checkpoints"""
        self.ensure_one()
        
        # Create milestone
        milestone_vals = {
            'name': template.milestone_name,
            'project_id': self.project_id.id,
            'deadline': template.milestone_deadline,
        }
        milestone = self.env['project.milestone'].create(milestone_vals)
        
        # Create checkpoints
        for line in template.checkpoint_line_ids:
            checkpoint_vals = {
                'name': line.name,
                'sequence': line.sequence,
                'milestone_id': milestone.id,
                'tag_ids': [(6, 0, line.tag_ids.ids)],
                'auto_advance_stage': line.auto_advance_stage,
                'target_stage_id': line.target_stage_id.id if line.target_stage_id else False,
                'notes': line.notes,
            }
            self.env['project.task.checkpoint'].create(checkpoint_vals)
        
        return milestone
    
    def apply_milestone_template_from_project(self, template):
        """Apply milestone template from project context"""
        if not self.project_id:
            raise ValidationError(_("No project associated with this milestone"))
        
        return self.apply_milestone_template(template)
