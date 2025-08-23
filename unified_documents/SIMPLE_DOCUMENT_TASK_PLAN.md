# 📋 Simple Document-to-Task Plan

## 🎯 **Simplified Approach**

Instead of creating individual tasks for each document, we create **one task per document category** when a project is created. This is much simpler and more practical.

## 🔄 **Current Workflow**
1. Create product with service tracking (Project & Task)
2. Add documents to product (required, deliverable, reference, compliance)
3. Create quotation with product
4. Confirm quotation → Project created + Tasks created
5. Documents copied to project ✅

## 🚀 **Enhanced Workflow (Simple)**
1. Create product with service tracking
2. Add documents to product
3. Create quotation with product
4. Confirm quotation → Project created + Tasks created
5. Documents copied to project ✅
6. **NEW**: Create tasks for document categories ✅

## 🏗️ **Simple Implementation**

### **Step 1: Extend Project Model**
**File**: `models/integrations/project_extension.py`

```python
class ProjectProject(models.Model):
    _inherit = 'project.project'
    
    def create_document_category_tasks(self):
        """Create tasks for each document category that has documents"""
        self.ensure_one()
        
        # Get document counts by category
        required_count = len(self.document_ids.filtered(lambda d: d.category == 'required'))
        deliverable_count = len(self.document_ids.filtered(lambda d: d.category == 'deliverable'))
        reference_count = len(self.document_ids.filtered(lambda d: d.category == 'reference'))
        compliance_count = len(self.document_ids.filtered(lambda d: d.category == 'compliance'))
        
        created_tasks = []
        
        # Create task for Required Documents
        if required_count > 0:
            task_vals = {
                'name': f'Required Documents ({required_count})',
                'description': f'Process {required_count} required documents for project {self.name}',
                'project_id': self.id,
                'priority': '2',  # High priority for required docs
                'planned_hours': required_count * 0.5,  # 30 min per document
            }
            task = self.env['project.task'].create(task_vals)
            created_tasks.append(task)
        
        # Create task for Deliverable Documents
        if deliverable_count > 0:
            task_vals = {
                'name': f'Deliverable Documents ({deliverable_count})',
                'description': f'Prepare {deliverable_count} deliverable documents for project {self.name}',
                'project_id': self.id,
                'priority': '1',  # Normal priority
                'planned_hours': deliverable_count * 1.0,  # 1 hour per document
            }
            task = self.env['project.task'].create(task_vals)
            created_tasks.append(task)
        
        # Create task for Reference Documents
        if reference_count > 0:
            task_vals = {
                'name': f'Reference Documents ({reference_count})',
                'description': f'Review {reference_count} reference documents for project {self.name}',
                'project_id': self.id,
                'priority': '0',  # Low priority
                'planned_hours': reference_count * 0.25,  # 15 min per document
            }
            task = self.env['project.task'].create(task_vals)
            created_tasks.append(task)
        
        # Create task for Compliance Documents
        if compliance_count > 0:
            task_vals = {
                'name': f'Compliance Documents ({compliance_count})',
                'description': f'Process {compliance_count} compliance documents for project {self.name}',
                'project_id': self.id,
                'priority': '3',  # Critical priority
                'planned_hours': compliance_count * 1.5,  # 1.5 hours per document
            }
            task = self.env['project.task'].create(task_vals)
            created_tasks.append(task)
        
        return created_tasks
```

### **Step 2: Extend Sale Order Line**
**File**: `models/integrations/sale_order_line_extension.py`

```python
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    def _timesheet_create_project(self):
        """Override to create document category tasks after project creation"""
        project = super()._timesheet_create_project()
        
        # Create tasks for document categories
        if project and self.product_id and self.product_id.document_ids:
            project.create_document_category_tasks()
        
        return project
```

### **Step 3: Add Project View Enhancement**
**File**: `views/integrations/project_views.xml`

```xml
<!-- Add to project.project form view -->
<group string="Document Tasks">
    <field name="required_document_count" widget="statinfo" string="Required Docs"/>
    <field name="deliverable_document_count" widget="statinfo" string="Deliverable Docs"/>
    <field name="reference_document_count" widget="statinfo" string="Reference Docs"/>
    <field name="compliance_document_count" widget="statinfo" string="Compliance Docs"/>
    <button name="create_document_category_tasks" type="object" 
            string="Create Document Tasks" class="btn btn-primary"/>
</group>
```

### **Step 4: Add Computed Fields to Project**
**File**: `models/integrations/project_extension.py`

```python
class ProjectProject(models.Model):
    _inherit = 'project.project'
    
    # Document category counts
    required_document_count = fields.Integer(
        compute='_compute_document_category_counts',
        string='Required Documents'
    )
    deliverable_document_count = fields.Integer(
        compute='_compute_document_category_counts',
        string='Deliverable Documents'
    )
    reference_document_count = fields.Integer(
        compute='_compute_document_category_counts',
        string='Reference Documents'
    )
    compliance_document_count = fields.Integer(
        compute='_compute_document_category_counts',
        string='Compliance Documents'
    )
    
    @api.depends('document_ids', 'document_ids.category')
    def _compute_document_category_counts(self):
        """Compute document counts by category"""
        for project in self:
            project.required_document_count = len(project.document_ids.filtered(lambda d: d.category == 'required'))
            project.deliverable_document_count = len(project.document_ids.filtered(lambda d: d.category == 'deliverable'))
            project.reference_document_count = len(project.document_ids.filtered(lambda d: d.category == 'reference'))
            project.compliance_document_count = len(project.document_ids.filtered(lambda d: d.category == 'compliance'))
```

## 📊 **Expected Result**

When a project is created, you'll get tasks like:
- **Required Documents (3)** - Process 3 required documents
- **Deliverable Documents (2)** - Prepare 2 deliverable documents  
- **Reference Documents (1)** - Review 1 reference document
- **Compliance Documents (1)** - Process 1 compliance document

## 🎯 **Benefits of This Approach**

1. **Simple** - One task per category, not per document
2. **Practical** - Teams work on document categories, not individual documents
3. **Progress Tracking** - Can track progress by category
4. **Minimal Code** - Just a few methods to add
5. **Existing Infrastructure** - Uses your current document copying system

## 🔧 **Implementation Steps**

1. **Add the `create_document_category_tasks()` method to project model**
2. **Enhance `_timesheet_create_project()` in sale order line**
3. **Add computed fields for document category counts**
4. **Add button to project view for manual task creation**
5. **Test the workflow**

## 📋 **Usage**

1. Create product with documents
2. Create and confirm quotation
3. Project is created with tasks
4. **NEW**: Document category tasks are automatically created
5. Team can work on document categories as tasks

This is much simpler and more practical than creating individual tasks for each document!

---

**Status**: Ready for Simple Implementation 🚀  
**Effort**: 1-2 hours  
**Complexity**: Low
