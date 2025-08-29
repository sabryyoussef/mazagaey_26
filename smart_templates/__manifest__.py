# -*- coding: utf-8 -*-
{
    "name": "Smart Templates",
    "summary": "Intelligent template management system with user preferences and smart suggestions",
    "version": "18.0.1.0.0",
    "category": "Project Management",
    "author": "Sabry",
    "license": "LGPL-3",
    "website": "https://github.com/sabryyoussef",
    "depends": [
        "base",
        "project",
        "product",
        "documents",
        "sale_management",
        "project_checkpoints_basic",  # For checkpoint functionality
        "unified_documents",  # For document integration
    ],
    "data": [
        # Security
        "security/smart_templates_security.xml",
        "security/ir.model.access.csv",
        
        # Core Models
        "models/core/__init__.py",
        "models/preferences/__init__.py",
        "models/integrations/__init__.py",
        "models/__init__.py",
        
        # Views - Core
        "views/core/project_template_views.xml",
        "views/core/workflow_template_views.xml",
        "views/core/task_template_views.xml",
        "views/core/document_template_views.xml",
        "views/core/checkpoint_template_views.xml",
        "views/core/milestone_template_views.xml",
        
        # Views - Preferences
        "views/preferences/user_preferences_views.xml",
        "views/preferences/template_preferences_views.xml",
        
        # Views - Wizard
        "views/wizard/template_suggestion_wizard_views.xml",
        "views/wizard/preferences_configuration_wizard_views.xml",
        
        # Menus
        "views/menu_views.xml",
        
        # Data
        "data/smart_templates_data.xml",
        "data/demo_data.xml",
    ],
    "demo": [
        "data/demo_data.xml",
    ],
    "application": True,
    "installable": True,
    "auto_install": False,
    "sequence": 1,
    "images": [
        "static/description/banner.png",
        "static/description/icon.png",
    ],
    "description": """
Smart Templates Module
=====================

An intelligent template management system that provides:

**Core Features:**
- Smart template suggestions based on context
- User-configurable behavior preferences
- Intelligent template relationships
- Learning from usage patterns

**Template Types:**
- Project Templates (primary)
- Workflow Templates (advanced)
- Task Templates
- Document Templates
- Checkpoint Templates
- Milestone Templates

**Smart Features:**
- Context-aware suggestions
- Dynamic template filtering
- Intelligent default values
- Template compatibility checking
- Usage pattern learning

**User Experience:**
- Configurable aggressiveness levels
- Flexible trigger behaviors
- Intuitive interface
- Comprehensive guidance
- Performance optimization

**Integration:**
- Seamless integration with existing modules
- Document management integration
- Quotation system integration
- FSM workflow integration
- Reporting and analytics

This module replaces the existing template system with a more intelligent, user-friendly, and maintainable solution.
    """,
}
