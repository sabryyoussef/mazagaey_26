# -*- coding: utf-8 -*-
{
    'name': 'Portal My Tasks',
    'version': '18.0.1.0.0',
    'category': 'Project',
    'summary': 'Portal workspace for employees to manage assigned tasks and submit handover notes',
    'description': """
Portal My Tasks Module
======================

This module enables employees to operate as Portal users with a dedicated 
"My Tasks" workspace. Key features:

* Portal users see only their assigned tasks
* Task updates and status changes from portal
* Handover note submission workflow
* Manager approval process
* Full accountability and audit trail

Benefits:
* Reduces licensing costs (Portal users are free)
* Maintains full employee accountability
* Controlled workflow with approval gates
* No backend access for employees
    """,
    'author': 'Sabry Youssef',
    'website': 'https://github.com/sabryyoussef',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'portal',
        'project',
        'hr',
        'mail',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/portal_menu_data.xml',
        'data/sequence_data.xml',
        
        # Views
        'views/portal_templates.xml',
        'views/task_views.xml',
        'views/handover_views.xml',
        'views/reporting_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'portal_my_tasks/static/src/css/portal_my_tasks.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'sequence': 10,
}
