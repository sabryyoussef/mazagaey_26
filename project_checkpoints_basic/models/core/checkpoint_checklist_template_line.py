# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ProjectCheckpointChecklistTemplateLine(models.Model):
    _name = 'project.checkpoint.checklist.template.line'
    _description = 'Checkpoint Checklist Template Line'
    _order = 'sequence, id'

    name = fields.Char(
        string='Checklist Item Template',
        required=True,
        help='Template name for the checklist item'
    )
    
    description = fields.Text(
        string='Description Template',
        help='Template description for the checklist item'
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of the checklist item template'
    )
    
    checkpoint_template_id = fields.Many2one(
        'project.milestone.template.checkpoint',
        string='Checkpoint Template',
        required=True,
        ondelete='cascade',
        help='Checkpoint template this checklist template belongs to'
    )
    
    is_required = fields.Boolean(
        string='Required',
        default=True,
        help='Whether this checklist item should be required'
    )
    
    notes = fields.Text(
        string='Template Notes',
        help='Template notes for this checklist item'
    )
    
    # Pattern support for dynamic content
    name_pattern = fields.Char(
        string='Name Pattern',
        help='Pattern for checklist item names. Use {checkpoint}, {sequence}, {project}, {task} as placeholders'
    )
    
    description_pattern = fields.Text(
        string='Description Pattern',
        help='Pattern for checklist item descriptions. Use {checkpoint}, {sequence}, {project}, {task} as placeholders'
    )
    
    def get_checklist_item_name(self, context_data=None):
        """Get the actual checklist item name with pattern substitution"""
        if self.name_pattern and context_data:
            try:
                return self.name_pattern.format(**context_data)
            except (KeyError, ValueError):
                pass
        return self.name or f"Checklist Item {self.sequence}"
    
    def get_checklist_item_description(self, context_data=None):
        """Get the actual checklist item description with pattern substitution"""
        if self.description_pattern and context_data:
            try:
                return self.description_pattern.format(**context_data)
            except (KeyError, ValueError):
                pass
        return self.description or ""
    
    def create_checklist_item(self, checkpoint, context_data=None):
        """Create a checklist item from this template line"""
        if not context_data:
            context_data = {
                'checkpoint': checkpoint.name,
                'sequence': self.sequence,
                'project': checkpoint.task_id.project_id.name if checkpoint.task_id else '',
                'task': checkpoint.task_id.name if checkpoint.task_id else '',
            }
        
        checklist_item_vals = {
            'name': self.get_checklist_item_name(context_data),
            'description': self.get_checklist_item_description(context_data),
            'sequence': self.sequence,
            'checkpoint_id': checkpoint.id,
            'is_required': self.is_required,
            'notes': self.notes,
            'template_line_id': self.id,
        }
        
        return self.env['project.checkpoint.checklist.item'].create(checklist_item_vals)
