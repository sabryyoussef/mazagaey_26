# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProjectApplyCheckpointTemplateWizard(models.TransientModel):
    _name = 'project.apply.checkpoint.template.wizard'
    _description = 'Apply Checkpoint Template Wizard'

    template_ids = fields.Many2many(
        'project.task.checkpoint.template',
        'apply_template_wizard_rel',
        'wizard_id',
        'template_id',
        string='Templates to Apply',
        required=True,
        help='Select templates to apply to the selected tasks'
    )
    
    merge_duplicates = fields.Boolean(
        string='Merge Duplicates',
        default=True,
        help='Merge checkpoints with same name and tags'
    )
    
    overwrite_existing = fields.Boolean(
        string='Overwrite Existing Checkpoints',
        default=False,
        help='Danger: Remove existing checkpoints before applying templates'
    )
    
    append_only = fields.Boolean(
        string='Append Only',
        default=True,
        help='Only add new checkpoints, do not modify existing ones'
    )
    
    @api.onchange('overwrite_existing')
    def _onchange_overwrite_existing(self):
        """Update append_only when overwrite_existing changes"""
        if self.overwrite_existing:
            self.append_only = False
    
    @api.onchange('append_only')
    def _onchange_append_only(self):
        """Update overwrite_existing when append_only changes"""
        if self.append_only:
            self.overwrite_existing = False
    
    def action_apply_templates(self):
        """Apply selected templates to tasks"""
        task_ids = self.env.context.get('active_ids', [])
        tasks = self.env['project.task'].browse(task_ids)
        
        for task in tasks:
            if self.overwrite_existing:
                # Remove existing checkpoints
                task.checkpoint_ids.unlink()
            
            for template in self.template_ids:
                if self.append_only:
                    # Check for existing checkpoints from this template
                    existing_checkpoints = task.checkpoint_ids.filtered(
                        lambda c: c.name in template.line_ids.mapped('name')
                    )
                    if existing_checkpoints:
                        continue
                
                task._instantiate_template_checkpoints(template)
                
                if template not in task.applied_checkpoint_template_ids:
                    task.applied_checkpoint_template_ids = [(4, template.id)]
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Templates applied to %d tasks') % len(tasks),
                'type': 'success',
            }
        }
