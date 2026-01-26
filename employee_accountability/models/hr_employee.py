# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import secrets
import string

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    # Employee Code for accountability
    employee_code = fields.Char(
        string='Employee Code',
        required=True,
        unique=True,
        copy=False,
        default=lambda self: self._generate_employee_code(),
        help='Unique code for employee identification (e.g., EMP-A1B2-C3D4)'
    )
    
    # Link to shared user
    parent_user_id = fields.Many2one(
        'res.users',
        string='Shared User',
        help='Odoo user account shared by multiple employees in this department'
    )
    
    # Employee tags for classification
    employee_tag_ids = fields.Many2many(
        'hr.employee.category',
        'employee_tag_rel',
        string='Employee Tags',
        help='Tags for skills, department, role, project specialization'
    )
    
    # KPI fields
    total_tasks = fields.Integer(
        string='Total Tasks',
        compute='_compute_kpis',
        store=False
    )
    
    total_hours = fields.Float(
        string='Total Hours',
        compute='_compute_kpis',
        store=False
    )
    
    total_commission = fields.Monetary(
        string='Total Commission',
        compute='_compute_kpis',
        store=False
    )
    
    # Current session tracking
    current_session_id = fields.Many2one(
        'employee.session.context',
        string='Current Session',
        compute='_compute_current_session',
        store=False
    )
    
    def _generate_employee_code(self):
        """Generate unique employee code"""
        while True:
            # Format: EMP-XXXX-XXXX
            code = 'EMP-' + ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4)) + '-' + \
                   ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
            if not self.search([('employee_code', '=', code)], limit=1):
                return code
    
    @api.depends('employee_code')
    def _compute_current_session(self):
        """Get current active session for this employee"""
        for employee in self:
            session = self.env['employee.session.context'].search([
                ('employee_id', '=', employee.id),
                ('state', '=', 'active')
            ], limit=1, order='create_date desc')
            employee.current_session_id = session
    
    def _compute_kpis(self):
        """Compute employee KPIs"""
        for employee in self:
            # Tasks assigned to this employee
            tasks = self.env['project.task'].search([
                ('employee_id', '=', employee.id)
            ])
            employee.total_tasks = len(tasks)
            
            # Timesheet hours
            timesheets = self.env['account.analytic.line'].search([
                ('employee_id', '=', employee.id)
            ])
            employee.total_hours = sum(timesheets.mapped('unit_amount'))
            
            # Commission (if sale_commission module is installed)
            employee.total_commission = 0.0
            if 'sale.commission' in self.env:
                commissions = self.env['sale.commission'].search([
                    ('employee_id', '=', employee.id)
                ])
                employee.total_commission = sum(commissions.mapped('amount'))
    
    @api.constrains('employee_code')
    def _check_employee_code_unique(self):
        """Ensure employee code is unique"""
        for employee in self:
            if self.search_count([
                ('employee_code', '=', employee.employee_code),
                ('id', '!=', employee.id)
            ]) > 0:
                raise ValidationError(_('Employee code must be unique!'))
    
    def action_view_kpis(self):
        """Open KPI view for this employee"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Employee KPIs'),
            'res_model': 'hr.employee',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_view_timesheets(self):
        """Open timesheets for this employee"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Employee Timesheets'),
            'res_model': 'account.analytic.line',
            'domain': [('employee_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }
