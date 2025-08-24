# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProjectCheckpointTemplate(models.Model):
    _name = 'project.checkpoint.template'
    _description = 'Project Checkpoint Template'
    _order = 'name'

    name = fields.Char(
        string='Template Name',
        required=True,
        help='Name of the checkpoint template'
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of the template'
    )
    
    line_ids = fields.One2many(
        'project.checkpoint.template.line',
        'template_id',
        string='Checkpoint Lines',
        help='Individual checkpoint definitions'
    )
    
    # Note: Rules functionality moved to project_checkpoints_basic module
    # This template module focuses only on template definition
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Whether this template is active'
    )
    
    notes = fields.Text(
        string='Notes',
        help='Additional notes for this template'
    )
    
    # Milestone integration fields
    create_milestone = fields.Boolean(
        string='Create Milestone',
        default=False,
        help='Whether to create a milestone when applying this template'
    )
    
    milestone_name = fields.Char(
        string='Milestone Name',
        help='Name for the milestone to be created (if different from template name)'
    )
    
    milestone_deadline = fields.Date(
        string='Milestone Deadline',
        help='Deadline for the milestone to be created'
    )
    
    milestone_notes = fields.Text(
        string='Milestone Notes',
        help='Additional notes for the milestone'
    )
    
    # Computed fields for statistics
    line_count = fields.Integer(
        string='Checkpoint Count',
        compute='_compute_line_count',
        store=True
    )
    
    # Note: Rule count removed as rules are handled by project_checkpoints_basic module
    
    display_milestone_name = fields.Char(
        string='Display Milestone Name',
        compute='_compute_display_milestone_name',
        store=False,
        help='Display name for the milestone (template name or custom name)'
    )
    
    @api.depends('line_ids')
    def _compute_line_count(self):
        """Compute the number of checkpoint lines"""
        for template in self:
            template.line_count = len(template.line_ids)
    
    # Note: Rule count computation removed as rules are handled by project_checkpoints_basic module
    
    @api.depends('name', 'milestone_name', 'create_milestone')
    def _compute_display_milestone_name(self):
        """Compute the display name for the milestone"""
        for template in self:
            if template.create_milestone:
                template.display_milestone_name = template.milestone_name or template.name
            else:
                template.display_milestone_name = False
