{
    'name': "Project Handover Notes",
    'summary': "Comprehensive handover notes functionality for Odoo projects",
    'description': """
        This module provides comprehensive handover notes functionality for Odoo projects, 
        allowing project managers and administrators to create, manage, and track project 
        handovers with detailed documentation and approval workflows.
    """,
    'author': "BeshoyWageh",
    'version': '18.0.1.0.0',
    'category': 'Project Management',
    'depends': [
        'base',
        'project',
        'mail',
        'unified_documents',
        'project_templates_basic',
        'project_checkpoints_basic',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/handover_data.xml',
        'views/handover_notes.xml',
        'views/project_handover.xml',
        'views/partner_handover.xml',
        "views/checkpoint_handover.xml",
        'wizard/return_handover_wizard.xml',
        'wizard/handover_summary_wizard.xml',
    ],
    'demo': [
        'demo/handover_demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
