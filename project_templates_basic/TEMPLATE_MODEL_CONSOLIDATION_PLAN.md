# Template Model Consolidation Plan

## Overview

This document outlines the plan for consolidating all template models into a unified, maintainable structure within the `project_templates_basic` module.

## Current State Analysis

### Template Models Distribution

| Model | Current Location | Purpose | Status |
|-------|-----------------|---------|--------|
| `project.checkpoint.template` | `project_templates_basic` | Checkpoint templates | ✅ Consolidated |
| `project.document.template` | `project_templates_basic` | Document templates | ✅ Consolidated |
| `project.milestone.template` | `project_checkpoints_basic` | Milestone templates | 🔄 To be moved |
| `project.task.template` | `project_templates_basic` | Task templates | ✅ Consolidated |
| `workflow.template` | `project_templates_basic` | Workflow templates | ✅ Consolidated |
| `project.project` (template fields) | `project_templates_basic` | Project templates | ✅ Consolidated |

### Related Models

| Model | Current Location | Purpose | Status |
|-------|-----------------|---------|--------|
| `project.checkpoint.template.line` | `project_templates_basic` | Checkpoint template lines | ✅ Consolidated |
| `project.document.template.line` | `project_templates_basic` | Document template lines | ✅ Consolidated |
| `project.milestone.template.checkpoint` | `project_checkpoints_basic` | Milestone template checkpoints | 🔄 To be moved |
| `project.checklist.template.line` | `project_templates_basic` | Checklist template lines | ✅ Consolidated |
| `project.template.usage` | `project_templates_basic` | Template usage tracking | ✅ Consolidated |
| `project.checklist.item` | `project_templates_basic` | Checklist items | ✅ Consolidated |

## Consolidation Strategy

### Phase 1: Move Milestone Templates (Priority: High)

#### 1.1 Move Milestone Template Models

**Source:** `mazagawy/custom_addons/project_checkpoints_basic/models/templates/`
**Destination:** `mazagawy/custom_addons/project_templates_basic/models/templates/`

**Files to Move:**
- `milestone_template.py` → `milestone_template.py` (already exists, merge content)
- `milestone_template_checkpoint.py` → `milestone_template_checkpoint.py` (already exists, merge content)

#### 1.2 Update Model Imports

**File:** `mazagawy/custom_addons/project_templates_basic/models/templates/__init__.py`
```python
# Already includes:
from . import milestone_template
from . import milestone_template_checkpoint
```

#### 1.3 Update Security Access Rights

**File:** `mazagawy/custom_addons/project_templates_basic/security/ir.model.access.csv`
```csv
# Already includes milestone template access rights
access_project_milestone_template_user,project.milestone.template.user,model_project_milestone_template,base.group_user,1,1,1,0
access_project_milestone_template_manager,project.milestone.template.manager,model_project_milestone_template,base.group_system,1,1,1,1
access_project_milestone_template_checkpoint_user,project.milestone.template.checkpoint.user,model_project_milestone_template_checkpoint,base.group_user,1,1,1,0
access_project_milestone_template_checkpoint_manager,project.milestone.template.checkpoint.manager,model_project_milestone_template_checkpoint,base.group_system,1,1,1,1
```

#### 1.4 Update Views

**File:** `mazagawy/custom_addons/project_templates_basic/views/templates/milestone_template_views.xml`
- ✅ Already exists and properly configured

#### 1.5 Update Demo Data

**File:** `mazagawy/custom_addons/project_templates_basic/data/demo_data_consolidated.xml`
- ✅ Already includes milestone template demo data

### Phase 2: Update Module Dependencies

#### 2.1 Update project_checkpoints_basic Manifest

**File:** `mazagawy/custom_addons/project_checkpoints_basic/__manifest__.py`
```python
{
    "depends": [
        "base",
        "project",
        "product",
        "documents",
        "project_templates_basic"  # Add dependency
    ],
    # Remove milestone template views from data list
    "data": [
        "security/ir.model.access.csv",
        "views/core/checkpoint_views.xml",
        "views/core/checkpoint_tag_views.xml",
        "views/extensions/task_views.xml",
        "views/extensions/product_views.xml",
        "views/extensions/milestone_views.xml",
        # Remove: "views/templates/milestone_template_views.xml",
        "views/core/menu_views.xml"
    ],
}
```

#### 2.2 Update project_templates_basic Manifest

**File:** `mazagawy/custom_addons/project_templates_basic/__manifest__.py`
```python
{
    "depends": [
        "base",
        "project",
        "product",
        "documents",
        "project_checkpoints_basic"  # Keep dependency for core functionality
    ],
}
```

### Phase 3: Clean Up project_checkpoints_basic

#### 3.1 Remove Milestone Template Files

**Files to Delete:**
- `mazagawy/custom_addons/project_checkpoints_basic/models/templates/milestone_template.py`
- `mazagawy/custom_addons/project_checkpoints_basic/models/templates/milestone_template_checkpoint.py`
- `mazagawy/custom_addons/project_checkpoints_basic/models/templates/__init__.py`

#### 3.2 Update project_checkpoints_basic Models Init

**File:** `mazagawy/custom_addons/project_checkpoints_basic/models/__init__.py`
```python
# Core models
from .core import project_task_checkpoint
from .core import checkpoint_tag

# Extension models
from .extensions import task_extension
from .extensions import product_extension
from .extensions import milestone_extension

# Rule models
from .rules import checkpoint_rule

# Remove template imports:
# from .templates import milestone_template
# from .templates import milestone_template_checkpoint
```

#### 3.3 Remove Template Directory

**Directory to Delete:**
- `mazagawy/custom_addons/project_checkpoints_basic/models/templates/`

### Phase 4: Update References and Imports

#### 4.1 Update Any Remaining References

**Search and Replace:**
- `project_checkpoints_basic.milestone_template` → `project_templates_basic.milestone_template`
- `project_checkpoints_basic.milestone_template_checkpoint` → `project_templates_basic.milestone_template_checkpoint`

#### 4.2 Update Action References

**File:** `mazagawy/custom_addons/project_templates_basic/views/menu_views.xml`
```xml
<!-- Milestone Templates Submenu -->
<menuitem id="menu_project_templates_milestone_templates"
          name="Milestone Templates"
          parent="menu_project_templates_root"
          action="action_project_milestone_template"
          sequence="25"
          groups="base.group_user"/>
```

### Phase 5: Testing and Validation

#### 5.1 Test Cases

1. **Module Loading Test**
   - Verify both modules load without errors
   - Check for any missing dependencies

2. **Model Access Test**
   - Verify milestone template models are accessible
   - Test CRUD operations on milestone templates

3. **View Loading Test**
   - Verify milestone template views load correctly
   - Test menu navigation to milestone templates

4. **Demo Data Test**
   - Verify demo milestone templates are created
   - Test template application functionality

#### 5.2 Validation Checklist

- [ ] All milestone template models accessible
- [ ] Views load without errors
- [ ] Menus display correctly
- [ ] Demo data loads properly
- [ ] No duplicate menus
- [ ] No broken references
- [ ] Module dependencies correct

## Final Structure

### After Consolidation

```
project_templates_basic/
├── models/
│   ├── templates/
│   │   ├── __init__.py
│   │   ├── checkpoint_template.py
│   │   ├── checkpoint_template_line.py
│   │   ├── document_template.py
│   │   ├── document_template_line.py
│   │   ├── checklist_template_line.py
│   │   ├── template_usage.py
│   │   ├── checklist_item.py
│   │   ├── milestone_template.py
│   │   ├── milestone_template_checkpoint.py
│   │   ├── project_template.py
│   │   └── task_template.py
│   ├── core/
│   │   ├── workflow_template.py
│   │   └── task_generation_service.py
│   └── __init__.py
├── views/
│   ├── templates/
│   │   ├── checkpoint_template_views.xml
│   │   ├── document_template_views.xml
│   │   ├── milestone_template_views.xml
│   │   ├── project_template_views.xml
│   │   └── task_template_views.xml
│   └── menu_views.xml
├── data/
│   └── demo_data_consolidated.xml
└── security/
    └── ir.model.access.csv
```

```
project_checkpoints_basic/
├── models/
│   ├── core/
│   │   ├── project_task_checkpoint.py
│   │   └── checkpoint_tag.py
│   ├── extensions/
│   │   ├── task_extension.py
│   │   ├── product_extension.py
│   │   └── milestone_extension.py
│   ├── rules/
│   │   └── checkpoint_rule.py
│   └── __init__.py
├── views/
│   ├── core/
│   │   ├── checkpoint_views.xml
│   │   ├── checkpoint_tag_views.xml
│   │   └── menu_views.xml
│   └── extensions/
│       ├── task_views.xml
│       ├── product_views.xml
│       └── milestone_views.xml
└── security/
    └── ir.model.access.csv
```

## Benefits of Consolidation

### 1. **Unified Template Management**
- All template models in one place
- Consistent template management interface
- Easier to maintain and extend

### 2. **Clear Module Responsibilities**
- `project_templates_basic`: Template management and creation
- `project_checkpoints_basic`: Core checkpoint functionality

### 3. **Reduced Complexity**
- No duplicate models
- Clear dependencies
- Simplified module structure

### 4. **Better User Experience**
- All templates accessible from one menu
- Consistent interface across template types
- Unified demo data

## Risk Mitigation

### 1. **Backup Strategy**
- Create backup of current state before changes
- Use version control for rollback capability

### 2. **Incremental Implementation**
- Implement changes in phases
- Test each phase before proceeding

### 3. **Validation Testing**
- Comprehensive testing after each phase
- Verify no breaking changes

### 4. **Documentation Updates**
- Update all related documentation
- Update README files
- Update module descriptions

## Implementation Timeline

### Week 1: Phase 1 - Move Milestone Templates
- Move milestone template models
- Update imports and security
- Test basic functionality

### Week 2: Phase 2-3 - Update Dependencies and Cleanup
- Update module dependencies
- Clean up old files
- Test module loading

### Week 3: Phase 4-5 - Final Updates and Testing
- Update remaining references
- Comprehensive testing
- Documentation updates

## Success Criteria

1. **✅ All template models consolidated** in `project_templates_basic`
2. **✅ No duplicate models** across modules
3. **✅ All views and menus work** correctly
4. **✅ Demo data loads** without errors
5. **✅ No breaking changes** for existing functionality
6. **✅ Clear module separation** of concerns
7. **✅ Comprehensive documentation** updated

## Rollback Plan

If issues arise during consolidation:

1. **Immediate Rollback**: Restore from version control
2. **Partial Rollback**: Revert specific phases
3. **Alternative Approach**: Keep current structure if consolidation proves problematic

---

**Last Updated:** 2025-08-24  
**Author:** Template Consolidation Team  
**Status:** Planning Phase
