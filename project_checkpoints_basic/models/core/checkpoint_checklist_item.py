# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectCheckpointChecklistItem(models.Model):
    _name = 'project.checkpoint.checklist.item'
    _description = 'Checkpoint Checklist Item'
    _order = 'sequence, id'

    name = fields.Char(
        string='Checklist Item',
        required=True,
        help='Name of the checklist item'
    )
    
    description = fields.Text(
        string='Description',
        help='Detailed description of this checklist item'
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of the checklist item'
    )
    
    checkpoint_id = fields.Many2one(
        'project.task.checkpoint',
        string='Checkpoint',
        required=True,
        ondelete='cascade',
        help='Checkpoint this checklist item belongs to'
    )
    
    is_required = fields.Boolean(
        string='Required',
        default=True,
        help='Whether this checklist item is required'
    )
    
    is_completed = fields.Boolean(
        string='Completed',
        default=False,
        help='Whether this checklist item has been completed'
    )
    
    completed_by = fields.Many2one(
        'res.users',
        string='Completed By',
        help='User who completed this checklist item'
    )
    
    completed_date = fields.Datetime(
        string='Completed Date',
        help='Date when this checklist item was completed'
    )
    
    notes = fields.Text(
        string='Notes',
        help='Additional notes about this checklist item'
    )
    
    # Template tracking
    template_line_id = fields.Many2one(
        'project.checkpoint.checklist.template.line',
        string='Template Line',
        help='Template line this item was created from'
    )
    
    @api.onchange('is_completed')
    def _onchange_is_completed(self):
        """Handle completion status change"""
        if self.is_completed:
            self.completed_by = self.env.user.id
            self.completed_date = fields.Datetime.now()
        else:
            self.completed_by = False
            self.completed_date = False
    
    def action_toggle_completion(self):
        """Toggle the completion status of this checklist item"""
        self.ensure_one()
        self.is_completed = not self.is_completed
        return True
    
    def action_mark_complete(self):
        """Mark this checklist item as complete"""
        self.ensure_one()
        self.write({
            'is_completed': True,
            'completed_by': self.env.user.id,
            'completed_date': fields.Datetime.now(),
        })
        return True
    
    def action_mark_incomplete(self):
        """Mark this checklist item as incomplete"""
        self.ensure_one()
        self.write({
            'is_completed': False,
            'completed_by': False,
            'completed_date': False,
        })
        return True
