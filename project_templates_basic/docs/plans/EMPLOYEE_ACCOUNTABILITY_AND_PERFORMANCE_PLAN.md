# Employee Accountability & Performance Plan (Project Templates Basic)

## 1. Goal

Design a **shared-user friendly** architecture where:

- You can **reduce the number of Odoo users** (one user per department + global admin + individual salespersons).
- Still have **full accountability per employee** for:
  - Task ownership and participation
  - Tagging and classification
  - Leave management
  - Commission calculation
  - KPI tracking and performance reviews
- Integrate with the existing `project_templates_basic` / `project_checkpoints_basic` / `unified_documents` workflow.

---

## 2. Current Situation (Simplified)

- ~33 employees currently mapped 1:1 to Odoo users.
- Project/task work managed mainly through:
  - `project.task` (core)
  - `project_templates_basic` (task/document templates, checklists)
  - `project_checkpoints_basic` (checkpoints & milestones)
  - `unified_documents` (document-centric workflow & subtasks)
  - `project_handover_notes` / `project_compliance` (handover and compliance flows)
- Enterprise apps available for:
  - Timesheets, KPIs (`hr_timesheet`, `sale_timesheet`, `timesheet_grid`)
  - Commission (`sale_commission`)
  - Leaves (`hr_holidays`)

Key pain point: **license cost** vs **accountability** when multiple people share the same technical user.

---

## 3. Target User / Employee Model

### 3.1 Users (access)

Reduce to something like:

- `admin` → Global system admin
- `admin.dept.sales` → Shared user for Sales team
- `admin.dept.projects` → Shared user for Project/PMO team
- `admin.dept.ops` → Shared user for Operations/Compliance
- `sales.person.X` → Individual users for sales reps with direct customer access

> All **day-to-day operations in back-office departments** happen under shared users.

### 3.2 Employees (accountability)

- Keep **one `hr.employee` per real person** (all 33).
- Each employee links to a **shared user**:
  - `employee.user_id` = shared department user
- Everything that requires **who really did what** must be tied to:
  - `employee_id` (NOT only `user_id`)

---

## 4. Functional Requirements by Topic

### 4.1 Task Assignment

**Requirement**

- Assign tasks using shared users, but also know **which employee** is responsible and who actually worked.

**Plan**

1. Extend `project.task`:
   - Add `employee_id` (primary accountable employee).
   - Add `actual_worker_ids` (Many2many to `hr.employee` via timesheets & activity logs).
2. Update:
   - Task templates to optionally store **default role/employee tags**.
   - Wizards that generate tasks from templates to:
     - Set `employee_id` based on department rules / manager choices.

### 4.2 Tagging Users / Employees

**Requirement**

- Tag people for:
  - Skills (Odoo, Python, Sales…)
  - Department
  - Role (Manager, Senior, Junior)
  - Project specialization

**Plan**

1. Use / extend `hr.employee.category` or custom `hr.employee.tag`:
   - Fields:
     - `name`
     - `category_type` (`skill`, `department`, `role`, `project`, …).
2. On `hr.employee`:
   - `employee_tag_ids` Many2many.
3. In `project_templates_basic`:
   - Allow **task templates** to specify:
     - Required tags or preferred tags for responsible employee.
   - Wizard logic:
     - When generating tasks, auto-suggest employees based on tags.

### 4.3 Leaves (Annual / Sick)

**Requirement**

- Leave requests per employee, independent from shared user.

**Plan**

1. Use standard `hr_holidays`:
   - Leaves are **already employee-based** (`employee_id`), not user-based.
2. Make sure:
   - Every real person has a proper `hr.employee`.
   - For managers:
     - Approvals visible to department admin / HR via security groups and record rules.
3. Optionally add in Mazagawy views:
   - Smart button from employee to **“Open Projects/Tasks impacted by leaves”** (optional future enhancement).

### 4.4 Commission Calculation

**Requirement**

- Calculate commissions:
  - For salespersons (individual users).
  - For other employees if needed (e.g., project bonuses).

**Plan**

1. For Sales:
   - Keep **1:1 user ↔ salesperson** where commissions matter.
   - Use Enterprise `sale_commission` standard flows.
2. For non-sales employees:
   - Add field on `hr.employee`:
     - `commission_profile_id` or link to commission rules.
   - Align project/task billing + timesheets:
     - Use `employee_id` on `account.analytic.line` to compute bonus metrics.
3. Reporting:
   - Build aggregated views by `employee_id`:
     - Sales commission from `sale_commission` tables.
     - Delivery / project bonuses based on:
       - `hours_logged`
       - `tasks_completed`
       - `milestones_reached`

### 4.5 Employee KPIs

**Requirement**

- Track performance per employee:
  - Hours
  - Tasks closed
  - Checkpoints & milestones
  - SLA / delays

**Plan**

1. New model: `hr.employee.kpi.snapshot` (or similar):
   - `employee_id`
   - `period_type` (`month`, `quarter`, `year`)
   - `date_from`, `date_to`
   - Metrics:
     - `tasks_completed`
     - `tasks_overdue`
     - `hours_logged`
     - `avg_cycle_time`
     - `checkpoints_completed`
     - `handover_completed`
2. Compute sources:
   - `project.task`:
     - `employee_id`
     - `date_deadline`, `date_end`
   - `account.analytic.line`:
     - `employee_id`, `unit_amount`
   - `project_checkpoints_basic`:
     - Completed checkpoints linked to tasks/projects.
   - `project_handover_notes`:
     - Handover actions / approvals by employee.
3. UI:
   - Employee form:
     - Smart button **“KPIs”** → list/dashboard of KPI snapshots.

### 4.6 Accountability with Shared Users

**Requirement**

> If all employees in same department use the same user, how to know **who actually worked** on a project/task?

**Plan**

Use **three layers**:

1. **Assignment Layer** (who is responsible):
   - `project.task.employee_id`
   - `project.project.manager_employee_id` (optional extension).
2. **Activity Layer** (who touched the work):
   - Timesheets: `account.analytic.line.employee_id`
   - Chatter messages: `mail.message.author_id` + implicit employee mapping.
   - Checklists & checkpoints:
     - Optional `completed_by_employee_id`.
3. **Audit Layer**:
   - Reports and kanban views showing:
     - Responsible employee.
     - Actual workers (derived from timesheets / checkpoints).
     - Department + role tags (for context).

---

## 5. Technical Design – Integration with `project_templates_basic`

### 5.1 Extend Task Template to support roles / tags

- Model: `project.task.template` (in `project_templates_basic`):
  - Add fields:
    - `role_tag_ids` (Many2many to `hr.employee.category` or `hr.employee.tag`)
    - `default_department_id` (optional, via `hr.department`)
    - `kpi_weight` (float, for KPI scoring).

**Behavior:**

- When creating tasks from a template:
  - Suggest employees in this order:
    1. Matching department + tag(s)
    2. Matching tag(s) only
    3. Fallback to department shared user (no specific employee)
- Assign:
  - `user_ids` → shared dept user
  - `employee_id` → chosen employee (if any)

### 5.2 Task Generation Wizard Changes

- Wizard: task/template selection (existing in `project_templates_basic`):
  - Add:
    - Employee selection field (optional override).
    - Filter employees by tag/department.
  - On confirmation:
    - Create tasks with correct `employee_id`.

---

## 6. Data Model Summary

### Core Fields

- `hr.employee`
  - `shared_user_id` (`res.users`)
  - `employee_tag_ids` (`hr.employee.category` / custom tag)
  - KPI fields or link to KPI snapshots.

- `project.task`
  - `employee_id` (`hr.employee`)
  - `actual_worker_ids` (Many2many via timesheets)

- `account.analytic.line` (timesheet)
  - Already has `employee_id` in Enterprise stack.

- `project.task.template`
  - `role_tag_ids`
  - `kpi_weight`

---

## 7. Implementation Phases

### Phase 1 – Foundations

1. Create **employee-tagging** mechanism.
2. Ensure all 33 employees have proper `hr.employee` records.
3. Add `employee_id` to `project.task` and expose in tree/form views.
4. Create basic **Employee KPI** model with simple metrics (tasks completed, hours).

### Phase 2 – Deep Integration

1. Integrate tags and roles into `project.task.template`.
2. Extend task generation wizards to:
   - Suggest employees.
   - Set `employee_id` automatically.
3. Link KPI metrics with:
   - Checkpoints (`project_checkpoints_basic`)
   - Handover notes
   - Unified documents subtasks.

### Phase 3 – Commission & Advanced KPIs

1. Connect to `sale_commission`:
   - Map commission to `employee_id` where relevant.
2. Build dashboards:
   - Per employee
   - Per department
   - Per role (manager vs. staff).
3. Fine-tune reports for:
   - Accountability (who did what)
   - Performance (quality, speed, volume).

---

## 8. Risks & Mitigations

- **Risk:** Confusion between `user` and `employee`.
  - **Mitigation:** Always show both in key forms; document the pattern clearly.
- **Risk:** Performance issues in KPI calculations.
  - **Mitigation:** Use periodic snapshot records instead of live heavy queries.
- **Risk:** Wrong assignment due to tag misconfiguration.
  - **Mitigation:** Start with manual override options in the wizard; log assignment decisions.

---

## 9. Success Criteria

1. Number of **billable Odoo users** significantly reduced (e.g., 33 → ~10).
2. For any project/task, you can answer:
   - Who is responsible?
   - Who actually worked on it?
   - How much time did they spend?
3. Managers can:
   - See clear KPIs per employee.
   - Approve leaves per employee even with shared users.
   - Review commission and bonuses per employee.

