# Project Templates Basic - File Organization

## 📁 Proper Directory Structure

```
project_templates_basic/
├── __init__.py
├── __manifest__.py
├── README.md
├── FILE_ORGANIZATION.md
│
├── models/
│   ├── __init__.py
│   ├── core/                           # Core business models
│   │   ├── __init__.py
│   │   ├── task_template.py            # Task template model
│   │   ├── task_generation_service.py  # Task generation service
│   │   └── task_extension.py           # Task model extension
│   ├── template_types/                 # Template type models
│   │   ├── __init__.py
│   │   ├── project_template.py         # Project template model
│   │   ├── document_template.py        # Document template model
│   │   ├── checkpoint_template.py      # Checkpoint template model
│   │   └── checkpoint_template_line.py # Checkpoint template line
│   ├── extensions/                     # Model extensions
│   │   ├── __init__.py
│   │   └── task_extension_unified.py   # Unified task extension
│   └── base/                          # Base/abstract models
│       ├── __init__.py
│       ├── template_base.py            # Template base class
│       └── template_application.py     # Template application logic
│
├── views/
│   ├── menu_views.xml                  # Menu definitions
│   ├── core/                          # Core views
│   │   ├── task_template_views.xml     # Task template views
│   │   └── document_template_views.xml # Document template views
│   ├── template_types/                # Template type views
│   │   └── project_template_views.xml  # Project template views
│   ├── templates/                     # Legacy template views
│   │   └── checkpoint_template_views.xml
│   └── tasks/                         # Task-related views
│       └── task_views.xml
│
├── data/
│   ├── demo_data_consolidated.xml      # Consolidated demo data
│   └── demo_task_templates.xml         # Task template demo data
│
├── security/
│   ├── ir.model.access.csv            # Access rights
│   └── security.xml                   # Security rules
│
├── wizard/
│   ├── __init__.py
│   ├── task_template_selection_wizard.py
│   └── task_template_selection_wizard_views.xml
│
├── tests/
│   ├── __init__.py
│   ├── test_checkpoint_template.py
│   ├── test_project_template.py
│   └── test_template_application.py
│
├── docs/
│   └── plans/
│       ├── CONSOLIDATED_PLAN.md
│       └── TASK_TEMPLATE_GENERATION_PLAN.md
│
└── demo/
    └── demo_data.xml
```

## 🎯 Organization Principles

### **Models Organization:**
- **`core/`**: Main business logic models (task templates, generation service)
- **`template_types/`**: Different types of templates (project, document, checkpoint)
- **`extensions/`**: Model extensions and overrides
- **`base/`**: Abstract models and base classes

### **Views Organization:**
- **`core/`**: Core functionality views (task templates, document templates)
- **`template_types/`**: Template-specific views
- **`templates/`**: Legacy template views (to be migrated)
- **`tasks/`**: Task-related views

### **Data Organization:**
- **`data/`**: XML data files (demo data, configurations)
- **`security/`**: Access rights and security rules
- **`wizard/`**: Wizard models and views
- **`tests/`**: Unit tests
- **`docs/`**: Documentation and plans

## 🔄 Migration Status

### ✅ **Completed:**
- Task template models moved to `models/core/`
- Document template views moved to `views/core/`
- Project template views moved to `views/template_types/`
- Base models moved to `models/base/`
- All `__init__.py` files updated
- Manifest updated with new paths

### 📋 **Pending:**
- Migrate checkpoint template views from `views/templates/` to `views/template_types/`
- Consolidate demo data files
- Update test file organization
- Clean up legacy files

## 🚀 Benefits

1. **Clear Separation**: Each type of functionality has its own directory
2. **Maintainable**: Easy to find and modify specific components
3. **Scalable**: New features can be added to appropriate directories
4. **Consistent**: Follows established Odoo module patterns
5. **Documented**: Clear structure documentation for future development
