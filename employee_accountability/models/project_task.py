# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    # ===========================================
    # Employee Assignment Fields
    # ===========================================
    responsible_employee_id = fields.Many2one(
        'hr.employee',
        string='Responsible Employee',
        tracking=True,
        index=True,
        help='The employee responsible for completing this task.',
    )
    performed_by_employee_id = fields.Many2one(
        'hr.employee',
        string='Performed By',
        tracking=True,
        index=True,
        help='The employee who actually performed/completed the task.',
    )
    
    # ===========================================
    # Additional Employee Info
    # ===========================================
    participant_employee_ids = fields.Many2many(
        'hr.employee',
        'project_task_employee_participant_rel',
        'task_id',
        'employee_id',
        string='Participating Employees',
        help='Additional employees who participated in this task.',
    )
    
    # ===========================================
    # Computed Fields
    # ===========================================
    responsible_employee_department_id = fields.Many2one(
        'hr.department',
        string='Responsible Department',
        related='responsible_employee_id.department_id',
        store=True,
        help='Department of the responsible employee.',
    )
    
    # ===========================================
    # Default Value Methods
    # ===========================================
    @api.model
    def default_get(self, fields_list):
        """Set default performed_by from active employee context."""
        defaults = super().default_get(fields_list)
        
        # Auto-fill performed_by from active employee context
        if 'performed_by_employee_id' in fields_list:
            active_employee = self.env.user.get_active_employee()
            if active_employee:
                defaults['performed_by_employee_id'] = active_employee.id
        
        return defaults

    # ===========================================
    # CRUD Overrides
    # ===========================================
    @api.model_create_multi
    def create(self, vals_list):
        """Auto-fill performed_by on task creation."""
        active_employee = self.env.user.get_active_employee()
        
        for vals in vals_list:
            # Auto-fill performed_by if not set
            if not vals.get('performed_by_employee_id') and active_employee:
                vals['performed_by_employee_id'] = active_employee.id
        
        return super().create(vals_list)

    def write(self, vals):
        """Track employee changes on significant updates."""
        # If task is being marked as done, record who completed it
        if vals.get('stage_id'):
            stage = self.env['project.task.type'].browse(vals['stage_id'])
            if stage.fold:  # Folded stages are typically "done" stages
                active_employee = self.env.user.get_active_employee()
                if active_employee:
                    vals['performed_by_employee_id'] = active_employee.id
        
        return super().write(vals)

    # ===========================================
    # Business Methods
    # ===========================================
    def action_set_responsible_to_me(self):
        """Set the current active employee as responsible."""
        active_employee = self.env.user.get_active_employee()
        if active_employee:
            self.write({'responsible_employee_id': active_employee.id})
        else:
            # Fallback to user's first employee
            employee = self.env['hr.employee'].search([
                ('user_id', '=', self.env.uid)
            ], limit=1)
            if employee:
                self.write({'responsible_employee_id': employee.id})
        return True

    def action_add_me_as_participant(self):
        """Add current active employee as a participant."""
        active_employee = self.env.user.get_active_employee()
        if active_employee and active_employee not in self.participant_employee_ids:
            self.write({
                'participant_employee_ids': [(4, active_employee.id)]
            })
        return True
