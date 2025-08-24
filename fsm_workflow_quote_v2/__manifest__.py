{
    'name': 'FSM Workflow → Quotation v2',
    'version': '18.0.1.4.0',
    'summary': 'FSM Workflow Quotation System with Advanced Features',
    'description': """
FSM Workflow → Quotation System v2

Features:
- Create workflow instances from templates
- Automatic project and task generation
- Checkpoint tracking and progress calculation
- Quotation generation with multiple pricing policies
- Integration with existing local modules
- Smart buttons for navigation
- Handover notes creation
- Timesheet integration
- Optional FSM integration

Pricing Policies:
- Fixed Price
- Time & Material
- Hourly Rate

Dependencies:
- project_templates_basic
- project_checkpoints_basic
- project_handover_notes
- sale_management
- hr_timesheet
    """,
    'author': 'Sabry',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'project',
        'sale_management',
        'hr_timesheet',
        'project_templates_basic',  # Provides workflow.template model
        'project_checkpoints_basic',  # Provides checkpoint functionality
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'views/fsm_workflow_instance_views.xml',
        'wizards/fsm_workflow_create_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
