# 📋 Document-to-Task Automation Workflow Plan

## 🎯 **Overview**

This plan outlines the implementation of an automated workflow that creates tasks for each document copied from a product to a project when a quotation is confirmed. The workflow ensures that every document becomes a trackable task in the project management system.

## 🔄 **Current Workflow Analysis**

### **Existing Workflow Steps:**
1. **Product Creation**: Create product with service tracking enabled
2. **Document Addition**: Add documents to the product (required, deliverable, reference, compliance)
3. **Quotation Creation**: Create sale order with the product
4. **Quotation Confirmation**: Confirm the sale order
5. **Project Creation**: Project is automatically created (via `_timesheet_create_project`)
6. **Document Copying**: Documents are copied from product to project (via `_copy_product_documents_to_project`)

### **Current Code Flow:**
```python
# In sale_order_line_extension.py
def _timesheet_create_project(self):
    project = super()._timesheet_create_project()
    # Documents are marked for copying
    if self.product_id and self.product_id.document_ids:
        self.documents_copied = False
    return project

def _copy_product_documents_to_project(self, project):
    # Documents are copied from product to project
    for doc in self.product_id.document_ids:
        new_doc_vals = {
            'name': f"{doc.name} - {project.name}",
            'res_model': 'project.project',
            'res_id': project.id,
            # ... other fields
        }
        new_doc = self.env['documents.document'].create(new_doc_vals)
```

## 🚀 **Enhanced Workflow with Task Automation**

### **New Workflow Steps:**
1. **Product Creation**: Create product with service tracking enabled
2. **Document Addition**: Add documents to the product
3. **Quotation Creation**: Create sale order with the product
4. **Quotation Confirmation**: Confirm the sale order
5. **Project Creation**: Project is automatically created
6. **Document Copying**: Documents are copied from product to project
7. **Task Creation**: **NEW** - Tasks are automatically created for each copied document
8. **Task Assignment**: **NEW** - Tasks are assigned to appropriate team members
9. **Workflow Tracking**: **NEW** - Document status changes trigger task updates

## 🏗️ **Implementation Plan**

### **Phase 1: Core Task Creation Logic**

#### **1.1 Extend Document Model**
**File**: `models/core/documents_document.py`

```python
class DocumentsDocument(models.Model):
    _inherit = 'documents.document'
    
    # New fields for task integration
    related_task_id = fields.Many2one(
        'project.task',
        string='Related Task',
        help='Task created for this document'
    )
    auto_create_task = fields.Boolean(
        string='Auto Create Task',
        default=True,
        help='Automatically create a task when this document is copied to a project'
    )
    task_template_id = fields.Many2one(
        'project.task.template',
        string='Task Template',
        help='Template to use when creating task for this document'
    )
    task_assignee_id = fields.Many2one(
        'res.users',
        string='Task Assignee',
        help='User to assign the task to'
    )
    task_priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Critical')
    ], string='Task Priority', default='1')
    task_duration = fields.Float(
        string='Estimated Duration (Hours)',
        help='Estimated time to complete the task'
    )
    
    def create_task_for_document(self, project):
        """Create a task for this document in the given project"""
        self.ensure_one()
        
        if not self.auto_create_task:
            return False
            
        task_vals = {
            'name': f"Document: {self.name}",
            'description': f"Task for document: {self.name}\n\nDocument Details:\n- Category: {self.category}\n- Status: {self.status}\n- Priority: {self.priority}\n- Notes: {self.notes or 'No notes'}",
            'project_id': project.id,
            'priority': self.task_priority,
            'user_ids': [(4, self.task_assignee_id.id)] if self.task_assignee_id else False,
            'planned_hours': self.task_duration or 1.0,
            'tag_ids': [(6, 0, self.tag_ids.ids)] if self.tag_ids else False,
        }
        
        # Apply task template if specified
        if self.task_template_id:
            task_vals.update(self.task_template_id._get_task_vals())
        
        task = self.env['project.task'].create(task_vals)
        
        # Link the task back to the document
        self.related_task_id = task.id
        
        return task
```

#### **1.2 Extend Sale Order Line**
**File**: `models/integrations/sale_order_line_extension.py`

```python
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    # New fields
    tasks_created = fields.Boolean(
        string='Tasks Created',
        default=False,
        help='Indicates if tasks have been created for copied documents'
    )
    
    def _copy_product_documents_to_project(self, project):
        """Enhanced method to copy documents and create tasks"""
        self.ensure_one()
        
        if not self.product_id or not self.product_id.document_ids:
            return
        
        copied_docs = []
        created_tasks = []
        
        for doc in self.product_id.document_ids:
            try:
                # Copy document to project
                new_doc_vals = {
                    'name': f"{doc.name} - {project.name}",
                    'category': doc.category or 'reference',
                    'status': doc.status or 'draft',
                    'priority': doc.priority or '1',
                    'description': doc.description or '',
                    'notes': doc.notes or '',
                    'tag_ids': [(6, 0, doc.tag_ids.ids)] if doc.tag_ids else False,
                    'res_model': 'project.project',
                    'res_id': project.id,
                    'linked_product_id': self.product_id.id,
                    'auto_create_task': doc.auto_create_task,
                    'task_assignee_id': doc.task_assignee_id.id if doc.task_assignee_id else False,
                    'task_priority': doc.task_priority,
                    'task_duration': doc.task_duration,
                }
                
                if doc.attachment_id and doc.attachment_id.exists():
                    new_doc_vals['attachment_id'] = doc.attachment_id.id
                
                new_doc = self.env['documents.document'].sudo().create(new_doc_vals)
                copied_docs.append(new_doc)
                
                # Create task for the document
                if new_doc.auto_create_task:
                    task = new_doc.create_task_for_document(project)
                    if task:
                        created_tasks.append(task)
                
            except Exception as e:
                _logger.warning(f"Failed to copy document '{doc.name}': {e}")
                continue
        
        # Update tracking fields
        self.documents_copied = True
        self.tasks_created = len(created_tasks) > 0
        
        _logger.info(f"Copied {len(copied_docs)} documents and created {len(created_tasks)} tasks for project {project.name}")
        
        return {
            'documents': copied_docs,
            'tasks': created_tasks
        }
```

#### **1.3 Extend Project Model**
**File**: `models/integrations/project_extension.py`

```python
class ProjectProject(models.Model):
    _inherit = 'project.project'
    
    # New fields for task tracking
    document_tasks_count = fields.Integer(
        compute='_compute_document_tasks_count',
        string='Document Tasks',
        help='Number of tasks created from documents'
    )
    document_tasks_ids = fields.Many2many(
        'project.task',
        compute='_compute_document_tasks',
        string='Document Tasks',
        help='Tasks created from documents'
    )
    
    @api.depends('document_ids.related_task_id')
    def _compute_document_tasks_count(self):
        """Compute the number of tasks created from documents"""
        for project in self:
            project.document_tasks_count = len(project.document_ids.mapped('related_task_id'))
    
    @api.depends('document_ids.related_task_id')
    def _compute_document_tasks(self):
        """Get all tasks created from documents"""
        for project in self:
            project.document_tasks_ids = project.document_ids.mapped('related_task_id')
    
    def action_view_document_tasks(self):
        """Open the document tasks view"""
        self.ensure_one()
        tasks = self.document_tasks_ids
        
        if not tasks:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Document Tasks'),
                    'message': _('No tasks have been created from documents yet.'),
                    'type': 'info',
                }
            }
        
        return {
            'name': _('Document Tasks'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', tasks.ids)],
            'context': {
                'default_project_id': self.id,
            },
        }
    
    def create_tasks_for_documents(self):
        """Manually create tasks for documents that don't have tasks"""
        self.ensure_one()
        
        docs_without_tasks = self.document_ids.filtered(lambda d: not d.related_task_id and d.auto_create_task)
        
        created_tasks = []
        for doc in docs_without_tasks:
            task = doc.create_task_for_document(self)
            if task:
                created_tasks.append(task)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Tasks Created'),
                'message': _('Successfully created %d tasks for documents.') % len(created_tasks),
                'type': 'success',
            }
        }
```

### **Phase 2: Task Templates and Configuration**

#### **2.1 Task Template Model**
**File**: `models/core/task_template.py` (New file)

```python
class ProjectTaskTemplate(models.Model):
    _name = 'project.task.template'
    _description = 'Project Task Template'
    _order = 'name'
    
    name = fields.Char(
        string='Template Name',
        required=True,
        help='Name of the task template'
    )
    
    description_template = fields.Text(
        string='Description Template',
        help='Template for task description. Use {document_name}, {category}, {status}, etc.'
    )
    
    default_priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Critical')
    ], string='Default Priority', default='1')
    
    default_duration = fields.Float(
        string='Default Duration (Hours)',
        default=1.0,
        help='Default estimated duration for tasks'
    )
    
    default_assignee_id = fields.Many2one(
        'res.users',
        string='Default Assignee',
        help='Default user to assign tasks to'
    )
    
    tag_ids = fields.Many2many(
        'project.tags',
        string='Default Tags',
        help='Default tags to apply to tasks'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Whether this template is active'
    )
    
    def _get_task_vals(self):
        """Get task values from template"""
        return {
            'priority': self.default_priority,
            'planned_hours': self.default_duration,
            'user_ids': [(4, self.default_assignee_id.id)] if self.default_assignee_id else False,
            'tag_ids': [(6, 0, self.tag_ids.ids)] if self.tag_ids else False,
        }
```

#### **2.2 Document Category Task Templates**
**File**: `models/core/document_category_task_template.py` (New file)

```python
class DocumentCategoryTaskTemplate(models.Model):
    _name = 'document.category.task.template'
    _description = 'Document Category Task Template'
    _order = 'category,sequence'
    
    category = fields.Selection([
        ('required', 'Required'),
        ('deliverable', 'Deliverable'),
        ('reference', 'Reference'),
        ('compliance', 'Compliance')
    ], string='Document Category', required=True)
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of the template'
    )
    
    task_template_id = fields.Many2one(
        'project.task.template',
        string='Task Template',
        required=True,
        help='Task template to use for this document category'
    )
    
    default_assignee_id = fields.Many2one(
        'res.users',
        string='Default Assignee',
        help='Default assignee for this category (overrides template)'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Whether this template is active'
    )
    
    @api.model
    def get_template_for_category(self, category):
        """Get the task template for a document category"""
        template = self.search([
            ('category', '=', category),
            ('active', '=', True)
        ], order='sequence', limit=1)
        
        return template.task_template_id if template else False
```

### **Phase 3: Views and User Interface**

#### **3.1 Document Form View Enhancement**
**File**: `views/core/documents_document_views.xml`

```xml
<!-- Add to documents.document form view -->
<group string="Task Integration">
    <field name="auto_create_task"/>
    <field name="related_task_id" readonly="1"/>
    <field name="task_template_id" attrs="{'invisible': [('auto_create_task', '=', False)]}"/>
    <field name="task_assignee_id" attrs="{'invisible': [('auto_create_task', '=', False)]}"/>
    <field name="task_priority" attrs="{'invisible': [('auto_create_task', '=', False)]}"/>
    <field name="task_duration" attrs="{'invisible': [('auto_create_task', '=', False)]}"/>
</group>

<!-- Add action buttons -->
<div class="oe_button_box" name="button_box">
    <button name="action_create_task" type="object" 
            string="Create Task" class="oe_stat_button"
            attrs="{'invisible': [('related_task_id', '!=', False), ('auto_create_task', '=', False)]}"/>
    <button name="action_view_task" type="object" 
            string="View Task" class="oe_stat_button"
            attrs="{'invisible': [('related_task_id', '=', False)]}"/>
</div>
```

#### **3.2 Project Form View Enhancement**
**File**: `views/integrations/project_views.xml`

```xml
<!-- Add to project.project form view -->
<group string="Document Tasks">
    <field name="document_tasks_count" widget="statinfo" string="Document Tasks"/>
    <button name="action_view_document_tasks" type="object" 
            string="View Document Tasks" class="btn btn-secondary"/>
    <button name="create_tasks_for_documents" type="object" 
            string="Create Tasks for Documents" class="btn btn-primary"/>
</group>
```

#### **3.3 Task Template Views**
**File**: `views/core/task_template_views.xml` (New file)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Task Template Form View -->
        <record id="view_project_task_template_form" model="ir.ui.view">
            <field name="name">project.task.template.form</field>
            <field name="model">project.task.template</field>
            <field name="arch" type="xml">
                <form>
                    <sheet>
                        <group>
                            <group>
                                <field name="name"/>
                                <field name="default_priority"/>
                                <field name="default_duration"/>
                            </group>
                            <group>
                                <field name="default_assignee_id"/>
                                <field name="tag_ids" widget="many2many_tags"/>
                                <field name="active"/>
                            </group>
                        </group>
                        <group string="Description Template">
                            <field name="description_template" placeholder="Use {document_name}, {category}, {status}, {priority}, {notes} as placeholders"/>
                        </group>
                    </sheet>
                </form>
            </field>
        </record>

        <!-- Task Template Tree View -->
        <record id="view_project_task_template_tree" model="ir.ui.view">
            <field name="name">project.task.template.tree</field>
            <field name="model">project.task.template</field>
            <field name="arch" type="xml">
                <tree>
                    <field name="name"/>
                    <field name="default_priority"/>
                    <field name="default_duration"/>
                    <field name="default_assignee_id"/>
                    <field name="active"/>
                </tree>
            </field>
        </record>

        <!-- Task Template Action -->
        <record id="action_project_task_template" model="ir.actions.act_window">
            <field name="name">Task Templates</field>
            <field name="res_model">project.task.template</field>
            <field name="view_mode">tree,form</field>
        </record>

        <!-- Menu Item -->
        <menuitem id="menu_project_task_template"
                  name="Task Templates"
                  parent="project.menu_project_config"
                  action="action_project_task_template"
                  sequence="50"/>
    </data>
</odoo>
```

### **Phase 4: Automation and Workflow**

#### **4.1 Document Status Change Automation**
**File**: `models/core/documents_document.py`

```python
class DocumentsDocument(models.Model):
    _inherit = 'documents.document'
    
    def write(self, vals):
        """Override to handle status changes and update related tasks"""
        result = super().write(vals)
        
        # If status changed, update related task
        if 'status' in vals and self.related_task_id:
            self._update_task_from_status_change(vals['status'])
        
        return result
    
    def _update_task_from_status_change(self, new_status):
        """Update related task based on document status change"""
        self.ensure_one()
        
        if not self.related_task_id:
            return
        
        task = self.related_task_id
        
        # Map document status to task stage
        status_to_stage_mapping = {
            'draft': 'draft',
            'pending': 'pending',
            'in_progress': 'in_progress',
            'completed': 'done',
            'verified': 'done',
            'delivered': 'done',
            'expired': 'cancelled',
            'cancelled': 'cancelled'
        }
        
        new_stage = status_to_stage_mapping.get(new_status)
        if new_stage and hasattr(task, 'stage_id'):
            # Find stage by name or create mapping
            stage = self.env['project.task.type'].search([('name', 'ilike', new_stage)], limit=1)
            if stage:
                task.stage_id = stage.id
        
        # Update task description with new status
        task.description = f"Task for document: {self.name}\n\nDocument Details:\n- Category: {self.category}\n- Status: {self.status}\n- Priority: {self.priority}\n- Notes: {self.notes or 'No notes'}"
```

#### **4.2 Task Completion Automation**
**File**: `models/integrations/project_extension.py`

```python
class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    related_document_id = fields.Many2one(
        'documents.document',
        string='Related Document',
        help='Document this task was created for'
    )
    
    def write(self, vals):
        """Override to handle task completion and update related document"""
        result = super().write(vals)
        
        # If task is completed, update related document
        if 'stage_id' in vals and self.related_document_id:
            stage = self.env['project.task.type'].browse(vals['stage_id'])
            if stage.name.lower() in ['done', 'completed', 'finished']:
                self._update_document_from_task_completion()
        
        return result
    
    def _update_document_from_task_completion(self):
        """Update related document when task is completed"""
        self.ensure_one()
        
        if not self.related_document_id:
            return
        
        document = self.related_document_id
        
        # Update document status to completed
        document.status = 'completed'
        
        # Add completion note
        completion_note = f"Task completed on {fields.Datetime.now()}"
        if document.notes:
            document.notes += f"\n\n{completion_note}"
        else:
            document.notes = completion_note
```

### **Phase 5: Configuration and Settings**

#### **5.1 Settings Model**
**File**: `models/core/settings.py` (New file)

```python
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Document to Task settings
    auto_create_tasks_for_documents = fields.Boolean(
        string='Auto Create Tasks for Documents',
        default=True,
        help='Automatically create tasks when documents are copied to projects'
    )
    
    default_task_priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Critical')
    ], string='Default Task Priority', default='1')
    
    default_task_duration = fields.Float(
        string='Default Task Duration (Hours)',
        default=1.0,
        help='Default estimated duration for document tasks'
    )
    
    default_task_assignee_id = fields.Many2one(
        'res.users',
        string='Default Task Assignee',
        help='Default user to assign document tasks to'
    )
    
    # Category-based settings
    required_doc_task_template_id = fields.Many2one(
        'project.task.template',
        string='Required Document Task Template',
        help='Task template for required documents'
    )
    
    deliverable_doc_task_template_id = fields.Many2one(
        'project.task.template',
        string='Deliverable Document Task Template',
        help='Task template for deliverable documents'
    )
    
    reference_doc_task_template_id = fields.Many2one(
        'project.task.template',
        string='Reference Document Task Template',
        help='Task template for reference documents'
    )
    
    compliance_doc_task_template_id = fields.Many2one(
        'project.task.template',
        string='Compliance Document Task Template',
        help='Task template for compliance documents'
    )
```

## 📋 **Implementation Steps**

### **Step 1: Core Model Extensions**
1. Extend `documents.document` model with task integration fields
2. Extend `sale.order.line` with enhanced document copying and task creation
3. Extend `project.project` with document task tracking
4. Create task template models

### **Step 2: Views and UI**
1. Update document form views with task integration fields
2. Update project form views with document task management
3. Create task template management views
4. Add action buttons and smart buttons

### **Step 3: Automation Logic**
1. Implement document-to-task creation logic
2. Implement status synchronization between documents and tasks
3. Add task completion automation
4. Create configuration settings

### **Step 4: Testing and Validation**
1. Test the complete workflow from product creation to task completion
2. Validate document status changes trigger task updates
3. Test task completion updates document status
4. Verify all edge cases and error handling

### **Step 5: Documentation and Training**
1. Update module documentation
2. Create user guides for the new workflow
3. Document configuration options
4. Create troubleshooting guides

## 🎯 **Expected Benefits**

1. **Automated Task Creation**: Every document becomes a trackable task
2. **Workflow Integration**: Seamless integration between document and task management
3. **Status Synchronization**: Document and task status stay in sync
4. **Template-Based Configuration**: Flexible task creation based on document categories
5. **Improved Project Management**: Better visibility into document-related work
6. **Reduced Manual Work**: Automatic task creation eliminates manual setup

## 🔧 **Technical Considerations**

1. **Performance**: Efficient task creation and status updates
2. **Error Handling**: Robust error handling for failed task creation
3. **Data Integrity**: Maintain referential integrity between documents and tasks
4. **User Permissions**: Proper access rights for task creation and management
5. **Backward Compatibility**: Ensure existing functionality remains intact

## 📈 **Future Enhancements**

1. **Advanced Task Dependencies**: Create dependencies between document tasks
2. **Time Tracking**: Automatic time tracking for document-related tasks
3. **Reporting**: Enhanced reporting on document task completion
4. **Notifications**: Email notifications for task creation and completion
5. **Mobile Support**: Mobile-friendly task management for documents

---

**Version**: 1.0  
**Author**: Sabry  
**Status**: Planning Phase 📋
