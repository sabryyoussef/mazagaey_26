# Dynamic Quotation System for FSM Workflows

## Overview

The Dynamic Quotation System allows you to create quotations automatically or manually at any point during a workflow execution. This system integrates seamlessly with milestones, checkpoints, and workflow instances to provide flexible quotation generation.

## Key Features

### 🎯 **Trigger-Based Quotations**
- **Milestone Reached**: Automatically create quotations when milestones are completed
- **Checkpoint Reached**: Generate quotations when specific checkpoints are reached
- **Manual Creation**: Create quotations manually from workflow instances
- **Template Integration**: Use quotation templates for consistent formatting

### 📋 **Workflow Integration**
- **Smart Buttons**: Quick access to create and view quotations
- **Context Awareness**: Quotations are linked to workflow instances with trigger information
- **Automatic Logging**: All quotation activities are logged in workflow messages
- **Template Application**: Apply predefined quotation templates automatically

## How It Works

### 1. **Milestone-Triggered Quotations**

When a milestone is reached (all checkpoints completed), the system can automatically create a quotation:

```python
# Milestone configuration
milestone = {
    'name': 'Phase 1 Complete',
    'create_quotation_on_reach': True,
    'quotation_template_id': template_id,
    'quotation_notes': 'Phase 1 deliverables completed'
}
```

**Features:**
- ✅ Automatic quotation creation when milestone is reached
- ✅ Template application for consistent formatting
- ✅ Custom notes inclusion
- ✅ Workflow instance linking

### 2. **Checkpoint-Triggered Quotations**

Individual checkpoints can trigger quotations when reached:

```python
# Checkpoint configuration
checkpoint = {
    'name': 'Quality Review Complete',
    'create_quotation_on_reach': True,
    'quotation_template_id': quality_template_id,
    'quotation_notes': 'Quality review passed - ready for client approval'
}
```

**Features:**
- ✅ Granular quotation control
- ✅ Individual checkpoint tracking
- ✅ Context-specific templates
- ✅ Detailed trigger logging

### 3. **Manual Quotation Creation**

Create quotations manually from workflow instances:

```python
# Manual quotation creation
workflow_instance.action_create_quotation()
```

**Features:**
- ✅ On-demand quotation creation
- ✅ Full quotation form access
- ✅ Workflow context preservation
- ✅ Manual trigger tracking

## Implementation Details

### **FSM Workflow Instance Extensions**

#### New Methods:
- `action_create_quotation()`: Opens quotation creation form
- `create_milestone_quotation()`: Creates quotation with milestone/checkpoint context
- `action_open_quotations()`: Shows all workflow quotations

#### New Fields:
- `sale_order_id`: Links to the most recent quotation
- Smart buttons for quotation management

### **Sale Order Extensions**

#### New Fields:
- `workflow_instance_id`: Links to the creating workflow instance
- `is_workflow_quotation`: Boolean flag for workflow quotations
- `workflow_trigger_type`: Type of trigger (manual/milestone/checkpoint)
- `workflow_trigger_name`: Name of the triggering milestone/checkpoint

#### New Methods:
- `action_open_workflow_instance()`: Navigate back to workflow
- Enhanced `create()` method with workflow context handling

### **Checkpoint Extensions**

#### New Fields:
- `create_quotation_on_reach`: Boolean to enable quotation creation
- `quotation_template_id`: Template to apply
- `quotation_notes`: Additional notes for the quotation

#### New Methods:
- `_create_quotation_on_reach()`: Handles quotation creation logic

### **Milestone Extensions**

#### New Fields:
- `create_quotation_on_reach`: Boolean to enable quotation creation
- `quotation_template_id`: Template to apply
- `quotation_notes`: Additional notes for the quotation

#### New Methods:
- `_create_quotation_on_reach()`: Handles quotation creation logic

## Usage Examples

### **Example 1: Milestone-Based Quotation**

```python
# Configure milestone to create quotation
milestone = self.env['project.milestone'].create({
    'name': 'Design Phase Complete',
    'project_id': project.id,
    'create_quotation_on_reach': True,
    'quotation_template_id': design_template.id,
    'quotation_notes': 'Design phase deliverables ready for client review'
})

# When all checkpoints are reached, quotation is automatically created
```

### **Example 2: Checkpoint-Based Quotation**

```python
# Configure checkpoint to create quotation
checkpoint = self.env['project.task.checkpoint'].create({
    'name': 'Code Review Complete',
    'compliance_project_id': project.id,
    'create_quotation_on_reach': True,
    'quotation_template_id': code_review_template.id,
    'quotation_notes': 'Code review passed - ready for testing phase'
})

# When checkpoint is reached, quotation is automatically created
```

### **Example 3: Manual Quotation Creation**

```python
# Create quotation manually from workflow
workflow_instance = self.env['fsm.workflow.instance'].browse(workflow_id)
quotation_action = workflow_instance.action_create_quotation()

# This opens the quotation form with workflow context
```

## UI Integration

### **Workflow Instance Form**
- **Create Quotation** button: Opens quotation creation form
- **All Quotations** button: Shows all workflow quotations
- **Open Quotation** button: Opens the most recent quotation

### **Sale Order Form**
- **Workflow Integration** section: Shows workflow context
- **Workflow Instance** button: Navigate back to workflow
- **Trigger Information**: Displays what triggered the quotation

### **Checkpoint/Milestone Forms**
- **Quotation Integration** tab: Configure quotation triggers
- **Template Selection**: Choose quotation templates
- **Notes Field**: Add context-specific notes

## Benefits

### **For Project Managers:**
- 🎯 **Progressive Billing**: Create quotations as work progresses
- 📊 **Better Tracking**: Link quotations to specific deliverables
- ⚡ **Automation**: Reduce manual quotation creation
- 📋 **Context**: Maintain workflow context in quotations

### **For Clients:**
- 💰 **Transparency**: See quotations linked to specific milestones
- 📈 **Progress Tracking**: Understand what triggers each quotation
- 🎯 **Clarity**: Clear connection between work and billing

### **For Teams:**
- 🔄 **Workflow Integration**: Seamless quotation creation
- 📝 **Template Consistency**: Standardized quotation formats
- 📊 **Reporting**: Better quotation tracking and reporting

## Configuration

### **Enable Quotation Triggers**

1. **For Milestones:**
   - Open milestone form
   - Go to "Quotation Integration" tab
   - Check "Create Quotation on Reach"
   - Select quotation template (optional)
   - Add quotation notes (optional)

2. **For Checkpoints:**
   - Open checkpoint form
   - Go to "Quotation Integration" tab
   - Check "Create Quotation on Reach"
   - Select quotation template (optional)
   - Add quotation notes (optional)

### **Quotation Templates**

Create quotation templates in Sales → Configuration → Quotation Templates:

```python
# Example template configuration
template = {
    'name': 'Phase Completion Template',
    'sale_order_template_line_ids': [
        (0, 0, {
            'name': 'Phase Completion',
            'product_id': phase_product.id,
            'product_uom_qty': 1.0,
            'price_unit': 1000.0
        })
    ]
}
```

## Best Practices

### **1. Template Design**
- Create specific templates for different milestone types
- Include standard terms and conditions
- Use consistent pricing structures

### **2. Trigger Configuration**
- Use milestone triggers for major phase completions
- Use checkpoint triggers for specific deliverables
- Include meaningful notes for context

### **3. Workflow Design**
- Plan quotation triggers during workflow design
- Consider client billing preferences
- Balance automation with manual control

### **4. Monitoring**
- Regularly review quotation triggers
- Monitor quotation creation patterns
- Adjust templates based on feedback

## Troubleshooting

### **Common Issues:**

1. **Quotations Not Creating:**
   - Check if workflow instance exists
   - Verify partner is set on workflow
   - Ensure quotation triggers are enabled

2. **Template Not Applying:**
   - Verify template exists and is active
   - Check template line configurations
   - Review error logs for template issues

3. **Context Missing:**
   - Ensure workflow instance is properly linked
   - Check trigger type and name fields
   - Verify quotation creation context

### **Debug Information:**

```python
# Check workflow instance
workflow = self.env['fsm.workflow.instance'].browse(workflow_id)
print(f"Workflow: {workflow.name}")
print(f"Partner: {workflow.partner_id.name}")
print(f"Project: {workflow.project_id.name}")

# Check quotation triggers
checkpoint = self.env['project.task.checkpoint'].browse(checkpoint_id)
print(f"Checkpoint: {checkpoint.name}")
print(f"Create Quotation: {checkpoint.create_quotation_on_reach}")
print(f"Template: {checkpoint.quotation_template_id.name}")
```

## Future Enhancements

### **Planned Features:**
- 📊 **Quotation Analytics**: Track quotation patterns and success rates
- 🔄 **Recurring Quotations**: Set up recurring quotation schedules
- 📱 **Mobile Integration**: Create quotations from mobile devices
- 🤖 **AI Suggestions**: Intelligent quotation amount suggestions
- 📈 **Progress-Based Pricing**: Dynamic pricing based on progress

### **Integration Opportunities:**
- **Accounting**: Direct integration with accounting workflows
- **CRM**: Enhanced customer relationship tracking
- **Reporting**: Advanced quotation and billing reports
- **Automation**: Further workflow automation possibilities

---

This dynamic quotation system provides a comprehensive solution for creating quotations at any point in your workflow, ensuring better project tracking, client communication, and billing management.
