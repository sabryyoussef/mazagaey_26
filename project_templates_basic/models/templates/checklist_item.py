# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProjectChecklistItem(models.Model):
    _name = 'project.checklist.item'
    _description = 'Project Checklist Item'
    _order = 'sequence'

    name = fields.Char('Checklist Item', required=True)
    description = fields.Text('Description')
    task_id = fields.Many2one('project.task', string='Task', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', default=10)
    is_required = fields.Boolean('Required', default=True)
    is_completed = fields.Boolean('Completed', default=False)
    completed_by = fields.Many2one('res.users', string='Completed By')
    completed_date = fields.Datetime('Completed Date')
    
    def action_toggle_completion(self):
        """Toggle the completion status of this checklist item"""
        self.ensure_one()
        if self.is_completed:
            self.write({
                'is_completed': False,
                'completed_by': False,
                'completed_date': False,
            })
        else:
            self.write({
                'is_completed': True,
                'completed_by': self.env.user.id,
                'completed_date': fields.Datetime.now(),
            })
        return True
