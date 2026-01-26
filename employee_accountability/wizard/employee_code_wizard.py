# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class EmployeeCodeWizard(models.TransientModel):
    _name = 'employee.code.wizard'
    _description = 'Employee Code Authentication Wizard'
    
    employee_code = fields.Char(
        string='Employee Code',
        required=True,
        help='Enter your employee code (e.g., EMP-A1B2-C3D4)'
    )
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        compute='_compute_employee',
        store=False
    )
    
    employee_name = fields.Char(
        string='Employee Name',
        compute='_compute_employee',
        store=False
    )
    
    @api.depends('employee_code')
    def _compute_employee(self):
        """Find employee by code"""
        for wizard in self:
            if wizard.employee_code:
                employee = self.env['hr.employee'].search([
                    ('employee_code', '=', wizard.employee_code.upper().strip())
                ], limit=1)
                wizard.employee_id = employee
                wizard.employee_name = employee.name if employee else False
            else:
                wizard.employee_id = False
                wizard.employee_name = False
    
    def action_authenticate(self):
        """Authenticate with employee code and create session"""
        self.ensure_one()
        
        if not self.employee_id:
            raise ValidationError(_(
                'Invalid employee code: %s\n'
                'Please check your code and try again.'
            ) % self.employee_code)
        
        # Create active session
        session = self.env['employee.session.context'].create_active_session(
            self.employee_code.upper().strip()
        )
        
        # Show success message
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Authentication Successful'),
                'message': _('You are now identified as: %s (%s)') % (
                    self.employee_id.name,
                    self.employee_code.upper()
                ),
                'type': 'success',
                'sticky': False,
            }
        }
