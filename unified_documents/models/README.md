# Unified Documents Models Organization

This directory contains all the models for the Unified Documents module, organized into logical subdirectories for better maintainability and clarity.

## 📁 Directory Structure

```
models/
├── __init__.py                    # Main models import file
├── core/                          # Core document functionality
│   ├── __init__.py
│   ├── documents_document.py      # Extended documents.document model
│   ├── unified_document_service.py # Main service logic and utilities
│   └── document_copy_automation.py # Document copy automation rules
├── extensions/                    # Odoo model extensions
│   ├── __init__.py
│   ├── ir_attachment.py          # Extended ir.attachment model
│   ├── ir_attachment_extension.py # Additional attachment features
│   └── task_extension.py         # Project task extensions
└── integrations/                  # Third-party module integrations
    ├── __init__.py
    ├── product_extension.py      # Product template integration
    ├── product_template.py       # Product template logic
    ├── project_extension.py      # Project integration
    ├── sale_order_extension.py   # Sale order integration
    └── sale_order_line_extension.py # Sale order line integration
```

## 🎯 Purpose of Each Directory

### **Core Models (`core/`)**
Contains the fundamental document management functionality:
- **`documents_document.py`**: Extends the base `documents.document` model with additional fields and methods
- **`unified_document_service.py`**: Main service class with document copy, categorization, and automation logic
- **`document_copy_automation.py`**: Defines automation rules for copying documents between models

### **Extension Models (`extensions/`)**
Contains extensions to existing Odoo models:
- **`ir_attachment.py`**: Extends `ir.attachment` with folder selection and document linking
- **`ir_attachment_extension.py`**: Additional attachment functionality and utilities
- **`task_extension.py`**: Extends project tasks with document management features

### **Integration Models (`integrations/`)**
Contains integrations with other Odoo modules:
- **`product_extension.py`**: Product template document management
- **`product_template.py`**: Product template logic and document associations
- **`project_extension.py`**: Project document management and automation
- **`sale_order_extension.py`**: Sale order document integration
- **`sale_order_line_extension.py`**: Sale order line document management

## 📋 File Descriptions

### Core Files
- **`documents_document.py`** (10KB): Extended document model with categories, status, expiry dates, and verification
- **`unified_document_service.py`** (51KB): Main service with document copy, categorization, and automation methods
- **`document_copy_automation.py`** (15KB): Automation rules and execution logic

### Extension Files
- **`ir_attachment.py`** (5.6KB): Attachment model with folder selection and document linking
- **`ir_attachment_extension.py`** (2.1KB): Additional attachment features and utilities
- **`task_extension.py`** (944B): Task-specific document management extensions

### Integration Files
- **`product_extension.py`** (27KB): Product template document management and automation
- **`product_template.py`** (27KB): Product template logic and document associations
- **`project_extension.py`** (27KB): Project document management and automation
- **`sale_order_extension.py`** (1.8KB): Sale order document integration
- **`sale_order_line_extension.py`** (5.7KB): Sale order line document management

## 🔧 Development Guidelines

1. **Adding New Models**: Place them in the appropriate subdirectory based on their purpose
2. **Import Updates**: Always update the appropriate `__init__.py` file when adding new models
3. **File Naming**: Use descriptive names that indicate the model's purpose
4. **Documentation**: Add docstrings and comments for complex methods
5. **Dependencies**: Be mindful of import dependencies between subdirectories

## 🚀 Benefits of This Organization

- **Maintainability**: Easier to find and modify specific functionality
- **Scalability**: Clear structure for adding new features
- **Clarity**: Logical separation of concerns
- **Collaboration**: Multiple developers can work on different areas without conflicts
- **Testing**: Easier to write and organize tests for specific functionality
