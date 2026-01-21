# Employee Accountability Module - Implementation Plan

## Overview

This document outlines the complete implementation plan for the Employee Accountability module, broken down into stages, phases, and actionable steps.

**Goal:** Reduce Odoo users from 33 → 21 while maintaining full employee accountability.

**Timeline Estimate:** 6-8 weeks (depending on team size and parallel work)

---

## Stage 1: Foundation (Week 1-2)

### Phase 1.1: Module Setup & Core Models

**Objective:** Create the base module structure and core models.

| Step | Task | Priority | Effort | Dependencies |
|------|------|----------|--------|--------------|
| 1.1.1 | Create module folder structure (models, views, security, data, wizard, static) | High | 2h | None |
| 1.1.2 | Update `__manifest__.py` with proper dependencies (hr, project, hr_holidays) | High | 1h | 1.1.1 |
| 1.1.3 | Create `hr.employee` extension model with PIN field | High | 4h | 1.1.2 |
| 1.1.4 | Create `employee.session.context` model for active employee tracking | High | 6h | 1.1.3 |
| 1.1.5 | Create security groups and access rules | High | 4h | 1.1.4 |
| 1.1.6 | Write unit tests for core models | Medium | 4h | 1.1.5 |

**Deliverables:**
- [ ] Module installable without errors
- [ ] Employee PIN field working
- [ ] Session context model storing active employee
- [ ] Basic security groups defined

---

### Phase 1.2: Employee PIN & Verification

**Objective:** Implement secure PIN system for employee identification.

| Step | Task | Priority | Effort | Dependencies |
|------|------|----------|--------|--------------|
| 1.2.1 | Add `employee_pin` field (encrypted) to `hr.employee` | High | 3h | 1.1.3 |
| 1.2.2 | Add `pin_required` boolean field with default=True | High | 1h | 1.2.1 |
| 1.2.3 | Create PIN setup wizard for employees | High | 4h | 1.2.2 |
| 1.2.4 | Create PIN verification method with rate limiting | High | 4h | 1.2.3 |
| 1.2.5 | Add "Reset PIN" functionality for managers | Medium | 3h | 1.2.4 |
| 1.2.6 | Create employee form view with PIN management tab | Medium | 2h | 1.2.5 |

**Deliverables:**
- [ ] Employees can set/change their PIN
- [ ] PIN is stored encrypted
- [ ] Managers can reset employee PINs
- [ ] Rate limiting prevents brute force

---

### Phase 1.3: Active Employee Context System

**Objective:** Build the session-based employee switching mechanism.

| Step | Task | Priority | Effort | Dependencies |
|------|------|----------|--------|--------------|
| 1.3.1 | Create `employee.session.context` model | High | 4h | 1.2.4 |
| 1.3.2 | Implement `get_active_employee()` helper method on res.users | High | 3h | 1.3.1 |
| 1.3.3 | Implement `set_active_employee()` with PIN verification | High | 4h | 1.3.2 |
| 1.3.4 | Create employee selection wizard (post-login) | High | 6h | 1.3.3 |
| 1.3.5 | Hook into login flow to trigger employee selection | High | 4h | 1.3.4 |
| 1.3.6 | Handle session timeout/cleanup | Medium | 3h | 1.3.5 |

**Deliverables:**
- [ ] After login, user is prompted to select employee
- [ ] PIN verification works
- [ ] Active employee stored in session
- [ ] Session cleanup on logout/timeout

---

## Stage 2: UI Components (Week 2-3)

### Phase 2.1: Top-Bar Employee Switcher Widget

**Objective:** Create the "You are: Ahmed ▼ (Switch)" widget in the navbar.

| Step | Task | Priority | Effort | Dependencies |
|------|------|----------|--------|--------------|
| 2.1.1 | Create OWL component for employee switcher | High | 8h | 1.3.6 |
| 2.1.2 | Style the widget (CSS) to match Odoo theme | Medium | 3h | 2.1.1 |
| 2.1.3 | Implement click handler to open switch wizard | High | 4h | 2.1.2 |
| 2.1.4 | Create switch employee wizard with PIN re-verification | High | 4h | 2.1.3 |
| 2.1.5 | Add employee avatar/photo to widget (optional) | Low | 2h | 2.1.4 |
| 2.1.6 | Test on mobile/responsive views | Medium | 2h | 2.1.5 |

**Deliverables:**
- [ ] Widget visible in top navbar
- [ ] Shows current active employee name
- [ ] Click opens switch wizard
- [ ] Responsive on all screen sizes

---

### Phase 2.2: Employee Selection Views

**Objective:** Create consistent employee selection UI across the system.

| Step | Task | Priority | Effort | Dependencies |
|------|------|----------|--------|--------------|
| 2.2.1 | Create reusable employee selection widget | High | 6h | 2.1.6 |
| 2.2.2 | Add department filter to employee dropdown | High | 3h | 2.2.1 |
| 2.2.3 | Add employee tags/skills filter (optional) | Medium | 4h | 2.2.2 |
| 2.2.4 | Create "No employee selected" warning banner | Medium | 2h | 2.2.3 |
| 2.2.5 | Add keyboard navigation support | Low | 2h | 2.2.4 |

**Deliverables:**
- [ ] Reusable employee selector component
- [ ] Filters by department and tags
- [ ] Clear warning when no employee selected

---

## Stage 3: Task & Project Integration (Week 3-4)

### Phase 3.1: Task Employee Assignment

**Objective:** Add employee tracking fields to project.task.

| Step | Task | Priority | Effort | Dependencies |
|------|------|----------|--------|--------------|
| 3.1.1 | Extend `project.task` with `responsible_employee_id` field | High | 3h | 2.2.5 |
| 3.1.2 | Extend `project.task` with `performed_by_employee_id` field | High | 2h | 3.1.1 |
| 3.1.3 | Update task form view to show employee fields | High | 3h | 3.1.2 |
| 3.1.4 | Update task tree/kanban views with employee info | High | 4h | 3.1.3 |
| 3.1.5 | Auto-fill `performed_by_employee_id` from active context | High | 3h | 3.1.4 |
| 3.1.6 | Add validation: require employee on task creation | Medium | 2h | 3.1.5 |
| 3.1.7 | Create search filters by employee | Medium | 2h | 3.1.6 |

**Deliverables:**
- [ ] Tasks have responsible employee field
- [ ] Employee auto-filled from context
- [ ] Views updated with employee info
- [ ] Search/filter by employee works

---

### Phase 3.2: Template-Based Task Assignment

**Objective:** Integrate employee assignment into task template workflow.

| Step | Task | Priority | Effort | Dependencies |
|------|------|----------|--------|--------------|
| 3.2.1 | Extend `project.task.template` with `default_employee_tag_ids` | High | 3h | 3.1.7 |
| 3.2.2 | Extend `project.task.template` with `default_department_id` | Medium | 2h | 3.2.1 |
| 3.2.3 | Update template form view with new fields | Medium | 2h | 3.2.2 |
| 3.2.4 | Modify task generation wizard to show employee assignment panel | High | 8h | 3.2.3 |
| 3.2.5 | Implement employee suggestion logic (by dept/tags) | High | 6h | 3.2.4 |
| 3.2.6 | Add bulk assignment option in wizard | Medium | 4h | 3.2.5 |

**Deliverables:**
- [ ] Templates can specify preferred employee tags/dept
- [ ] Wizard shows assignment panel after template selection
- [ ] System suggests employees based on tags
- [ ] Bulk assignment for multiple tasks

---

### Phase 3.3: Project Manager Employee Extension

**Objective:** Add employee tracking at project level.

| Step | Task | Priority | Effort | Dependencies |
|------|------|----------|--------|--------------|
| 3.3.1 | Extend `project.project` with `manager_employee_id` | Medium | 2h | 3.2.6 |
| 3.3.2 | Update project form view | Medium | 2h | 3.3.1 |
| 3.3.3 | Inherit manager employee on new tasks (optional) | Low | 3h | 3.3.2 |

**Deliverables:**
- [ ] Projects have manager employee field
- [ ] View updated

---

## Stage 4: Checkpoint & Handover Integration (Week 4-5)

### Phase 4.1: Checkpoint Employee Tracking

**Objective:** Track who completes checkpoints in project_checkpoints_basic.

| Step | Task | Priority | Effort | Dependencies |
|------|------|----------|--------|--------------|
| 4.1.1 | Extend `project.checkpoint` with `completed_by_employee_id` | High | 3h | 3.3.3 |
| 4.1.2 | Extend with `completed_date` (if not exists) | High | 1h | 4.1.1 |
| 4.1.3 | Auto-fill employee on checkpoint completion action | High | 4h | 4.1.2 |
| 4.1.4 | Update checkpoint views with employee info | Medium | 3h | 4.1.3 |
| 4.1.5 | Add chatter log on completion with employee name | Medium | 2h | 4.1.4 |
| 4.1.6 | Create search filters by completing employee | Medium | 2h | 4.1.5 |

**Deliverables:**
- [ ] Checkpoint completion tracks employee
- [ ] Auto-filled from active context
- [ ] Chatter logs completion

---

### Phase 4.2: Task Handover System

**Objective:** Implement formal handover tracking between employees.

| Step | Task | Priority | Effort | Dependencies |
|------|------|----------|--------|--------------|
| 4.2.1 | Create `project.task.handover` model | High | 4h | 4.1.6 |
| 4.2.2 | Add `handover_history_ids` One2many on `project.task` | High | 2h | 4.2.1 |
| 4.2.3 | Create handover wizard (from/to/reason/notes) | High | 6h | 4.2.2 |
| 4.2.4 | Add "Handover" button on task form | High | 2h | 4.2.3 |
| 4.2.5 | Auto-update `responsible_employee_id` after handover | High | 3h | 4.2.4 |
| 4.2.6 | Create handover history view (timeline/list) | Medium | 4h | 4.2.5 |
| 4.2.7 | Add chatter log for handover events | Medium | 2h | 4.2.6 |
| 4.2.8 | Integrate with `project_handover_notes` if applicable | Low | 4h | 4.2.7 |

**Deliverables:**
- [ ] Handover button on tasks
- [ ] Wizard captures from/to/reason
- [ ] History preserved
- [ ] Responsible employee updated

---

## Stage 5: Timesheet & Leave Integration (Week 5-6)

### Phase 5.1: Timesheet Employee Context

**Objective:** Auto-fill employee on timesheet entries from active context.

| Step | Task | Priority | Effort | Dependencies |
|------|------|----------|--------|--------------|
| 5.1.1 | Override `account.analytic.line` default for `employee_id` | High | 4h | 4.2.8 |
| 5.1.2 | Add validation to prevent employee mismatch | High | 3h | 5.1.1 |
| 5.1.3 | Allow manager override with permission check | Medium | 3h | 5.1.2 |
| 5.1.4 | Update timesheet views to show employee clearly | Medium | 2h | 5.1.3 |
| 5.1.5 | Test with Enterprise timesheet grid | Medium | 2h | 5.1.4 |

**Deliverables:**
- [ ] Timesheet employee auto-filled from context
- [ ] Managers can override
- [ ] Works with Enterprise grid

---

### Phase 5.2: Leave Request Employee Context

**Objective:** Auto-fill employee on leave requests from active context.

| Step | Task | Priority | Effort | Dependencies |
|------|------|----------|--------|--------------|
| 5.2.1 | Override `hr.leave` default for `employee_id` | High | 3h | 5.1.5 |
| 5.2.2 | Restrict employee dropdown for non-managers | High | 3h | 5.2.1 |
| 5.2.3 | Allow HR managers to create leave for others | Medium | 2h | 5.2.2 |
| 5.2.4 | Test leave approval workflow | Medium | 2h | 5.2.3 |

**Deliverables:**
- [ ] Leave request employee auto-filled
- [ ] Non-managers can't change employee
- [ ] Approval workflow works

---

## Stage 6: KPI & Reporting (Week 6-7)

### Phase 6.1: KPI Snapshot Model

**Objective:** Create the employee KPI aggregation system.

| Step | Task | Priority | Effort | Dependencies |
|------|------|----------|--------|--------------|
| 6.1.1 | Create `hr.employee.kpi.snapshot` model | High | 4h | 5.2.4 |
| 6.1.2 | Implement `_compute_tasks_completed()` method | High | 4h | 6.1.1 |
| 6.1.3 | Implement `_compute_tasks_overdue()` method | High | 3h | 6.1.2 |
| 6.1.4 | Implement `_compute_hours_logged()` method | High | 3h | 6.1.3 |
| 6.1.5 | Implement `_compute_checkpoints_completed()` method | High | 3h | 6.1.4 |
| 6.1.6 | Implement `_compute_avg_cycle_time()` method | Medium | 4h | 6.1.5 |
| 6.1.7 | Create KPI snapshot form/tree views | Medium | 3h | 6.1.6 |
| 6.1.8 | Add smart button on employee form: "View KPIs" | Medium | 2h | 6.1.7 |

**Deliverables:**
- [ ] KPI snapshot model with all metrics
- [ ] Views for viewing snapshots
- [ ] Smart button on employee form

---

### Phase 6.2: KPI Cron Job & Manual Trigger

**Objective:** Automate KPI calculation.

| Step | Task | Priority | Effort | Dependencies |
|------|------|----------|--------|--------------|
| 6.2.1 | Create nightly cron job for KPI calculation | High | 4h | 6.1.8 |
| 6.2.2 | Implement batch processing for all employees | High | 4h | 6.2.1 |
| 6.2.3 | Add period selection (day/week/month) | Medium | 3h | 6.2.2 |
| 6.2.4 | Create "Recompute KPI" server action for managers | Medium | 2h | 6.2.3 |
| 6.2.5 | Add progress logging/notification | Low | 2h | 6.2.4 |
| 6.2.6 | Handle edge cases (no data, new employees) | Medium | 3h | 6.2.5 |

**Deliverables:**
- [ ] Nightly cron runs KPI calculation
- [ ] Manual recompute button works
- [ ] Handles all edge cases

---

### Phase 6.3: Employee Performance Dashboard

**Objective:** Build manager dashboard for team performance.

| Step | Task | Priority | Effort | Dependencies |
|------|------|----------|--------|--------------|
| 6.3.1 | Create dashboard action/menu | High | 2h | 6.2.6 |
| 6.3.2 | Implement employee KPI comparison view | High | 6h | 6.3.1 |
| 6.3.3 | Add date range filter | High | 3h | 6.3.2 |
| 6.3.4 | Add department filter | Medium | 2h | 6.3.3 |
| 6.3.5 | Create pivot view for KPI analysis | Medium | 4h | 6.3.4 |
| 6.3.6 | Create graph views (bar/pie charts) | Medium | 4h | 6.3.5 |
| 6.3.7 | Add export to Excel functionality | Low | 3h | 6.3.6 |

**Deliverables:**
- [ ] Manager dashboard with team KPIs
- [ ] Filters by date/department
- [ ] Pivot and graph views
- [ ] Export capability

---

## Stage 7: Testing & Documentation (Week 7-8)

### Phase 7.1: Comprehensive Testing

| Step | Task | Priority | Effort | Dependencies |
|------|------|----------|--------|--------------|
| 7.1.1 | Write unit tests for all models | High | 8h | 6.3.7 |
| 7.1.2 | Write integration tests for workflows | High | 8h | 7.1.1 |
| 7.1.3 | Create test scenarios for shared user flow | High | 4h | 7.1.2 |
| 7.1.4 | Test PIN security (brute force, encryption) | High | 4h | 7.1.3 |
| 7.1.5 | Perform UAT with sample department | High | 8h | 7.1.4 |
| 7.1.6 | Fix bugs from testing | High | Variable | 7.1.5 |

**Deliverables:**
- [ ] All tests passing
- [ ] UAT completed
- [ ] Bugs fixed

---

### Phase 7.2: Documentation

| Step | Task | Priority | Effort | Dependencies |
|------|------|----------|--------|--------------|
| 7.2.1 | Write user guide for employees | High | 4h | 7.1.6 |
| 7.2.2 | Write admin guide for managers | High | 4h | 7.2.1 |
| 7.2.3 | Document API/technical specs | Medium | 4h | 7.2.2 |
| 7.2.4 | Create training materials/screenshots | Medium | 4h | 7.2.3 |
| 7.2.5 | Update README.md | Medium | 2h | 7.2.4 |

**Deliverables:**
- [ ] User guide
- [ ] Admin guide
- [ ] Technical documentation
- [ ] Training materials

---

### Phase 7.3: Deployment & Rollout

| Step | Task | Priority | Effort | Dependencies |
|------|------|----------|--------|--------------|
| 7.3.1 | Deploy to staging environment | High | 2h | 7.2.5 |
| 7.3.2 | Migrate existing employees (set PINs) | High | 4h | 7.3.1 |
| 7.3.3 | Create shared department users | High | 2h | 7.3.2 |
| 7.3.4 | Link employees to shared users | High | 4h | 7.3.3 |
| 7.3.5 | Train pilot department | High | 8h | 7.3.4 |
| 7.3.6 | Monitor and gather feedback | High | Ongoing | 7.3.5 |
| 7.3.7 | Deploy to production | High | 2h | 7.3.6 |
| 7.3.8 | Roll out to all departments | High | Variable | 7.3.7 |

**Deliverables:**
- [ ] Staging deployment successful
- [ ] Data migration complete
- [ ] Pilot training done
- [ ] Production deployment

---

## Summary Timeline

| Stage | Description | Weeks | Key Milestones |
|-------|-------------|-------|----------------|
| 1 | Foundation | 1-2 | Module installable, PIN system, Session context |
| 2 | UI Components | 2-3 | Top-bar widget, Employee selector |
| 3 | Task & Project | 3-4 | Task employee fields, Template integration |
| 4 | Checkpoint & Handover | 4-5 | Checkpoint tracking, Handover system |
| 5 | Timesheet & Leave | 5-6 | Auto-fill employee on timesheets/leaves |
| 6 | KPI & Reporting | 6-7 | KPI model, Cron job, Dashboard |
| 7 | Testing & Docs | 7-8 | Tests, Documentation, Deployment |

---

## Resource Estimation

| Role | Effort | Notes |
|------|--------|-------|
| Backend Developer | 120-140h | Models, logic, cron jobs |
| Frontend Developer | 40-50h | OWL widgets, views |
| QA Engineer | 30-40h | Testing, UAT |
| Technical Writer | 16-20h | Documentation |
| Project Manager | Ongoing | Coordination |

**Total Estimated Effort:** ~200-250 hours

---

## Risk Mitigation Checkpoints

| Checkpoint | Week | Criteria | Action if Failed |
|------------|------|----------|------------------|
| Core models working | 2 | Module installs, PIN works | Simplify scope |
| UI widget functional | 3 | Switcher works in navbar | Use simpler dropdown |
| Task integration done | 4 | Employee fields on tasks | Prioritize over checkpoints |
| KPI basics working | 7 | Nightly cron calculates | Defer advanced metrics |
| UAT passed | 8 | Pilot team approved | Extend timeline |

---

## Dependencies on Other Modules

| Module | Required | Optional | Integration Point |
|--------|----------|----------|-------------------|
| hr | ✅ | | hr.employee extension |
| project | ✅ | | project.task extension |
| hr_holidays | ✅ | | Leave request defaults |
| hr_timesheet | | ✅ | Timesheet employee |
| project_checkpoints_basic | | ✅ | Checkpoint completion |
| project_handover_notes | | ✅ | Handover integration |
| project_templates_basic | | ✅ | Template assignment |

---

## Success Criteria Checklist

- [ ] Users reduced from 33 to 21
- [ ] Every task has `responsible_employee_id`
- [ ] PIN security implemented and tested
- [ ] Top-bar employee switcher working
- [ ] Timesheets auto-filled with employee
- [ ] Leave requests auto-filled with employee
- [ ] Checkpoint completion tracked by employee
- [ ] Handover system functional
- [ ] KPI snapshots calculated nightly
- [ ] Manager dashboard available
- [ ] All documentation complete
- [ ] UAT passed by pilot department
