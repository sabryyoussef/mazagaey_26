# Employee Accountability Module - Enhancement Plan

## Current State (v18.0.2.0.0)

The module currently provides:
- ✅ Employee Code generation and validation
- ✅ Session tracking (who is active when)
- ✅ Systray widget for code entry
- ✅ Task/Project employee assignment fields
- ✅ Basic audit trail via sessions

**Current Limitation:** Employees inherit all permissions from the shared user account.

---

## Phase 1: Quick Wins (Low Effort, High Impact)

### 1.1 Auto-Assign Employee on Task Creation
**Priority:** High | **Effort:** 2 hours

When an employee creates a task, automatically set `employee_id` to the active session employee.

```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if not vals.get('employee_id'):
            session = self.env['employee.session.context'].get_current_employee()
            if session:
                vals['employee_id'] = session.id
    return super().create(vals_list)
```

### 1.2 Session Timeout Warning
**Priority:** Medium | **Effort:** 3 hours

Show warning in systray 30 minutes before session expires.

### 1.3 Quick Code Entry via Barcode
**Priority:** Medium | **Effort:** 4 hours

Support barcode scanner input for Employee Code entry. Print codes as barcodes on ID badges.

### 1.4 Session Activity Log
**Priority:** Medium | **Effort:** 4 hours

Track what actions employee performed during session:
- Tasks created/modified
- Timesheets logged
- Documents uploaded

---

## Phase 2: Access Control (Medium Effort)

### 2.1 Task Visibility Filter
**Priority:** High | **Effort:** 1 day

Add optional record rule to filter tasks by assigned employee:

```xml
<record id="rule_task_employee_filter" model="ir.rule">
    <field name="name">Employee sees assigned tasks</field>
    <field name="model_id" ref="project.model_project_task"/>
    <field name="domain_force">[
        '|',
        ('employee_id.parent_user_id', '=', user.id),
        ('employee_id', '=', False)
    ]</field>
    <field name="active" eval="False"/>  <!-- Disabled by default -->
</record>
```

Make this configurable in Settings.

### 2.2 Prevent Self-Assignment
**Priority:** Medium | **Effort:** 4 hours

Add constraint: employees cannot assign tasks to themselves. Only managers can assign.

```python
@api.constrains('employee_id')
def _check_employee_assignment(self):
    for task in self:
        current_employee = self.env['employee.session.context'].get_current_employee()
        if task.employee_id == current_employee and not self.env.user.has_group('employee_accountability.group_employee_accountability_manager'):
            raise ValidationError("You cannot assign tasks to yourself.")
```

### 2.3 Project Access Based on Assignment
**Priority:** Medium | **Effort:** 1 day

Employees only see projects where they have assigned tasks.

---

## Phase 3: Enhanced Tracking (Medium Effort)

### 3.1 Time-Based Session Reports
**Priority:** High | **Effort:** 1 day

Dashboard showing:
- Hours worked per employee per day/week/month
- Session duration statistics
- Peak usage times

### 3.2 Task Completion Tracking
**Priority:** Medium | **Effort:** 1 day

Track which employee completed (not just assigned) each task:

```python
performed_by_employee_id = fields.Many2one(
    'hr.employee',
    string='Completed By',
    compute='_compute_performed_by',
    store=True
)
```

### 3.3 Timesheet Auto-Attribution
**Priority:** High | **Effort:** 4 hours

When logging timesheets, automatically use active session employee instead of requiring manual selection.

### 3.4 Chatter Integration
**Priority:** Medium | **Effort:** 4 hours

Show employee name (not just user) in message posts and activity logs.

---

## Phase 4: Advanced Features (High Effort)

### 4.1 Shift Management Integration
**Priority:** Medium | **Effort:** 2-3 days

- Define shifts (Morning, Evening, Night)
- Validate employee code only during their shift
- Automatic session end at shift end

### 4.2 Location-Based Restrictions
**Priority:** Low | **Effort:** 2 days

- Track IP address of session
- Optionally restrict to specific IP ranges
- Geolocation tracking (if using mobile)

### 4.3 Performance Dashboard
**Priority:** Medium | **Effort:** 3 days

KPI dashboard per employee:
- Tasks completed
- Hours logged
- On-time completion rate
- Quality metrics (if integrated)

### 4.4 Mobile App Support
**Priority:** High | **Effort:** 1 week

- QR code scanning for employee code
- Offline session tracking
- Push notifications for task assignments

---

## Phase 5: Security Hardening

### 5.1 Code Expiration
**Priority:** Medium | **Effort:** 4 hours

- Employee codes expire after X days
- Automatic notification to regenerate
- HR approval for new code

### 5.2 Failed Attempt Lockout
**Priority:** High | **Effort:** 4 hours

- Track failed code entries
- Lock out after 5 failed attempts
- Notify manager of lockout

```python
failed_attempts = fields.Integer(default=0)
lockout_until = fields.Datetime()

def validate_code(self, code):
    if self.lockout_until and self.lockout_until > fields.Datetime.now():
        raise ValidationError("Account locked. Contact your manager.")
    # ... validation logic
```

### 5.3 Two-Factor for Sensitive Operations
**Priority:** Low | **Effort:** 2 days

Require code + PIN for:
- Financial transactions
- Inventory adjustments
- Time-off requests

### 5.4 Session Hijacking Prevention
**Priority:** Medium | **Effort:** 1 day

- Bind session to browser fingerprint
- Detect unusual activity patterns
- Alert on concurrent sessions

---

## Configuration Options to Add

### Settings Page
```
Employee Accountability Settings
├── [ ] Require employee code to create tasks
├── [ ] Auto-assign employee on task creation
├── [ ] Restrict task visibility to assigned only
├── [ ] Prevent self-assignment
├── Session timeout: [24] hours
├── [ ] Enable failed attempt lockout
├── Lockout after: [5] failed attempts
└── [ ] Send email on new session
```

---

## Integration Opportunities

### With Existing Modules

| Module | Integration |
|--------|-------------|
| **hr_timesheet** | Auto-set employee on timesheet lines |
| **project** | Filter tasks by active employee |
| **sale** | Track which employee created/confirmed orders |
| **stock** | Track who performed inventory operations |
| **helpdesk** | Attribute tickets to employee |
| **field_service** | Track technician per job |

### With External Systems

| System | Integration |
|--------|-------------|
| **Biometric** | Validate employee code with fingerprint |
| **Door Access** | Log entry/exit with same code |
| **Time Clock** | Sync session with punch-in/out |
| **HR System** | Sync employee data |

---

## Recommended Implementation Order

1. **Week 1:** Auto-assign employee on task creation (1.1)
2. **Week 1:** Session activity log (1.4)
3. **Week 2:** Task visibility filter - optional (2.1)
4. **Week 2:** Timesheet auto-attribution (3.3)
5. **Week 3:** Failed attempt lockout (5.2)
6. **Week 3:** Time-based reports (3.1)
7. **Week 4:** Performance dashboard (4.3)

---

## Database Considerations

### New Tables Needed

```sql
-- Session activity log
CREATE TABLE employee_session_activity (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES employee_session_context(id),
    model VARCHAR(128),
    res_id INT,
    action VARCHAR(32),  -- create, write, unlink
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Failed login attempts
CREATE TABLE employee_code_attempt (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES res_users(id),
    code_entered VARCHAR(16),
    success BOOLEAN,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT NOW()
);
```

---

## Success Metrics

| Metric | Target |
|--------|--------|
| License cost reduction | 50-80% |
| Audit trail completeness | 100% of actions traced to employee |
| Session adoption rate | 95% of shifts have active session |
| Failed attempt rate | < 5% |
| Average session duration | 6-8 hours |

---

## Questions to Discuss

1. Should employees be able to see each other's tasks? (Team collaboration vs privacy)
2. What happens when employee forgets code? (Self-service reset vs manager intervention)
3. Should sessions auto-extend if user is active? (Prevent timeout during work)
4. Integrate with existing attendance module or keep separate?
5. Multi-company support needed?

---

## Version Roadmap

| Version | Features |
|---------|----------|
| 18.0.2.1.0 | Auto-assign, session activity log |
| 18.0.2.2.0 | Task visibility filter, prevent self-assign |
| 18.0.2.3.0 | Timesheet integration, reports |
| 18.0.3.0.0 | Security hardening, lockout |
| 18.0.4.0.0 | Performance dashboard, shift management |
