# -*- coding: utf-8 -*-
{
    "name": "Project Checkpoints Basic",
    "summary": "Basic checkpoint functionality for project tasks - Step by step development",
    "version": "18.0.1.0.0",
    "category": "Project",
    "author": "Sabry",
    "license": "LGPL-3",
    "depends": [
        "base",
        "project",
        "product",
        "documents"  # For document integration
    ],
    "data": [
        # Security (load first)
        "security/ir.model.access.csv",
        # Core views (actions first)
        "views/core/checkpoint_views.xml",
        "views/core/checkpoint_tag_views.xml",
        "views/core/checkpoint_checklist_views.xml",
        # Extension views (actions first)
        "views/extensions/task_views.xml",
        "views/extensions/product_views.xml",
        "views/extensions/milestone_views.xml",
        # Template views
        "views/templates/milestone_template_views.xml",
        # Menu views (load last after all actions are defined)
        "views/core/menu_views.xml"
    ],
    "demo": [
        "data/demo_data_consolidated.xml",
        "data/demo_visibility_conditions.xml",
        "demo/demo_data.xml"
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
}
