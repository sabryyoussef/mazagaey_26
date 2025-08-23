# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    # Template relationships
    task_template_id = fields.Many2one(
        'project.document.template', 
        string='Task Template',
        help='Template used to create this task'
    )
    
    # Checklist items
    checklist_item_ids = fields.One2many(
        'project.checklist.item', 'task_id',
        string='Checklist Items'
    )
    
    # Template statistics
    checklist_completed_count = fields.Integer(
        'Completed Checklist Items', 
        compute='_compute_checklist_stats', 
        store=True
    )
    checklist_total_count = fields.Integer(
        'Total Checklist Items', 
        compute='_compute_checklist_stats', 
        store=True
    )
    checklist_completion_percentage = fields.Float(
        'Checklist Completion %', 
        compute='_compute_checklist_stats', 
        store=True
    )
    
    # Template application
    available_template_ids = fields.Many2many(
        'project.document.template',
        compute='_compute_available_templates',
        string='Available Templates'
    )
    
    @api.depends('checklist_item_ids', 'checklist_item_ids.is_completed')
    def _compute_checklist_stats(self):
        for task in self:
            total_items = len(task.checklist_item_ids)
            completed_items = len(task.checklist_item_ids.filtered(lambda item: item.is_completed))
            
            task.checklist_total_count = total_items
            task.checklist_completed_count = completed_items
            
            if total_items > 0:
                task.checklist_completion_percentage = (completed_items / total_items) * 100
            else:
                task.checklist_completion_percentage = 0.0
    
    def _compute_available_templates(self):
        for task in self:
            # Get all active templates that can be applied to tasks
            available_templates = self.env['project.document.template'].search([
                ('active', '=', True),
                ('apply_to_tasks', '=', True)
            ])
            task.available_template_ids = available_templates
    
    def action_apply_template(self, template):
        """Apply a template to this task"""
        self.ensure_one()
        if template:
            template.action_apply_to_task(self)
            self.task_template_id = template.id
            
            # Show success message
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Template Applied'),
                    'message': _('Template "%s" has been successfully applied to task "%s"') % (template.name, self.name),
                    'type': 'success',
                    'sticky': False,
                }
            }
        return True
    
    def action_view_checklist(self):
        """Open checklist view for this task"""
        self.ensure_one()
        return {
            'name': _('Task Checklist: %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'project.checklist.item',
            'view_mode': 'list,form',
            'domain': [('task_id', '=', self.id)],
            'context': {
                'default_task_id': self.id,
                'default_sequence': 10,
            },
            'target': 'current',
        }
    
    def action_view_template_usage(self):
        """View template usage history for this task"""
        self.ensure_one()
        return {
            'name': _('Template Usage History'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.template.usage',
            'view_mode': 'list,form',
            'domain': [('task_id', '=', self.id)],
            'context': {
                'default_task_id': self.id,
            },
            'target': 'current',
        }
    
    def action_create_from_template(self):
        """Action to create task from template"""
        self.ensure_one()
        return {
            'name': _('Apply Template'),
            'type': 'ir.actions.act_window',
            'res_model': 'task.template.selection.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_task_id': self.id,
            },
        }
    
    @api.model
    def create(self, vals):
        """Override create to auto-apply templates if configured"""
        task = super(ProjectTask, self).create(vals)
        
        # Auto-apply templates if configured (commented out for now)
        # if task.project_id and task.project_id.auto_apply_task_template_id:
        #     task.action_apply_template(task.project_id.auto_apply_task_template_id)
        
        return task
