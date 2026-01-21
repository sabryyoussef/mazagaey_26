# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    # ===========================================
    # Computed Fields
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
        help='True if multiple employees share this user account.',
    )
    shared_employee_ids = fields.One2many(
        'hr.employee',
        'user_id',
        string='Linked Employees',
        help='All employees linked to this user account.',
    )
    shared_employee_count = fields.Integer(
        string='Linked Employees Count',
        compute='_compute_shared_employee_count',
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
        """Check if this user is shared by multiple employees."""
        for user in self:
            employee_count = self.env['hr.employee'].search_count([
                ('user_id', '=', user.id),
            ])
            user.is_shared_user = employee_count > 1

    def _compute_shared_employee_count(self):
        """Count employees linked to this user."""
        for user in self:
            user.shared_employee_count = self.env['hr.employee'].search_count([
                ('user_id', '=', user.id),
            ])

    # ===========================================
    # Helper Methods
    # ===========================================
    def get_active_employee(self):
        """Get the active employee for the current user."""
        self.ensure_one()
        return self.env['employee.session.context'].get_active_employee(self.id)

    def set_active_employee(self, employee_id, pin=None):
        """Set the active employee for this user.
        
        Returns:
            dict: Result with success status and employee info for OWL widget
        """
        self.ensure_one()
        try:
            session = self.env['employee.session.context'].set_active_employee(
                employee_id, 
                pin=pin
            )
            if session:
                return {
                    'success': True,
                    'employee_id': session.active_employee_id.id,
                    'employee_name': session.active_employee_id.name,
                    'session_id': session.id,
                    'message': f'Now working as {session.active_employee_id.name}',
                }
            return {
                'success': False,
                'message': 'Failed to create session',
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e),
            }

    def clear_active_employee(self):
        """Clear the active employee session."""
        self.ensure_one()
        return self.env['employee.session.context'].clear_active_employee(self.id)

    def requires_employee_selection(self):
        """Check if this user needs to select an employee on login."""
        self.ensure_one()
        # If multiple employees share this user, selection is required
        if self.shared_employee_count > 1:
            # Check if there's already an active session
            session = self.env['employee.session.context'].get_active_session(self.id)
            return not session
        return False

    def get_selectable_employees(self):
        """Get employees that this user can select from."""
        self.ensure_one()
        return self.env['hr.employee'].search([
            ('user_id', '=', self.id),
        ])

    # ===========================================
    # Action Methods
    # ===========================================
    def action_select_employee(self):
        """Open the employee selection wizard."""
        self.ensure_one()
        return {
            'name': 'Select Employee',
            'type': 'ir.actions.act_window',
            'res_model': 'employee.select.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_user_id': self.id,
            },
        }

    def action_view_linked_employees(self):
        """View all employees linked to this user."""
        self.ensure_one()
        return {
            'name': 'Linked Employees',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'view_mode': 'list,form',
            'domain': [('user_id', '=', self.id)],
            'context': {'create': False},
        }

    # ===========================================
    # API Methods for OWL Components
    # ===========================================
    @api.model
    def get_employee_switcher_data(self):
        """
        Get data for the employee switcher widget.
        Called from the OWL component in the navbar.
        
        Returns:
            dict: Employee switcher data including active employee and available employees
        """
        user = self.env.user
        
        # Get all employees linked to this user
        employees = self.env['hr.employee'].search([
            ('user_id', '=', user.id),
        ])
        
        # Check if this is a shared user
        is_shared_user = len(employees) > 1
        
        # Get active employee from session
        active_employee = None
        session = self.env['employee.session.context'].get_active_session(user.id)
        if session and session.active_employee_id:
            emp = session.active_employee_id
            active_employee = {
                'id': emp.id,
                'name': emp.name,
                'job_title': emp.job_title or '',
                'avatar_128': emp.avatar_128 or False,
            }
        
        # Build available employees list
        available_employees = []
        for emp in employees:
            available_employees.append({
                'id': emp.id,
                'name': emp.name,
                'job_title': emp.job_title or '',
                'avatar_128': emp.avatar_128 or False,
                'pin_required': emp.pin_required,
                'department_id': emp.department_id.id if emp.department_id else False,
                'department_name': emp.department_id.name if emp.department_id else '',
            })
        
        return {
            'active_employee': active_employee,
            'available_employees': available_employees,
            'is_shared_user': is_shared_user,
            'user_id': user.id,
            'user_name': user.name,
        }
