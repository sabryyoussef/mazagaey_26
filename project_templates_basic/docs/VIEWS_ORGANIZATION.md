# Views Organization

## 📁 **Views Directory Structure**

```
views/
├── templates/           # Template-related views
│   ├── project_template_views.xml
│   ├── checkpoint_template_views.xml
│   └── task_template_views.xml
├── tasks/              # Task-related views
│   └── task_views.xml
├── wizards/            # Wizard views (future)
│   └── (wizard views will go here)
└── menu_views.xml      # Menu definitions
```

## 🎯 **Organization Logic**

### **Templates Directory**
- **Purpose**: All template-related views
- **Files**: Project, checkpoint, and task template views
- **Models**: `project.project`, `project.checkpoint.template`, `project.document.template`

### **Tasks Directory**  
- **Purpose**: Task-related views and extensions
- **Files**: Task views with template integration
- **Models**: `project.task` extensions

### **Wizards Directory**
- **Purpose**: Wizard views for template selection and application
- **Files**: Template selection wizards (located in wizard/ directory)
- **Models**: `task.template.selection.wizard`

### **Root Views Directory**
- **Purpose**: Menu definitions and general views
- **Files**: Menu structures and navigation

## 📊 **Manifest Configuration**

The views are loaded in the following order in `__manifest__.py`:

```python
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
```

## ✅ **Benefits of This Organization**

1. **Clear Separation**: Each directory has a specific purpose
2. **Easy Maintenance**: Related views are grouped together
3. **Scalability**: Easy to add new view categories
4. **Logical Structure**: Follows Odoo best practices
5. **Better Navigation**: Developers can quickly find relevant views

## 🔍 **View File Contents**

### **Project Template Views** (`templates/project_template_views.xml`)
- List view with template-specific fields
- Form view with template configuration
- Search view with category filters
- Action and menu definitions

### **Checkpoint Template Views** (`templates/checkpoint_template_views.xml`)
- Template form and list views
- Milestone configuration
- Checkpoint lines management

### **Task Template Views** (`templates/task_template_views.xml`)
- Document template views
- Task template configuration
- Template line management

### **Task Views** (`tasks/task_views.xml`)
- Extended task views with template integration
- Template application features

### **Menu Views** (`menu_views.xml`)
- Main menu structure
- Template navigation
- Action definitions

## 🚀 **Future Enhancements**

The organized structure allows for easy addition of:
- **Wizard Views**: In `wizards/` directory
- **Report Views**: In `reports/` directory
- **Dashboard Views**: In `dashboards/` directory
- **Mobile Views**: In `mobile/` directory

This organization ensures the module remains maintainable and scalable as it grows.
