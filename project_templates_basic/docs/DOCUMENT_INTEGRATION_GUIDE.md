# Document Integration Guide

## Overview

This guide explains how the system handles document creation when multiple sources are available:
1. **Product Documents** - Documents attached to products
2. **Task Template Document Templates** - Document templates linked to task templates

## How It Works

### Scenario: Product + Task Template with Document Templates

When you have:
- A **product** with documents in its document tab
- A **task template** with linked document templates
- You create a task using that task template

The system will **combine both sources** to create a comprehensive set of documents for the task.

### Document Creation Process

1. **Product Documents** (if applicable):
   - Documents from the product's document tab
   - Filtered based on task template settings
   - Marked with source: 'product'

2. **Document Template Documents**:
   - Documents created from linked document templates
   - Marked with source: 'template'

3. **Checklist Items**:
   - Created from document template checklist lines
   - Marked with source: 'template'

## Configuration Options

### Task Template Document Category Settings

The task template's **Document Category** field controls which product documents are included:

- **All Documents**: Includes all product documents
- **Required**: Only includes product documents with category 'required'
- **Deliverable**: Only includes product documents with category 'deliverable'
- **Reference**: Only includes product documents with category 'reference'
- **Compliance**: Only includes product documents with category 'compliance'

### Document Template Types

Document templates can be:
- **Document-Based**: Contains predefined document structures
- **Checklist-Based**: Contains task-oriented checklists
- **Hybrid**: Contains both documents and checklists

## Step-by-Step Usage

### 1. Set Up Product Documents
1. Go to **Products** → Select a product
2. Go to **Documents** tab
3. Add documents with appropriate categories and priorities

### 2. Create Document Templates
1. Go to **Project Management** → **Document Templates**
2. Create document templates with:
   - Document template lines (specific documents)
   - Checklist template lines (task items)
   - Appropriate template type

### 3. Link Document Templates to Task Templates
1. Go to **Project Management** → **Task Templates**
2. Select or create a task template
3. Go to **Document Templates** tab
4. Select document templates to link
5. Configure document category settings

### 4. Create Tasks
When you create a task using the task template:
- Product documents (filtered by category) will be copied
- Document template documents will be created
- Document template checklists will be created
- All items will be linked to the task

## Example Scenario

### Product Setup
**Product**: "Software Development Package"
**Documents**:
- Requirements Document (Required, High Priority)
- Technical Specification (Required, High Priority)
- User Manual (Deliverable, Normal Priority)

### Document Template Setup
**Document Template**: "Development Process"
**Document Lines**:
- Code Review Checklist (Required, High Priority)
- Testing Plan (Required, High Priority)
- Deployment Guide (Deliverable, Normal Priority)

**Checklist Lines**:
- Code Review Completed (Required)
- Unit Tests Written (Required)
- Integration Tests Passed (Required)

### Task Template Setup
**Task Template**: "Development Task"
**Document Category**: "All Documents"
**Linked Document Templates**: "Development Process"

### Result
When a task is created using this template, it will have:

**Documents from Product**:
- Requirements Document
- Technical Specification  
- User Manual

**Documents from Template**:
- Code Review Checklist
- Testing Plan
- Deployment Guide

**Checklist Items**:
- Code Review Completed
- Unit Tests Written
- Integration Tests Passed

## Source Tracking

All created documents and checklist items include source tracking:

### Document Source Fields
- **source**: 'product', 'template', or 'manual'
- **source_document_id**: Original product document (if from product)
- **source_template_id**: Document template (if from template)
- **template_line_id**: Specific template line

### Checklist Source Fields
- **source**: 'template' or 'manual'
- **source_template_id**: Document template
- **template_line_id**: Specific template line

## Best Practices

1. **Organize Product Documents**: Use appropriate categories and priorities
2. **Create Reusable Templates**: Design document templates for common scenarios
3. **Link Appropriately**: Choose document templates that complement product documents
4. **Monitor Usage**: Check template usage history to optimize configurations
5. **Maintain Consistency**: Use consistent naming and categorization

## Troubleshooting

### No Documents Created
- Check if product has documents
- Verify task template has linked document templates
- Ensure document category settings are correct

### Missing Documents
- Check document category filtering
- Verify document template is active
- Review template line configurations

### Duplicate Documents
- Check for overlapping document names
- Review product and template document configurations
- Use source tracking to identify duplicates

## Advanced Features

### Custom Document Creation
You can extend the system to:
- Add custom document creation logic
- Implement document validation rules
- Create document approval workflows

### Integration with Other Modules
The system integrates with:
- Project management workflows
- Document management systems
- Task tracking and reporting
