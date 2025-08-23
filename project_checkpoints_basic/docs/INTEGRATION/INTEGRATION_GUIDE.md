# Template Integration Guide

## Overview

This guide explains how the dual template system works, providing both milestone templates and enhanced checkpoint templates for flexible project management.

## Template Types

### 1. Milestone Templates (`project.milestone.template`)

**Purpose**: Create project-level milestones with predefined checkpoints
**Workflow**: Milestone → Checkpoints
**Best For**: Project planning, milestone-driven workflows

**Features**:
- Define milestone name, deadline, and notes
- Add multiple checkpoint definitions
- Apply to projects to create milestones with checkpoints
- Natural project management hierarchy

**Usage**:
1. Create milestone template with checkpoint definitions
2. Apply template to project
3. Milestone is created with all checkpoints linked

### 2. Enhanced Checkpoint Templates (`project.task.checkpoint.template`)

**Purpose**: Create task-level checkpoints with optional milestone creation
**Workflow**: Checkpoints → Optional Milestone
**Best For**: Task management, flexible workflows

**Features**:
- Define checkpoints for tasks
- Optional milestone creation
- Backward compatible with existing templates
- Granular control over checkpoint creation

**Usage**:
1. Create checkpoint template
2. Enable milestone creation if desired
3. Apply to tasks
4. Checkpoints created with optional milestone linking

## Template Selection Wizard

### Unified Interface

The template selection wizard provides a single interface for both template types:

**Features**:
- Template type selection (Milestone vs Checkpoint)
- Dynamic field visibility based on selection
- Template preview functionality
- Context-aware project and task selection
- Validation and error handling

**Usage**:
1. Navigate to Project → Configuration → Apply Template
2. Select template type
3. Choose project and template
4. Preview template if desired
5. Apply template

## Integration Points

### 1. Menu Organization

```
Project → Configuration
├── Checkpoint Templates (sequence 51)
├── Milestone Templates (sequence 52)
└── Apply Template (sequence 53)
```

### 2. Data Consistency

- **No Conflicts**: Both template types can coexist
- **Shared Resources**: Both use the same checkpoint tags
- **Project Integration**: Both work within project context
- **Task Integration**: Checkpoint templates link to tasks

### 3. Auto-Advancement

- **Milestone Auto-Advancement**: Milestones automatically marked as reached when all checkpoints are completed
- **Bidirectional Logic**: Milestones unmark when checkpoints are unchecked
- **Real-time Updates**: Immediate feedback on checkpoint state changes

## Use Case Scenarios

### Scenario 1: Project Planning
**Use**: Milestone Templates
**Workflow**:
1. Create milestone template for "Development Phase"
2. Add checkpoints: "Requirements Review", "Design Approval", "Code Review"
3. Apply to project
4. Milestone created with all checkpoints

### Scenario 2: Task Management
**Use**: Checkpoint Templates
**Workflow**:
1. Create checkpoint template for "Bug Fix Process"
2. Add checkpoints: "Reproduce Issue", "Fix Code", "Test Fix"
3. Apply to specific tasks
4. Checkpoints created for task

### Scenario 3: Hybrid Approach
**Use**: Both Template Types
**Workflow**:
1. Use milestone templates for major project phases
2. Use checkpoint templates for detailed task workflows
3. Both systems work together seamlessly

## Testing Checklist

### Milestone Templates
- [ ] Create milestone template with checkpoints
- [ ] Apply template to project
- [ ] Verify milestone creation
- [ ] Verify checkpoint linking
- [ ] Test auto-advancement logic

### Checkpoint Templates
- [ ] Create checkpoint template without milestone
- [ ] Create checkpoint template with milestone
- [ ] Apply to tasks
- [ ] Verify checkpoint creation
- [ ] Verify optional milestone creation

### Template Selection Wizard
- [ ] Open wizard
- [ ] Select template type
- [ ] Choose template
- [ ] Preview template
- [ ] Apply template
- [ ] Verify results

### Integration Testing
- [ ] Both template types work independently
- [ ] Both template types work together
- [ ] No conflicts between systems
- [ ] Backward compatibility maintained

## Best Practices

### 1. Template Design
- **Clear Naming**: Use descriptive names for templates
- **Logical Grouping**: Group related checkpoints together
- **Appropriate Tags**: Use tags for categorization
- **Realistic Deadlines**: Set achievable milestone deadlines

### 2. Template Application
- **Right Tool**: Choose appropriate template type for use case
- **Project Context**: Ensure templates are applied to correct projects
- **Task Context**: For checkpoint templates, ensure correct task selection
- **Validation**: Verify template details before application

### 3. Maintenance
- **Regular Review**: Periodically review and update templates
- **Version Control**: Keep track of template changes
- **User Training**: Train users on both template types
- **Feedback Loop**: Collect user feedback for improvements

## Troubleshooting

### Common Issues

1. **Template Not Applying**
   - Check template is active
   - Verify project/task selection
   - Ensure template has checkpoints

2. **Milestone Not Auto-Advancing**
   - Check all checkpoints are marked as reached
   - Verify milestone-checkpoint linking
   - Check for JavaScript errors

3. **Wizard Not Working**
   - Verify security access rights
   - Check template type selection
   - Ensure required fields are filled

### Error Messages

- **"No project specified"**: Select a project before applying template
- **"No checkpoints defined"**: Add checkpoints to template before applying
- **"Template not found"**: Check template is active and accessible

## Future Enhancements

### Planned Features
- Template versioning
- Template import/export
- Advanced template rules
- Template analytics
- Bulk template application

### Integration Opportunities
- Calendar integration
- Reporting integration
- Workflow automation
- Mobile app support
