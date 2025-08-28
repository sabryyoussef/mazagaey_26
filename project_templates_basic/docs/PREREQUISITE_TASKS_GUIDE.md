# 📋 Prerequisite Tasks Guide

## Overview
The **Prerequisite Tasks** feature allows you to define dependencies between task templates, ensuring that tasks are executed in the correct order when projects are created from templates.

---

## 🎯 What are Prerequisite Tasks?

Prerequisite tasks define **which task templates must be completed before the current template can start**. This creates an automatic workflow sequence that prevents tasks from being started out of order.

### Key Benefits:
- ✅ **Workflow Standardization** - Consistent task execution order across all projects
- ✅ **Quality Control** - Prevents tasks from starting before prerequisites are complete
- ✅ **Automatic Dependencies** - No manual configuration needed for each project
- ✅ **Template Reusability** - Dependencies are preserved when templates are reused

---

## 🚀 Simple Example: Company Formation Project

### Scenario
You're setting up templates for a company formation project with these logical steps:

1. **Collect Required Documents** (passport, application forms)
2. **Review Documents** (check completeness)  
3. **Submit Documents** (to government authority)
4. **Get Approval** (receive company license)

### Template Setup

```
Template 1: "Collect Required Documents"
├── Prerequisites: None ❌
└── Can start: Immediately ✅

Template 2: "Review Documents" 
├── Prerequisites: "Collect Required Documents" ✅
└── Can start: Only after Template 1 is complete

Template 3: "Submit Documents"
├── Prerequisites: "Review Documents" ✅
└── Can start: Only after Template 2 is complete

Template 4: "Get Approval"
├── Prerequisites: "Submit Documents" ✅
└── Can start: Only after Template 3 is complete
```

### Generated Project Flow

```
✅ Task 1: "Collect Required Documents" (Status: In Progress)
    ↓ (Task 1 must be completed first)
⏳ Task 2: "Review Documents" (Status: Waiting)
    ↓ (Task 2 must be completed first)
⏳ Task 3: "Submit Documents" (Status: Waiting)
    ↓ (Task 3 must be completed first)
⏳ Task 4: "Get Approval" (Status: Waiting)
```

---

## 🔧 How to Configure Prerequisites

### Step 1: Access Task Template
1. Go to **Project Templates** → **Task Templates**
2. Open an existing template or create a new one
3. Navigate to the **Task Configuration** tab

### Step 2: Set Prerequisites
1. In the **Task Configuration** tab, find the **Prerequisite Tasks** field
2. Click the field to see a dropdown of available task templates
3. Select one or more templates that must be completed first
4. Save the template

### UI Location
```
Task Template Form
├── General Information Tab
├── Description Tab
├── Task Configuration Tab ← HERE
│   ├── Task Name Pattern
│   ├── Task Description Pattern  
│   └── Prerequisite Tasks ← THIS FIELD
├── Usage History Tab
└── Milestone Templates Tab
```

---

## 📊 Advanced Examples

### Example 1: Document Processing Workflow

```
Template: "Collect Required Documents"
├── Prerequisites: None
└── Purpose: Initial document collection

Template: "Collect Deliverable Documents" 
├── Prerequisites: "Collect Required Documents"
└── Purpose: Additional deliverables after required docs

Template: "Review All Documents"
├── Prerequisites: ["Collect Required Documents", "Collect Deliverable Documents"]
└── Purpose: Cannot review until ALL documents are collected

Template: "Submit to Authority"
├── Prerequisites: "Review All Documents"
└── Purpose: Final submission after review
```

### Example 2: Milestone Dependencies

```
Template: "Project Setup"
├── Prerequisites: None
└── Type: Custom

Template: "Document Collection Complete"
├── Prerequisites: "Project Setup"
└── Type: Milestone

Template: "Quality Assurance"
├── Prerequisites: "Document Collection Complete"
└── Type: Progress Tracking

Template: "Project Completion"
├── Prerequisites: "Quality Assurance"
└── Type: Milestone
```

---

## ⚙️ Technical Details

### Field Definition
```python
prerequisite_task_ids = fields.Many2many(
    'project.task.template', 
    'task_template_prerequisite_rel', 
    'task_id', 'prerequisite_id',
    string='Prerequisite Tasks'
)
```

### How Dependencies are Applied
1. **Template Level**: Prerequisites defined between task templates
2. **Generation Time**: When creating project from template, system:
   - Creates all tasks from templates
   - Maps template prerequisites to actual task dependencies
   - Sets `depend_on_ids` on generated tasks
3. **Runtime**: Odoo's native task dependency system prevents early task execution

### Pattern Variables Available
When using prerequisites, these variables work in task name/description patterns:
- `{category}` - Document category (Required, Deliverable, etc.)
- `{count}` - Number of documents in the category
- `{project}` - Project name
- `{template}` - Template name
- `{description}` - Template description

---

## 🎯 Best Practices

### 1. Logical Sequence
- Define prerequisites that match real-world workflow
- Avoid circular dependencies (Template A depends on B, B depends on A)

### 2. Clear Naming
- Use descriptive template names that clearly indicate the task purpose
- Example: "Collect Required Documents" instead of "Task 1"

### 3. Granular Dependencies
- Break complex workflows into smaller, manageable tasks
- Each task should have a clear completion criteria

### 4. Test Your Workflow
- Create a test project from your templates to verify the dependency chain
- Ensure the sequence makes business sense

---

## 🚨 Common Issues and Solutions

### Issue 1: Circular Dependencies
**Problem**: Template A depends on Template B, and Template B depends on Template A

**Solution**: Review your workflow logic and break the circle by:
- Adding an intermediate step
- Removing unnecessary dependencies
- Restructuring the workflow

### Issue 2: Too Many Prerequisites
**Problem**: A template depends on many other templates, making it hard to start

**Solution**: 
- Consider if all dependencies are truly necessary
- Group related tasks into milestone templates
- Use progress tracking templates for overview tasks

### Issue 3: Dependencies Not Working
**Problem**: Tasks are created but dependencies are not set

**Troubleshooting**:
1. Check that prerequisite templates exist and are active
2. Verify template names are unique and descriptive
3. Ensure task generation service is properly configured

---

## 📚 Related Documentation

- [Task Template Generation Plan](./plans/TASK_TEMPLATE_GENERATION_PLAN.md)
- [Consolidated Plan](./plans/CONSOLIDATED_PLAN.md)
- [Demo Task Templates](../data/demo_task_templates.xml)

---

## 🆘 Need Help?

If you encounter issues with prerequisite tasks:

1. **Check Demo Data**: Review `demo_task_templates.xml` for working examples
2. **Test Simple Case**: Start with a 2-template dependency chain
3. **Verify Template Names**: Ensure task name patterns generate unique, identifiable names
4. **Check Logs**: Look for task generation errors in Odoo logs

---

*Last Updated: $(date)*
*Module: project_templates_basic*
