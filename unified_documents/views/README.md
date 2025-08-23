# Unified Documents Views Organization

This directory contains all the view definitions for the Unified Documents module, organized into logical subdirectories for better maintainability and clarity.

## 📁 Directory Structure

```
views/
├── README.md                           # This documentation file
├── core/                               # Core document functionality views
│   ├── documents_document_views.xml    # Extended documents.document views
│   ├── document_copy_automation_views.xml # Automation rule views
│   └── document_management_views.xml   # Document management views
├── extensions/                         # Odoo model extension views
│   ├── ir_attachment_views.xml        # Extended ir.attachment views
│   ├── task_views.xml                 # Project task extension views
│   └── task_views_new.xml             # New task view implementations
├── integrations/                       # Third-party module integration views
│   ├── product_views.xml              # Product integration views
│   ├── product_template_views.xml     # Product template views
│   ├── project_views.xml              # Project integration views
│   ├── sale_order_views.xml           # Sale order integration views
│   └── sale_order_line_views.xml      # Sale order line integration views
└── menu_views.xml                     # Menu structure and navigation
```

## 🎯 Purpose of Each Directory

### **Core Views (`core/`)**
Contains the fundamental document management view definitions:
- **`documents_document_views.xml`** (4.3KB): Extended views for the base `documents.document` model with additional fields and functionality
- **`document_copy_automation_views.xml`** (10KB): Views for document copy automation rules and management
- **`document_management_views.xml`** (945B): General document management interface views

### **Extension Views (`extensions/`)**
Contains views that extend existing Odoo models:
- **`ir_attachment_views.xml`** (1.3KB): Extended views for `ir.attachment` with folder selection and document linking
- **`task_views.xml`** (1.7KB): Views for project task document management extensions
- **`task_views_new.xml`** (1.7KB): New implementation of task views with enhanced features

### **Integration Views (`integrations/`)**
Contains views for integrating with other Odoo modules:
- **`product_views.xml`** (15KB): Product template document management views with smart buttons and statistics
- **`product_template_views.xml`** (10KB): Product template specific views and forms
- **`project_views.xml`** (13KB): Project document management and automation views
- **`sale_order_views.xml`** (951B): Sale order document integration views
- **`sale_order_line_views.xml`** (1.7KB): Sale order line document management views

### **Menu Views (`menu_views.xml`)**
Contains the menu structure and navigation:
- **`menu_views.xml`** (3.3KB): Main menu structure, submenus, and navigation hierarchy

## 📋 View Descriptions

### Core Views
- **`documents_document_views.xml`**: Extends the base document views with categories, status, expiry dates, verification, and smart buttons
- **`document_copy_automation_views.xml`**: Provides interface for managing document copy automation rules and execution
- **`document_management_views.xml`**: General document management and browsing interface

### Extension Views
- **`ir_attachment_views.xml`**: Extends attachment views with folder selection and document linking capabilities
- **`task_views.xml`**: Adds document management features to project task views
- **`task_views_new.xml`**: Enhanced task views with improved document integration

### Integration Views
- **`product_views.xml`**: Comprehensive product document management with smart buttons, statistics, and copy functionality
- **`product_template_views.xml`**: Product template specific views and document associations
- **`project_views.xml`**: Project document management with automation and smart buttons
- **`sale_order_views.xml`**: Sale order document integration and management
- **`sale_order_line_views.xml`**: Sale order line document handling and automation

## 🔧 Development Guidelines

1. **Adding New Views**: Place them in the appropriate subdirectory based on their purpose
2. **View Naming**: Use descriptive names that indicate the model and functionality
3. **Inheritance**: Prefer view inheritance over creating new views when extending existing functionality
4. **Smart Buttons**: Use smart buttons for related record navigation and statistics
5. **Consistency**: Maintain consistent styling and layout across similar views
6. **Documentation**: Add comments for complex view logic and custom widgets

## 🚀 Benefits of This Organization

- **Maintainability**: Easier to find and modify specific view functionality
- **Scalability**: Clear structure for adding new views and features
- **Clarity**: Logical separation of concerns between core, extensions, and integrations
- **Collaboration**: Multiple developers can work on different view areas without conflicts
- **Testing**: Easier to write and organize view-specific tests

## 📝 View Loading Order

The views are loaded in the following order in the manifest:
1. **Core views** - Fundamental document functionality
2. **Extension views** - Model extensions and enhancements
3. **Integration views** - Third-party module integrations
4. **Menu views** - Navigation structure (loaded last)

This ensures that all view dependencies are available before they are referenced.
