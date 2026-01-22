# Developer Decisions: Employee Accountability Implementation

## Overview

This document captures the **final decisions** for implementing the shared-user architecture with full employee accountability.

---

## ⚠️ Important Architecture Change (January 2026)

**Odoo Constraint:** Odoo 18 strictly enforces that each employee can only be linked to ONE user account. This cannot be overridden.

**Solution:** Instead of linking multiple employees to one user (blocked by Odoo), we use a **"Selectable Employees"** approach:

1. The shared user (`user.dept.ops`) is **NOT linked** to any employees via the standard `user_id` field
2. Employees have a Many2many field `selectable_by_user_ids` listing which users can select them
3. Users have an inverse field `selectable_employee_ids` showing which employees they can select
4. The `employee.session.context` tracks the currently "active" employee for each user session

This approach:
- ✅ Works with Odoo's security model (no constraint violations)
- ✅ Allows multiple employees to be selectable by one shared user
- ✅ Maintains full accountability via session tracking
- ✅ Supports PIN verification per employee

---

## Core Decision: Active Employee Context (Session-Based)

**Selected Approach:** Use **Session-based Active Employee** as the default UX, plus **mandatory employee stamping** on critical actions.

### How It Works:

1. When someone logs in as `user.dept.ops`, they must **choose who they are today** (Ahmed / Fatima / Omar…)
2. The system stores `active_employee_id` in the **server session** (not cookie-only)
3. Every relevant create/write action automatically stamps:
   - `performed_by_employee_id`
   - and optionally `performed_by_user_id` (always `user.dept.ops` in your case, but still useful)
4. Add a top-bar switcher: **"You are: Ahmed ▼ (Switch)"**

### Security Add-on (Strongly Advised):

- Require a **PIN** (or password) per employee when selecting/switching employee
- Otherwise anyone can select "Sara" and act as manager, which is a governance disaster

---

## The Clean Story Flow

### Monday 9:00 AM — Sara Creates the Project

Sara logs in using `admin.dept.ops`.

Because she is a manager, she can **assign work to employees** directly, not just to the shared user.

She creates project: **"Trade License Renewal - ABC Trading LLC"** from template, which generates 5 tasks.

Right after tasks are created, Sara sees a lightweight assignment panel:

| Task | Assigned Employee |
|------|-------------------|
| Task 1 - Collect client documents | Ahmed |
| Task 2 - Prepare application | Fatima |
| Task 3 - Submit to authority | Omar |
| Task 4 - Follow up on approval | Layla |
| Task 5 - Deliver license to client | Hassan |

She clicks **Confirm**. Now every task has:
- `responsible_employee_id`
- and optionally `responsible_user_id` (still `user.dept.ops` if needed for access)

---

### Monday 9:30 AM — Ahmed Starts Task 1

Ahmed logs in using the shared user `user.dept.ops`.

Immediately after login, the system asks:
**"Who are you?"**

Ahmed selects **Ahmed** and enters his PIN.

Now the header shows: **Active Employee: Ahmed**

Ahmed opens Task 1 and logs **2 hours**.
The timesheet line automatically gets:
- `employee_id = Ahmed`
- `create_uid = user.dept.ops`
- `performed_by_employee_id = Ahmed` (explicit audit beyond Odoo defaults)

---

### Monday 2:00 PM — Ahmed Completes a Checkpoint

Ahmed clicks "Checkpoint Complete".
The checkpoint record stores:
- `completed_by_employee_id = Ahmed`
- `completed_date`
- System logs it in chatter as an auditable note

---

### Tuesday 10:00 AM — Fatima Requests Sick Leave

Fatima logs in with the same shared user.
She selects **Fatima** in the "Who are you?" step.

When she opens Leave Request, the form defaults to:
- `employee_id = Fatima`

No guessing. No dropdown hunting. No wrong employee requests.

---

### Tuesday 11:00 AM — Sara Reviews Performance

Sara opens the Ops dashboard and filters by employee:
- Tasks completed by Ahmed (this month)
- Hours logged by Fatima (this month)
- Overdue tasks by responsible employee

Because everything is stamped with `employee_id`, the reporting is straightforward.

---

### Wednesday — Ahmed Hands Over Task 3 to Omar

Ahmed (active employee: Ahmed) opens Task 3 → clicks **Handover**:
- Transfer to: Omar
- Reason: Vacation next week
- Notes: "Application draft ready, awaiting client signature."

System creates a handover log entry and updates:
- `responsible_employee_id = Omar`

And preserves history:
- `handover_history_ids`: from Ahmed → Omar, reason, timestamp

---

### End of Month — Bonuses

A KPI snapshot job runs nightly (or weekly) and aggregates:
- Tasks completed per employee
- Hours logged per employee
- Checkpoints completed per employee

Sara sees a single KPI sheet per employee and exports it.

---

## Gap-by-Gap Answers (Final Decisions)

### GAP 1 — Assign Tasks to Employee from Template

**Decision:** Make `responsible_employee_id` **mandatory** on tasks created from template (manager-facing UI).

**Implementation:**
- Provide dropdown filtered by:
  - Project department, or
  - Allowed employees list, or
  - Employee job/role (optional)

**Rationale:** If it's optional, you'll end up with unassigned work and no accountability.

**Status:** ✅ Decided

---

### GAP 2 — Timesheets: Who Logged the Hours?

**Decision:** Use **Active Employee Context** to default `employee_id` on timesheets.

**Implementation:**
- Allow override only if user has manager permission

**Rationale:** Timesheets must be attributable. Employee selector "every time" is annoying; session default is clean.

**Status:** ✅ Decided

---

### GAP 3 — Checkpoints: Who Completed It?

**Decision:** Add `completed_by_employee_id` (mandatory on completion action).

**Implementation:**
- Automatically filled from active employee context

**Rationale:** Completion is a performance signal. Must be stamped.

**Status:** ✅ Decided

---

### GAP 4 — Leave Request Default Employee

**Decision:** Default `employee_id` from Active Employee Context.

**Implementation:**
- No dropdown for normal employees
- Managers can switch employee only if they have HR permission

**Rationale:** Prevent wrong requests and avoid accidental misuse.

**Status:** ✅ Decided

---

### GAP 5 — Reports by Employee Not User

**Decision:** Extend/enable reporting with employee dimensions.

**Implementation:**
- Tasks: pivot by `responsible_employee_id`, `completed_by_employee_id`
- Timesheets: already employee-based (in most setups)
- Checkpoints: by `completed_by_employee_id`

**Recommendation:** Build **one Ops dashboard** (custom) rather than hacking many standard reports.

**Status:** ✅ Decided

---

### GAP 6 — Task Handover Tracking

**Decision:** Implement a handover model (or reuse `project_handover_notes` if it already exists).

**Implementation:**
- `from_employee_id`
- `to_employee_id`
- `reason`
- `handover_date`
- `notes`
- Keep current responsibility in `responsible_employee_id`

**Rationale:** You need both current owner and history for audit.

**Status:** ✅ Decided

---

### GAP 7 — KPI Aggregation

**Decision:** Use a scheduled job.

**Implementation:**
- **Nightly** is the sweet spot (low noise, fresh enough)
- Keep a manual "Recompute KPI" button for admin/manager
- Model: `hr.employee.kpi.snapshot` with period fields (day/week/month) and computed totals

**Status:** ✅ Decided

---

## Summary Table

| Gap # | Description | Decision | Status |
|-------|-------------|----------|--------|
| 1 | Assign task to employee from template | Mandatory `responsible_employee_id` with department filter | ✅ Implemented |
| 2 | Identify employee when logging timesheet | Active Employee Context default | ✅ Implemented |
| 3 | Record who completed checkpoint | `completed_by_employee_id` auto-filled from context | ⬜ Pending |
| 4 | Default employee on leave request | Active Employee Context default | ⬜ Pending |
| 5 | Reports by employee not user | Custom Ops dashboard with employee dimensions | ⬜ Pending |
| 6 | Task handover tracking | Handover model with history | ⬜ Pending |
| 7 | KPI aggregation | Nightly cron + manual recompute button | ⬜ Pending |

---

## Core Technical Components Required

### 1. Active Employee Context System ✅ IMPLEMENTED

```
Model: employee.session.context
Fields:
  - user_id (Many2one: res.users)
  - active_employee_id (Many2one: hr.employee)
  - pin_verified (Boolean)
  - session_start (Datetime)
  - session_end (Datetime)
  - ip_address (Char)
  - user_agent (Char)
  - state (Selection: active/ended/expired)
```

### 2. Employee PIN Security ✅ IMPLEMENTED

```
Model: hr.employee (extend)
Fields:
  - employee_pin (Char, encrypted with salt)
  - employee_pin_salt (Char)
  - pin_required (Boolean, default=True)
  - pin_failed_attempts (Integer)
  - pin_locked_until (Datetime)
  - is_shared_user_employee (Boolean, computed)
  - shared_user_employee_ids (Many2many, computed)
```

### 3. Top-Bar Employee Switcher ⬜ PENDING

- Widget in top navbar
- Shows: "You are: Ahmed ▼ (Switch)"
- Click opens employee selector wizard with PIN verification

### 4. Task Employee Assignment ✅ IMPLEMENTED

```
Model: project.task (extend)
Fields:
  - responsible_employee_id (Many2one: hr.employee)
  - performed_by_employee_id (Many2one: hr.employee)
  - participant_employee_ids (Many2many: hr.employee)
  - responsible_employee_department_id (Many2one, related)
```

### 5. Checkpoint Completion Tracking ⬜ PENDING

```
Model: project.checkpoint (extend)
Fields:
  - completed_by_employee_id (Many2one: hr.employee)
  - completed_date (Datetime)
```

### 6. Handover History ⬜ PENDING

```
Model: project.task.handover (new or extend project_handover_notes)
Fields:
  - task_id (Many2one: project.task)
  - from_employee_id (Many2one: hr.employee)
  - to_employee_id (Many2one: hr.employee)
  - reason (Selection: vacation, workload, skill_match, other)
  - notes (Text)
  - handover_date (Datetime)
```

### 7. KPI Snapshot ⬜ PENDING

```
Model: hr.employee.kpi.snapshot
Fields:
  - employee_id (Many2one: hr.employee)
  - period_type (Selection: day, week, month, quarter, year)
  - date_from (Date)
  - date_to (Date)
  - tasks_completed (Integer)
  - tasks_overdue (Integer)
  - hours_logged (Float)
  - checkpoints_completed (Integer)
  - avg_cycle_time (Float)
```

---

## Important Warning

> **Best-practice recommendation (hard stance):** Give every employee their own Odoo user. Even if they all belong to the same department and same permissions group, each person must have a unique `res.users`.
>
> The shared-login approach described here is a **workaround** for license cost constraints. It introduces complexity and potential governance risks.
>
> **If you want this to survive real-world audits, don't skip the PIN.**

---

## Implementation Status

### ✅ Completed Components

| Component | File(s) | Status |
|-----------|---------|--------|
| Active Employee Context System | `models/employee_session_context.py` | ✅ Complete |
| Employee PIN Security | `models/hr_employee.py` | ✅ Complete |
| Shared User Support | `models/hr_employee.py`, `models/res_users.py` | ✅ Complete |
| Task Employee Assignment | `models/project_task.py` | ✅ Complete |
| Employee Select Wizard | `wizard/employee_select_wizard.py` | ✅ Complete |
| Session Cleanup Cron | `data/ir_cron.xml` | ✅ Complete |
| Views & Forms | `views/*.xml` | ✅ Complete |
| Security Rules | `security/` | ✅ Complete |

### Implemented Features

1. **Employee Session Context** (`employee.session.context`)
   - Session tracking with start/end times
   - PIN verification flag
   - IP address and user agent logging
   - Automatic session ending on new session creation
   - State management (active/ended/expired)

2. **Employee PIN Security** (`hr.employee` extension)
   - Encrypted PIN storage with salt
   - PIN verification with lockout protection
   - Failed attempt tracking
   - Configurable PIN requirement per employee

3. **Shared User Support**
   - Removed unique user constraint on employees
   - `is_shared_user_employee` computed field
   - `shared_user_employee_ids` relationship
   - Multiple employees can share one `res.users` account

4. **Task Employee Assignment** (`project.task` extension)
   - `responsible_employee_id` - who is assigned
   - `performed_by_employee_id` - who actually did the work
   - `participant_employee_ids` - additional participants
   - Auto-fill from active employee context on create/write
   - "Set Responsible to Me" action
   - "Add Me as Participant" action

5. **Employee Select Wizard**
   - Employee selection dropdown filtered by user
   - PIN verification when required
   - Display notification on successful selection

6. **res.users Extensions**
   - `get_active_employee()` helper method
   - `set_active_employee()` helper method
   - `is_shared_user` computed field
   - `shared_employee_count` computed field

---

## Next Steps

1. ✅ Decisions documented
2. ✅ Create technical blueprint (models, fields, hooks, menus)
3. ✅ Design UI mockups for employee switcher
4. ✅ Implement Phase 1 - Active Employee Context
5. ✅ Implement Phase 2 - Task Employee stamping
6. ⬜ Implement Top-Bar Employee Switcher Widget (OWL component)
7. ⬜ Implement Checkpoint completion tracking (`completed_by_employee_id`)
8. ⬜ Implement Handover History model
9. ⬜ Implement KPI Snapshots and dashboards
10. ⬜ Leave Request default employee integration
