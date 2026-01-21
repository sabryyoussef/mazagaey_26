# -*- coding: utf-8 -*-
{
    'name': 'Employee Accountability',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Shared-user friendly architecture with full employee accountability',
    'description': """
Employee Accountability & Performance
======================================

This module provides:
- Reduced Odoo user licenses (shared users per department)
- Full accountability per employee via hr.employee records
- Session-based active employee tracking with PIN security
- Task ownership and participation tracking
- Employee tagging and classification
- Leave management integration
- Commission calculation support
- KPI tracking and performance reviews

Key Features:
- Active Employee Context: Select which employee you are when using shared logins
- PIN Security: Verify employee identity with encrypted PIN
- Session Tracking: Audit trail of who worked when
- Top-bar Employee Switcher: Easy switching between employees
    """,
    'author': 'Mazagawy',
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
        'wizard/employee_select_wizard_views.xml',
        # Data
        'data/ir_cron.xml',
        'data/demo_data.xml',
    ],
    'demo': [
    ],
    'assets': {
        'web.assets_backend': [
            'employee_accountability/static/src/components/**/*.js',
            'employee_accountability/static/src/components/**/*.xml',
            'employee_accountability/static/src/components/**/*.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
