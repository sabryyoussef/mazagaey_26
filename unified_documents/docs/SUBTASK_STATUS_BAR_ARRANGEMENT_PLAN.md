# Subtask Status Bar Arrangement & Workflow Progress Plan

## 🎯 **Project Overview**

This plan outlines the complete arrangement of subtask status bars, workflow steps, and progress bars for the unified documents module. The goal is to create a cohesive, intuitive interface that clearly shows the progression of document processing tasks.

---

## 📋 **Current State Analysis**

### **Existing Components:**
1. **Main Category Tasks** (e.g., "Required Documents Processing")
2. **Document Subtasks** (e.g., "Process: sabry1", "Process: sabry2")
3. **Document Processing Stages** (Upload → Review → Approval → Delivery → Completed)
4. **Checkpoint System** (4 checkpoints per document)
5. **Progress Tracking** (Currently showing invalid values like 10000%)

### **Current Issues:**
- Progress calculation showing invalid values (10000%)
- Status bar inconsistency between main workflow and document processing
- Debug/refresh buttons not visible in UI
- Stage progression not synchronized with checkpoint completion

---

## 🏗️ **Architecture Design**

### **Three-Tier Status System:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROJECT LEVEL STATUS                        │
│  [Planning] → [In Progress] → [Review] → [Completed]          │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                  CATEGORY LEVEL STATUS                        │
│  [Required Documents] [Compliance Documents] [Deliverables]   │
│  [Upload ✓] → [Review ✓] → [Approval ✓] → [Delivery ✓]      │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                   DOCUMENT LEVEL STATUS                       │
│  [Document: sabry1] [Document: sabry2] [Document: sabry3]    │
│  [Upload ✓] → [Review ✓] → [Approval ✓] → [Delivery ✓]      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎨 **Frontend Implementation Plan**

### **Phase 1: Enhanced Task Form Views**

#### **1.1 Main Category Task Form View**
**File**: `views/extensions/category_task_form_view.xml`

```xml
<!-- Main Category Task Header -->
<header>
    <!-- Project Workflow Status Bar -->
    <field name="stage_id" widget="statusbar" 
           statusbar_visible="draft,in_progress,review,done"/>
    
    <!-- Document Processing Status Bar -->
    <field name="document_processing_stage" widget="statusbar" 
           statusbar_visible="upload,review,approval,delivery,completed"
           invisible="document_checkpoint_count == 0"/>
    
    <!-- Overall Progress Indicator -->
    <div class="oe_button_box">
        <button name="action_view_document_progress" type="object" 
                class="oe_stat_button" icon="fa-tasks">
            <div class="o_field_widget o_stat_info">
                <span class="o_stat_value">
                    <field name="overall_document_progress" widget="percentage"/>
                </span>
                <span class="o_stat_text">Overall Progress</span>
            </div>
        </button>
        
        <button name="action_view_subtasks" type="object" 
                class="oe_stat_button" icon="fa-list">
            <div class="o_field_widget o_stat_info">
                <span class="o_stat_value">
                    <field name="subtask_count"/>
                </span>
                <span class="o_stat_text">Subtasks</span>
            </div>
        </button>
    </div>
</header>

<!-- Document Processing Tab -->
<notebook>
    <page string="Document Processing" name="document_processing">
        <!-- Category Progress Overview -->
        <group string="Category Progress">
            <field name="document_checkpoint_progress" widget="percentage"/>
            <field name="document_checkpoint_count"/>
            <field name="document_checkpoint_reached_count"/>
        </group>
        
        <!-- Subtasks List -->
        <field name="child_ids" readonly="1">
            <tree>
                <field name="name"/>
                <field name="document_processing_stage"/>
                <field name="document_checkpoint_progress" widget="percentage"/>
                <field name="document_checkpoint_reached_count"/>
                <field name="document_checkpoint_count"/>
                <field name="stage_id"/>
            </tree>
        </field>
    </page>
</notebook>
```

#### **1.2 Document Subtask Form View**
**File**: `views/extensions/document_subtask_form_view.xml`

```xml
<!-- Document Subtask Header -->
<header>
    <!-- Document Processing Status Bar -->
    <field name="document_processing_stage" widget="statusbar" 
           statusbar_visible="upload,review,approval,delivery,completed"/>
    
    <!-- Action Buttons for Stage Progression -->
    <button name="action_complete_upload" type="object" 
            string="Complete Upload" class="btn-success"
            invisible="document_processing_stage != 'upload'"/>
            
    <button name="action_complete_review" type="object" 
            string="Complete Review" class="btn-warning"
            invisible="document_processing_stage != 'review'"/>
            
    <button name="action_complete_approval" type="object" 
            string="Complete Approval" class="btn-info"
            invisible="document_processing_stage != 'approval'"/>
            
    <button name="action_complete_delivery" type="object" 
            string="Complete Delivery" class="btn-primary"
            invisible="document_processing_stage != 'delivery'"/>
    
    <!-- Progress Tracking Buttons -->
    <div class="oe_button_box">
        <button name="action_refresh_checkpoint_stats" type="object" 
                class="oe_stat_button" icon="fa-refresh">
            <div class="o_field_widget o_stat_info">
                <span class="o_stat_value">
                    <i class="fa fa-refresh"/>
                </span>
                <span class="o_stat_text">Refresh</span>
            </div>
        </button>
        
        <button name="action_debug_checkpoint_stats" type="object" 
                class="oe_stat_button" icon="fa-bug">
            <div class="o_field_widget o_stat_info">
                <span class="o_stat_value">
                    <i class="fa fa-bug"/>
                </span>
                <span class="o_stat_text">Debug</span>
            </div>
        </button>
        
        <button name="action_fix_checkpoint_data" type="object" 
                class="oe_stat_button" icon="fa-wrench">
            <div class="o_field_widget o_stat_info">
                <span class="o_stat_value">
                    <i class="fa fa-wrench"/>
                </span>
                <span class="o_stat_text">Fix Data</span>
            </div>
        </button>
    </div>
</header>

<!-- Document Processing Tab -->
<notebook>
    <page string="Document Processing" name="document_processing">
        <!-- Document Information -->
        <group string="Document Information">
            <field name="document_id" readonly="1"/>
            <field name="document_category" readonly="1"/>
        </group>
        
        <!-- Progress Tracking -->
        <group string="Progress Tracking">
            <field name="document_checkpoint_progress" widget="percentage"/>
            <field name="document_checkpoint_count"/>
            <field name="document_checkpoint_reached_count"/>
        </group>
        
        <!-- Checkpoints -->
        <field name="document_checkpoint_ids">
            <tree>
                <field name="name"/>
                <field name="sequence"/>
                <field name="is_reached"/>
                <field name="notes"/>
            </tree>
        </field>
    </page>
</notebook>
```

### **Phase 2: Enhanced List Views**

#### **2.1 Category Task List View**
**File**: `views/extensions/category_task_list_view.xml`

```xml
<record id="view_category_task_list_document_processing" model="ir.ui.view">
    <field name="name">project.task.list.category.document.processing</field>
    <field name="model">project.task</field>
    <field name="inherit_id" ref="project.view_task_tree2"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='name']" position="after">
            <field name="document_category" optional="show"/>
            <field name="overall_document_progress" widget="percentage" optional="show"/>
            <field name="subtask_count" optional="show"/>
            <field name="document_processing_stage" optional="show"/>
        </xpath>
    </field>
</record>
```

#### **2.2 Document Subtask List View**
**File**: `views/extensions/document_subtask_list_view.xml`

```xml
<record id="view_document_subtask_list_document_processing" model="ir.ui.view">
    <field name="name">project.task.list.document.subtask.processing</field>
    <field name="model">project.task</field>
    <field name="inherit_id" ref="project.view_task_tree2"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='name']" position="after">
            <field name="document_id" optional="hide"/>
            <field name="document_category" optional="show"/>
            <field name="document_processing_stage" optional="show"/>
            <field name="document_checkpoint_progress" widget="percentage" optional="show"/>
            <field name="document_checkpoint_reached_count" optional="hide"/>
            <field name="document_checkpoint_count" optional="hide"/>
        </xpath>
    </field>
</record>
```

### **Phase 3: Progress Visualization Components**

#### **3.1 Progress Bar Widget**
**File**: `static/src/js/progress_bar_widget.js`

```javascript
odoo.define('unified_documents.progress_bar_widget', function (require) {
    "use strict";
    
    var AbstractField = require('web.AbstractField');
    var fieldRegistry = require('web.field_registry');
    
    var DocumentProgressBar = AbstractField.extend({
        template: 'DocumentProgressBar',
        
        init: function () {
            this._super.apply(this, arguments);
            this.progress = this.value || 0;
            this.stages = ['upload', 'review', 'approval', 'delivery', 'completed'];
        },
        
        _render: function () {
            this.$el.empty();
            this.$el.append(this._renderProgressBar());
            this.$el.append(this._renderStageIndicators());
        },
        
        _renderProgressBar: function () {
            var $progressBar = $('<div class="progress">');
            var $progressBarInner = $('<div class="progress-bar" role="progressbar">');
            $progressBarInner.css('width', this.progress + '%');
            $progressBarInner.text(this.progress.toFixed(1) + '%');
            $progressBar.append($progressBarInner);
            return $progressBar;
        },
        
        _renderStageIndicators: function () {
            var $stages = $('<div class="stage-indicators">');
            this.stages.forEach(function(stage, index) {
                var $stage = $('<span class="stage-indicator">');
                $stage.text(stage.charAt(0).toUpperCase() + stage.slice(1));
                $stages.append($stage);
            });
            return $stages;
        }
    });
    
    fieldRegistry.add('document_progress_bar', DocumentProgressBar);
    return DocumentProgressBar;
});
```

#### **3.2 Progress Bar Template**
**File**: `static/src/xml/progress_bar_template.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="DocumentProgressBar">
        <div class="document_progress_bar">
            <div class="progress-container">
                <div class="progress-bar-container">
                    <div class="progress-bar-fill" t-att-style="'width: ' + progress + '%'"></div>
                </div>
                <div class="progress-text"><t t-esc="progress"/>%</div>
            </div>
            <div class="stage-indicators">
                <span class="stage" t-att-class="'stage-' + (index < currentStage ? 'completed' : 'pending')" 
                      t-foreach="stages" t-as="stage" t-key="stage">
                    <i class="fa fa-circle" t-att-class="'fa-' + (index < currentStage ? 'check' : 'circle-o')"></i>
                    <span class="stage-name"><t t-esc="stage"/></span>
                </span>
            </div>
        </div>
    </t>
</templates>
```

---

## 🔧 **Backend Implementation Plan**

### **Phase 1: Enhanced Task Model**

#### **1.1 New Fields for Status Management**
**File**: `models/extensions/task_extension.py`

```python
class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    # Enhanced status tracking
    overall_document_progress = fields.Float(
        compute='_compute_overall_document_progress',
        string='Overall Document Progress (%)',
        store=True
    )
    
    current_document_stage = fields.Selection([
        ('upload', 'Upload'),
        ('review', 'Review'),
        ('approval', 'Approval'),
        ('delivery', 'Delivery'),
        ('completed', 'Completed')
    ], compute='_compute_current_document_stage', store=True)
    
    stage_completion_dates = fields.Json(
        string='Stage Completion Dates',
        default=lambda self: {
            'upload': None,
            'review': None,
            'approval': None,
            'delivery': None,
            'completed': None
        }
    )
    
    # Workflow automation
    auto_advance_stages = fields.Boolean(
        string='Auto-advance Stages',
        default=True,
        help='Automatically advance stages when checkpoints are completed'
    )
    
    workflow_notifications = fields.Boolean(
        string='Workflow Notifications',
        default=True,
        help='Send notifications when stages are completed'
    )
```

#### **1.2 Enhanced Compute Methods**
```python
@api.depends('child_ids.document_checkpoint_progress', 'document_checkpoint_progress')
def _compute_overall_document_progress(self):
    """Compute overall progress across all subtasks"""
    for task in self:
        if task.child_ids:
            # Calculate average progress of all subtasks
            subtask_progress = sum(task.child_ids.mapped('document_checkpoint_progress'))
            task.overall_document_progress = subtask_progress / len(task.child_ids)
        else:
            # Use own progress if no subtasks
            task.overall_document_progress = task.document_checkpoint_progress

@api.depends('document_checkpoint_ids.is_reached', 'document_processing_stage')
def _compute_current_document_stage(self):
    """Compute current stage based on checkpoint completion"""
    for task in self:
        if not task.document_checkpoint_ids:
            task.current_document_stage = 'upload'
            continue
            
        # Determine current stage based on checkpoint completion
        checkpoints = task.document_checkpoint_ids.sorted('sequence')
        completed_stages = []
        
        for checkpoint in checkpoints:
            if checkpoint.is_reached:
                stage_name = checkpoint.name.lower()
                if 'upload' in stage_name:
                    completed_stages.append('upload')
                elif 'review' in stage_name:
                    completed_stages.append('review')
                elif 'approval' in stage_name:
                    completed_stages.append('approval')
                elif 'delivery' in stage_name:
                    completed_stages.append('delivery')
        
        # Determine current stage
        if 'delivery' in completed_stages:
            task.current_document_stage = 'completed'
        elif 'approval' in completed_stages:
            task.current_document_stage = 'delivery'
        elif 'review' in completed_stages:
            task.current_document_stage = 'approval'
        elif 'upload' in completed_stages:
            task.current_document_stage = 'review'
        else:
            task.current_document_stage = 'upload'
```

#### **1.3 Enhanced Stage Progression Methods**
```python
def action_complete_upload(self):
    """Complete upload stage and move to review"""
    self.ensure_one()
    
    # Update stage completion
    completion_dates = self.stage_completion_dates or {}
    completion_dates['upload'] = fields.Datetime.now().isoformat()
    
    self.write({
        'document_uploaded': True,
        'document_upload_date': fields.Datetime.now(),
        'document_processing_stage': 'review',
        'stage_completion_dates': completion_dates
    })
    
    # Advance checkpoint
    self._advance_checkpoint('upload')
    
    # Update document status
    self._update_document_status('uploaded')
    
    # Send notification
    if self.workflow_notifications:
        self._send_stage_notification('upload')
    
    # Auto-advance if enabled
    if self.auto_advance_stages:
        self._auto_advance_next_stage()
    
    return self._get_stage_completion_response('upload')

def _auto_advance_next_stage(self):
    """Automatically advance to next stage if conditions are met"""
    self.ensure_one()
    
    if self.current_document_stage == 'upload' and self.document_uploaded:
        self.action_complete_upload()
    elif self.current_document_stage == 'review' and self.document_reviewed:
        self.action_complete_review()
    elif self.current_document_stage == 'approval' and self.document_approved:
        self.action_complete_approval()
    elif self.current_document_stage == 'delivery' and self.document_delivered:
        self.action_complete_delivery()
```

### **Phase 2: Workflow Automation Service**

#### **2.1 Workflow Service Class**
**File**: `services/document_workflow_service.py`

```python
class DocumentWorkflowService:
    """Service class for managing document workflow automation"""
    
    def __init__(self, env):
        self.env = env
        self.logger = logging.getLogger(__name__)
    
    def process_stage_transitions(self, task):
        """Process automatic stage transitions based on checkpoint completion"""
        if not task.auto_advance_stages:
            return
            
        current_stage = task.current_document_stage
        next_stage = self._get_next_stage(current_stage)
        
        if self._can_advance_to_stage(task, next_stage):
            self._advance_to_stage(task, next_stage)
    
    def _get_next_stage(self, current_stage):
        """Get the next stage in the workflow"""
        stage_sequence = ['upload', 'review', 'approval', 'delivery', 'completed']
        try:
            current_index = stage_sequence.index(current_stage)
            if current_index < len(stage_sequence) - 1:
                return stage_sequence[current_index + 1]
        except ValueError:
            pass
        return current_stage
    
    def _can_advance_to_stage(self, task, target_stage):
        """Check if task can advance to target stage"""
        if target_stage == 'review':
            return task.document_uploaded
        elif target_stage == 'approval':
            return task.document_reviewed
        elif target_stage == 'delivery':
            return task.document_approved
        elif target_stage == 'completed':
            return task.document_delivered
        return False
    
    def _advance_to_stage(self, task, target_stage):
        """Advance task to target stage"""
        stage_methods = {
            'review': task.action_complete_upload,
            'approval': task.action_complete_review,
            'delivery': task.action_complete_approval,
            'completed': task.action_complete_delivery
        }
        
        if target_stage in stage_methods:
            try:
                stage_methods[target_stage]()
                self.logger.info(f"Task {task.name} advanced to {target_stage} stage")
            except Exception as e:
                self.logger.error(f"Failed to advance task {task.name} to {target_stage}: {e}")
```

### **Phase 3: Progress Calculation Engine**

#### **3.1 Progress Calculation Service**
**File**: `services/progress_calculation_service.py`

```python
class ProgressCalculationService:
    """Service class for calculating and managing progress values"""
    
    def __init__(self, env):
        self.env = env
        self.logger = logging.getLogger(__name__)
    
    def calculate_task_progress(self, task):
        """Calculate progress for a single task"""
        if not task.document_checkpoint_ids:
            return 0.0
        
        total_checkpoints = len(task.document_checkpoint_ids)
        reached_checkpoints = len(task.document_checkpoint_ids.filtered(lambda c: c.is_reached))
        
        if total_checkpoints == 0:
            return 0.0
        
        progress = (reached_checkpoints / total_checkpoints) * 100
        return max(0.0, min(100.0, progress))  # Ensure 0-100 range
    
    def calculate_category_progress(self, category_task):
        """Calculate overall progress for a category task"""
        if not category_task.child_ids:
            return self.calculate_task_progress(category_task)
        
        subtask_progresses = [
            self.calculate_task_progress(subtask) 
            for subtask in category_task.child_ids
        ]
        
        if not subtask_progresses:
            return 0.0
        
        return sum(subtask_progresses) / len(subtask_progresses)
    
    def calculate_project_progress(self, project):
        """Calculate overall progress for an entire project"""
        category_tasks = project.task_ids.filtered(
            lambda t: t.document_category and not t.parent_id
        )
        
        if not category_tasks:
            return 0.0
        
        category_progresses = [
            self.calculate_category_progress(category_task)
            for category_task in category_tasks
        ]
        
        return sum(category_progresses) / len(category_progresses)
    
    def validate_progress_value(self, progress):
        """Validate that progress is within valid range"""
        if not isinstance(progress, (int, float)):
            return False
        return 0.0 <= progress <= 100.0
    
    def fix_invalid_progress(self, task):
        """Fix invalid progress values for a task"""
        current_progress = task.document_checkpoint_progress
        
        if not self.validate_progress_value(current_progress):
            self.logger.warning(f"Task {task.name} has invalid progress: {current_progress}")
            
            # Recalculate progress
            correct_progress = self.calculate_task_progress(task)
            
            # Update the task
            task.write({
                'document_checkpoint_progress': correct_progress
            })
            
            self.logger.info(f"Fixed task {task.name} progress: {current_progress} → {correct_progress}")
            return True
        
        return False
```

---

## 🎨 **UI/UX Design Guidelines**

### **Color Scheme:**
- **Upload Stage**: Blue (#007bff)
- **Review Stage**: Yellow (#ffc107)
- **Approval Stage**: Purple (#6f42c1)
- **Delivery Stage**: Green (#28a745)
- **Completed Stage**: Dark Green (#155724)

### **Progress Bar Styles:**
- **Main Progress Bar**: Thick, prominent with percentage display
- **Stage Progress Bars**: Medium thickness with stage labels
- **Checkpoint Progress**: Thin bars with checkpoint indicators

### **Status Indicators:**
- **Completed**: ✓ Green checkmark
- **In Progress**: 🔄 Spinning icon
- **Pending**: ⏳ Clock icon
- **Blocked**: ⚠️ Warning icon

### **Responsive Design:**
- **Desktop**: Full status bars with detailed information
- **Tablet**: Condensed status bars with essential info
- **Mobile**: Stacked status indicators with touch-friendly buttons

---

## 🚀 **Implementation Roadmap**

### **Sprint 1: Core Infrastructure (Week 1-2)**
- [ ] Enhanced task model with new fields
- [ ] Progress calculation service
- [ ] Basic status bar components

### **Sprint 2: Frontend Views (Week 3-4)**
- [ ] Enhanced task form views
- [ ] Progress visualization components
- [ ] Status bar widgets

### **Sprint 3: Workflow Automation (Week 5-6)**
- [ ] Workflow automation service
- [ ] Stage progression logic
- [ ] Notification system

### **Sprint 4: Testing & Polish (Week 7-8)**
- [ ] Comprehensive testing
- [ ] UI/UX refinements
- [ ] Performance optimization

---

## 🧪 **Testing Strategy**

### **Unit Tests:**
- Progress calculation accuracy
- Stage progression logic
- Data validation

### **Integration Tests:**
- End-to-end workflow execution
- UI component interactions
- Database consistency

### **User Acceptance Tests:**
- Status bar clarity
- Workflow intuitiveness
- Progress tracking accuracy

---

## 📊 **Success Metrics**

### **Technical Metrics:**
- Progress calculation accuracy: 100%
- Stage progression reliability: 99.9%
- UI response time: <200ms

### **User Experience Metrics:**
- Task completion time reduction: 25%
- User confusion reduction: 50%
- Workflow adoption rate: 90%

---

## 🔧 **Maintenance & Support**

### **Monitoring:**
- Progress calculation errors
- Stage transition failures
- UI performance metrics

### **Updates:**
- Quarterly UI/UX improvements
- Monthly workflow optimizations
- Weekly bug fixes

---

This plan provides a comprehensive roadmap for implementing a sophisticated subtask status bar system with workflow automation and progress tracking. The modular approach allows for incremental implementation and testing at each phase.
