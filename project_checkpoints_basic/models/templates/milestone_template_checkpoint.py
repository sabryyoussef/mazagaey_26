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
    
    # Checklist template lines for this checkpoint
    checklist_template_line_ids = fields.One2many(
        'project.checkpoint.checklist.template.line',
        'checkpoint_template_id',
        string='Checklist Template Lines',
        help='Checklist items template for this checkpoint'
    )
    
    # Statistics
    checklist_template_count = fields.Integer(
        string='Checklist Templates Count',
        compute='_compute_checklist_template_count',
        store=True,
        help='Number of checklist template lines'
    )
    
    @api.depends('checklist_template_line_ids')
    def _compute_checklist_template_count(self):
        """Compute the number of checklist template lines"""
        for checkpoint in self:
            checkpoint.checklist_template_count = len(checkpoint.checklist_template_line_ids)
    
    def create_checkpoint_from_template(self, task_or_milestone, context_data=None):
        """Create a checkpoint from this template with its checklist items"""
        if not context_data:
            context_data = {
                'sequence': self.sequence,
                'checkpoint': self.name,
                'project': '',
                'task': '',
            }
            
            if hasattr(task_or_milestone, 'project_id'):  # Task
                context_data.update({
                    'project': task_or_milestone.project_id.name,
                    'task': task_or_milestone.name,
                })
            elif hasattr(task_or_milestone, 'project_id'):  # Milestone
                context_data.update({
                    'project': task_or_milestone.project_id.name,
                })
        
        # Create the checkpoint
        checkpoint_vals = {
            'name': self.name,
            'sequence': self.sequence,
            'auto_advance_stage': self.auto_advance_stage,
            'target_stage_id': self.target_stage_id.id if self.target_stage_id else False,
            'notes': self.notes,
            'tag_ids': [(6, 0, self.tag_ids.ids)],
        }
        
        # Link to task or milestone
        if hasattr(task_or_milestone, 'stage_id'):  # Task
            checkpoint_vals['task_id'] = task_or_milestone.id
        else:  # Milestone
            checkpoint_vals['milestone_id'] = task_or_milestone.id
        
        checkpoint = self.env['project.task.checkpoint'].create(checkpoint_vals)
        
        # Create checklist items from template lines
        for template_line in self.checklist_template_line_ids:
            template_line.create_checklist_item(checkpoint, context_data)
        
        return checkpoint
    
    def action_open_checkpoint_form(self):
        """Open the detailed form view for this checkpoint template"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Checkpoint Template: {self.name}',
            'res_model': 'project.milestone.template.checkpoint',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }