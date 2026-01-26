# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    # Employee assignment for accountability
    employee_id = fields.Many2one(
        'hr.employee',
        string='Assigned Employee',
        tracking=True,
        help='The actual employee working on this task (for accountability)'
    )
    
    employee_code = fields.Char(
        string='Employee Code',
        related='employee_id.employee_code',
        store=True,
        readonly=True
    )
    
    # Actual workers (from timesheets and activities)
    actual_worker_ids = fields.Many2many(
        'hr.employee',
        'task_actual_worker_rel',
        string='Actual Workers',
        compute='_compute_actual_workers',
        store=False,
        help='Employees who actually worked on this task (from timesheets)'
    )
    
    def _compute_actual_workers(self):
        """Compute actual workers from timesheets"""
        for task in self:
            if 'account.analytic.line' in self.env:
                timesheets = self.env['account.analytic.line'].search([
                    ('task_id', '=', task.id)
                ])
                task.actual_worker_ids = timesheets.mapped('employee_id')
            else:
                task.actual_worker_ids = False
    
    def write(self, vals):
        """Override write to track employee changes"""
        result = super().write(vals)
        
        # If employee_id changed, log it
        if 'employee_id' in vals:
            for task in self:
                employee = self.env['hr.employee'].browse(vals['employee_id'])
                if employee:
                    task.message_post(
                        body=_('Task assigned to employee: %s (%s)') % (
                            employee.name, employee.employee_code
                        ),
                        subtype_xmlid='mail.mt_note'
                    )
        
        return result
