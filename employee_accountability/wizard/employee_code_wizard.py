# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EmployeeCodeWizard(models.TransientModel):
    """
    Wizard for entering employee code to authenticate.
    Used when a shared user needs to identify themselves.
    """
    _name = 'employee.code.wizard'
    _description = 'Employee Code Entry Wizard'

    # ===========================================
    # Fields
    # ===========================================
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        readonly=True,
    )
    employee_code = fields.Char(
        string='Employee Code',
        required=True,
        help='Enter your employee code (e.g., EMP-A1B2-C3D4).',
    )
    
    # ===========================================
    # Action Methods
    # ===========================================
    def action_authenticate(self):
        """Authenticate with the entered employee code."""
        self.ensure_one()
        
        if not self.employee_code:
            raise ValidationError("Please enter your employee code.")
        
        # Clean up the code (remove extra spaces, uppercase)
        code = self.employee_code.strip().upper()
        
        # Find employee with this code
        employee = self.env['hr.employee'].find_by_code(code, self.user_id.id)
        
        if not employee:
            raise ValidationError(
                "Invalid employee code. Please check your code and try again.\n"
                "Contact your manager if you don't have a code."
            )
        
        # Create session
        self.env['employee.session.context'].set_active_employee_by_code(
            employee.id,
            self.user_id.id,
        )
        
        # Close dialog and show notification
        return {
            'type': 'ir.actions.act_window_close',
        }

    def action_cancel(self):
        """Cancel and close wizard."""
        return {'type': 'ir.actions.act_window_close'}

