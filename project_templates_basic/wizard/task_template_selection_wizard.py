# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class TaskTemplateSelectionWizard(models.TransientModel):
    _name = 'task.template.selection.wizard'
    _description = 'Task Template Selection Wizard'

    task_id = fields.Many2one(
        'project.task',
        string='Task',
        required=True,
        readonly=True
    )
    template_id = fields.Many2one(
        'project.document.template',
        string='Template',
        domain=[('active', '=', True), ('apply_to_tasks', '=', True)],
        required=True
    )
    
    # Template preview fields
    template_name = fields.Char(
        string='Template Name',
        related='template_id.name',
        readonly=True
    )
    template_description = fields.Text(
        string='Template Description',
        related='template_id.description',
        readonly=True
    )
    template_type = fields.Selection(
        string='Template Type',
        related='template_id.template_type',
        readonly=True
    )
    document_count = fields.Integer(
        string='Document Count',
        related='template_id.document_count',
        readonly=True
    )
    checklist_count = fields.Integer(
        string='Checklist Count',
        related='template_id.checklist_count',
        readonly=True
    )

    def action_preview_template(self):
        """Preview the selected template"""
        self.ensure_one()
        if not self.template_id:
            raise ValidationError(_('Please select a template to preview.'))
        
        return {
            'name': _('Template Preview: %s') % self.template_id.name,
            'type': 'ir.actions.act_window',
            'res_model': 'project.document.template',
            'view_mode': 'form',
            'res_id': self.template_id.id,
            'view_id': self.env.ref('project_templates_basic.view_project_document_template_preview').id,
            'target': 'new',
            'context': {'form_view_initial_mode': 'readonly'},
        }

    def action_apply_template(self):
        """Apply the selected template to the task"""
        self.ensure_one()
        if not self.template_id:
            raise ValidationError(_('Please select a template to apply.'))
        
        if not self.task_id:
            raise ValidationError(_('No task specified.'))
        
        # Apply the template
        result = self.task_id.action_apply_template(self.template_id)
        
        # Close the wizard
        return {
            'type': 'ir.actions.act_window_close',
        }
