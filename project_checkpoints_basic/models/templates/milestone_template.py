# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectMilestoneTemplate(models.Model):
    _name = 'project.milestone.template'
    _description = 'Project Milestone Template'
    _order = 'sequence, name'

    name = fields.Char(
        string='Template Name',
        required=True,
        help='Name of the milestone template'
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of the template'
    )
    
    project_id = fields.Many2one(
        'project.project',
        string='Default Project',
        help='Default project to apply this template to'
    )
    
    # Milestone fields
    milestone_name = fields.Char(
        string='Milestone Name',
        required=True,
        help='Name for the milestone to be created'
    )
    
    milestone_deadline = fields.Date(
        string='Default Deadline',
        help='Default deadline for the milestone'
    )
    
    milestone_notes = fields.Text(
        string='Milestone Notes',
        help='Default notes for the milestone'
    )
    
    # Checkpoint definitions
    checkpoint_line_ids = fields.One2many(
        'project.milestone.template.checkpoint',
        'template_id',
        string='Checkpoint Definitions',
        help='Checkpoints that will be created with this milestone'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Whether this template is active'
    )
    
    notes = fields.Text(
        string='Template Notes',
        help='Additional notes for this template'
    )
    
    # Computed fields for statistics
    checkpoint_count = fields.Integer(
        string='Checkpoint Count',
        compute='_compute_checkpoint_count',
        store=True,
        help='Number of checkpoints in this template'
    )
    
    @api.depends('checkpoint_line_ids')
    def _compute_checkpoint_count(self):
        """Compute the number of checkpoint lines"""
        for template in self:
            template.checkpoint_count = len(template.checkpoint_line_ids)
    
    def apply_to_project(self, project):
        """Apply this milestone template to a project"""
        self.ensure_one()
        
        # Create milestone
        milestone_vals = {
            'name': self.milestone_name,
            'project_id': project.id,
            'deadline': self.milestone_deadline,
        }
        milestone = self.env['project.milestone'].create(milestone_vals)
        
        # Create checkpoints
        for line in self.checkpoint_line_ids:
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
    
    def apply_to_current_project(self):
        """Apply this milestone template to the current project context"""
        self.ensure_one()
        
        # Check if template has checkpoints
        if not self.checkpoint_line_ids:
            raise ValidationError(_("Cannot apply template: No checkpoints defined"))
        
        # Get current project from context or use default
        project = self.env.context.get('default_project_id') or self.project_id
        if not project:
            raise ValidationError(_("No project specified for template application"))
        
        # Apply the template
        milestone = self.apply_to_project(project)
        
        # Show success message and redirect to milestone
        message = _("Milestone '%s' created successfully with %d checkpoints!") % (
            milestone.name, len(milestone.checkpoint_ids)
        )
        
        # Return action to show the created milestone
        return {
            'type': 'ir.actions.act_window',
            'name': _('Milestone Created'),
            'res_model': 'project.milestone',
            'res_id': milestone.id,
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_project_id': project.id,
                'create': False,
            },
        }
