# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TemplateSelectionWizard(models.TransientModel):
    _name = 'template.selection.wizard'
    _description = 'Template Selection Wizard'

    template_type = fields.Selection([
        ('milestone', 'Milestone Templates'),
        ('checkpoint', 'Checkpoint Templates')
    ], string='Template Type', required=True, default='milestone',
       help='Type of template to apply')

    milestone_template_id = fields.Many2one(
        'project.milestone.template',
        string='Milestone Template',
        domain=[('active', '=', True)],
        help='Select a milestone template to apply'
    )

    checkpoint_template_id = fields.Many2one(
        'project.task.checkpoint.template',
        string='Checkpoint Template',
        domain=[('active', '=', True)],
        help='Select a checkpoint template to apply'
    )

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        help='Project to apply the template to'
    )

    task_id = fields.Many2one(
        'project.task',
        string='Task',
        help='Task to apply checkpoint template to (optional for milestone templates)'
    )

    # Computed fields for template details
    template_name = fields.Char(
        string='Template Name',
        compute='_compute_template_details',
        store=False
    )

    template_description = fields.Text(
        string='Template Description',
        compute='_compute_template_details',
        store=False
    )

    checkpoint_count = fields.Integer(
        string='Checkpoint Count',
        compute='_compute_template_details',
        store=False
    )

    @api.depends('template_type', 'milestone_template_id', 'checkpoint_template_id')
    def _compute_template_details(self):
        """Compute template details for display"""
        for wizard in self:
            if wizard.template_type == 'milestone' and wizard.milestone_template_id:
                template = wizard.milestone_template_id
                wizard.template_name = template.name
                wizard.template_description = template.notes or f"Milestone: {template.milestone_name}"
                wizard.checkpoint_count = template.checkpoint_count
            elif wizard.template_type == 'checkpoint' and wizard.checkpoint_template_id:
                template = wizard.checkpoint_template_id
                wizard.template_name = template.name
                wizard.template_description = template.notes or "Checkpoint template"
                wizard.checkpoint_count = template.line_count
            else:
                wizard.template_name = False
                wizard.template_description = False
                wizard.checkpoint_count = 0

    @api.onchange('template_type')
    def _onchange_template_type(self):
        """Clear template selection when type changes"""
        self.milestone_template_id = False
        self.checkpoint_template_id = False

    @api.onchange('project_id')
    def _onchange_project_id(self):
        """Update task domain when project changes"""
        if self.project_id:
            return {
                'domain': {
                    'task_id': [('project_id', '=', self.project_id.id)]
                }
            }

    def action_apply_template(self):
        """Apply the selected template"""
        self.ensure_one()

        if self.template_type == 'milestone':
            if not self.milestone_template_id:
                raise ValidationError(_("Please select a milestone template"))
            
            # Apply milestone template
            milestone = self.milestone_template_id.apply_to_project(self.project_id)
            
            # Return action to show created milestone
            return {
                'type': 'ir.actions.act_window',
                'name': _('Milestone Created'),
                'res_model': 'project.milestone',
                'res_id': milestone.id,
                'view_mode': 'form',
                'target': 'current',
            }

        elif self.template_type == 'checkpoint':
            if not self.checkpoint_template_id:
                raise ValidationError(_("Please select a checkpoint template"))
            
            if not self.task_id:
                raise ValidationError(_("Please select a task for checkpoint template application"))
            
            # Apply checkpoint template
            self.task_id._instantiate_template_checkpoints(self.checkpoint_template_id)
            
            # Return action to show updated task
            return {
                'type': 'ir.actions.act_window',
                'name': _('Task Updated'),
                'res_model': 'project.task',
                'res_id': self.task_id.id,
                'view_mode': 'form',
                'target': 'current',
            }

    def action_preview_template(self):
        """Preview the selected template details"""
        self.ensure_one()
        
        if self.template_type == 'milestone' and self.milestone_template_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Template Preview'),
                'res_model': 'project.milestone.template',
                'res_id': self.milestone_template_id.id,
                'view_mode': 'form',
                'target': 'new',
                'flags': {'mode': 'readonly'},
            }
        elif self.template_type == 'checkpoint' and self.checkpoint_template_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Template Preview'),
                'res_model': 'project.task.checkpoint.template',
                'res_id': self.checkpoint_template_id.id,
                'view_mode': 'form',
                'target': 'new',
                'flags': {'mode': 'readonly'},
            }
