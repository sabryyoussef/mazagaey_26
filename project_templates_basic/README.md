# Project Templates Basic

## Overview

**Project Templates Basic** is a standalone Odoo module that provides a unified template management system for project tasks. It consolidates the template functionality from both `project_checkpoints_basic` and `unified_documents` modules into a single, maintainable solution.

## 📚 **Documentation**

📖 **[Full Documentation](docs/README.md)** - Complete documentation with guides, API references, and examples

📋 **[Development Plans](docs/plans/)** - Implementation plans and roadmaps

🔧 **[API Reference](docs/api/)** - Technical documentation and model references

💡 **[Examples](docs/examples/)** - Code examples and use cases

## 🎯 **Key Features**

- ✅ **Unified Template System** - Single interface for all template types
- ✅ **Multi-Type Templates** - Checkpoints, Documents, Checklists, Milestones
- ✅ **Flexible Application** - Apply to tasks, projects, or products
- ✅ **Progress Tracking** - Unified progress calculation
- ✅ **Auto-Application** - Configurable automatic template application
- ✅ **Audit Trail** - Complete tracking of template applications
- ✅ **Development-Friendly** - Simple module replacement approach

## 🏗️ **Architecture**

### **Core Models**

1. **ProjectTemplateBase** (`project.template.base`)
   - Abstract base model for all template types
   - Common fields and methods for template management
   - Template application logic

2. **ProjectTemplateApplication** (`project.template.application`)
   - Tracks all template applications
   - Provides audit trail and usage statistics
   - Progress monitoring and status tracking

3. **Template Type Models**
   - `project.checkpoint.template` - Checkpoint templates
   - `project.document.template` - Document templates
   - `project.checklist.template` - Checklist templates
   - `project.milestone.template` - Milestone templates

### **Extension Models**

- **Project Task Extension** - Adds template functionality to tasks
- **Project Extension** - Adds template configuration to projects
- **Product Extension** - Adds template associations to products

## 📦 **Installation**

### **Prerequisites**
- Odoo 18.0
- Project module
- Documents module (for document templates)

### **Installation Steps**

1. **Copy the module** to your Odoo addons directory
2. **Update the addons list** in Odoo
3. **Install the module** via Apps menu
4. **Configure security groups** as needed

```bash
# Copy module to addons directory
cp -r project_templates_basic /path/to/odoo/addons/

# Update addons list
./odoo-bin -c odoo.conf -u all

# Install module
./odoo-bin -c odoo.conf -i project_templates_basic
```

## 🔧 **Configuration**

### **Security Groups**

The module creates three security groups:

1. **Project Templates User**
   - View and apply templates
   - Track progress

2. **Project Templates Manager**
   - Create and edit templates
   - Manage template applications

3. **Project Templates Administrator**
   - Full access to all functionality
   - System configuration

### **Settings**

Configure template behavior in:
- **Project Settings** → **Templates**
- **Product Settings** → **Template Associations**
- **Task Settings** → **Template Application**

## 📊 **Usage**

### **Creating Templates**

1. **Navigate to** Project → Templates → [Template Type]
2. **Click Create** to add a new template
3. **Configure** template settings and items
4. **Save** the template

### **Applying Templates**

1. **Open** a task, project, or product
2. **Click** "Apply Template" button
3. **Select** the desired template
4. **Confirm** the application

### **Tracking Progress**

1. **View** template applications in the template record
2. **Monitor** progress percentages
3. **Update** status as items are completed

## 🔄 **Module Replacement**

### **Simple Replacement Strategy**

Since you're in development with demo data, the replacement process is straightforward:

1. **Build the new module** from scratch
2. **Create fresh demo data** for the new module
3. **Test functionality** in clean environment
4. **Replace old modules** when ready

### **Replacement Steps**

```bash
# 1. Create fresh database for testing
createdb odoo_test_template

# 2. Install new module only
./odoo-bin -c odoo.conf -d odoo_test_template -i project_templates_basic

# 3. Test all functionality
# - Template creation
# - Template application
# - Progress tracking
# - UI functionality

# 4. When ready, replace old modules
./odoo-bin -c odoo.conf -d odoo_production -u project_checkpoints_basic
./odoo-bin -c odoo.conf -d odoo_production -u unified_documents
./odoo-bin -c odoo.conf -d odoo_production -i project_templates_basic
```

### **No Complex Migration Needed:**
- ✅ Fresh database creation anytime
- ✅ Demo data only (no production data)
- ✅ Clean development environment
- ✅ Simple module replacement

## 🧪 **Testing**

### **Development Testing**

```bash
# Create test database
createdb odoo_test_template

# Install module
./odoo-bin -c odoo.conf -d odoo_test_template -i project_templates_basic

# Test functionality
# - Create templates
# - Apply to tasks
# - Check progress tracking
# - Verify UI

# If issues found, fix and repeat
```

### **Unit Tests**

Run unit tests to verify functionality:

```bash
./odoo-bin -c odoo.conf -d test_db --test-enable --stop-after-init
```

### **Test Coverage**

The module includes tests for:
- Template creation and management
- Template application
- Progress tracking
- Integration functionality

## 📈 **Performance Considerations**

### **Optimization Tips**

1. **Indexing** - Database indexes on frequently queried fields
2. **Caching** - Computed fields are cached where appropriate
3. **Batch Operations** - Use batch processing for large datasets
4. **Cleanup** - Regular cleanup of orphaned applications

### **Monitoring**

Monitor performance using:
- Database query logs
- Template application statistics
- Progress calculation metrics

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Template Not Applying**
   - Check user permissions
   - Verify template is active
   - Ensure target model is supported

2. **Progress Not Updating**
   - Run progress calculation manually
   - Check for data integrity issues
   - Verify template type implementation

3. **Module Conflicts**
   - Ensure old modules are uninstalled
   - Check for model inheritance conflicts
   - Verify view inheritance

### **Debug Mode**

Enable debug mode for detailed error information:

```python
# In Odoo shell
import logging
logging.getLogger('project_templates_basic').setLevel(logging.DEBUG)
```

## 📚 **API Reference**

### **Template Base Model**

```python
class ProjectTemplateBase(models.AbstractModel):
    _name = 'project.template.base'
    
    # Apply template to target
    def action_apply_template(self, target_model, target_id):
        pass
    
    # Get available templates
    @api.model
    def get_available_templates(self, target_model, target_id=None):
        pass
```

### **Template Application Model**

```python
class ProjectTemplateApplication(models.Model):
    _name = 'project.template.application'
    
    # Get applications for target
    @api.model
    def get_applications_for_target(self, target_model, target_id):
        pass
    
    # Update progress
    def action_update_progress(self):
        pass
```

## 🤝 **Contributing**

### **Development Setup**

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Add** tests for new functionality
5. **Submit** a pull request

### **Code Standards**

- Follow Odoo coding standards
- Add docstrings to all methods
- Include type hints where appropriate
- Write comprehensive tests

## 📄 **License**

This module is licensed under LGPL-3. See the LICENSE file for details.

## 🆘 **Support**

### **Documentation**

- [User Guide](docs/user_guide.md)
- [Developer Guide](docs/developer_guide.md)
- [Development Plan](DEVELOPMENT_PLAN.md)
- [Module Replacement Plan](MIGRATION_PLAN.md)

### **Issues**

Report issues and feature requests on the project repository.

### **Community**

Join the community discussion for:
- Best practices
- Customization tips
- Integration examples

## 🔮 **Roadmap**

### **Future Features**

- [ ] Advanced template inheritance
- [ ] Template versioning
- [ ] Bulk template operations
- [ ] Template analytics dashboard
- [ ] API endpoints for external integration
- [ ] Mobile app support

### **Performance Improvements**

- [ ] Database query optimization
- [ ] Caching improvements
- [ ] Background job processing
- [ ] Real-time progress updates

---

**Version:** 18.0.1.0.0  
**Last Updated:** 2024  
**Compatibility:** Odoo 18.0+
