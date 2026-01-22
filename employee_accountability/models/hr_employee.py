# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import hashlib
import secrets


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # ===========================================
    # Employee Code System
    # NOTE: Instead of linking multiple employees to one user (blocked by Odoo),
    # each employee gets their own Employee Code that identifies them.
    # The code is linked to a parent user account for authentication.
    # ===========================================
    
    employee_code = fields.Char(
        string='Employee Code',
        copy=False,
        readonly=True,
        index=True,
        help='Unique code for this employee. Used for identification in shared user scenarios.',
    )
    employee_code_hash = fields.Char(
        string='Code Hash',
        copy=False,
        readonly=True,
        groups='hr.group_hr_user',
        help='Hashed version of the employee code for secure validation.',
    )
    code_created_date = fields.Datetime(
        string='Code Created',
        readonly=True,
    )
    code_last_used = fields.Datetime(
        string='Code Last Used',
        readonly=True,
    )
    code_active = fields.Boolean(
        string='Code Active',
        default=True,
        help='If unchecked, this employee cannot use their code to authenticate.',
    )
    
    # Parent user for authentication (the shared user account)
    parent_user_id = fields.Many2one(
        'res.users',
        string='Parent User Account',
        help='The Odoo user account this employee authenticates through. '
             'Multiple employees can share one parent user (license sharing).',
        index=True,
    )
    
    is_shared_user_employee = fields.Boolean(
        string='Uses Shared Login',
        compute='_compute_is_shared_user_employee',
        store=True,
        help='True if this employee uses a shared user account via employee code.',
    )

    @api.depends('parent_user_id', 'employee_code')
    def _compute_is_shared_user_employee(self):
        """Check if this employee uses shared user authentication."""
        for employee in self:
            employee.is_shared_user_employee = bool(employee.parent_user_id and employee.employee_code)

    # ===========================================
    # Employee Code Generation & Management
    # ===========================================
    def _generate_employee_code(self):
        """Generate a unique employee code."""
        # Format: EMP-XXXX-XXXX (readable, 8 chars)
        code = f"EMP-{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}"
        return code

    def _hash_code(self, code):
        """Hash the employee code using SHA-256."""
        return hashlib.sha256(code.encode()).hexdigest()

    def generate_employee_code(self):
        """Generate a new employee code for this employee."""
        self.ensure_one()
        
        if not self.parent_user_id:
            raise ValidationError("Please set a Parent User Account before generating an employee code.")
        
        new_code = self._generate_employee_code()
        
        # Ensure uniqueness
        while self.search_count([('employee_code', '=', new_code)]) > 0:
            new_code = self._generate_employee_code()
        
        self.write({
            'employee_code': new_code,
            'employee_code_hash': self._hash_code(new_code),
            'code_created_date': fields.Datetime.now(),
            'code_active': True,
        })
        
        return new_code

    def verify_employee_code(self, code):
        """Verify the provided employee code."""
        self.ensure_one()
        
        if not self.code_active:
            raise ValidationError("This employee code has been deactivated.")
        
        if not self.employee_code:
            raise ValidationError("No employee code has been set.")
        
        if code == self.employee_code:
            # Update last used timestamp
            self.sudo().write({'code_last_used': fields.Datetime.now()})
            return True
        
        return False

    def deactivate_employee_code(self):
        """Deactivate the employee code (revoke access)."""
        self.ensure_one()
        self.write({'code_active': False})
        return True

    def reactivate_employee_code(self):
        """Reactivate the employee code."""
        self.ensure_one()
        if not self.employee_code:
            raise ValidationError("No employee code exists. Please generate one first.")
        self.write({'code_active': True})
        return True

    @api.model
    def find_by_code(self, code, parent_user_id=None):
        """Find an employee by their code, optionally filtered by parent user."""
        domain = [
            ('employee_code', '=', code),
            ('code_active', '=', True),
        ]
        if parent_user_id:
            domain.append(('parent_user_id', '=', parent_user_id))
        
        employee = self.search(domain, limit=1)
        if employee:
            # Update last used
            employee.sudo().write({'code_last_used': fields.Datetime.now()})
        return employee

    # ===========================================
    # Action Methods
    # ===========================================
    def action_generate_code(self):
        """Generate employee code and show it."""
        self.ensure_one()
        code = self.generate_employee_code()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Employee Code Generated',
                'message': f'Employee code for {self.name}: {code}',
                'type': 'success',
                'sticky': True,
            }
        }

    def action_deactivate_code(self):
        """Deactivate the employee code."""
        self.ensure_one()
        self.deactivate_employee_code()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Code Deactivated',
                'message': f'Employee code for {self.name} has been deactivated.',
                'type': 'warning',
                'sticky': False,
            }
        }

    def action_reactivate_code(self):
        """Reactivate the employee code."""
        self.ensure_one()
        self.reactivate_employee_code()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Code Reactivated',
                'message': f'Employee code for {self.name} has been reactivated.',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_regenerate_code(self):
        """Regenerate a new employee code (invalidates old one)."""
        self.ensure_one()
        code = self.generate_employee_code()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'New Employee Code Generated',
                'message': f'New code for {self.name}: {code}\n(Previous code is now invalid)',
                'type': 'success',
                'sticky': True,
            }
        }
