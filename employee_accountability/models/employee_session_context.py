# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class EmployeeSessionContext(models.Model):
    _name = 'employee.session.context'
    _description = 'Employee Session Context'
    _order = 'create_date desc'
    
    name = fields.Char(
        string='Session Name',
        compute='_compute_name',
        store=True
    )
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        ondelete='cascade'
    )
    
    employee_code = fields.Char(
        string='Employee Code',
        related='employee_id.employee_code',
        store=True,
        readonly=True
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        default=lambda self: self.env.user
    )
    
    state = fields.Selection([
        ('active', 'Active'),
        ('ended', 'Ended'),
    ], string='State', default='active', required=True)
    
    start_date = fields.Datetime(
        string='Start Date',
        default=fields.Datetime.now,
        required=True
    )
    
    end_date = fields.Datetime(
        string='End Date'
    )
    
    @api.depends('employee_id', 'start_date')
    def _compute_name(self):
        """Generate session name"""
        for session in self:
            if session.employee_id and session.start_date:
                session.name = f"{session.employee_id.name} - {session.start_date.strftime('%Y-%m-%d %H:%M')}"
            else:
                session.name = _('New Session')
    
    def action_end_session(self):
        """End the current session"""
        for session in self:
            session.state = 'ended'
            session.end_date = fields.Datetime.now()
    
    @api.model
    def create_active_session(self, employee_code):
        """Create a new active session for employee code"""
        employee = self.env['hr.employee'].search([
            ('employee_code', '=', employee_code)
        ], limit=1)
        
        if not employee:
            raise ValidationError(_('Employee with code %s not found!') % employee_code)
        
        # End any existing active sessions for this employee
        active_sessions = self.search([
            ('employee_id', '=', employee.id),
            ('state', '=', 'active')
        ])
        active_sessions.action_end_session()
        
        # Create new session
        session = self.create({
            'employee_id': employee.id,
            'user_id': self.env.user.id,
            'state': 'active',
        })
        
        return session
    
    @api.model
    def get_current_employee(self):
        """Get current employee from active session"""
        session = self.search([
            ('user_id', '=', self.env.user.id),
            ('state', '=', 'active')
        ], limit=1, order='create_date desc')
        
        return session.employee_id if session else False
    
    @api.model
    def _end_old_sessions(self):
        """End sessions that are older than 24 hours"""
        from datetime import timedelta
        cutoff_time = fields.Datetime.now() - timedelta(hours=24)
        
        old_sessions = self.search([
            ('state', '=', 'active'),
            ('start_date', '<', cutoff_time)
        ])
        
        for session in old_sessions:
            session.action_end_session()
        
        return len(old_sessions)
