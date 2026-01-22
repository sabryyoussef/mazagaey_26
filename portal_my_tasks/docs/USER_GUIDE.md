# Portal My Tasks - User Guide

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [User Roles & Permissions](#user-roles--permissions)
4. [Use Cases & Examples](#use-cases--examples)
5. [Allowed Actions](#allowed-actions)
6. [Approval Requirements](#approval-requirements)
7. [Workflow Examples](#workflow-examples)
8. [Troubleshooting](#troubleshooting)

---

## Introduction

The **Portal My Tasks** module provides employees with a dedicated workspace to manage their assigned tasks without requiring full Odoo internal access. This guide explains how to use the portal interface, what you can do, and what requires manager approval.

### Key Benefits

- ✅ Access your tasks from anywhere via web browser
- ✅ Update task progress in real-time
- ✅ Submit handover notes for task completion
- ✅ No need for expensive internal user licenses
- ✅ Full accountability and audit trail

---

## Getting Started

### Accessing Portal My Tasks

1. **Login**: Go to your company's Odoo portal URL (e.g., `https://yourcompany.odoo.com`)
2. **Credentials**: Use your portal user credentials (provided by your manager)
3. **Navigation**: Click on **"My Tasks"** in the portal menu

### First Time Setup

- Your manager will create your portal user account
- You'll receive login credentials via email
- Tasks will be assigned to you by your manager
- You'll see only tasks assigned to you

---

## User Roles & Permissions

### Portal User (Employee)

**What You Can Do:**
- View your assigned tasks
- Post updates and comments
- Change task status (within allowed stages)
- Upload attachments
- Submit handover notes
- View task history and chatter

**What You Cannot Do:**
- Access backend/internal Odoo apps
- Create new tasks
- Assign tasks to others
- Delete tasks
- Access other employees' tasks
- Approve handover notes
- Close tasks without approved handover

### Internal User (Manager)

**What Managers Can Do:**
- Create and assign tasks
- View all tasks and projects
- Approve/reject handover notes
- Close tasks
- Access full reporting and analytics
- Manage portal user assignments

---

## Use Cases & Examples

### Use Case 1: Daily Task Updates

**Scenario**: You're working on a task and want to update your progress.

**Steps:**
1. Login to portal
2. Navigate to **My Tasks**
3. Click on the task you're working on
4. Click **"Post Update"** button
5. Type your progress update
6. Click **"Post"**

**Result**: Your update appears in the task's activity feed, and your manager is notified.

**Example Update:**
```
"Completed the initial design mockups. 
Attached the design files for review. 
Next step: Get client feedback."
```

---

### Use Case 2: Changing Task Status

**Scenario**: You've completed a phase of work and want to move the task to "Review" stage.

**Steps:**
1. Open the task detail page
2. Click **"Change Status"** button
3. Select **"Review"** from the dropdown
4. Confirm the change

**Result**: Task status updates, and manager receives notification.

**Note**: You can only move tasks to specific allowed stages:
- ✅ In Progress
- ✅ Review
- ✅ Waiting Approval
- ❌ Cannot move to "Done" (requires manager approval)

---

### Use Case 3: Submitting Handover Note

**Scenario**: You've completed a task and need to submit a handover note for manager approval.

**Steps:**
1. Open the completed task
2. Click **"Submit Handover Note"** button
3. Fill in the handover content:
   - What was completed
   - Key deliverables
   - Important notes for next person
   - Any issues encountered
4. Upload required attachments (at least one required)
5. Click **"Submit for Approval"**

**Result**: 
- Handover note is submitted
- Task status changes to "Waiting Handover Review"
- Manager receives notification
- Task cannot be closed until handover is approved

**Example Handover Content:**
```html
<h3>Task Completion Summary</h3>
<p><strong>Completed:</strong> Website redesign project</p>

<h4>Deliverables:</h4>
<ul>
    <li>Homepage mockup (attached: homepage_design.png)</li>
    <li>Product page templates (attached: product_templates.zip)</li>
    <li>Style guide document (attached: style_guide.pdf)</li>
</ul>

<h4>Important Notes:</h4>
<p>The client requested changes to the color scheme. 
Updated colors are documented in the style guide.</p>

<h4>Next Steps:</h4>
<p>Ready for development team to implement designs.</p>
```

---

### Use Case 4: Responding to Rejected Handover

**Scenario**: Your manager rejected your handover note and requested changes.

**Steps:**
1. You receive email notification about rejection
2. Login to portal and open the task
3. View the manager's comment explaining what's missing
4. Click **"Submit Handover Note"** again (creates new version)
5. Address the manager's feedback
6. Update handover content and attachments
7. Resubmit for approval

**Result**: New version of handover note is created and submitted.

---

### Use Case 5: Viewing Task History

**Scenario**: You want to see all activity on a task.

**Steps:**
1. Open the task detail page
2. Scroll to **"Activity Feed"** section
3. View all updates, comments, and status changes
4. See who made each change and when

**Result**: Complete audit trail of task activity.

---

## Allowed Actions

### ✅ What Portal Users CAN Do

#### Task Viewing
- ✅ View all tasks assigned to you
- ✅ Filter tasks by status (In Progress, Waiting, Overdue)
- ✅ Sort tasks by due date, priority, or name
- ✅ View task details, description, and attachments
- ✅ View project information
- ✅ See task history and activity feed

#### Task Updates
- ✅ Post updates and comments to tasks
- ✅ Upload attachments to tasks
- ✅ Change task status to allowed stages:
  - In Progress
  - Review
  - Waiting Approval
- ✅ Update task progress percentage (if enabled)

#### Handover Notes
- ✅ Create handover notes for your tasks
- ✅ Upload multiple attachments to handover notes
- ✅ Edit draft handover notes
- ✅ Resubmit rejected handover notes
- ✅ View handover note history

#### Communication
- ✅ Reply to messages in task chatter
- ✅ Mention other users in comments
- ✅ Receive email notifications

---

## Approval Requirements

### ❌ What Requires Manager Approval

#### Task Closure
- ❌ **Cannot close tasks yourself**
- ✅ Manager must close tasks after handover approval
- ✅ Task must have approved handover note (if required)

**Why**: Ensures quality control and proper documentation before task completion.

#### Handover Note Approval
- ❌ **Cannot approve your own handover notes**
- ✅ Manager reviews and approves/rejects
- ✅ Manager can request changes via comments

**Why**: Ensures handover documentation meets quality standards.

#### Status Changes (Restricted)
- ❌ **Cannot move task to "Done"**
- ❌ **Cannot move task to "Cancelled"**
- ❌ **Cannot change task priority**
- ❌ **Cannot reassign task to another user**

**Why**: These actions require managerial oversight and decision-making.

#### Task Creation
- ❌ **Cannot create new tasks**
- ✅ Manager creates and assigns tasks

**Why**: Task creation requires project planning and resource allocation decisions.

---

## Workflow Examples

### Complete Workflow: Task Assignment to Completion

#### Step 1: Task Assignment (Manager)
1. Manager creates task in backend
2. Manager assigns task to you (portal user)
3. You receive email notification

#### Step 2: Task Work (You - Portal User)
1. Login to portal
2. View assigned task
3. Post progress updates as you work
4. Upload work files as attachments
5. Change status to "Review" when ready

#### Step 3: Handover Submission (You - Portal User)
1. Complete all work
2. Click "Submit Handover Note"
3. Fill in completion details
4. Upload required deliverables
5. Submit for approval

#### Step 4: Manager Review (Manager)
1. Manager receives notification
2. Manager reviews handover note
3. Manager approves or rejects

**If Approved:**
- Task can be closed
- Handover note is archived
- Task marked as complete

**If Rejected:**
- You receive notification with feedback
- Task returns to "In Progress"
- You can resubmit with corrections

#### Step 5: Task Closure (Manager)
1. Manager closes task
2. Task marked as "Done"
3. All stakeholders notified

---

### Workflow: Handling Overdue Tasks

#### Scenario
You have a task that's past its due date.

#### Your Actions (Portal User)
1. View overdue task (filtered in "Overdue" section)
2. Post update explaining delay:
   ```
   "Task is delayed due to client feedback delay. 
   New completion date: [date]. 
   Waiting for client approval on design changes."
   ```
3. Update task status if needed
4. Continue working on task

#### Manager Actions
1. Manager sees overdue task in dashboard
2. Manager reviews your update
3. Manager may:
   - Extend due date
   - Reassign task
   - Provide additional resources
   - Close task if no longer needed

---

### Workflow: Collaborative Task (Multiple Assignees)

#### Scenario
A task is assigned to multiple portal users (team task).

#### Your Actions
1. You see task in "My Tasks"
2. You can see other assignees' updates
3. You post your own updates
4. You can see all team members' handover notes
5. Each team member submits their own handover note

#### Manager Actions
1. Manager sees all team updates
2. Manager reviews all handover notes
3. Manager approves when all required handovers are submitted
4. Manager closes task

---

## Troubleshooting

### Common Issues & Solutions

#### Issue 1: "I can't see my tasks"

**Possible Causes:**
- Task not assigned to you
- Wrong portal user account
- Browser cache issues

**Solutions:**
1. Contact your manager to verify task assignment
2. Logout and login again
3. Clear browser cache
4. Try different browser

---

#### Issue 2: "I can't submit handover note"

**Possible Causes:**
- No attachments uploaded (at least one required)
- Task already has approved handover
- Missing required fields

**Solutions:**
1. Ensure at least one attachment is uploaded
2. Check if handover was already approved
3. Fill in all required fields (content is required)
4. Contact manager if issue persists

---

#### Issue 3: "I can't change task status"

**Possible Causes:**
- Trying to move to restricted stage (like "Done")
- Task is locked for editing
- Permission issue

**Solutions:**
1. Only use allowed stages (In Progress, Review, Waiting Approval)
2. Contact manager to move to "Done"
3. Refresh page and try again
4. Contact IT support if problem persists

---

#### Issue 4: "My handover note was rejected"

**What to Do:**
1. Read manager's comment explaining rejection
2. Address the feedback provided
3. Create new handover note version
4. Update content and attachments
5. Resubmit for approval

**Common Rejection Reasons:**
- Missing required attachments
- Incomplete handover content
- Missing important information
- Quality issues

---

#### Issue 5: "I can't upload attachments"

**Possible Causes:**
- File size too large
- Unsupported file type
- Browser compatibility issue

**Solutions:**
1. Check file size (max usually 10-25MB)
2. Ensure file type is supported (PDF, images, documents)
3. Try compressing large files
4. Try different browser
5. Contact IT support

---

## Best Practices

### For Portal Users (Employees)

1. **Regular Updates**: Post progress updates daily or as you make progress
2. **Clear Communication**: Be specific in your updates and comments
3. **Timely Submissions**: Submit handover notes as soon as work is complete
4. **Complete Documentation**: Include all relevant information in handover notes
5. **Attachment Quality**: Ensure attachments are clear and properly named
6. **Professional Tone**: Maintain professional communication in all updates

### Handover Note Best Practices

✅ **DO:**
- Include comprehensive completion summary
- List all deliverables clearly
- Document important decisions made
- Note any issues or challenges encountered
- Provide context for next steps
- Attach all relevant files

❌ **DON'T:**
- Submit incomplete handover notes
- Forget to attach required files
- Use vague or unclear language
- Skip important details
- Submit without reviewing content

---

## Quick Reference

### Portal User Actions Matrix

| Action | Allowed | Requires Approval | Notes |
|--------|---------|------------------|-------|
| View assigned tasks | ✅ | ❌ | Only your tasks |
| Post updates | ✅ | ❌ | Real-time updates |
| Upload attachments | ✅ | ❌ | To tasks and handovers |
| Change status (allowed stages) | ✅ | ❌ | In Progress, Review, Waiting |
| Change status (Done) | ❌ | ✅ | Manager only |
| Submit handover note | ✅ | ✅ | Requires manager approval |
| Approve handover | ❌ | N/A | Manager only |
| Close task | ❌ | N/A | Manager only |
| Create task | ❌ | N/A | Manager only |
| Assign task | ❌ | N/A | Manager only |

### Status Flow

```
[Draft/New] 
    ↓ (Manager assigns)
[In Progress] ← Portal user can set
    ↓ (Portal user updates)
[Review] ← Portal user can set
    ↓ (Portal user submits handover)
[Waiting Handover Review] ← Automatic
    ↓ (Manager approves)
[Ready to Close] ← Manager can close
    ↓ (Manager closes)
[Done] ← Manager only
```

---

## Support & Contact

### Getting Help

1. **Technical Issues**: Contact IT support
2. **Task Assignment Questions**: Contact your manager
3. **Portal Access Issues**: Contact system administrator
4. **Workflow Questions**: Refer to this guide or contact your manager

### Additional Resources

- **Implementation Plan**: See `docs/IMPLEMENTATION_PLAN.md` for technical details
- **Module README**: See `README.md` for module overview
- **Odoo Portal Documentation**: [Odoo Portal Guide](https://www.odoo.com/documentation/15.0/uk/applications/general/users/portal.html)

---

## Glossary

- **Portal User**: Employee with portal-only access (no backend)
- **Internal User**: Manager/admin with full Odoo access
- **Handover Note**: Documentation submitted when completing a task
- **Task Assignment**: Process of assigning work to an employee
- **Approval Workflow**: Process where manager reviews and approves submissions
- **Chatter**: Activity feed showing all task updates and comments
- **Stage**: Current status/phase of a task (In Progress, Review, Done, etc.)

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-22  
**Module Version**: 18.0.1.0.0
