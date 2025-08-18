# Prompt Task Template Implementation Plan - UPDATED

## Overview
This document provides a detailed, step-by-step implementation plan for adding reusable "Task Checkpoint Configuration Templates" to the project_checkpoints_basic module. The goal is to enable checkpoint templates that can be linked to service products and automatically instantiated when tasks are created from sales orders.

## Current Implementation Status

### **✅ COMPLETED PHASES:**

**Phase 1: Core Data Models (Steps 1-4)** - ✅ **COMPLETE**
- ✅ Step 1: Create Checkpoint Tag Model
- ✅ Step 2: Create Checkpoint Template Line Model
- ✅ Step 3: Create Checkpoint Rule Model
- ✅ Step 4: Create Checkpoint Template Model

**Phase 2: Product Integration (Steps 5-6)** - ✅ **COMPLETE**
- ✅ Step 5: Extend Product Template Model
- ✅ Step 6: Extend Task Model

**Phase 3: Template Application Logic (Steps 7-9)** - ✅ **COMPLETE**
- ✅ Step 7: Add Template Application Method
- ✅ Step 8: Add Rule Evaluation Method
- ✅ Step 9: Integrate with Checkpoint Changes

**Phase 4: Views and UI (Steps 10-14)** - ✅ **COMPLETE**
- ✅ Step 10: Create Tag Views
- ✅ Step 11: Create Template Views
- ✅ Step 12: Update Product Views
- ✅ Step 13: Update Task Views
- ✅ Step 14: Create Template Application Wizard

**Phase 5: Security and Demo Data (Steps 15-16)** - ✅ **COMPLETE**
- ✅ Step 15: Update Security Rules
- ✅ Step 16: Create Demo Data

### **❌ MISSING/INCOMPLETE:**

**Phase 6: Testing and Integration (Steps 17-20)** - ❌ **NOT STARTED**
- ❌ Step 17: Create Unit Tests
- ❌ Step 18: Add Missing Dependencies
- ❌ Step 19: Implement Automatic Template Application
- ❌ Step 20: Final Integration Testing

---

## Phase 6: Testing and Integration (Steps 17-20)

### **Step 17: Create Unit Tests**
**Goal**: Create comprehensive unit tests

**Files to Create**:
- `tests/__init__.py`
- `tests/test_checkpoint_templates.py`

**Content for `tests/__init__.py`**:
```python
# -*- coding: utf-8 -*-
from . import test_checkpoint_templates
```

**Content for `tests/test_checkpoint_templates.py`**:
```python
# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestCheckpointTemplates(TransactionCase):
    
    def setUp(self):
        super().setUp()
        # Create test data
        self.tag_legal = self.env['project.task.checkpoint.tag'].create({
            'name': 'Legal',
            'color': 1
        })
        
        self.template = self.env['project.task.checkpoint.template'].create({
            'name': 'Test Template',
            'line_ids': [(0, 0, {
                'name': 'Test Checkpoint',
                'tag_ids': [(6, 0, [self.tag_legal.id])],
                'auto_advance_stage': True
            })]
        })
        
        self.product = self.env['product.template'].create({
            'name': 'Test Service',
            'type': 'service',
            'service_tracking': 'task_in_project',
            'checkpoint_template_ids': [(6, 0, [self.template.id])],
            'auto_apply_checkpoint_templates': True
        })
    
    def test_template_creation(self):
        """Test template creation and line association"""
        self.assertEqual(len(self.template.line_ids), 1)
        self.assertEqual(self.template.line_ids[0].name, 'Test Checkpoint')
    
    def test_product_constraints(self):
        """Test product constraint validation"""
        # Should not allow checkpoint templates on non-service products
        with self.assertRaises(ValidationError):
            self.product.type = 'consu'
            self.product.flush_recordset()
    
    def test_task_template_application(self):
        """Test applying templates to tasks"""
        task = self.env['project.task'].create({
            'name': 'Test Task'
        })
        
        # Apply template
        task._apply_checkpoint_templates_from_products([self.product])
        
        # Check that checkpoints were created
        self.assertEqual(len(task.checkpoint_ids), 1)
        self.assertEqual(task.checkpoint_ids[0].name, 'Test Checkpoint')
        self.assertIn(self.template, task.applied_checkpoint_template_ids)
    
    def test_rule_evaluation(self):
        """Test rule evaluation logic"""
        # Create a rule
        rule = self.env['project.task.checkpoint.rule'].create({
            'name': 'Test Rule',
            'template_id': self.template.id,
            'condition_type': 'min_count',
            'min_count': 1,
            'target_stage_id': self.env['project.task.type'].search([], limit=1).id
        })
        
        # Create task and apply template
        task = self.env['project.task'].create({'name': 'Test Task'})
        task._apply_checkpoint_templates_from_products([self.product])
        
        # Mark checkpoint as reached
        task.checkpoint_ids[0].is_reached = True
        
        # Check rule evaluation
        task._evaluate_checkpoint_rules()
        # Add assertions based on expected behavior
```

**Files to Modify**:
- `__manifest__.py` - Add tests to data files

**Test**: Run tests and verify they pass

---

### **Step 18: Add Missing Dependencies**
**Goal**: Fix missing dependencies in manifest

**Files to Modify**:
- `__manifest__.py`

**Update Dependencies**:
```python
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
        "sale_project",  # Added for sale_line_id field support
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/checkpoint_views.xml",
        "views/task_views.xml",
        "views/checkpoint_tag_views.xml",
        "views/checkpoint_template_views.xml",
        "views/product_views.xml",
        "wizard/apply_checkpoint_template_wizard_views.xml",
        "views/menu_views.xml",
    ],
    "demo": [
        "data/demo_data.xml",
        "data/demo_checkpoint_templates.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
}
```

**Test**: Update module and verify no dependency errors

---

### **Step 19: Implement Automatic Template Application**
**Goal**: Automatically apply templates when tasks are created from sale orders

**Files to Modify**:
- `models/task_extension.py`

**Add Method**:
```python
@api.model
def create(self, vals):
    """Override create to automatically apply checkpoint templates"""
    task = super().create(vals)
    
    # Try to apply templates from sale line
    if hasattr(task, 'sale_line_id') and task.sale_line_id:
        task._apply_checkpoint_templates_from_products([task.sale_line_id.product_id])
    
    return task
```

**Alternative: Extend Sale Order Line**
**Files to Create**:
- `models/sale_order_line_extension.py`

**Content**:
```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _timesheet_create_task_prepare_values(self, project):
        """Override to apply checkpoint templates when creating tasks"""
        task_vals = super()._timesheet_create_task_prepare_values(project)
        
        # Apply checkpoint templates if product has them
        if (self.product_id.type == 'service' and 
            self.product_id.auto_apply_checkpoint_templates and 
            self.product_id.checkpoint_template_ids):
            
            # Create task first
            task = self.env['project.task'].create(task_vals)
            
            # Apply templates
            task._apply_checkpoint_templates_from_products([self.product_id])
            
            # Return the task instead of vals
            return task
        
        return task_vals
```

**Files to Modify**:
- `models/__init__.py` - Add import

**Test**: Create sale order with service product and verify templates are applied

---

### **Step 20: Final Integration Testing**
**Goal**: Test complete workflow end-to-end

**Test Scenarios**:

1. **Template Management**:
   - Create checkpoint tags
   - Create checkpoint template with lines and rules
   - Verify template statistics

2. **Product Configuration**:
   - Create service product
   - Assign checkpoint templates
   - Verify constraints work

3. **Task Creation**:
   - Create task manually
   - Apply templates via wizard
   - Verify checkpoints are created

4. **Sale Order Integration**:
   - Create sale order with service product
   - Confirm order
   - Verify task is created with checkpoints

5. **Checkpoint Workflow**:
   - Mark checkpoints as reached
   - Verify stage advancement
   - Verify rule evaluation

6. **Rule Testing**:
   - Test all condition types (all, min_count, by_tag_count, percentage)
   - Verify stage transitions work correctly

**Files to Create**:
- `tests/test_integration.py`

**Content**:
```python
# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase

class TestCheckpointIntegration(TransactionCase):
    
    def setUp(self):
        super().setUp()
        # Setup comprehensive test data
        self.setup_test_data()
    
    def setup_test_data(self):
        """Setup comprehensive test data"""
        # Create tags
        self.tag_legal = self.env['project.task.checkpoint.tag'].create({
            'name': 'Legal',
            'color': 1
        })
        self.tag_kyc = self.env['project.task.checkpoint.tag'].create({
            'name': 'KYC',
            'color': 2
        })
        
        # Create template
        self.template = self.env['project.task.checkpoint.template'].create({
            'name': 'Company Formation',
            'line_ids': [
                (0, 0, {
                    'name': 'Passport Copy',
                    'tag_ids': [(6, 0, [self.tag_legal.id])],
                    'sequence': 10
                }),
                (0, 0, {
                    'name': 'KYC Form',
                    'tag_ids': [(6, 0, [self.tag_kyc.id])],
                    'sequence': 20
                })
            ]
        })
        
        # Create product
        self.product = self.env['product.template'].create({
            'name': 'Company Formation Service',
            'type': 'service',
            'service_tracking': 'task_in_project',
            'checkpoint_template_ids': [(6, 0, [self.template.id])],
            'auto_apply_checkpoint_templates': True
        })
    
    def test_complete_workflow(self):
        """Test complete workflow from sale order to task completion"""
        # Create sale order
        partner = self.env['res.partner'].create({'name': 'Test Partner'})
        order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.product_variant_id.id,
                'name': 'Company Formation',
                'product_uom_qty': 1,
                'price_unit': 1000
            })]
        })
        
        # Confirm order
        order.action_confirm()
        
        # Check if task was created
        self.assertTrue(order.tasks_ids)
        task = order.tasks_ids[0]
        
        # Check if checkpoints were applied
        self.assertEqual(len(task.checkpoint_ids), 2)
        self.assertIn(self.template, task.applied_checkpoint_template_ids)
        
        # Mark checkpoints as reached
        task.checkpoint_ids[0].is_reached = True
        task.checkpoint_ids[1].is_reached = True
        
        # Verify progress
        self.assertEqual(task.checkpoint_reached_count, 2)
        self.assertEqual(task.checkpoint_progress, 100.0)
```

**Test**: Run all tests and verify complete workflow

---

## Updated Implementation Checklist

### **Phase 1: Core Data Models** ✅ **COMPLETE**
- [x] Step 1: Create Checkpoint Tag Model
- [x] Step 2: Create Checkpoint Template Line Model
- [x] Step 3: Create Checkpoint Rule Model
- [x] Step 4: Create Checkpoint Template Model

### **Phase 2: Product Integration** ✅ **COMPLETE**
- [x] Step 5: Extend Product Template Model
- [x] Step 6: Extend Task Model

### **Phase 3: Template Application Logic** ✅ **COMPLETE**
- [x] Step 7: Add Template Application Method
- [x] Step 8: Add Rule Evaluation Method
- [x] Step 9: Integrate with Checkpoint Changes

### **Phase 4: Views and UI** ✅ **COMPLETE**
- [x] Step 10: Create Tag Views
- [x] Step 11: Create Template Views
- [x] Step 12: Update Product Views
- [x] Step 13: Update Task Views
- [x] Step 14: Create Template Application Wizard

### **Phase 5: Security and Demo Data** ✅ **COMPLETE**
- [x] Step 15: Update Security Rules
- [x] Step 16: Create Demo Data

### **Phase 6: Testing and Integration** ❌ **PENDING**
- [ ] Step 17: Create Unit Tests
- [ ] Step 18: Add Missing Dependencies
- [ ] Step 19: Implement Automatic Template Application
- [ ] Step 20: Final Integration Testing

## Success Criteria

### **Complete Implementation When**:
- [x] All models load without errors
- [x] All views render correctly
- [x] Template application works from products
- [x] Rule evaluation works for all condition types
- [x] Wizard can apply templates to existing tasks
- [x] Demo data loads correctly
- [ ] Unit tests pass
- [ ] Complete workflow testing successful
- [ ] Automatic template application works
- [ ] Sale order integration works

## Notes

### **Key Implementation Principles**:
1. **Incremental Development**: Implement one step at a time
2. **Test After Each Step**: Verify functionality before proceeding
3. **Error Handling**: Implement proper validation and error handling
4. **Performance**: Use efficient queries and avoid N+1 problems
5. **User Experience**: Provide clear UI and helpful error messages

### **Common Pitfalls to Avoid**:
1. **Circular Dependencies**: Be careful with model imports
2. **View Inheritance**: Test view inheritance carefully
3. **Data Integrity**: Ensure proper constraints and validation
4. **Performance**: Avoid expensive computations in loops

### **Expected Timeline for Remaining Work**:
- **Step 17**: 2-3 hours (Unit Tests)
- **Step 18**: 0.5 hours (Dependencies)
- **Step 19**: 1-2 hours (Automatic Application)
- **Step 20**: 2-3 hours (Integration Testing)
- **Total Remaining**: 5.5-8.5 hours

## Current Status
🔄 **Phase 6 Pending** - Core functionality complete, testing and integration remaining

## Next Steps
1. Complete Step 17: Create Unit Tests
2. Complete Step 18: Add Missing Dependencies
3. Complete Step 19: Implement Automatic Template Application
4. Complete Step 20: Final Integration Testing
5. Deploy and test in production environment

## Critical Issues to Address

### **1. Missing Dependencies**
- Add `sale_project` to manifest dependencies
- This is critical for `sale_line_id` field support

### **2. Automatic Template Application**
- Implement automatic template application on task creation
- Extend sale order line creation process

### **3. Testing Coverage**
- Create comprehensive unit tests
- Test all rule condition types
- Test complete workflow scenarios

### **4. Integration Testing**
- Test sale order to task workflow
- Test template application wizard
- Test rule evaluation and stage advancement
