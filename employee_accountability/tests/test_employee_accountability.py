# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install')
class TestEmployeeAccountability(TransactionCase):

    def setUp(self):
        super().setUp()
        # Create test employee
        self.employee = self.env['hr.employee'].create({
            'name': 'Test Employee',
        })
        
        # Create test user
        self.user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'test_user',
            'email': 'test@example.com',
        })

    def test_employee_code_generation(self):
        """Test that employee code is automatically generated"""
        self.assertTrue(self.employee.employee_code)
        self.assertTrue(self.employee.employee_code.startswith('EMP-'))
        self.assertEqual(len(self.employee.employee_code), 13)  # EMP-XXXX-XXXX

    def test_employee_code_uniqueness(self):
        """Test that employee codes are unique"""
        employee2 = self.env['hr.employee'].create({
            'name': 'Test Employee 2',
        })
        self.assertNotEqual(self.employee.employee_code, employee2.employee_code)

    def test_employee_session_creation(self):
        """Test creating an employee session"""
        session = self.env['employee.session.context'].create({
            'employee_id': self.employee.id,
            'user_id': self.user.id,
            'state': 'active',
        })
        self.assertEqual(session.employee_id, self.employee)
        self.assertEqual(session.state, 'active')
        self.assertTrue(session.name)

    def test_employee_session_end(self):
        """Test ending an employee session"""
        session = self.env['employee.session.context'].create({
            'employee_id': self.employee.id,
            'user_id': self.user.id,
            'state': 'active',
        })
        session.action_end_session()
        self.assertEqual(session.state, 'ended')
        self.assertTrue(session.end_date)

    def test_create_active_session(self):
        """Test creating active session via method"""
        session = self.env['employee.session.context'].create_active_session(
            self.employee.employee_code
        )
        self.assertEqual(session.employee_id, self.employee)
        self.assertEqual(session.state, 'active')

    def test_get_current_employee(self):
        """Test getting current employee from session"""
        session = self.env['employee.session.context'].create({
            'employee_id': self.employee.id,
            'user_id': self.env.user.id,
            'state': 'active',
        })
        current_employee = self.env['employee.session.context'].get_current_employee()
        self.assertEqual(current_employee, self.employee)

    def test_project_task_employee_assignment(self):
        """Test assigning employee to project task"""
        project = self.env['project.project'].create({
            'name': 'Test Project',
        })
        task = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': project.id,
            'employee_id': self.employee.id,
        })
        self.assertEqual(task.employee_id, self.employee)
        self.assertEqual(task.employee_code, self.employee.employee_code)

    def test_employee_code_wizard(self):
        """Test employee code wizard"""
        wizard = self.env['employee.code.wizard'].create({
            'employee_code': self.employee.employee_code,
        })
        self.assertEqual(wizard.employee_id, self.employee)
        self.assertEqual(wizard.employee_name, self.employee.name)
