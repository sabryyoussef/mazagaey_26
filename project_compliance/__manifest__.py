{
    'name': "Project Compliance",
    'summary': "Compliance functionality for Odoo projects with shareholder management",
    'description': """
        This module provides comprehensive compliance functionality for Odoo projects,
        including shareholder management, UBO tracking, and compliance workflows.
        Integrates with project_handover_notes, unified_documents, project_templates_basic,
        and project_checkpoints_basic modules.
    """,
    'author': "BeshoyWageh",
    'version': '18.0.1.0.0',
    'category': 'Project Management',
    'depends': [
        'base',
        'project',
        'mail',
        'unified_documents',
        'project_handover_notes',
        'project_templates_basic',
        'project_checkpoints_basic'
    ],
                    'data': [
                    'security/security.xml',
                    'security/ir.model.access.csv',
                    'data/compliance_data.xml',
                    'data/fix_dangling_fks.xml',
                    'demo/demo_data.xml',
                    'views/business_shareholder.xml',
                    'views/project_compliance.xml',
                    'views/partner_compliance.xml',
                    'wizard/return_compliance_wizard.xml'
                ],
    'demo': [
        'demo/demo_data.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
