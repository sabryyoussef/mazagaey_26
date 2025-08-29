{
    'name': 'FSM Workflow → Quotation v2',
    'version': '18.0.1.0.0',
    'summary': 'FSM Workflow Quotation System',
    'description': """
        FSM Workflow Quotation System v2
        ================================
        
        This module provides a comprehensive Field Service Management (FSM) workflow 
        system integrated with quotations and project management.
        
        Key Features:
        * FSM Workflow Instances
        * Integrated Quotation System  
        * Project and Checkpoint Management
        * Time & Materials or Fixed Price workflows
        * Handover Notes Integration
        
    """,
    'author': 'Sabry',
    'website': 'https://github.com/sabryyoussef/mazagawy',
    'category': 'Services',
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
        'security/ir.model.access.csv',
        'views/fsm_workflow_instance_views.xml',
        'wizards/fsm_workflow_create_wizard_views.xml',
    ],
    'installable': True,
    'application': True,
}
