# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import hashlib
import secrets


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # ===========================================
    # Remove the unique user constraint to allow shared users
    # ===========================================
    _sql_constraints = [
        # Override the original constraint with a dummy one that always passes
        ('user_uniq', 'CHECK(1=1)', 'A user can be linked to multiple employees when using shared user accounts.'),
    ]

    @api.constrains('user_id', 'company_id')
    def _check_user_id(self):
        """Override to allow multiple employees per user (shared users)."""
        # Skip the original constraint - we allow shared users
        pass

    # ===========================================
    # PIN Security Fields
    # ===========================================
    employee_pin = fields.Char(
        string='Employee PIN',
        help='Encrypted PIN for employee identification when using shared user accounts.',
        copy=False,
        groups='hr.group_hr_user',
    )
    employee_pin_salt = fields.Char(
        string='PIN Salt',
        copy=False,
        groups='hr.group_hr_user',
    )
    pin_required = fields.Boolean(
        string='PIN Required',
        default=True,
        help='If checked, this employee must enter PIN when selecting themselves on shared user login.',
    )
    pin_failed_attempts = fields.Integer(
        string='Failed PIN Attempts',
        default=0,
        help='Number of consecutive failed PIN attempts. Resets on successful verification.',
    )
    pin_locked_until = fields.Datetime(
        string='PIN Locked Until',
        help='If set, PIN verification is locked until this datetime.',
    )

    # ===========================================
    # Shared User Configuration
    # ===========================================
    is_shared_user_employee = fields.Boolean(
        string='Uses Shared User',
        compute='_compute_is_shared_user_employee',
        store=True,
        help='Automatically set to True if this employee shares their user account with other employees.',
    )
    shared_user_employee_ids = fields.Many2many(
        'hr.employee',
        'hr_employee_shared_user_rel',
        'employee_id',
        'shared_employee_id',
        string='Employees Sharing Same User',
        compute='_compute_shared_user_employee_ids',
        help='Other employees who share the same user account.',
    )

    # ===========================================
    # Computed Fields
    # ===========================================
    @api.depends('user_id')
    def _compute_is_shared_user_employee(self):
        """Check if this employee shares their user with other employees."""
        for employee in self:
            if employee.user_id:
                other_employees = self.search([
                    ('user_id', '=', employee.user_id.id),
                    ('id', '!=', employee.id),
                ])
                employee.is_shared_user_employee = bool(other_employees)
            else:
                employee.is_shared_user_employee = False

    @api.depends('user_id')
    def _compute_shared_user_employee_ids(self):
        """Get all other employees sharing the same user."""
        for employee in self:
            if employee.user_id:
                shared_employees = self.search([
                    ('user_id', '=', employee.user_id.id),
                    ('id', '!=', employee.id),
                ])
                employee.shared_user_employee_ids = shared_employees
            else:
                employee.shared_user_employee_ids = False

    # ===========================================
    # PIN Management Methods
    # ===========================================
    def _hash_pin(self, pin, salt=None):
        """Hash the PIN with salt using SHA-256."""
        if not salt:
            salt = secrets.token_hex(16)
        hashed = hashlib.sha256((pin + salt).encode()).hexdigest()
        return hashed, salt

    def set_employee_pin(self, new_pin):
        """Set a new PIN for the employee."""
        self.ensure_one()
        if not new_pin or len(new_pin) < 4:
            raise ValidationError("PIN must be at least 4 characters long.")
        if len(new_pin) > 8:
            raise ValidationError("PIN must not exceed 8 characters.")
        if not new_pin.isdigit():
            raise ValidationError("PIN must contain only digits.")
        
        hashed_pin, salt = self._hash_pin(new_pin)
        self.write({
            'employee_pin': hashed_pin,
            'employee_pin_salt': salt,
            'pin_failed_attempts': 0,
            'pin_locked_until': False,
        })
        return True

    def verify_employee_pin(self, pin):
        """Verify the provided PIN against stored hash."""
        self.ensure_one()
        
        # Check if PIN is locked
        if self.pin_locked_until and fields.Datetime.now() < self.pin_locked_until:
            remaining = (self.pin_locked_until - fields.Datetime.now()).seconds // 60
            raise ValidationError(f"PIN is locked. Try again in {remaining} minutes.")
        
        # If no PIN set, and PIN not required, allow access
        if not self.employee_pin:
            if not self.pin_required:
                return True
            raise ValidationError("No PIN has been set for this employee. Please contact your manager.")
        
        # Verify PIN
        hashed_input, _ = self._hash_pin(pin, self.employee_pin_salt)
        if hashed_input == self.employee_pin:
            # Reset failed attempts on success
            self.write({
                'pin_failed_attempts': 0,
                'pin_locked_until': False,
            })
            return True
        else:
            # Increment failed attempts
            failed = self.pin_failed_attempts + 1
            lock_until = False
            
            # Lock after 5 failed attempts for 15 minutes
            if failed >= 5:
                lock_until = fields.Datetime.add(fields.Datetime.now(), minutes=15)
            
            self.write({
                'pin_failed_attempts': failed,
                'pin_locked_until': lock_until,
            })
            
            if lock_until:
                raise ValidationError("Too many failed attempts. PIN locked for 15 minutes.")
            else:
                remaining = 5 - failed
                raise ValidationError(f"Incorrect PIN. {remaining} attempts remaining.")

    def reset_employee_pin(self):
        """Reset PIN (for managers). Clears PIN and requires new setup."""
        self.ensure_one()
        self.write({
            'employee_pin': False,
            'employee_pin_salt': False,
            'pin_failed_attempts': 0,
            'pin_locked_until': False,
        })
        return True

    # ===========================================
    # Action Methods
    # ===========================================
    def action_set_pin(self):
        """Open wizard to set employee PIN."""
        self.ensure_one()
        return {
            'name': 'Set Employee PIN',
            'type': 'ir.actions.act_window',
            'res_model': 'employee.pin.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_employee_id': self.id,
            },
        }

    def action_reset_pin(self):
        """Reset the employee PIN (manager action)."""
        self.ensure_one()
        self.reset_employee_pin()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'PIN Reset',
                'message': f'PIN has been reset for {self.name}. They will need to set a new PIN.',
                'type': 'success',
                'sticky': False,
            }
        }
