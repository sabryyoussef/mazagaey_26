# -*- coding: utf-8 -*-
{
    'name': 'Employee Accountability',
    'version': '18.0.2.0.0',
    'category': 'Human Resources',
    'summary': 'Employee Code authentication for shared-user accountability',
    'description': """
Employee Accountability with Employee Codes
============================================

This module provides:
- Reduced Odoo user licenses (shared users per department)
- Full accountability per employee via unique Employee Codes
- Simple code-based authentication (like API keys)
- Task ownership and participation tracking
- Employee tagging and classification
- Leave management integration
- Commission calculation support
- KPI tracking and performance reviews

Key Features:
- Employee Codes: Each employee gets a unique code (e.g., EMP-A1B2-C3D4)
- Parent User Linking: Multiple employees share one Odoo user license
- Session Tracking: Audit trail of who worked when via their code
- Simple Wizard: Enter code to identify yourself
    """,
    'author': 'Sabry Youssef',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'hr',
        'project',
        'hr_holidays',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        # Views
        'views/hr_employee_views.xml',
        'views/employee_session_context_views.xml',
        'views/project_task_views.xml',
        'views/project_project_views.xml',
        # Wizards
        'wizard/employee_code_wizard_views.xml',
        # Data
        'data/ir_cron.xml',
        'data/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'employee_accountability/static/src/js/employee_systray.js',
            'employee_accountability/static/src/xml/employee_systray.xml',
        ],
    },
    'demo': [
    ],
    'test': [
        'tests/test_employee_accountability.py',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
