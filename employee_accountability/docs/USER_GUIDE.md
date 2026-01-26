# Employee Accountability Module - User Guide

## Overview

The Employee Accountability module enables organizations to track individual employee activities even when multiple employees share a single Odoo user account. This is particularly useful for reducing license costs while maintaining full accountability.

## Key Concepts

### Employee Codes
- Each employee receives a unique code (e.g., `EMP-A1B2-C3D4`)
- Codes are automatically generated when an employee is created
- Codes can be regenerated if compromised

### Shared User Accounts
- Multiple employees can be linked to a single Odoo user account
- Each employee authenticates using their unique Employee Code
- All actions are tracked to the individual employee, not just the user account

### Session Context
- When an employee enters their code, a session is created
- The session tracks who is currently "active" on the shared account
- Sessions automatically expire after 24 hours

---

## Getting Started

### 1. Enable Employee Accountability

1. Go to **Apps** menu
2. Search for "Employee Accountability"
3. Click **Install**

### 2. Configure Employees

1. Go to **Employees** → **Employees**
2. Open an employee record
3. In the **Accountability** tab:
   - **Employee Code**: Auto-generated unique identifier
   - **Parent User**: The Odoo user account this employee uses
   - **Is Shared User Employee**: Check if this employee shares a user account

### 3. Using the Employee Code

#### Via Systray (Top Right Menu)
1. Click the **Employee Code** icon in the top-right systray
2. A popup will show:
   - Current active employee (if any)
   - Button to enter/change code

#### Via Wizard
1. Click **Enter Employee Code** button
2. Enter your unique Employee Code
3. Click **Confirm**
4. Your session is now active

---

## Features

### Employee Management

| Field | Description |
|-------|-------------|
| Employee Code | Unique 12-character code (EMP-XXXX-XXXX) |
| Parent User | The Odoo user account used for login |
| Is Shared User | Indicates if employee shares a user account |
| Department | Employee's department |

### Session Tracking

- **Active Sessions**: View who is currently logged in
- **Session History**: Audit trail of all sessions
- **Auto-Expiry**: Sessions expire after 24 hours

### Task Integration

When viewing tasks:
- **Assigned Employee**: The employee responsible for the task
- **Employee Code**: Quick reference to the assigned employee's code
- **Actual Workers**: Employees who logged time on the task

### Project Integration

Projects can track:
- **Manager Employee**: The employee managing the project
- **Portal Collaborators**: External collaborators with access

---

## Menu Navigation

| Menu Path | Description |
|-----------|-------------|
| Employees → Employees | Manage employee records and codes |
| Employees → Sessions | View active and past sessions |
| Project → Tasks | View tasks with employee assignments |

---

## Security Groups

### Employee Accountability User
- Can enter their own employee code
- Can view their own sessions
- Can view task assignments

### Employee Accountability Manager
- All user permissions
- Can view all employee sessions
- Can manage employee codes
- Can assign employees to tasks

---

## Troubleshooting

### "Employee Code Not Found"
- Verify the code is entered correctly (case-sensitive)
- Check if the employee record exists
- Ensure the employee has a valid code generated

### Session Not Active
- Codes must be re-entered after 24 hours
- Check if another employee ended your session
- Try entering the code again

### Cannot See Employee Code Field
- Ensure you have the "Employee Accountability User" group assigned
- Check if the module is properly installed

---

## Best Practices

1. **Code Security**: Treat employee codes like passwords - don't share them
2. **Regular Sessions**: Enter your code at the start of each work day
3. **End Sessions**: End your session when you're done for the day
4. **Audit Trail**: Managers should regularly review session logs
5. **Code Rotation**: Regenerate codes periodically for security

---

## Technical Notes

### Automatic Code Generation
Codes are generated using a secure random algorithm:
- Format: `EMP-XXXX-XXXX`
- Characters: Uppercase letters and numbers
- Uniqueness: Guaranteed unique across all employees

### Session Cleanup
A scheduled job runs daily to:
- End sessions older than 24 hours
- Clean up orphaned session records

### Database Tables
- `hr.employee`: Extended with accountability fields
- `employee.session.context`: Stores session data
- `employee.code.wizard`: Transient model for code entry
