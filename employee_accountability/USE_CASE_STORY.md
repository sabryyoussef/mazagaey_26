# Use Case Story: Employee Accountability with Employee Codes

## Overview

This document demonstrates the **Employee Code authentication system** that enables multiple employees to share a single Odoo user account while maintaining individual accountability.

**Version:** 18.0.2.0.0  
**Last Updated:** January 2026

---

## 🏢 Scenario: Mazagawy Compliance Department

### Company Setup

**Company:** Mazagawy Business Services LLC  
**Department:** Compliance & Document Processing  
**Problem:** 10 employees need Odoo access but only 2 Enterprise licenses available

### The Solution: Shared User Architecture

| Role | Odoo User Account | Employees Linked |
|------|-------------------|------------------|
| Manager | `compliance.manager` | Sara (Manager) |
| Staff | `compliance.team` | Ahmed, Fatima, Omar, Layla, Hassan, Nora, Khalid, Mona, Youssef |

---

## 📖 Story: Trade License Renewal Project

### Step 1: Admin Generates Employee Codes

**Actor:** IT Administrator  
**Time:** Initial Setup

The IT Admin opens **Employees → Employees** and selects Ahmed's employee record.

1. Click **"Generate Employee Code"** button
2. System generates a unique 8-character code: `AHM-7X9K2`
3. Admin securely provides this code to Ahmed
4. Repeat for all 9 employees

```
Employee Codes Generated:
├── Ahmed    → AHM-7X9K2
├── Fatima   → FAT-3M5N8
├── Omar     → OMA-9P2Q4
├── Layla    → LAY-1R6S7
├── Hassan   → HAS-4T8U3
├── Nora     → NOR-6V2W9
├── Khalid   → KHA-8X4Y1
├── Mona     → MON-2Z7A5
└── Youssef  → YOU-5B9C6
```

---

### Step 2: Manager Creates Project

**Actor:** Sara (Manager)  
**Time:** Monday 9:00 AM  
**User Account:** `compliance.manager`

Sara logs in and creates project **"Trade License Renewal - ABC Trading LLC"** with 5 tasks:

| Task | Assigned To |
|------|-------------|
| 1. Collect client documents | Ahmed |
| 2. Prepare application | Fatima |
| 3. Submit to authority | Omar |
| 4. Follow up on approval | Ahmed |
| 5. Deliver license to client | Layla |

**Key Point:** Sara can assign tasks to specific employees even though they share the same user account.

---

### Step 3: Ahmed Starts His Workday

**Actor:** Ahmed  
**Time:** Monday 9:30 AM  
**User Account:** `compliance.team` (shared with 8 others)

#### Login Flow:

1. Ahmed opens browser and goes to Odoo
2. Logs in with shared credentials: `compliance.team / TeamPass2026`
3. **Employee Code Prompt appears** (because this user has linked employees)
4. Ahmed enters his code: `AHM-7X9K2`
5. System validates and creates **Employee Session Context**

```
Session Context Created:
├── User: compliance.team
├── Active Employee: Ahmed (hr.employee ID: 15)
├── Code Verified: ✓
├── Session Start: 2026-01-22 09:30:00
└── IP Address: 192.168.1.100
```

#### Ahmed Works on Task 1:

Ahmed opens **"Collect client documents"** task and:

1. Updates task status to "In Progress"
2. Logs 2 hours on timesheet
3. Adds a note: "Called client, documents arriving tomorrow"
4. Attaches received email as document

**All actions are tracked with Ahmed's employee identity:**

```
Task Activity Log:
├── 09:35 - Ahmed marked task "In Progress"
├── 09:36 - Ahmed created timesheet entry (2 hours)
├── 09:40 - Ahmed added note
└── 09:45 - Ahmed uploaded document
```

---

### Step 4: Fatima Takes Over Same Computer

**Actor:** Fatima  
**Time:** Monday 11:00 AM  
**Situation:** Ahmed goes to meeting, Fatima uses same workstation

#### Session Switch Flow:

1. Fatima clicks **"Switch Employee"** button (or session times out)
2. Current session for Ahmed is closed
3. Fatima enters her code: `FAT-3M5N8`
4. New session context created for Fatima

```
Session Switch:
├── Previous: Ahmed (closed at 11:00)
└── New: Fatima (started at 11:00)
```

#### Fatima Works on Task 2:

Fatima opens **"Prepare application"** task:

1. Downloads template documents
2. Fills application form
3. Logs 3 hours on timesheet
4. Marks task as "Ready for Review"

**All actions tracked under Fatima's identity:**

```
Task Activity Log:
├── 11:05 - Fatima downloaded template
├── 11:10 - Fatima started working
├── 14:00 - Fatima logged 3 hours timesheet
└── 14:05 - Fatima changed status to "Ready for Review"
```

---

### Step 5: Manager Reviews Work

**Actor:** Sara (Manager)  
**Time:** Monday 3:00 PM

Sara opens the project dashboard and sees:

```
Project: Trade License Renewal - ABC Trading LLC
┌─────────────────────────────────┬───────────┬─────────────────┬───────────┐
│ Task                            │ Assignee  │ Last Updated By │ Status    │
├─────────────────────────────────┼───────────┼─────────────────┼───────────┤
│ 1. Collect client documents     │ Ahmed     │ Ahmed           │ In Prog.  │
│ 2. Prepare application          │ Fatima    │ Fatima          │ Review    │
│ 3. Submit to authority          │ Omar      │ -               │ To Do     │
│ 4. Follow up on approval        │ Ahmed     │ -               │ To Do     │
│ 5. Deliver license to client    │ Layla     │ -               │ To Do     │
└─────────────────────────────────┴───────────┴─────────────────┴───────────┘

Timesheet Summary:
├── Ahmed:  2 hours (Task 1)
├── Fatima: 3 hours (Task 2)
└── Total:  5 hours
```

**Key Insight:** Sara sees exactly WHO did WHAT and WHEN, even though Ahmed and Fatima used the same login account.

---

### Step 6: Timesheet Report

**Actor:** HR Department  
**Time:** End of Week

HR runs a timesheet report and sees accurate individual hours:

```
Weekly Timesheet Report - Compliance Team
Week: January 19-23, 2026

┌──────────────┬───────┬───────┬───────┬───────┬───────┬─────────┐
│ Employee     │ Mon   │ Tue   │ Wed   │ Thu   │ Fri   │ Total   │
├──────────────┼───────┼───────┼───────┼───────┼───────┼─────────┤
│ Ahmed        │ 6h    │ 8h    │ 7h    │ 8h    │ 6h    │ 35h     │
│ Fatima       │ 7h    │ 7h    │ 8h    │ 7h    │ 6h    │ 35h     │
│ Omar         │ 8h    │ 6h    │ 7h    │ 8h    │ 7h    │ 36h     │
│ Layla        │ 7h    │ 8h    │ 6h    │ 7h    │ 8h    │ 36h     │
│ ...          │ ...   │ ...   │ ...   │ ...   │ ...   │ ...     │
└──────────────┴───────┴───────┴───────┴───────┴───────┴─────────┘

Note: All entries tracked via Employee Code authentication
```

---

## 🔐 Security Features

### Code Security

| Feature | Description |
|---------|-------------|
| **Hashed Storage** | Employee codes stored as SHA-256 hash, never plain text |
| **Unique Codes** | Each employee has unique code within company |
| **Expiration** | Codes can have expiration dates |
| **Deactivation** | Admin can deactivate code instantly if compromised |

### Session Tracking

| Field | Purpose |
|-------|---------|
| `session_start` | When employee authenticated |
| `session_end` | When session closed/switched |
| `code_verified` | Confirms code was validated |
| `employee_code_used` | Links to the code record used |

### Audit Trail

Every action records:
- **User ID:** The Odoo user (e.g., `compliance.team`)
- **Employee ID:** The actual person (e.g., Ahmed)
- **Timestamp:** When action occurred
- **IP Address:** Where action originated

---

## 💡 Key Benefits

### For Management

1. **Full Visibility:** Know exactly who did what
2. **Accurate Timesheets:** Individual hours, not just user hours
3. **Task Accountability:** Clear ownership of work
4. **Audit Compliance:** Complete trail for regulatory needs

### For Employees

1. **Personal Recognition:** Work attributed to them, not generic user
2. **Fair Assessment:** Performance based on actual contributions
3. **Simple Process:** Just enter a code, no complex login

### For IT/Finance

1. **License Savings:** 9 employees, 1 license = major savings
2. **Simplified Management:** Fewer user accounts to maintain
3. **Security:** Revoke one code without affecting others

---

## 🔄 Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     EMPLOYEE CODE WORKFLOW                       │
└─────────────────────────────────────────────────────────────────┘

     ┌──────────┐
     │  Admin   │
     └────┬─────┘
          │
          ▼
    ┌───────────────┐
    │ Generate Code │───────────────────┐
    │ for Employee  │                   │
    └───────────────┘                   │
                                        ▼
                              ┌─────────────────┐
                              │ Employee Record │
                              │ ├─ employee_code│
                              │ ├─ code_hash    │
                              │ ├─ parent_user  │
                              │ └─ code_active  │
                              └────────┬────────┘
                                       │
     ┌──────────┐                      │
     │ Employee │                      │
     └────┬─────┘                      │
          │                            │
          ▼                            │
    ┌───────────────┐                  │
    │ Login with    │                  │
    │ Shared User   │                  │
    └───────┬───────┘                  │
            │                          │
            ▼                          │
    ┌───────────────┐                  │
    │ Enter Employee│◄─────────────────┘
    │ Code Prompt   │
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐     ┌───────────────┐
    │ Validate Code │────►│ Create Session│
    └───────────────┘     │ Context       │
                          └───────┬───────┘
                                  │
                                  ▼
                          ┌───────────────┐
                          │ Employee Works│
                          │ ├─ Tasks      │
                          │ ├─ Timesheets │
                          │ └─ Documents  │
                          └───────┬───────┘
                                  │
                                  ▼
                          ┌───────────────┐
                          │ All Actions   │
                          │ Tracked with  │
                          │ Employee ID   │
                          └───────────────┘
```

---

## 📋 Quick Reference: How to Use

### For Employees

1. Login with shared account credentials
2. When prompted, enter your personal Employee Code
3. Work normally - all actions tracked to you
4. When done, logout or click "Switch Employee"

### For Managers

1. Assign tasks to specific employees (not users)
2. Review work with full employee attribution
3. Run reports filtered by employee

### For Administrators

1. **Generate Code:** Employee form → "Generate Employee Code"
2. **View Sessions:** Employee Accountability → Session Contexts
3. **Deactivate Code:** Employee form → uncheck "Code Active"
4. **Regenerate Code:** Employee form → "Regenerate Code"

---

## ✅ Summary

The Employee Code system solves the shared-user problem by:

| Challenge | Solution |
|-----------|----------|
| "Who did this task?" | Session context tracks active employee |
| "How many hours did Ahmed work?" | Timesheets linked to employee, not user |
| "Can we audit individual actions?" | Full session history with timestamps |
| "What if someone loses their code?" | Admin regenerates, old code invalid |
| "How do we save on licenses?" | 9 employees share 1 user account |

**Result:** Full accountability, accurate tracking, significant license savings.

---

## 🔧 Technical Implementation (Resolved Gaps)

### All Previous Gaps: RESOLVED ✅

| Gap # | Original Question | Solution |
|-------|-------------------|----------|
| 1 | Assign task to employee | Tasks assigned to `employee_id`, not `user_id` |
| 2 | Identify employee on timesheet | Session Context provides active employee |
| 3 | Record checkpoint completion | `completed_by_employee_id` from session |
| 4 | Default employee on forms | Session Context auto-populates |
| 5 | Reports by employee | Filter by `employee_id` field |
| 6 | Task handover | Integrates with `project_handover_notes` |
| 7 | KPI aggregation | Employee KPI model with cron job |

### Selected Approach: Employee Code + Session Context

**Why Employee Codes?**
- ✅ Works within Odoo's constraint (1 user per employee)
- ✅ Uses `parent_user_id` field for shared access
- ✅ Simple 8-character code, easy to remember
- ✅ Secure hash storage
- ✅ Quick session switching
- ✅ Full audit trail
