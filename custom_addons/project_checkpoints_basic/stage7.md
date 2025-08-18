# Phase 7: Milestone Integration - Step-by-Step Implementation Plan

## Stage: Milestone Integration
**Status**: 🔄 IN PROGRESS  
**Previous Stage**: Phase 6 - Auto-Advancement Logic ✅ COMPLETED  
**Next Stage**: Phase 8 - Template Enhancement 🔄 PLANNED
**Current Progress**: Steps 1-6 ✅ COMPLETED, Steps 7-8 🔄 PENDING

## Overview
This document provides a detailed, step-by-step approach to implement milestone integration for the project_checkpoints_basic module, avoiding the JavaScript errors we encountered previously.

## Error Analysis Summary
- **JavaScript Error**: `TypeError: Cannot read properties of undefined (reading 'type')`
- **Root Causes**: 
  - Incorrect view inheritance xpath expressions
  - Broken action references in smart buttons
  - Complex field relationships causing cascading issues
  - Milestone view structure different from task views

## Phase 7 Strategy: Incremental Implementation

### **Step 1: Add Basic Milestone Field (Safest First Step)** ✅ COMPLETED
**Goal**: Add milestone_id field to checkpoint model without any view changes

**Files to Modify**:
- `models/project_task_checkpoint.py`

**Changes**:
```python
# Add this field after task_id field
milestone_id = fields.Many2one(
    'project.milestone',
    string='Milestone',
    required=False,
    ondelete='cascade',
    help='Milestone this checkpoint belongs to'
)
```

**Test**: ✅ Update module and verify no errors
**Status**: ✅ COMPLETED - Field added successfully, no errors

---

### **Step 2: Update Checkpoint Views (Simple Field Addition)** ✅ COMPLETED
**Goal**: Add milestone_id field to existing checkpoint views

**Files to Modify**:
- `views/checkpoint_views.xml`

**Changes**:
```xml
<!-- In form view, add after task_id -->
<field name="milestone_id"/>

<!-- In list view, add after task_id -->
<field name="milestone_id"/>
```

**Test**: ✅ Update module and verify views render correctly
**Status**: ✅ COMPLETED - Field added to both form and list views successfully

---

### **Step 3: Create Basic Milestone Extension Model** ✅ COMPLETED
**Goal**: Create minimal milestone extension without computed fields

**Files to Create**:
- `models/milestone_extension.py`

**Content**:
```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProjectMilestone(models.Model):
    _inherit = 'project.milestone'

    checkpoint_ids = fields.One2many(
        'project.task.checkpoint',
        'milestone_id',
        string='Checkpoints',
        help='Checkpoints for this milestone'
    )
```

**Files to Modify**:
- `models/__init__.py` - Add import

**Test**: ✅ Update module and verify no errors
**Status**: ✅ COMPLETED - Model created and imported successfully

---

### **Step 4: Add Simple Milestone Views (No Smart Buttons)** ✅ COMPLETED
**Goal**: Create basic milestone form view with checkpoints tab

**Files to Create**:
- `views/milestone_views.xml`

**Content**:
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Inherit Milestone Form View -->
        <record id="view_project_milestone_form_inherit_checkpoints" model="ir.ui.view">
            <field name="name">project.milestone.form.inherit.checkpoints</field>
            <field name="model">project.milestone</field>
            <field name="inherit_id" ref="project.project_milestone_view_form"/>
            <field name="arch" type="xml">
                <!-- Add Checkpoints tab -->
                <xpath expr="//sheet" position="inside">
                    <notebook>
                        <page string="Checkpoints" name="checkpoints">
                            <field name="checkpoint_ids">
                                <list editable="bottom">
                                    <field name="sequence" widget="handle"/>
                                    <field name="name"/>
                                    <field name="task_id"/>
                                    <field name="is_reached"/>
                                    <field name="notes"/>
                                </list>
                            </field>
                        </page>
                    </notebook>
                </xpath>
            </field>
        </record>
        
        <!-- Milestone Action -->
        <record id="action_project_milestone" model="ir.actions.act_window">
            <field name="name">Project Milestones</field>
            <field name="res_model">project.milestone</field>
            <field name="view_mode">list,form</field>
        </record>
    </data>
</odoo>
```

**Files to Modify**:
- `__manifest__.py` - Add milestone_views.xml to data files
- `views/menu_views.xml` - Add milestone menu item

**Test**: ✅ Update module and verify milestone form loads
**Status**: ✅ COMPLETED - Milestone views created with checkpoints tab and menu access

---

### **Step 5: Add Computed Fields to Milestone Extension** 🔄 PENDING
**Goal**: Add checkpoint count and progress fields

**Files to Modify**:
- `models/milestone_extension.py`

**Add Fields**:
```python
# Add after checkpoint_ids field
checkpoint_count = fields.Integer(
    string='Total Checkpoints',
    compute='_compute_checkpoint_counts',
    store=False,
    help='Total number of checkpoints for this milestone'
)

completed_checkpoint_count = fields.Integer(
    string='Completed Checkpoints',
    compute='_compute_checkpoint_counts',
    store=False,
    help='Number of completed checkpoints'
)

checkpoint_progress = fields.Float(
    string='Checkpoint Progress',
    compute='_compute_checkpoint_counts',
    store=False,
    help='Progress percentage of completed checkpoints'
)

@api.depends('checkpoint_ids', 'checkpoint_ids.is_reached')
def _compute_checkpoint_counts(self):
    """Compute checkpoint counts and progress"""
    for milestone in self:
        total_checkpoints = len(milestone.checkpoint_ids)
        completed_checkpoints = len(milestone.checkpoint_ids.filtered(lambda c: c.is_reached))
        
        milestone.checkpoint_count = total_checkpoints
        milestone.completed_checkpoint_count = completed_checkpoints
        
        if total_checkpoints > 0:
            milestone.checkpoint_progress = (completed_checkpoints / total_checkpoints) * 100
        else:
            milestone.checkpoint_progress = 0.0
```

**Test**: Update module and verify computed fields work
**Status**: 🔄 READY TO IMPLEMENT - Next step in sequence

---

### **Step 6: Add Smart Buttons to Milestone View** ✅ COMPLETED
**Goal**: Add smart buttons showing checkpoint counts

**Files to Modify**:
- `views/milestone_views.xml`

**Added Components**:
- **Milestone List View** - Shows milestones with checkpoint count columns
- **Milestone Form View** - Complete form with smart buttons and checkpoints tab
- **Smart Buttons** - Display checkpoint counts with flag checkered icon
- **Updated Action** - Uses custom views with explicit view references

**Smart Button Features**:
```xml
<button name="%(action_project_task_checkpoint)d" 
        type="action" 
        string="Checkpoints" 
        class="oe_stat_button"
        icon="fa-flag-checkered"
        invisible="checkpoint_count == 0">
    <div class="o_form_field o_stat_info">
        <span class="o_stat_value">
            <field name="checkpoint_count" nolabel="1"/>
            <span class="fw-normal"> Total</span>
        </span>
        <span class="o_stat_value" invisible="completed_checkpoint_count == 0">
            <field name="completed_checkpoint_count" nolabel="1"/>
            <span class="fw-normal"> Done</span>
        </span>
    </div>
</button>
```

**Test**: ✅ Update module and verify smart buttons display
**Status**: ✅ COMPLETED - Smart buttons added with complete milestone views

---

### **Step 7: Add Progress Bar to Milestone View** ✅ COMPLETED
**Goal**: Add progress bar for checkpoint completion

**Files to Modify**:
- `views/milestone_views.xml`

**Added Progress Bar**:
```xml
<!-- Progress Bar Section -->
<group invisible="checkpoint_count == 0">
    <field name="checkpoint_progress" widget="progressbar" string="Checkpoint Progress"/>
</group>
```

**Features**:
- **Visual Progress Indicator** - Shows checkpoint completion percentage
- **Conditional Display** - Only shows when there are checkpoints
- **Progress Bar Widget** - Uses Odoo's built-in progressbar widget
- **Real-time Updates** - Updates when checkpoints are marked as reached

**Test**: ✅ Update module and verify progress bar displays
**Status**: ✅ COMPLETED - Progress bar added with conditional display

---

### **Step 8: Add Auto-Advancement Logic** ✅ COMPLETED
**Goal**: Implement milestone auto-advancement when all checkpoints are reached

**Files to Modify**:
- `models/milestone_extension.py`

**Added Methods**:
```python
def _advance_milestone_on_checkpoint(self, checkpoint):
    """Mark milestone as reached when all checkpoints are reached"""
    if all(self.checkpoint_ids.mapped('is_reached')):
        if not self.is_reached:
            self.is_reached = True
            return True
    else:
        # If not all checkpoints are reached, milestone should not be reached
        if self.is_reached:
            self.is_reached = False
            return True
    return False

def write(self, vals):
    """Override write to handle checkpoint milestone advancement"""
    result = super().write(vals)
    
    # Check if any checkpoints were marked as reached
    if 'checkpoint_ids' in vals:
        for milestone in self:
            for checkpoint in milestone.checkpoint_ids:
                if checkpoint.is_reached:
                    milestone._advance_milestone_on_checkpoint(checkpoint)
    
    return result
```

**Files to Modify**:
- `models/project_task_checkpoint.py` - Updated _onchange_is_reached method

**Auto-Advancement Features**:
- **Bidirectional Logic** - Works for both checking and unchecking checkpoints
- **Smart Advancement** - Only marks milestone as reached when ALL checkpoints are completed
- **Smart Reversal** - Unmarks milestone when any checkpoint is unchecked
- **Real-time Updates** - Triggers on checkpoint state changes
- **Safety Checks** - Prevents duplicate advancement and handles edge cases

**Test**: ✅ Update module and verify auto-advancement works in both directions
**Status**: ✅ COMPLETED - Auto-advancement logic implemented with bidirectional support

---

## Phase 8: Dual Template System (Future Implementation)

### **Overview**
Implement both **Milestone Templates** and **Checkpoint Templates with Milestone Integration** to provide users with flexible template options for different use cases.

### **Architecture Decision: Option B - Both Approaches**

#### **Approach 1: Milestone Templates (New)**
- **Model**: `project.milestone.template`
- **Workflow**: Milestone → Checkpoints
- **Use Case**: Project-level planning, milestone-driven workflows
- **Benefits**: Natural hierarchy, project management focus

#### **Approach 2: Checkpoint Templates with Milestone Integration (Current)**
- **Model**: `project.task.checkpoint.template` (enhanced)
- **Workflow**: Checkpoints → Optional Milestone
- **Use Case**: Task-level workflows, flexible checkpoint creation
- **Benefits**: Backward compatible, granular control

---

## **Phase 8A: Milestone Templates (Steps 9-12)**

### **Step 9: Create Milestone Template Model** ✅ COMPLETED
**Goal**: Create new milestone template model with checkpoint definitions

**Files to Create**:
- `models/milestone_template.py`

**Model Structure**:
```python
class ProjectMilestoneTemplate(models.Model):
    _name = 'project.milestone.template'
    _description = 'Project Milestone Template'
    
    name = fields.Char(string='Template Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    project_id = fields.Many2one('project.project', string='Default Project')
    
    # Milestone fields
    milestone_name = fields.Char(string='Milestone Name', required=True)
    milestone_deadline = fields.Date(string='Default Deadline')
    milestone_notes = fields.Text(string='Milestone Notes')
    
    # Checkpoint definitions
    checkpoint_line_ids = fields.One2many(
        'project.milestone.template.checkpoint',
        'template_id',
        string='Checkpoint Definitions'
    )
    
    active = fields.Boolean(string='Active', default=True)
    notes = fields.Text(string='Template Notes')
```

**Test**: ✅ Create model and verify no errors
**Status**: ✅ COMPLETED - Milestone template model created successfully

---

### **Step 10: Create Milestone Template Checkpoint Model** ✅ COMPLETED
**Goal**: Create checkpoint definition model for milestone templates

**Files to Create**:
- `models/milestone_template_checkpoint.py`

**Model Structure**:
```python
class ProjectMilestoneTemplateCheckpoint(models.Model):
    _name = 'project.milestone.template.checkpoint'
    _description = 'Milestone Template Checkpoint Definition'
    _order = 'sequence, id'
    
    template_id = fields.Many2one('project.milestone.template', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Checkpoint Name', required=True)
    
    tag_ids = fields.Many2many('project.task.checkpoint.tag', string='Tags')
    auto_advance_stage = fields.Boolean(string='Auto Advance Stage', default=True)
    target_stage_id = fields.Many2one('project.task.type', string='Target Stage')
    notes = fields.Text(string='Notes')
```

**Test**: ✅ Create model and verify no errors
**Status**: ✅ COMPLETED - Milestone template checkpoint model created successfully

---

### **Step 11: Create Milestone Template Views** ✅ COMPLETED
**Goal**: Create views for milestone templates

**Files to Create**:
- `views/milestone_template_views.xml`

**Views to Include**:
- **List View**: Shows template name, milestone name, checkpoint count
- **Form View**: Milestone config + checkpoint definitions in notebook
- **Action**: Window action for milestone templates
- **Menu**: Menu item under Project Configuration

**Created Components**:
- **List View**: Template name, sequence, milestone name, checkpoint count, deadline, active
- **Form View**: Smart button, basic info, notebook with 3 pages (Milestone Config, Checkpoints, Notes)
- **Action**: Window action with help text
- **Menu**: Project → Configuration → Milestone Templates (sequence 52)
- **Security**: Access rights for both models (user read-only, manager full access)

**Test**: ✅ Create views and verify they render correctly
**Status**: ✅ COMPLETED - Milestone template views created with menu access

---

### **Step 12: Implement Milestone Template Application** ✅ COMPLETED
**Goal**: Add method to apply milestone templates to projects

**Files to Modify**:
- `models/milestone_extension.py`
- `models/milestone_template.py`

**Added Methods**:
```python
# In milestone_template.py
def apply_to_project(self, project):
    """Apply this milestone template to a project"""
    # Create milestone with valid fields only
    milestone_vals = {
        'name': self.milestone_name,
        'project_id': project.id,
        'deadline': self.milestone_deadline,
    }
    milestone = self.env['project.milestone'].create(milestone_vals)
    
    # Create checkpoints with all configuration
    for line in self.checkpoint_line_ids:
        checkpoint_vals = {
            'name': line.name,
            'sequence': line.sequence,
            'milestone_id': milestone.id,
            'tag_ids': [(6, 0, line.tag_ids.ids)],
            'auto_advance_stage': line.auto_advance_stage,
            'target_stage_id': line.target_stage_id.id if line.target_stage_id else False,
            'notes': line.notes,
        }
        self.env['project.task.checkpoint'].create(checkpoint_vals)
    
    return milestone

def apply_to_current_project(self):
    """Apply this milestone template to the current project context"""
    # Validation and application with success feedback
    # Returns action to show created milestone
```

**UI Enhancements**:
- **Apply Template Button**: Added to milestone template form view
- **Success Feedback**: Shows confirmation message and redirects to created milestone
- **Error Handling**: Validates checkpoints and project before application
- **User Experience**: Clear visual feedback for successful application

**Test**: ✅ Apply milestone templates and verify creation
**Status**: ✅ COMPLETED - Milestone template application logic implemented with user feedback

---

## **Phase 8B: Enhanced Checkpoint Templates (Steps 13-16)**

### **Step 13: Complete Checkpoint Template Milestone Integration** ✅ COMPLETED
**Goal**: Finish the milestone integration in checkpoint templates (already started)

**Files to Modify**:
- `models/checkpoint_template.py` (already enhanced)
- `views/checkpoint_template_views.xml` (already enhanced)
- `models/task_extension.py` (enhanced application logic)

**Enhanced Application Logic**:
```python
def _instantiate_template_checkpoints(self, template):
    """Instantiate checkpoints from a template with milestone support"""
    # Create milestone if requested
    milestone = None
    if template.create_milestone:
        milestone_vals = {
            'name': template.milestone_name or template.name,
            'project_id': self.project_id.id,
            'deadline': template.milestone_deadline,
        }
        milestone = self.env['project.milestone'].create(milestone_vals)
    
    # Create checkpoints with milestone linking
    for line in template.line_ids:
        checkpoint_vals = {
            'name': line.name,
            'sequence': line.sequence,
            'task_id': self.id,
            'milestone_id': milestone.id if milestone else False,
            'tag_ids': [(6, 0, line.tag_ids.ids)],
            'auto_advance_stage': line.auto_advance_stage,
            'target_stage_id': line.target_stage_id.id if line.target_stage_id else False,
            'notes': line.notes,
        }
        self.env['project.task.checkpoint'].create(checkpoint_vals)
```

**Key Features**:
- **✅ Milestone Creation**: Creates milestone when template has milestone enabled
- **✅ Checkpoint Linking**: Links checkpoints to created milestone
- **✅ Backward Compatible**: Existing templates work without changes
- **✅ Project Integration**: Milestone created in task's project

**Test**: ✅ Apply checkpoint templates and verify milestone creation
**Status**: ✅ COMPLETED - Checkpoint template milestone integration fully implemented

---

### **Step 14: Create Template Selection Wizard** ✅ COMPLETED
**Goal**: Create wizard to choose between milestone and checkpoint templates

**Files to Create**:
- `wizard/template_selection_wizard.py`
- `wizard/template_selection_wizard_views.xml`

**Wizard Features**:
- **Template Type Selection**: Milestone vs Checkpoint templates
- **Template List**: Filtered by selected type
- **Preview**: Show template details before application
- **Application**: Apply selected template

**Created Components**:
- **Wizard Model**: TemplateSelectionWizard with template type selection
- **Form View**: Clean interface with conditional field visibility
- **Template Details**: Shows name, description, and checkpoint count
- **Action Buttons**: Preview and Apply template options
- **Menu Integration**: Project → Configuration → Apply Template (sequence 53)
- **Security**: Access rights for wizard model

**Key Features**:
- **✅ Unified Interface**: Single wizard for both template types
- **✅ Smart Field Visibility**: Shows relevant fields based on template type
- **✅ Template Preview**: View template details before applying
- **✅ Context Awareness**: Pre-fills project and task from context
- **✅ Error Handling**: Validates selections before application

**Test**: ✅ Test wizard functionality
**Status**: ✅ COMPLETED - Template selection wizard created with full functionality

---

### **Step 15: Integration and Testing** ✅ COMPLETED
**Goal**: Create comprehensive test suite and integration guide for the dual template system

**Files to Create**:
- `tests/test_template_integration.py`
- `INTEGRATION_GUIDE.md`

**Test Suite Features**:
- **Comprehensive Coverage**: Tests for milestone templates, checkpoint templates, wizard, auto-advancement
- **Validation Tests**: Template validation and error handling
- **Backward Compatibility**: Ensures existing functionality still works
- **Integration Tests**: Tests both template systems working together

**Created Components**:
- **Test Class**: TestTemplateIntegration with 7 test methods
- **Test Coverage**: 
  - `test_milestone_template_creation`: Tests milestone template creation and application
  - `test_checkpoint_template_with_milestone`: Tests checkpoint templates with milestone creation
  - `test_checkpoint_template_without_milestone`: Tests backward compatibility
  - `test_template_selection_wizard`: Tests wizard functionality
  - `test_milestone_auto_advancement`: Tests milestone auto-advancement logic
  - `test_template_validation`: Tests template validation and error handling
  - `test_backward_compatibility`: Ensures existing functionality works
- **Integration Guide**: Comprehensive documentation for the dual template system

**Test**: ✅ Test file created and ready for execution
**Status**: ✅ COMPLETED - Comprehensive test suite and integration guide created

---

### **Step 16: Final Integration and Testing** 🔄 IN PROGRESS
**Goal**: Final testing and validation of the complete dual template system

**Integration Points**:
- **Menu Organization**: Clear separation between template types
- **Template Application**: Consistent application process
- **Data Consistency**: No conflicts between template types
- **User Experience**: Intuitive workflow for both approaches

**Current Status**:
- **✅ Test Suite Created**: Comprehensive test file with 7 test methods
- **✅ Integration Guide**: Complete documentation for the dual template system
- **🔄 Test Execution**: Working on running tests in Odoo environment
- **✅ Dependencies Fixed**: Added `product` module dependency to manifest

**Test Execution Progress**:
- **✅ Environment Setup**: Odoo test environment configured
- **✅ Dependencies Installed**: `freezegun` dependency installed
- **✅ Module Dependencies**: Added `product` module to manifest
- **🔄 Test Execution**: Working on running the test suite

**Test**: 🔄 In progress - Final comprehensive testing of both template systems
**Status**: 🔄 IN PROGRESS - Test execution and final validation

---

## **Use Case Comparison**

### **Milestone Templates - Best For:**
- **Project Planning**: High-level milestone definition
- **Project Management**: Milestone-driven workflows
- **Team Coordination**: Milestone-based progress tracking
- **Client Communication**: Milestone-based reporting

### **Checkpoint Templates - Best For:**
- **Task Management**: Detailed task workflows
- **Process Automation**: Stage-based automation
- **Quality Control**: Step-by-step verification
- **Flexible Workflows**: Optional milestone creation

---

## **Implementation Timeline**

### **Phase 8A (Milestone Templates)**: ~4 hours
- **Step 9**: 30 minutes (Model creation)
- **Step 10**: 30 minutes (Checkpoint model)
- **Step 11**: 1 hour (Views and menus)
- **Step 12**: 1 hour (Application logic)
- **Testing**: 1 hour

### **Phase 8B (Enhanced Checkpoint Templates)**: ~2 hours
- **Step 13**: 15 minutes (Complete integration)
- **Step 14**: 30 minutes (Application logic)
- **Step 15**: 1 hour (Selection wizard)
- **Step 16**: 15 minutes (Integration testing)

### **Total**: ~6 hours for complete dual template system

**Add Elements**:
```xml
<!-- Add to template form view -->
<xpath expr="//group" position="after">
    <group string="Milestone Settings" invisible="not create_milestone">
        <field name="create_milestone"/>
        <field name="milestone_name" invisible="not create_milestone"/>
        <field name="milestone_deadline" invisible="not create_milestone"/>
        <field name="milestone_sequence" invisible="not create_milestone"/>
    </group>
</xpath>
```

**Test**: Verify milestone fields appear in template forms

---

### **Step 12: Add Template Examples**
**Goal**: Create demo templates showing milestone-checkpoint integration

**Files to Create**:
- `data/demo_milestone_templates.xml`

**Content**:
```xml
<!-- Company Formation Template -->
<record id="template_company_formation" model="project.task.checkpoint.template">
    <field name="name">Company Formation - Complete</field>
    <field name="create_milestone">True</field>
    <field name="milestone_name">Document Collection Phase</field>
    <field name="milestone_deadline" eval="(DateTime.now() + timedelta(days=30)).strftime('%Y-%m-%d')"/>
    <field name="milestone_sequence">10</field>
</record>
```

**Test**: Verify demo templates load correctly

---

## Template Enhancement Benefits

### **✅ Advantages:**
1. **Unified Template System** - One template creates milestone + checkpoints
2. **Logical Workflow** - Templates represent complete project phases
3. **Data Consistency** - Milestones and checkpoints created together
4. **Easier Management** - Single template for complete milestone structure
5. **Better User Experience** - Simplified template application process

### **🎯 Use Cases:**
- **Legal Services**: Company formation with document collection milestones
- **Software Development**: Development phases with feature completion milestones
- **Construction Projects**: Building phases with inspection milestones
- **Consulting Services**: Project phases with deliverable milestones

### **📋 Implementation Timeline:**
- **Step 9**: 1 hour (Add milestone fields to templates)
- **Step 10**: 1 hour (Update template application logic)
- **Step 11**: 30 minutes (Update template views)
- **Step 12**: 30 minutes (Add demo templates)
- **Total**: ~3 hours for complete template enhancement

---

## Testing Checklist for Each Step

### **After Each Step, Test**:
- [ ] Module updates without errors
- [ ] No JavaScript errors in browser console
- [ ] Views render correctly
- [ ] No `raw_value` errors
- [ ] Basic functionality works

### **Final Testing**:
- [ ] Create milestone
- [ ] Add checkpoints to milestone
- [ ] Mark checkpoints as reached
- [ ] Verify milestone auto-advancement
- [ ] Test smart buttons and progress bar
- [ ] Test milestone-checkpoint relationship

## Rollback Strategy

### **If Any Step Fails**:
1. **Comment out the problematic code**
2. **Update module to verify fix**
3. **Identify the specific cause**
4. **Implement alternative approach**
5. **Continue with next step**

### **Rollback Points**:
- **Step 1**: Remove milestone_id field
- **Step 2**: Remove milestone_id from views
- **Step 3**: Remove milestone_extension.py
- **Step 4**: Remove milestone_views.xml
- **Step 5**: Remove computed fields
- **Step 6**: Remove smart buttons
- **Step 7**: Remove progress bar
- **Step 8**: Remove auto-advancement logic

## Success Criteria

### **Phase 7 Complete When**:
- [ ] Checkpoints can be linked to milestones
- [ ] Milestone form shows checkpoints tab
- [ ] Smart buttons display checkpoint counts
- [ ] Progress bar shows completion percentage
- [ ] Auto-advancement works when all checkpoints reached
- [ ] No JavaScript errors
- [ ] No view inheritance errors
- [ ] All functionality works as expected

## Notes

### **Key Principles**:
1. **Incremental**: One small change at a time
2. **Test Immediately**: After each step
3. **Simple First**: Avoid complex features initially
4. **Rollback Ready**: Always have a way to revert

### **Common Pitfalls to Avoid**:
1. **Complex Xpath**: Use simple, direct xpath expressions
2. **Action References**: Ensure actions exist before referencing
3. **Field Dependencies**: Add fields one at a time
4. **View Inheritance**: Test view inheritance carefully

### **Expected Timeline**:
- **Step 1-2**: 15 minutes
- **Step 3-4**: 30 minutes
- **Step 5-6**: 45 minutes
- **Step 7-8**: 30 minutes
- **Testing**: 30 minutes
- **Total**: ~2.5 hours (with testing and potential rollbacks)

## Current Status
��🔄🔄🔄🔄 **IN PROGRESS** - Phase 7 milestone integration (Steps 1-7 Complete)

## Next Steps
1. **✅ Stage 7 Complete**: All milestone integration features implemented
2. **✅ Phase 8A Complete**: All milestone template features implemented
3. **🔄 Phase 8B**: Checkpoint Template Enhancement (Steps 13-14 Complete, Steps 15-16 Pending)
4. **Phase 6**: Testing and Integration (Steps 17-20) - From main plan
5. **Consider Phase 9**: Advanced Features and Polish

## Future Roadmap
- **✅ Stage 7**: Complete milestone integration (All Steps 1-8)
- **✅ Phase 8A**: Complete milestone templates (All Steps 9-12)
- **🔄 Phase 8B**: Enhanced Checkpoint Templates (Steps 13-14 Complete, Steps 15-16 In Progress)
- **Phase 6**: Testing and Integration (Steps 17-20) - From main plan
- **Phase 9**: Advanced Features and Polish

## Recent Progress Updates
- **✅ Step 15 Complete**: Comprehensive test suite created with 7 test methods
- **✅ Integration Guide**: Complete documentation for dual template system
- **✅ Dependencies Fixed**: Added `product` module dependency to manifest
- **🔄 Test Execution**: Working on running tests in Odoo environment
- **✅ Environment Setup**: Odoo test environment configured with freezegun dependency