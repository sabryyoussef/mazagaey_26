# Portal My Tasks Module - Production Implementation Plan

## 📋 Executive Summary

This document outlines a **production-grade implementation plan** for a custom Odoo module that enables **employees to operate as Portal users** with a dedicated "My Tasks" workspace. This approach significantly reduces licensing costs while maintaining full accountability, task management, and handover workflows.

**Module Name**: `portal_my_tasks`  
**Target Odoo Version**: 18.0  
**License**: LGPL-3  
**Author**: Sabry Youssef

---

## 🎯 Target Operating Model

### User Roles

| Role | User Type | Access Level | Purpose |
|------|-----------|--------------|---------|
| **Manager** | Internal | Full backend access | Create projects/tasks, assign work, review handovers, close tasks, run reporting |
| **Operations Admin** | Internal | Full backend access | Break-glass admin, system maintenance |
| **Employees** | Portal | Portal-only (My Tasks) | View assigned tasks, post updates, upload handover notes, submit for approval |
| **Sales Persons** | Internal | Customer-facing access | Direct customer access (keep as internal for CRM/sales features) |

### Key Principles

1. **Portal users are NOT internal licensed seats** - Cost-effective solution
2. **Hard security boundaries** - Portal cannot access backend/internal apps
3. **Full accountability** - Each portal login is unique, no shared accounts
4. **Controlled workflow** - Handover notes required before task closure
5. **Manager oversight** - All submissions require approval

---

## ⚠️ Phase 0: Contract & Governance (Non-Negotiable)

### 0.1 License Verification

**Critical Action Items:**

1. **Confirm Odoo subscription terms** explicitly allow employees as Portal-only users
   - Some contracts have strict definitions of "employee use"
   - Portal users are typically free/unlimited
   - Verify with Odoo support if needed

2. **Document the approach** in internal policy
   - Define who gets Portal vs Internal access
   - Establish break-glass procedures for shared admin account
   - Document security boundaries

3. **Legal/Compliance Review**
   - Ensure approach aligns with company policies
   - Document data access patterns for audit

**Deliverable**: Signed-off governance document

---

## 🏗️ Phase 1: Foundation - Data Model & Security

### 1.1 Module Structure

```
portal_my_tasks/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── project_task.py          # Extend project.task
│   ├── project_handover_note.py  # Handover note model
│   └── portal_assignee.py        # Portal assignment tracking
├── controllers/
│   ├── __init__.py
│   ├── portal_my_tasks.py        # Portal controllers
│   └── handover_controller.py    # Handover submission
├── views/
│   ├── portal_templates.xml      # Portal page templates
│   ├── task_views.xml            # Backend task views
│   └── handover_views.xml        # Handover management views
├── security/
│   ├── security.xml              # Security groups & rules
│   └── ir.model.access.csv      # Access rights
├── static/
│   └── description/
│       └── icon.png
└── data/
    └── portal_menu_data.xml      # Portal menu items
```

### 1.2 Data Model Extensions

#### 1.2.1 Project Task Extensions

**File**: `models/project_task.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    # Portal Assignment
    portal_assignee_id = fields.Many2one(
        'res.partner',
        string='Portal Assignee',
        tracking=True,
        help='Portal user assigned to this task (for employee accountability)'
    )
    
    portal_assignee_ids = fields.Many2many(
        'res.partner',
        'task_portal_assignee_rel',
        string='Portal Assignees',
        help='Multiple portal users can be assigned (for team tasks)'
    )
    
    # Link to employee for reporting (internal side)
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        compute='_compute_employee_id',
        store=True,
        help='Employee record linked to portal assignee (for KPI/reporting)'
    )
    
    # Handover Requirements
    requires_handover = fields.Boolean(
        string='Requires Handover',
        default=False,
        help='Task must have approved handover before closure'
    )
    
    latest_handover_note_id = fields.Many2one(
        'project.handover.note',
        string='Latest Handover Note',
        compute='_compute_latest_handover',
        store=False
    )
    
    approved_handover_exists = fields.Boolean(
        string='Has Approved Handover',
        compute='_compute_handover_status',
        store=False
    )
    
    # Portal-specific fields
    portal_stage_allowed_ids = fields.Many2many(
        'project.task.type',
        compute='_compute_portal_stage_allowed',
        string='Allowed Stages (Portal)',
        help='Stages portal users can move task to'
    )
    
    @api.depends('portal_assignee_id', 'portal_assignee_ids')
    def _compute_employee_id(self):
        """Link portal assignee to employee record"""
        for task in self:
            employee = False
            if task.portal_assignee_id:
                # Find employee linked to this partner
                employee = self.env['hr.employee'].search([
                    ('work_contact_id', '=', task.portal_assignee_id.id)
                ], limit=1)
            task.employee_id = employee
    
    @api.depends('handover_note_ids', 'handover_note_ids.state')
    def _compute_latest_handover(self):
        """Get the most recent handover note"""
        for task in self:
            latest = task.handover_note_ids.sorted('create_date', reverse=True)
            task.latest_handover_note_id = latest[0] if latest else False
    
    @api.depends('handover_note_ids', 'handover_note_ids.state')
    def _compute_handover_status(self):
        """Check if approved handover exists"""
        for task in self:
            approved = task.handover_note_ids.filtered(
                lambda h: h.state == 'approved'
            )
            task.approved_handover_exists = bool(approved)
    
    def _compute_portal_stage_allowed(self):
        """Define which stages portal users can move to"""
        allowed_stages = self.env['project.task.type'].search([
            ('name', 'in', ['In Progress', 'Review', 'Waiting Approval'])
        ])
        for task in self:
            task.portal_stage_allowed_ids = allowed_stages
    
    def action_portal_update_status(self, stage_id):
        """Portal action to update task status"""
        if not self._check_portal_access():
            raise UserError(_("You don't have permission to update this task"))
        
        if stage_id not in self.portal_stage_allowed_ids.ids:
            raise UserError(_("You cannot move task to this stage"))
        
        self.stage_id = stage_id
        self.message_post(
            body=_("Status updated by %s") % self.env.user.name,
            subtype_xmlid='mail.mt_note'
        )
    
    def _check_portal_access(self):
        """Verify portal user has access to this task"""
        if not self.env.user.has_group('base.group_portal'):
            return True  # Internal users always have access
        
        # Portal users can only access their assigned tasks
        return (
            self.portal_assignee_id == self.env.user.partner_id or
            self.env.user.partner_id in self.portal_assignee_ids or
            self.env.user.partner_id in self.message_partner_ids
        )
    
    def action_close_task(self):
        """Override close action to enforce handover requirement"""
        if self.requires_handover and not self.approved_handover_exists:
            raise ValidationError(_(
                "Cannot close task: Approved handover note is required. "
                "Please submit and get approval for a handover note first."
            ))
        return super().action_close_task()
```

#### 1.2.2 Handover Note Model

**File**: `models/project_handover_note.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ProjectHandoverNote(models.Model):
    _name = 'project.handover.note'
    _description = 'Project Task Handover Note'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    
    # Basic Information
    name = fields.Char(
        string='Reference',
        required=True,
        default=lambda self: _('New'),
        readonly=True,
        copy=False
    )
    
    task_id = fields.Many2one(
        'project.task',
        string='Task',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        related='task_id.project_id',
        store=True,
        readonly=True
    )
    
    # Submission Details
    submitted_by_partner_id = fields.Many2one(
        'res.partner',
        string='Submitted By',
        required=True,
        default=lambda self: self.env.user.partner_id,
        tracking=True
    )
    
    submitted_by_employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        compute='_compute_employee',
        store=True
    )
    
    version = fields.Integer(
        string='Version',
        default=1,
        help='Version number for this handover note'
    )
    
    # Content
    content = fields.Html(
        string='Handover Content',
        required=True,
        help='Detailed handover information'
    )
    
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'handover_attachment_rel',
        string='Attachments',
        help='Supporting documents for handover'
    )
    
    # Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='State', default='draft', tracking=True)
    
    # Approval
    manager_comment = fields.Text(
        string='Manager Comment',
        help='Manager feedback on handover note'
    )
    
    approved_by_id = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True
    )
    
    approved_date = fields.Datetime(
        string='Approved Date',
        readonly=True
    )
    
    rejected_by_id = fields.Many2one(
        'res.users',
        string='Rejected By',
        readonly=True
    )
    
    rejected_date = fields.Datetime(
        string='Rejected Date',
        readonly=True
    )
    
    # Computed Fields
    can_edit = fields.Boolean(
        string='Can Edit',
        compute='_compute_permissions'
    )
    
    can_submit = fields.Boolean(
        string='Can Submit',
        compute='_compute_permissions'
    )
    
    @api.model
    def create(self, vals):
        """Generate sequence for handover note"""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'project.handover.note'
            ) or _('New')
        return super().create(vals)
    
    @api.depends('submitted_by_partner_id')
    def _compute_employee(self):
        """Link partner to employee"""
        for note in self:
            employee = self.env['hr.employee'].search([
                ('work_contact_id', '=', note.submitted_by_partner_id.id)
            ], limit=1)
            note.submitted_by_employee_id = employee
    
    def _compute_permissions(self):
        """Compute portal user permissions"""
        for note in self:
            user = self.env.user
            is_portal = user.has_group('base.group_portal')
            is_owner = note.submitted_by_partner_id == user.partner_id
            
            note.can_edit = (
                is_portal and 
                is_owner and 
                note.state in ('draft', 'rejected')
            )
            note.can_submit = (
                is_portal and 
                is_owner and 
                note.state == 'draft'
            )
    
    def action_submit(self):
        """Submit handover note for approval"""
        if not self.can_submit:
            raise UserError(_("You cannot submit this handover note"))
        
        if not self.attachment_ids:
            raise ValidationError(_(
                "At least one attachment is required to submit handover note"
            ))
        
        self.state = 'submitted'
        
        # Notify manager
        manager = self.task_id.project_id.user_id
        if manager:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=manager.id,
                note=_('Handover note submitted for task: %s') % self.task_id.name
            )
        
        # Update task stage
        waiting_stage = self.env['project.task.type'].search([
            ('name', '=', 'Waiting Handover Review')
        ], limit=1)
        if waiting_stage:
            self.task_id.stage_id = waiting_stage
        
        self.message_post(
            body=_("Handover note submitted for approval"),
            subtype_xmlid='mail.mt_comment'
        )
    
    def action_approve(self):
        """Manager approves handover note"""
        if not self.env.user.has_group('project.group_project_manager'):
            raise UserError(_("Only project managers can approve handover notes"))
        
        self.state = 'approved'
        self.approved_by_id = self.env.user.id
        self.approved_date = fields.Datetime.now()
        
        # Allow task to be closed
        self.task_id.message_post(
            body=_("Handover note approved by %s") % self.env.user.name,
            subtype_xmlid='mail.mt_comment'
        )
    
    def action_reject(self):
        """Manager rejects handover note"""
        if not self.env.user.has_group('project.group_project_manager'):
            raise UserError(_("Only project managers can reject handover notes"))
        
        if not self.manager_comment:
            raise ValidationError(_("Manager comment is required when rejecting"))
        
        self.state = 'rejected'
        self.rejected_by_id = self.env.user.id
        self.rejected_date = fields.Datetime.now()
        
        # Move task back to In Progress
        in_progress_stage = self.env['project.task.type'].search([
            ('name', '=', 'In Progress')
        ], limit=1)
        if in_progress_stage:
            self.task_id.stage_id = in_progress_stage
        
        self.message_post(
            body=_("Handover note rejected: %s") % self.manager_comment,
            subtype_xmlid='mail.mt_comment'
        )
```

### 1.3 Security Model

**File**: `security/security.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Security Groups -->
        <record id="group_portal_my_tasks_user" model="res.groups">
            <field name="name">Portal My Tasks User</field>
            <field name="category_id" ref="base.module_category_hidden"/>
            <field name="implied_ids" eval="[(4, ref('base.group_portal'))]"/>
            <field name="comment">Portal users can access their assigned tasks</field>
        </record>

        <record id="group_portal_my_tasks_manager" model="res.groups">
            <field name="name">Portal My Tasks Manager</field>
            <field name="category_id" ref="base.module_category_hidden"/>
            <field name="implied_ids" eval="[(4, ref('project.group_project_manager'))]"/>
            <field name="comment">Managers can approve handover notes and manage portal assignments</field>
        </record>

        <!-- Record Rules for Portal Users -->
        <!-- Portal users can only see their assigned tasks -->
        <record id="rule_project_task_portal" model="ir.rule">
            <field name="name">Portal: Own Tasks Only</field>
            <field name="model_id" ref="project.model_project_task"/>
            <field name="domain_force">[
                '|',
                ('portal_assignee_id', '=', user.partner_id.id),
                ('portal_assignee_ids', 'in', [user.partner_id.id])
            ]</field>
            <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="False"/>
            <field name="perm_unlink" eval="False"/>
        </record>

        <!-- Portal users can only update specific fields -->
        <record id="rule_project_task_portal_write" model="ir.rule">
            <field name="name">Portal: Limited Write Access</field>
            <field name="model_id" ref="project.model_project_task"/>
            <field name="domain_force">[
                '|',
                ('portal_assignee_id', '=', user.partner_id.id),
                ('portal_assignee_ids', 'in', [user.partner_id.id])
            ]</field>
            <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="False"/>
            <field name="perm_unlink" eval="False"/>
        </record>

        <!-- Portal users can create handover notes for their tasks -->
        <record id="rule_handover_note_portal" model="ir.rule">
            <field name="name">Portal: Own Handover Notes</field>
            <field name="model_id" ref="model_project_handover_note"/>
            <field name="domain_force">[
                ('submitted_by_partner_id', '=', user.partner_id.id)
            ]</field>
            <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="False"/>
        </record>
    </data>
</odoo>
```

**File**: `security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_project_task_portal,project.task.portal,project.model_project_task,base.group_portal,1,1,0,0
access_handover_note_portal,handover.note.portal,model_project_handover_note,base.group_portal,1,1,1,0
access_handover_note_manager,handover.note.manager,model_project_handover_note,project.group_project_manager,1,1,1,1
```

---

## 🎨 Phase 2: Portal UX - "My Tasks" Workspace

### 2.1 Portal Menu Structure

**File**: `data/portal_menu_data.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Portal Menu Item -->
        <menuitem id="menu_portal_my_tasks"
                  name="My Tasks"
                  parent="portal.portal_menu"
                  action="action_portal_my_tasks"
                  sequence="10"/>
    </data>
</odoo>
```

### 2.2 Portal Controllers

**File**: `controllers/portal_my_tasks.py`

```python
# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class PortalMyTasks(CustomerPortal):
    
    def _prepare_portal_layout_values(self):
        """Add task count to portal dashboard"""
        values = super()._prepare_portal_layout_values()
        
        if request.env.user.has_group('base.group_portal'):
            Task = request.env['project.task']
            partner = request.env.user.partner_id
            
            # Count tasks
            task_count = Task.search_count([
                '|',
                ('portal_assignee_id', '=', partner.id),
                ('portal_assignee_ids', 'in', [partner.id])
            ])
            
            values['task_count'] = task_count
        
        return values
    
    @http.route(['/my/tasks', '/my/tasks/page/<int:page>'], 
                type='http', auth="user", website=True)
    def portal_my_tasks(self, page=1, sortby=None, filterby=None, **kw):
        """Portal task list page"""
        if not request.env.user.has_group('base.group_portal'):
            return request.redirect('/my')
        
        Task = request.env['project.task']
        partner = request.env.user.partner_id
        
        # Domain: only assigned tasks
        domain = [
            '|',
            ('portal_assignee_id', '=', partner.id),
            ('portal_assignee_ids', 'in', [partner.id])
        ]
        
        # Filters
        filter_options = {
            'all': {'label': 'All Tasks', 'domain': domain},
            'in_progress': {
                'label': 'In Progress',
                'domain': domain + [('stage_id.name', '=', 'In Progress')]
            },
            'waiting': {
                'label': 'Waiting Approval',
                'domain': domain + [('stage_id.name', '=', 'Waiting Handover Review')]
            },
            'overdue': {
                'label': 'Overdue',
                'domain': domain + [('date_deadline', '<', fields.Date.today())]
            },
        }
        
        filterby = filterby or 'all'
        domain = filter_options[filterby]['domain']
        
        # Sorting
        sort_options = {
            'date': {'label': 'Due Date', 'order': 'date_deadline asc'},
            'priority': {'label': 'Priority', 'order': 'priority desc'},
            'name': {'label': 'Name', 'order': 'name asc'},
        }
        
        sortby = sortby or 'date'
        order = sort_options[sortby]['order']
        
        # Paging
        task_count = Task.search_count(domain)
        pager = request.website.pager(
            url='/my/tasks',
            url_args={'sortby': sortby, 'filterby': filterby},
            total=task_count,
            page=page,
            step=20
        )
        
        tasks = Task.search(domain, order=order, limit=20, offset=pager['offset'])
        
        values = {
            'tasks': tasks,
            'page_name': 'my_tasks',
            'pager': pager,
            'sortby': sortby,
            'filterby': filterby,
            'sort_options': sort_options,
            'filter_options': filter_options,
        }
        
        return request.render('portal_my_tasks.portal_my_tasks', values)
    
    @http.route(['/my/tasks/<int:task_id>'], type='http', auth="user", website=True)
    def portal_task_detail(self, task_id, **kw):
        """Portal task detail page"""
        if not request.env.user.has_group('base.group_portal'):
            return request.redirect('/my')
        
        task = request.env['project.task'].browse(task_id)
        partner = request.env.user.partner_id
        
        # Security check
        if (task.portal_assignee_id != partner and 
            partner not in task.portal_assignee_ids):
            return request.redirect('/my/tasks')
        
        # Get handover notes
        handover_notes = request.env['project.handover.note'].search([
            ('task_id', '=', task_id),
            ('submitted_by_partner_id', '=', partner.id)
        ], order='create_date desc')
        
        values = {
            'task': task,
            'handover_notes': handover_notes,
            'page_name': 'task_detail',
        }
        
        return request.render('portal_my_tasks.portal_task_detail', values)
```

### 2.3 Portal Templates

**File**: `views/portal_templates.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="portal_my_tasks" name="My Tasks">
        <t t-call="portal.portal_layout">
            <t t-set="title">My Tasks</t>
            <div class="container mt-3">
                <div class="row">
                    <div class="col-12">
                        <h2>My Tasks</h2>
                        
                        <!-- Filters -->
                        <div class="btn-group mb-3" role="group">
                            <t t-foreach="filter_options" t-as="filter_option">
                                <a t-attf-href="/my/tasks?filterby={{filter_option[0]}}&amp;sortby={{sortby}}"
                                   t-attf-class="btn btn-sm #{filter_option[0] == filterby ? 'btn-primary' : 'btn-outline-primary'}">
                                    <t t-esc="filter_option[1]['label']"/>
                                </a>
                            </t>
                        </div>
                        
                        <!-- Sort Options -->
                        <div class="float-right">
                            <select class="form-control form-control-sm" 
                                    onchange="window.location.href='/my/tasks?sortby='+this.value+'&amp;filterby={{filterby}}'">
                                <t t-foreach="sort_options" t-as="sort_option">
                                    <option t-att-value="sort_option[0]" 
                                            t-att-selected="sort_option[0] == sortby">
                                        <t t-esc="sort_option[1]['label']"/>
                                    </option>
                                </t>
                            </select>
                        </div>
                        
                        <!-- Task List -->
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Task</th>
                                        <th>Project</th>
                                        <th>Stage</th>
                                        <th>Due Date</th>
                                        <th>Priority</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <t t-foreach="tasks" t-as="task">
                                        <tr>
                                            <td>
                                                <a t-attf-href="/my/tasks/{{task.id}}">
                                                    <t t-esc="task.name"/>
                                                </a>
                                            </td>
                                            <td><t t-esc="task.project_id.name"/></td>
                                            <td><t t-esc="task.stage_id.name"/></td>
                                            <td>
                                                <t t-if="task.date_deadline">
                                                    <t t-esc="task.date_deadline"/>
                                                </t>
                                                <t t-else="">-</t>
                                            </td>
                                            <td>
                                                <span t-attf-class="badge badge-#{task.priority == '1' ? 'danger' : task.priority == '2' ? 'warning' : 'info'}">
                                                    <t t-esc="task.priority == '1' ? 'High' : task.priority == '2' ? 'Medium' : 'Low'"/>
                                                </span>
                                            </td>
                                            <td>
                                                <a t-attf-href="/my/tasks/{{task.id}}" 
                                                   class="btn btn-sm btn-primary">View</a>
                                            </td>
                                        </tr>
                                    </t>
                                </tbody>
                            </table>
                        </div>
                        
                        <!-- Pager -->
                        <t t-raw="pager"/>
                    </div>
                </div>
            </div>
        </t>
    </template>

    <template id="portal_task_detail" name="Task Detail">
        <t t-call="portal.portal_layout">
            <t t-set="title" t-esc="task.name"/>
            <div class="container mt-3">
                <div class="row">
                    <div class="col-12">
                        <h2><t t-esc="task.name"/></h2>
                        
                        <!-- Task Info -->
                        <div class="card mb-3">
                            <div class="card-body">
                                <h5>Task Information</h5>
                                <p><strong>Project:</strong> <t t-esc="task.project_id.name"/></p>
                                <p><strong>Stage:</strong> <t t-esc="task.stage_id.name"/></p>
                                <p><strong>Due Date:</strong> 
                                    <t t-if="task.date_deadline">
                                        <t t-esc="task.date_deadline"/>
                                    </t>
                                    <t t-else="">Not set</t>
                                </p>
                                <p><strong>Priority:</strong> 
                                    <span t-attf-class="badge badge-#{task.priority == '1' ? 'danger' : task.priority == '2' ? 'warning' : 'info'}">
                                        <t t-esc="task.priority == '1' ? 'High' : task.priority == '2' ? 'Medium' : 'Low'"/>
                                    </span>
                                </p>
                                <div t-raw="task.description"/>
                            </div>
                        </div>
                        
                        <!-- Actions -->
                        <div class="card mb-3">
                            <div class="card-body">
                                <h5>Actions</h5>
                                <a href="#" class="btn btn-primary" data-toggle="modal" 
                                   data-target="#postUpdateModal">Post Update</a>
                                <a href="#" class="btn btn-secondary" data-toggle="modal" 
                                   data-target="#changeStatusModal">Change Status</a>
                                <a t-attf-href="/my/tasks/{{task.id}}/handover/new" 
                                   class="btn btn-success">Submit Handover Note</a>
                            </div>
                        </div>
                        
                        <!-- Handover Notes -->
                        <div class="card mb-3">
                            <div class="card-body">
                                <h5>Handover Notes</h5>
                                <t t-if="handover_notes">
                                    <ul class="list-group">
                                        <t t-foreach="handover_notes" t-as="note">
                                            <li class="list-group-item">
                                                <strong>Version <t t-esc="note.version"/></strong> - 
                                                <t t-esc="note.state"/>
                                                <t t-if="note.state == 'approved'">
                                                    <span class="badge badge-success">Approved</span>
                                                </t>
                                                <t t-if="note.state == 'rejected'">
                                                    <span class="badge badge-danger">Rejected</span>
                                                </t>
                                            </li>
                                        </t>
                                    </ul>
                                </t>
                                <t t-else="">
                                    <p>No handover notes submitted yet.</p>
                                </t>
                            </div>
                        </div>
                        
                        <!-- Chatter -->
                        <div class="card">
                            <div class="card-body">
                                <h5>Activity Feed</h5>
                                <div t-raw="task.message_ids"/>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </t>
    </template>
</odoo>
```

---

## 📝 Phase 3: Handover Notes Workflow

### 3.1 Handover Submission Controller

**File**: `controllers/handover_controller.py`

```python
# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError

class HandoverController(http.Controller):
    
    @http.route(['/my/tasks/<int:task_id>/handover/new'],
                type='http', auth="user", website=True, methods=['GET', 'POST'])
    def handover_note_form(self, task_id, **kw):
        """Handover note submission form"""
        if not request.env.user.has_group('base.group_portal'):
            return request.redirect('/my')
        
        task = request.env['project.task'].browse(task_id)
        partner = request.env.user.partner_id
        
        # Security check
        if (task.portal_assignee_id != partner and 
            partner not in task.portal_assignee_ids):
            return request.redirect('/my/tasks')
        
        if http.request.httprequest.method == 'POST':
            # Create handover note
            HandoverNote = request.env['project.handover.note']
            
            try:
                note = HandoverNote.create({
                    'task_id': task_id,
                    'submitted_by_partner_id': partner.id,
                    'content': kw.get('content', ''),
                    'state': 'draft',
                })
                
                # Handle file uploads
                files = http.request.httprequest.files.getlist('attachments')
                for file in files:
                    if file.filename:
                        attachment = request.env['ir.attachment'].create({
                            'name': file.filename,
                            'datas': file.read().encode('base64'),
                            'res_model': 'project.handover.note',
                            'res_id': note.id,
                        })
                        note.attachment_ids = [(4, attachment.id)]
                
                # Submit for approval
                note.action_submit()
                
                return request.redirect(f'/my/tasks/{task_id}?submitted=1')
            
            except ValidationError as e:
                return request.render('portal_my_tasks.handover_note_form', {
                    'task': task,
                    'error': str(e),
                    'content': kw.get('content', ''),
                })
        
        return request.render('portal_my_tasks.handover_note_form', {
            'task': task,
        })
```

### 3.2 Handover Form Template

**File**: `views/portal_templates.xml` (add to existing file)

```xml
<template id="handover_note_form" name="Submit Handover Note">
    <t t-call="portal.portal_layout">
        <t t-set="title">Submit Handover Note</t>
        <div class="container mt-3">
            <div class="row">
                <div class="col-12">
                    <h2>Submit Handover Note</h2>
                    <p><strong>Task:</strong> <t t-esc="task.name"/></p>
                    
                    <t t-if="error">
                        <div class="alert alert-danger" role="alert">
                            <t t-esc="error"/>
                        </div>
                    </t>
                    
                    <form t-attf-action="/my/tasks/{{task.id}}/handover/new" 
                          method="post" enctype="multipart/form-data">
                        <div class="form-group">
                            <label for="content">Handover Content *</label>
                            <textarea class="form-control" 
                                      id="content" 
                                      name="content" 
                                      rows="10" 
                                      required="required"
                                      t-esc="content or ''"/>
                        </div>
                        
                        <div class="form-group">
                            <label for="attachments">Attachments *</label>
                            <input type="file" 
                                   class="form-control-file" 
                                   id="attachments" 
                                   name="attachments" 
                                   multiple="multiple" 
                                   required="required"/>
                            <small class="form-text text-muted">
                                At least one attachment is required. 
                                You can select multiple files.
                            </small>
                        </div>
                        
                        <button type="submit" class="btn btn-primary">Submit for Approval</button>
                        <a t-attf-href="/my/tasks/{{task.id}}" class="btn btn-secondary">Cancel</a>
                    </form>
                </div>
            </div>
        </div>
    </t>
</template>
```

---

## 🔐 Phase 4: Project Sharing Strategy

### 4.1 Project Sharing Integration

Extend project sharing to work with portal assignments:

**File**: `models/project_project.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProjectProject(models.Model):
    _inherit = 'project.project'
    
    portal_collaborator_ids = fields.Many2many(
        'res.partner',
        'project_portal_collaborator_rel',
        string='Portal Collaborators',
        help='Portal users who can view all tasks in this project'
    )
    
    def action_share_portal(self):
        """Action to share project with portal users"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Share Project with Portal Users',
            'res_model': 'project.share.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_project_id': self.id,
            }
        }
```

---

## 📊 Phase 5: Manager Reporting & Dashboards

### 5.1 Manager Views

**File**: `views/task_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Extend task form view -->
        <record id="view_task_form_portal_extension" model="ir.ui.view">
            <field name="name">project.task.form.portal.extension</field>
            <field name="model">project.task</field>
            <field name="inherit_id" ref="project.view_task_form2"/>
            <field name="arch" type="xml">
                <xpath expr="//field[@name='user_ids']" position="after">
                    <field name="portal_assignee_id"/>
                    <field name="portal_assignee_ids" widget="many2many_tags"/>
                    <field name="employee_id"/>
                    <field name="requires_handover"/>
                    <field name="approved_handover_exists"/>
                </xpath>
            </field>
        </record>

        <!-- Handover Notes Tree View -->
        <record id="view_handover_note_tree" model="ir.ui.view">
            <field name="name">handover.note.tree</field>
            <field name="model">project.handover.note</field>
            <field name="arch" type="xml">
                <tree>
                    <field name="name"/>
                    <field name="task_id"/>
                    <field name="submitted_by_employee_id"/>
                    <field name="version"/>
                    <field name="state" widget="badge" 
                           decoration-success="state == 'approved'"
                           decoration-danger="state == 'rejected'"
                           decoration-info="state == 'submitted'"/>
                    <field name="create_date"/>
                </tree>
            </field>
        </record>

        <!-- Handover Notes Form View -->
        <record id="view_handover_note_form" model="ir.ui.view">
            <field name="name">handover.note.form</field>
            <field name="model">project.handover.note</field>
            <field name="arch" type="xml">
                <form>
                    <header>
                        <button name="action_approve" 
                                type="object" 
                                string="Approve"
                                class="oe_highlight"
                                attrs="{'invisible': [('state', '!=', 'submitted')]}"/>
                        <button name="action_reject" 
                                type="object" 
                                string="Reject"
                                attrs="{'invisible': [('state', '!=', 'submitted')]}"/>
                    </header>
                    <sheet>
                        <group>
                            <group>
                                <field name="name"/>
                                <field name="task_id"/>
                                <field name="submitted_by_employee_id"/>
                                <field name="version"/>
                                <field name="state"/>
                            </group>
                            <group>
                                <field name="approved_by_id" 
                                       attrs="{'readonly': [('state', '!=', 'approved')]}"/>
                                <field name="approved_date" 
                                       attrs="{'readonly': [('state', '!=', 'approved')]}"/>
                                <field name="rejected_by_id" 
                                       attrs="{'readonly': [('state', '!=', 'rejected')]}"/>
                                <field name="rejected_date" 
                                       attrs="{'readonly': [('state', '!=', 'rejected')]}"/>
                            </group>
                        </group>
                        <group>
                            <field name="content" widget="html"/>
                        </group>
                        <group>
                            <field name="attachment_ids" widget="many2many_binary"/>
                        </group>
                        <group>
                            <field name="manager_comment" 
                                   attrs="{'required': [('state', '=', 'rejected')]}"/>
                        </group>
                    </sheet>
                    <chatter/>
                </form>
            </field>
        </record>

        <!-- Handover Notes Action -->
        <record id="action_handover_notes" model="ir.actions.act_window">
            <field name="name">Handover Notes</field>
            <field name="res_model">project.handover.note</field>
            <field name="view_mode">tree,form</field>
            <field name="domain">[]</field>
            <field name="context">{}</field>
        </record>

        <!-- Menu Item -->
        <menuitem id="menu_handover_notes"
                  name="Handover Notes"
                  parent="project.menu_main_pm"
                  action="action_handover_notes"
                  sequence="50"/>
    </data>
</odoo>
```

### 5.2 Reporting Views

**File**: `views/reporting_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Task by Stage Pivot -->
        <record id="view_task_by_stage_pivot" model="ir.ui.view">
            <field name="name">Tasks by Stage (Portal)</field>
            <field name="model">project.task</field>
            <field name="arch" type="xml">
                <pivot>
                    <field name="stage_id" type="row"/>
                    <field name="employee_id" type="col"/>
                    <field name="id" type="measure"/>
                </pivot>
            </field>
        </record>

        <!-- Handover Cycle Time Graph -->
        <record id="view_handover_cycle_time" model="ir.ui.view">
            <field name="name">Handover Cycle Time</field>
            <field name="model">project.handover.note</field>
            <field name="arch" type="xml">
                <graph type="bar">
                    <field name="submitted_by_employee_id" type="row"/>
                    <field name="create_date" type="measure"/>
                    <field name="approved_date" type="measure"/>
                </graph>
            </field>
        </record>
    </data>
</odoo>
```

---

## ✅ Phase 6: QA, Rollout & Controls

### 6.1 Test Scenarios

#### Acceptance Criteria

1. **Portal Access Control**
   - ✅ Portal user sees ONLY their assigned tasks
   - ✅ Portal user cannot access other users' tasks
   - ✅ Portal user cannot access backend/internal apps
   - ✅ Portal user cannot create new tasks

2. **Task Management**
   - ✅ Portal user can post updates to assigned tasks
   - ✅ Portal user can change status within allowed stages
   - ✅ Portal user can view task details, attachments, chatter

3. **Handover Workflow**
   - ✅ Portal user can create handover note for assigned task
   - ✅ Portal user can upload attachments
   - ✅ Manager receives notification on submission
   - ✅ Manager can approve/reject with comments
   - ✅ Task cannot be closed without approved handover (if required)

4. **Security**
   - ✅ Record rules prevent data leakage
   - ✅ Portal users cannot bypass security
   - ✅ Internal users maintain full access

### 6.2 Rollout Plan

#### Phase 6.2.1: Pilot (Week 1-2)
- Select 3-5 employees for pilot
- Create portal users for pilot group
- Assign test tasks
- Monitor security logs
- Gather feedback

#### Phase 6.2.2: Security Hardening (Week 3)
- Review access logs
- Tighten record rules if needed
- Fix any security gaps
- Document lessons learned

#### Phase 6.2.3: Full Rollout (Week 4+)
- Create portal users for all employees
- Migrate existing task assignments
- Train employees on portal usage
- Train managers on approval workflow
- Monitor adoption and support

### 6.3 Controls & Monitoring

#### Key Metrics
- Number of portal users
- Tasks assigned per employee
- Handover submission rate
- Approval cycle time
- Security incidents (should be zero)

#### Monitoring Queries
```sql
-- Portal user activity
SELECT 
    u.login,
    COUNT(t.id) as tasks_assigned,
    COUNT(h.id) as handovers_submitted
FROM res_users u
JOIN res_partner p ON u.partner_id = p.id
LEFT JOIN project_task t ON t.portal_assignee_id = p.id
LEFT JOIN project_handover_note h ON h.submitted_by_partner_id = p.id
WHERE u.has_group('base.group_portal')
GROUP BY u.login;

-- Handover approval cycle time
SELECT 
    h.name,
    h.create_date as submitted,
    h.approved_date,
    EXTRACT(EPOCH FROM (h.approved_date - h.create_date))/3600 as hours_to_approve
FROM project_handover_note h
WHERE h.state = 'approved';
```

---

## 📦 Module Manifest

**File**: `__manifest__.py`

```python
# -*- coding: utf-8 -*-
{
    'name': 'Portal My Tasks',
    'version': '18.0.1.0.0',
    'category': 'Project',
    'summary': 'Portal workspace for employees to manage assigned tasks and submit handover notes',
    'description': """
Portal My Tasks Module
======================

This module enables employees to operate as Portal users with a dedicated 
"My Tasks" workspace. Key features:

* Portal users see only their assigned tasks
* Task updates and status changes from portal
* Handover note submission workflow
* Manager approval process
* Full accountability and audit trail

Benefits:
* Reduces licensing costs (Portal users are free)
* Maintains full employee accountability
* Controlled workflow with approval gates
* No backend access for employees
    """,
    'author': 'Sabry Youssef',
    'website': 'https://github.com/sabryyoussef',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'portal',
        'project',
        'hr',
        'mail',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/portal_menu_data.xml',
        'data/sequence_data.xml',
        
        # Views
        'views/portal_templates.xml',
        'views/task_views.xml',
        'views/handover_views.xml',
        'views/reporting_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'portal_my_tasks/static/src/css/portal_my_tasks.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'sequence': 10,
}
```

---

## 🚨 Risks & Mitigation

### Risk 1: Security Data Leakage
**Mitigation**: 
- Comprehensive record rules testing
- Regular security audits
- Portal user access logs monitoring

### Risk 2: Portal UX Limitations
**Mitigation**:
- Accept lighter UX vs backend
- Focus on essential features only
- Gather user feedback for improvements

### Risk 3: License Compliance
**Mitigation**:
- Verify with Odoo support before rollout
- Document approach in internal policy
- Regular compliance reviews

### Risk 4: Employee Adoption
**Mitigation**:
- Clear training materials
- Responsive support during rollout
- Gather feedback and iterate

---

## 📚 Implementation Backlog

### Epic 1: Foundation (Week 1)
- [ ] Create module structure
- [ ] Implement data models
- [ ] Set up security groups and rules
- [ ] Create access rights

### Epic 2: Portal UX (Week 2)
- [ ] Build portal controllers
- [ ] Create portal templates
- [ ] Implement task list view
- [ ] Implement task detail view

### Epic 3: Handover Workflow (Week 3)
- [ ] Handover note model
- [ ] Submission controller
- [ ] Approval workflow
- [ ] Task closure enforcement

### Epic 4: Manager Tools (Week 4)
- [ ] Manager views
- [ ] Reporting dashboards
- [ ] Approval interface
- [ ] Analytics

### Epic 5: Testing & Rollout (Week 5-6)
- [ ] Unit tests
- [ ] Integration tests
- [ ] Security testing
- [ ] Pilot rollout
- [ ] Full rollout

---

## 📖 References

- [Odoo Portal Documentation](https://www.odoo.com/documentation/15.0/uk/applications/general/users/portal.html)
- [Odoo Security Documentation](https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html)
- [Odoo Project Sharing](https://www.odoo.com/documentation/13.0/applications/services/project/overview/share.html)
- [Odoo Chatter Documentation](https://www.odoo.com/documentation/19.0/applications/productivity/discuss/chatter.html)

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-17  
**Status**: Ready for Implementation
