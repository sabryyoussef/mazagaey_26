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
    ],
    "data": [
        # Security
        "security/security.xml",
        "security/ir.model.access.csv",
        
        # Views - Templates
        "views/templates/project_template_views.xml",
        "views/templates/checkpoint_template_views.xml",
        "views/templates/task_template_views.xml",
        
        # Views - Tasks
        "views/tasks/task_views.xml",
        
        # Views - Menus
        "views/menu_views.xml",
        
        # Wizards
        "wizard/task_template_selection_wizard_views.xml",
    ],
    "demo": [
        "data/demo_data_consolidated.xml",
        "demo/demo_data.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
    "sequence": 1,
}