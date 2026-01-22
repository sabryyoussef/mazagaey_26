# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class EmployeeCodeController(http.Controller):
    """
    API endpoints for employee code authentication.
    """

    @http.route('/employee_accountability/check_session', type='json', auth='user')
    def check_session(self):
        """
        Check if current user needs to enter an employee code.
        Called by frontend to determine if wizard should be shown.
        """
        user = request.env.user
        
        # Not a shared user
        if not user.child_employee_ids:
            return {
                'needs_code': False,
                'is_shared_user': False,
            }
        
        # Check for active session
        SessionContext = request.env['employee.session.context']
        active_session = SessionContext.get_active_session(user.id)
        
        if active_session:
            return {
                'needs_code': False,
                'is_shared_user': True,
                'active_employee': {
                    'id': active_session.active_employee_id.id,
                    'name': active_session.active_employee_id.name,
                },
            }
        
        return {
            'needs_code': True,
            'is_shared_user': True,
            'employee_count': len(user.child_employee_ids),
        }

    @http.route('/employee_accountability/authenticate', type='json', auth='user')
    def authenticate_code(self, code):
        """
        Authenticate with an employee code.
        
        Args:
            code: The employee code entered by user
            
        Returns:
            dict with success/failure info
        """
        user = request.env.user
        result = user.authenticate_employee_code(code)
        return result

    @http.route('/employee_accountability/end_session', type='json', auth='user')
    def end_session(self):
        """
        End the current employee session.
        Used when switching employees or logging out.
        """
        user = request.env.user
        SessionContext = request.env['employee.session.context']
        
        # Close active session
        session = SessionContext.get_active_session(user.id)
        if session:
            session.close_session()
            return {'success': True, 'message': 'Session ended'}
        
        return {'success': False, 'message': 'No active session'}

    @http.route('/employee_accountability/wizard_action', type='json', auth='user')
    def get_wizard_action(self):
        """
        Get the action to open the employee code wizard.
        """
        action = request.env.ref('employee_accountability.action_employee_code_wizard')
        return action.sudo().read()[0]
