# -*- coding: utf-8 -*-
{
    "name": "Project Templates Basic",
    "summary": "Unified template management system for project tasks - consolidates checkpoint and document templates",
    "version": "18.0.1.0.0",
    "category": "Project",
    "author": "Sabry",
    "license": "LGPL-3",
    "depends": [
        "base",
        "project",
        "product",
        "documents",  # For document templates
        "project_checkpoints_basic",  # For milestone templates
        "sale_management"  # For quotation templates
    ],
    "data": [
        # Security
        "security/security.xml",
        "security/ir.model.access.csv",
        
        # Views - Core
        "views/core/task_template_views.xml",
        "views/core/workflow_template_views.xml",
        
        # Views - Templates
        "views/templates/checkpoint_template_views.xml",
        "views/templates/milestone_template_views.xml",
        "views/templates/project_template_views.xml",
        "views/templates/document_template_views.xml",
        "views/template_quotation_views.xml",
        
        # Views - Tasks
        "views/tasks/task_views.xml",
        
        # Views - Menus
        "views/menu_views.xml",
        
        # Wizards
        "wizard/task_template_selection_wizard_views.xml",
        "wizard/workflow_template_wizard_views.xml",
        
        # Demo Data
        "data/demo_task_templates.xml",
        "data/demo_document_templates.xml"
    ],
    "demo": [
        "data/demo_data_consolidated.xml"
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
    "sequence": 1,
}