# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EmployeeSelectWizard(models.TransientModel):
    _name = 'employee.select.wizard'
    _description = 'Employee Selection Wizard'

    # ===========================================
    # Fields
    # ===========================================
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        readonly=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Select Employee',
        required=True,
        domain="[('user_id', '=', user_id)]",
    )
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Available Employees',
        compute='_compute_employee_ids',
    )
    pin = fields.Char(
        string='PIN',
        help='Enter your employee PIN to verify your identity.',
    )
    pin_required = fields.Boolean(
        string='PIN Required',
        compute='_compute_pin_required',
    )
    show_pin = fields.Boolean(
        string='Show PIN',
        default=False,
    )

    # ===========================================
    # Compute Methods
    # ===========================================
    @api.depends('user_id')
    def _compute_employee_ids(self):
        """Get available employees for selection."""
        for wizard in self:
            if wizard.user_id:
                wizard.employee_ids = self.env['hr.employee'].search([
                    ('user_id', '=', wizard.user_id.id),
                ])
            else:
                wizard.employee_ids = False

    @api.depends('employee_id')
    def _compute_pin_required(self):
        """Check if PIN is required for selected employee."""
        for wizard in self:
            if wizard.employee_id:
                wizard.pin_required = (
                    wizard.employee_id.pin_required and 
                    bool(wizard.employee_id.employee_pin)
                )
            else:
                wizard.pin_required = False

    # ===========================================
    # Action Methods
    # ===========================================
    def action_confirm(self):
        """Confirm employee selection and set active employee."""
        self.ensure_one()
        
        if not self.employee_id:
            raise ValidationError("Please select an employee.")
        
        # Set active employee (this will verify PIN if required)
        self.env['employee.session.context'].set_active_employee(
            self.employee_id.id,
            pin=self.pin if self.pin_required else None,
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Employee Selected',
                'message': f'You are now working as: {self.employee_id.name}',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_cancel(self):
        """Cancel and close wizard."""
        return {'type': 'ir.actions.act_window_close'}


class EmployeePinWizard(models.TransientModel):
    _name = 'employee.pin.wizard'
    _description = 'Employee PIN Setup Wizard'

    # ===========================================
    # Fields
    # ===========================================
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        readonly=True,
    )
    new_pin = fields.Char(
        string='New PIN',
        required=True,
        help='Enter a 4-8 digit PIN.',
    )
    confirm_pin = fields.Char(
        string='Confirm PIN',
        required=True,
        help='Re-enter the PIN to confirm.',
    )
    current_pin = fields.Char(
        string='Current PIN',
        help='Enter your current PIN (required if changing existing PIN).',
    )
    has_existing_pin = fields.Boolean(
        string='Has Existing PIN',
        compute='_compute_has_existing_pin',
    )

    # ===========================================
    # Compute Methods
    # ===========================================
    @api.depends('employee_id')
    def _compute_has_existing_pin(self):
        """Check if employee already has a PIN set."""
        for wizard in self:
            wizard.has_existing_pin = bool(
                wizard.employee_id and wizard.employee_id.employee_pin
            )

    # ===========================================
    # Validation
    # ===========================================
    @api.constrains('new_pin', 'confirm_pin')
    def _check_pin_match(self):
        """Ensure new PIN and confirmation match."""
        for wizard in self:
            if wizard.new_pin and wizard.confirm_pin:
                if wizard.new_pin != wizard.confirm_pin:
                    raise ValidationError("PINs do not match. Please try again.")

    # ===========================================
    # Action Methods
    # ===========================================
    def action_set_pin(self):
        """Set the new PIN for the employee."""
        self.ensure_one()
        
        # Verify current PIN if changing existing
        if self.has_existing_pin:
            if not self.current_pin:
                raise ValidationError("Please enter your current PIN.")
            self.employee_id.verify_employee_pin(self.current_pin)
        
        # Validate PIN format
        if self.new_pin != self.confirm_pin:
            raise ValidationError("PINs do not match.")
        
        # Set the new PIN
        self.employee_id.set_employee_pin(self.new_pin)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'PIN Set',
                'message': 'Your PIN has been set successfully.',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_cancel(self):
        """Cancel and close wizard."""
        return {'type': 'ir.actions.act_window_close'}
