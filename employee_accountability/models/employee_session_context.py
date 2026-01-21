# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EmployeeSessionContext(models.Model):
    _name = 'employee.session.context'
    _description = 'Employee Session Context'
    _order = 'session_start desc'

    # ===========================================
    # Core Fields
    # ===========================================
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        ondelete='cascade',
        index=True,
    )
    active_employee_id = fields.Many2one(
        'hr.employee',
        string='Active Employee',
        required=True,
        ondelete='cascade',
        index=True,
    )
    
    # ===========================================
    # Session Tracking
    # ===========================================
    session_start = fields.Datetime(
        string='Session Start',
        default=fields.Datetime.now,
        required=True,
    )
    session_end = fields.Datetime(
        string='Session End',
        help='Set when employee switches or logs out.',
    )
    pin_verified = fields.Boolean(
        string='PIN Verified',
        default=False,
        help='True if the employee verified their identity with PIN.',
    )
    
    # ===========================================
    # Audit Fields
    # ===========================================
    ip_address = fields.Char(
        string='IP Address',
        help='IP address from which the session was started.',
    )
    user_agent = fields.Char(
        string='User Agent',
        help='Browser/client information.',
    )
    
    # ===========================================
    # State
    # ===========================================
    state = fields.Selection([
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('expired', 'Expired'),
    ], string='State', default='active', required=True)

    # ===========================================
    # SQL Constraints
    # ===========================================
    # Note: Unique constraint removed - we handle this in create() by ending existing sessions

    # ===========================================
    # CRUD Overrides
    # ===========================================
    @api.model_create_multi
    def create(self, vals_list):
        """End any existing active sessions before creating new one."""
        for vals in vals_list:
            user_id = vals.get('user_id')
            if user_id:
                # End existing active sessions for this user
                existing = self.search([
                    ('user_id', '=', user_id),
                    ('state', '=', 'active'),
                ])
                existing._end_session()
        return super().create(vals_list)

    # ===========================================
    # Business Methods
    # ===========================================
    def _end_session(self):
        """End the current session(s)."""
        self.write({
            'session_end': fields.Datetime.now(),
            'state': 'ended',
        })

    @api.model
    def get_active_session(self, user_id=None):
        """Get the active employee session for a user."""
        if not user_id:
            user_id = self.env.uid
        
        session = self.search([
            ('user_id', '=', user_id),
            ('state', '=', 'active'),
        ], limit=1)
        
        return session

    @api.model
    def get_active_employee(self, user_id=None):
        """Get the active employee for the current or specified user."""
        session = self.get_active_session(user_id)
        if session:
            return session.active_employee_id
        return self.env['hr.employee']

    @api.model
    def set_active_employee(self, employee_id, pin=None, ip_address=None, user_agent=None):
        """Set the active employee for the current user."""
        user = self.env.user
        employee = self.env['hr.employee'].browse(employee_id)
        
        if not employee.exists():
            raise ValidationError("Employee not found.")
        
        # Verify employee belongs to this user
        if employee.user_id and employee.user_id.id != user.id:
            raise ValidationError("This employee is not linked to your user account.")
        
        # Verify PIN if required
        if employee.pin_required and employee.employee_pin:
            if not pin:
                raise ValidationError("PIN is required for this employee.")
            employee.verify_employee_pin(pin)
        
        # Create new session (this will end existing ones)
        session = self.create({
            'user_id': user.id,
            'active_employee_id': employee.id,
            'pin_verified': bool(pin),
            'ip_address': ip_address,
            'user_agent': user_agent,
        })
        
        return session

    @api.model
    def clear_active_employee(self, user_id=None):
        """Clear the active employee session for a user."""
        session = self.get_active_session(user_id)
        if session:
            session._end_session()
        return True

    # ===========================================
    # Cleanup Methods
    # ===========================================
    @api.model
    def _cron_cleanup_expired_sessions(self):
        """Cleanup sessions older than 24 hours."""
        cutoff = fields.Datetime.subtract(fields.Datetime.now(), hours=24)
        expired = self.search([
            ('state', '=', 'active'),
            ('session_start', '<', cutoff),
        ])
        expired.write({
            'session_end': fields.Datetime.now(),
            'state': 'expired',
        })
        return True
