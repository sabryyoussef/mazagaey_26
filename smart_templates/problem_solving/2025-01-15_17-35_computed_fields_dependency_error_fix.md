# Computed Fields Dependency Error Fix

## 🚨 **Problem Analysis**
**Date:** 2025-01-15 17:35  
**Issue:** ValueError: Wrong @depends on '_compute_compatibility_score' - Dependency field 'task_template_ids' not found  
**Root Cause:** Computed fields depending on commented-out Many2many fields

## 🔍 **Problem Details**
- Error: `ValueError: Wrong @depends on '_compute_compatibility_score' (compute method of field smart.project.template.compatibility_score). Dependency field 'task_template_ids' not found in model smart.project.template.`
- Two computed fields were depending on the commented-out template relationship fields:
  - `total_templates` field with `_compute_total_templates` method
  - `compatibility_score` field with `_compute_compatibility_score` method
- These methods had `@api.depends` decorators referencing non-existent fields

## ✅ **Solution Implemented**

### **Step 1: Commented Out Computed Fields in Model**
**File:** `models/core/project_template.py`
```python
# Computed fields (commented out until template relationships are created)
# total_templates = fields.Integer(
#     string='Total Related Templates',
#     compute='_compute_total_templates'
# )

# @api.depends('task_template_ids', 'document_template_ids', 
#              'checkpoint_template_ids', 'milestone_template_ids')
# def _compute_total_templates(self):
#     for record in self:
#         record.total_templates = (
#             len(record.task_template_ids) +
#             len(record.document_template_ids) +
#             len(record.checkpoint_template_ids) +
#             len(record.milestone_template_ids)
#         )

# @api.depends('task_template_ids', 'document_template_ids',
#              'checkpoint_template_ids', 'milestone_template_ids')
# def _compute_compatibility_score(self):
#     for record in self:
#         # Simple compatibility scoring based on template count and types
#         score = 0.0
#         if record.task_template_ids:
#             score += 0.3
#         if record.document_template_ids:
#             score += 0.2
#         if record.checkpoint_template_ids:
#             score += 0.3
#         if record.milestone_template_ids:
#             score += 0.2
#         record.compatibility_score = min(score, 1.0)
```

### **Step 2: Commented Out Field References in Views**
**File:** `views/core/project_template_views.xml`
```xml
<!-- Form view - commented out compatibility_score field -->
<!-- <field name="compatibility_score" readonly="1"/> -->

<!-- List view - commented out computed fields -->
<!-- <field name="total_templates"/> -->
<!-- <field name="compatibility_score"/> -->

<!-- Search view - commented out compatibility filter -->
<!-- <filter string="High Compatibility" name="high_compatibility" 
        domain="[('compatibility_score', '>=', 0.8)]"/> -->
```

## 🎯 **Files Modified**
1. **`models/core/project_template.py`** - Commented out computed fields and methods
2. **`views/core/project_template_views.xml`** - Commented out field references in all views

## 🧪 **Testing Steps**
1. **Upgrade module** from PyCharm
2. **Check logs** - Should be no more dependency errors
3. **Access Project Templates** - Should work without errors
4. **Verify form view** - Should display cleanly without computed fields
5. **Test list view** - Should show available fields only

## 📋 **Expected Results**
- ✅ **No dependency errors** - Module should load successfully
- ✅ **Clean form view** - No broken computed field references
- ✅ **Working list view** - Only existing fields displayed
- ✅ **Functional search** - No broken filter references

## 🔧 **Next Steps for Future Development**
1. **Create template relationship models** when ready
2. **Uncomment Many2many fields** in Project Template model
3. **Uncomment computed fields** and their methods
4. **Uncomment view field references** for computed fields
5. **Test computed field functionality** with real data

## 📝 **Notes**
- This is a temporary fix to resolve dependency errors
- Computed fields can be restored when template relationships are implemented
- Core Project Template functionality remains intact
- Demo data should load without issues

---
**Status:** ✅ **SOLVED** - Computed field dependency errors resolved
