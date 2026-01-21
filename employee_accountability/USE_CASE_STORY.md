# Use Case Story: Employee Accountability in Action

## Context

This document provides a live use case story to help visualize the workflow and identify implementation gaps for the shared-user architecture.

---

## Scenario: Operations Department - Daily Workflow

### Department Setup
- **Department:** Operations/Compliance
- **Users:** 
  - `admin.dept.ops` (used by Manager: Sara)
  - `user.dept.ops` (used by 9 employees: Ahmed, Fatima, Omar, Layla, Hassan, Nora, Khalid, Mona, Youssef)
- **All 10 people have `hr.employee` records**

---

## 📖 Story: License Renewal Project

### Monday 9:00 AM - Sara (Manager) Creates a Project

Sara logs in with `admin.dept.ops` and creates a new project "Trade License Renewal - ABC Trading LLC".

She uses a template from `project_templates_basic` which generates 5 tasks:
1. Collect client documents
2. Prepare application
3. Submit to authority
4. Follow up on approval
5. Deliver license to client

**🔴 GAP 1:** When Sara creates tasks from template, how does she assign each task to a specific employee (Ahmed, Fatima, etc.) if all 9 employees share the same `user.dept.ops` user?

> **Developer Question:** Do we show a dropdown of employees filtered by department? Is it mandatory or optional?

**Developer Answer:** 
```
_____________________________________________________________________
_____________________________________________________________________
_____________________________________________________________________
```

---

### Monday 9:30 AM - Ahmed Starts Working on Task 1

Ahmed logs in with `user.dept.ops` (same as Fatima, Omar, etc.). He opens the task "Collect client documents" and starts working.

He logs 2 hours on timesheet.

**🔴 GAP 2:** When Ahmed logs timesheet, how does the system know it's Ahmed and not Fatima who logged those hours? Both use `user.dept.ops`.

> **Developer Question:** Do we show employee selector when logging timesheet? Or does each employee have a "current active employee" stored in session/cookie?

**Developer Answer:** 
```
_____________________________________________________________________
_____________________________________________________________________
_____________________________________________________________________
```

---

### Monday 2:00 PM - Ahmed Completes Checkpoint

Ahmed finishes collecting documents and marks a checkpoint as complete in `project_checkpoints_basic`.

**🔴 GAP 3:** How do we record that Ahmed (not Omar) completed this checkpoint?

> **Developer Question:** Same as GAP 2 - need `completed_by_employee_id` field. How do we capture who the current employee is?

**Developer Answer:** 
```
_____________________________________________________________________
_____________________________________________________________________
_____________________________________________________________________
```

---

### Tuesday 10:00 AM - Fatima is Sick

Fatima wants to request sick leave. She needs to:
1. Log into system
2. Request leave for herself (not for Omar or Ahmed)

**✅ NO GAP:** Standard `hr_holidays` already uses `employee_id`. Fatima's employee record is linked to `user.dept.ops`, but leave request is per employee.

**🔴 GAP 4:** But wait - when Fatima logs in as `user.dept.ops`, how does the leave request form know to default to Fatima's employee record?

> **Developer Question:** Does Fatima select herself from dropdown? Or is there a "Switch Employee" mechanism?

**Developer Answer:** 
```
_____________________________________________________________________
_____________________________________________________________________
_____________________________________________________________________
```

---

### Tuesday 11:00 AM - Sara Reviews Team Performance

Sara (manager) wants to see:
- How many tasks did Ahmed complete this month?
- How many hours did Fatima log?
- Who is overdue on tasks?

**🔴 GAP 5:** Current Odoo reports filter by `user_id`. We need reports that filter by `employee_id`.

> **Developer Question:** Do we build custom dashboards/reports or extend existing ones?

**Developer Answer:** 
```
_____________________________________________________________________
_____________________________________________________________________
_____________________________________________________________________
```

---

### Wednesday - Task Handover

Ahmed is going on vacation next week. He needs to handover Task 3 "Submit to authority" to Omar.

**🔴 GAP 6:** How do we record:
- Ahmed was originally responsible
- Omar is now responsible
- Reason for handover

> **Developer Question:** Do we use `project_handover_notes` module? Do we need `previous_employee_id` field?

**Developer Answer:** 
```
_____________________________________________________________________
_____________________________________________________________________
_____________________________________________________________________
```

---

### End of Month - Commission/Bonus Calculation

Sara wants to calculate bonuses based on:
- Tasks completed per employee
- Hours logged per employee
- Checkpoints completed per employee

**🔴 GAP 7:** All data is scattered. Need aggregated KPI view per employee.

> **Developer Question:** Is `hr.employee.kpi.snapshot` calculated daily/weekly/monthly? Manually triggered or cron job?

**Developer Answer:** 
```
_____________________________________________________________________
_____________________________________________________________________
_____________________________________________________________________
```

---

## Summary of Gaps to Fill

| Gap # | Description | Question for Developer | Status |
|-------|-------------|------------------------|--------|
| 1 | Assign task to employee when creating from template | Mandatory employee selection? Dropdown filtered by dept? | ⬜ Pending |
| 2 | Identify employee when logging timesheet | Employee selector? Session-based? Cookie? | ⬜ Pending |
| 3 | Record who completed checkpoint | Add `completed_by_employee_id`? Same mechanism as #2? | ⬜ Pending |
| 4 | Default employee on leave request | Employee selector or "Switch Employee" feature? | ⬜ Pending |
| 5 | Reports by employee not user | Custom reports or extend existing? | ⬜ Pending |
| 6 | Task handover tracking | Use existing module or new field? | ⬜ Pending |
| 7 | KPI aggregation | Cron job frequency? Manual trigger? | ⬜ Pending |

---

## 🔑 Core Question for All Gaps

**How does the system know WHICH employee is currently working when multiple employees share the same user login?**

### Options:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A | **Employee Selector on each form** - User picks employee every time | Simple, explicit | Tedious, error-prone |
| B | **Session-based "Active Employee"** - User selects once at login, stored in session | Convenient, consistent | Requires logout to switch |
| C | **Browser cookie/local storage** - Remember last selected employee per browser | Persistent across sessions | Shared computers issue |
| D | **Mandatory employee field** - Every action requires explicit employee selection | Audit-friendly | Slow workflow |

**Selected Option:** 
```
_____________________________________________________________________
_____________________________________________________________________
```

**Justification:**
```
_____________________________________________________________________
_____________________________________________________________________
_____________________________________________________________________
```

---

## Next Steps

After filling the gaps above:
1. Update `EMPLOYEE_ACCOUNTABILITY_AND_PERFORMANCE_PLAN.md` with decisions
2. Create technical specifications for each gap
3. Prioritize implementation order
4. Begin Phase 1 development
