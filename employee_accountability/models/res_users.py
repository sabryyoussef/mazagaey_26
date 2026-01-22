# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    # ===========================================
    # Fields for Shared User Support (Employee Code System)
    # ===========================================
    active_employee_id = fields.Many2one(
        'hr.employee',
        string='Active Employee',
        compute='_compute_active_employee_id',
        help='The currently active employee for this user session.',
    )
    is_shared_user = fields.Boolean(
        string='Is Shared User',
        compute='_compute_is_shared_user',
        help='True if this user has employees linked via parent_user_id.',
    )
    
    # Employees that use this user as their parent (for shared login)
    child_employee_ids = fields.One2many(
        'hr.employee',
        'parent_user_id',
        string='Child Employees',
        help='Employees that authenticate through this user account.',
    )
    child_employee_count = fields.Integer(
        string='Child Employees Count',
        compute='_compute_child_employee_count',
    )

    # ===========================================
    # Compute Methods
    # ===========================================
    def _compute_active_employee_id(self):
        """Get active employee from session context."""
        SessionContext = self.env['employee.session.context']
        for user in self:
            session = SessionContext.get_active_session(user.id)
            user.active_employee_id = session.active_employee_id if session else False

    def _compute_is_shared_user(self):
        """Check if this user has child employees (is a shared account)."""
        for user in self:
            user.is_shared_user = len(user.child_employee_ids) > 0

    def _compute_child_employee_count(self):
        """Count employees that use this user as parent."""
        for user in self:
            user.child_employee_count = len(user.child_employee_ids)

    # ===========================================
    # Employee Code Authentication
    # ===========================================
    def authenticate_employee_code(self, code):
        """
        Authenticate an employee by their code.
        
        Args:
            code: The employee code (e.g., 'EMP-A1B2-C3D4')
            
        Returns:
            dict: Result with employee info or error
        """
        self.ensure_one()
        
        # Find employee with this code that belongs to this user
        employee = self.env['hr.employee'].find_by_code(code, self.id)
        
        if not employee:
            return {
                'success': False,
                'message': 'Invalid employee code or code not active.',
            }
        
        # Set active employee in session
        session = self.env['employee.session.context'].set_active_employee_by_code(
            employee.id,
            self.id,
        )
        
        if session:
            return {
                'success': True,
                'employee_id': employee.id,
                'employee_name': employee.name,
                'employee_code': employee.employee_code,
                'session_id': session.id,
                'message': f'Authenticated as {employee.name}',
            }
        
        return {
            'success': False,
            'message': 'Failed to create session.',
        }

    def get_active_employee(self):
        """Get the active employee for the current user."""
        self.ensure_one()
        return self.env['employee.session.context'].get_active_employee(self.id)

    def clear_active_employee(self):
        """Clear the active employee session."""
        self.ensure_one()
        return self.env['employee.session.context'].clear_active_employee(self.id)

    # ===========================================
    # Action Methods
    # ===========================================
    def action_view_child_employees(self):
        """View all employees that use this account."""
        self.ensure_one()
        return {
            'name': 'Child Employees',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'view_mode': 'list,form',
            'domain': [('parent_user_id', '=', self.id)],
            'context': {'default_parent_user_id': self.id},
        }

    def action_enter_employee_code(self):
        """Open wizard to enter employee code."""
        self.ensure_one()
        return {
            'name': 'Enter Employee Code',
            'type': 'ir.actions.act_window',
            'res_model': 'employee.code.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_user_id': self.id,
            },
        }

    # ===========================================
    # API Methods for Frontend
    # ===========================================
    def get_employee_status(self):
        """
        Get current employee status for the UI.
        
        Returns:
            dict: Current employee info and available actions
        """
        if self:
            user = self[0]
        else:
            user = self.env.user
        
        # Get active employee from session
        active_employee = None
        session = self.env['employee.session.context'].get_active_session(user.id)
        if session and session.active_employee_id:
            emp = session.active_employee_id
            active_employee = {
                'id': emp.id,
                'name': emp.name,
                'employee_code': emp.employee_code,
                'job_title': emp.job_title or '',
                'department_name': emp.department_id.name if emp.department_id else '',
            }
        
        # Check if this is a shared user
        is_shared_user = len(user.child_employee_ids) > 0
        
        return {
            'active_employee': active_employee,
            'is_shared_user': is_shared_user,
            'requires_code': is_shared_user and not active_employee,
            'child_employee_count': len(user.child_employee_ids),
            'user_id': user.id,
            'user_name': user.name,
        }
