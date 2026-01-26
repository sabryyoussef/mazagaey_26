# Employee Accountability Module - Use Cases

## Use Case 1: Shared Workstation in Warehouse

### Scenario
A warehouse has 10 workers but only 2 computer workstations. The company wants to reduce Odoo license costs while tracking individual employee activities.

### Setup
1. Create 2 Odoo user accounts: `warehouse_station_1` and `warehouse_station_2`
2. Create 10 employee records, each with a unique Employee Code
3. Assign 5 employees to each workstation user account

### Workflow
```
Morning Shift:
1. Ahmed arrives at Station 1
2. Logs into Odoo with shared account "warehouse_station_1"
3. Enters his Employee Code: EMP-AH12-3456
4. System records: "Ahmed is now active on Station 1"
5. Ahmed picks orders, scans items - all logged under his name

Shift Change:
6. Ahmed's shift ends, he clicks "End Session"
7. Fatima arrives, enters her code: EMP-FA78-9012
8. All subsequent actions are now tracked to Fatima
```

### Benefits
- 2 licenses instead of 10 = 80% cost reduction
- Full traceability of who did what
- Individual performance metrics possible

---

## Use Case 2: Field Service Technicians

### Scenario
A company has 20 field technicians who occasionally need to access Odoo from tablets. They don't need constant access, so sharing licenses makes sense.

### Setup
1. Create 5 Odoo user accounts for field access
2. Create 20 technician employee records
3. Each technician gets their unique Employee Code printed on their ID badge

### Workflow
```
Service Call:
1. Technician Mohamed arrives at customer site
2. Opens Odoo on shared tablet
3. Scans QR code on his badge (contains Employee Code)
4. System activates his session: EMP-MO34-5678
5. Logs work performed on the task
6. Takes photos, adds notes - all attributed to Mohamed
7. Completes task, session auto-ends

Back at Office:
- Manager reviews completed tasks
- Can see exactly which technician did each job
- Performance reports show individual metrics
```

### Benefits
- Technicians identified without complex logins
- Barcode/QR scanning for quick authentication
- Audit trail for customer disputes

---

## Use Case 3: Retail Store with Multiple Cashiers

### Scenario
A retail store has 8 cashiers sharing 3 POS terminals. Need to track individual sales performance and cash handling.

### Setup
1. Create 3 Odoo POS user accounts
2. Create 8 cashier employee records with codes
3. Cashiers enter code when starting their shift at a terminal

### Workflow
```
Opening:
1. Store opens, Cashier Sara logs into Terminal 1
2. Enters Employee Code: EMP-SA90-1234
3. All sales on Terminal 1 attributed to Sara

Break Time:
4. Sara goes on break, enters code to end session
5. Cashier Omar takes over Terminal 1
6. Omar enters his code: EMP-OM56-7890
7. Sales now attributed to Omar

End of Day:
- Manager runs report: "Sales by Employee"
- Sees individual performance: Sara $2,500, Omar $1,800
- Cash discrepancies traceable to specific employee
```

### Benefits
- Individual sales tracking
- Cash accountability
- Performance-based incentives possible

---

## Use Case 4: Manufacturing Shift Workers

### Scenario
A factory runs 3 shifts with 30 workers total. Workers rotate between workstations. Need to track who was at which station and when.

### Setup
1. Create 1 Odoo account per workstation (10 stations = 10 accounts)
2. Create 30 employee records
3. Print Employee Codes on worker badges

### Workflow
```
Shift Start:
1. Worker enters Employee Code at their assigned station
2. System logs: "Worker X at Station Y, started at 06:00"

Production Logging:
3. Worker produces items, scans them
4. Each scan linked to the active employee
5. Quality issues traceable to specific worker/shift

Shift End:
6. Session automatically ends after shift duration
7. Or worker manually ends session
8. Next shift worker enters their code
```

### Benefits
- Full production traceability
- Quality control by employee
- Training needs identification
- Shift handover documentation

---

## Use Case 5: Customer Support Team

### Scenario
A support team of 15 agents shares 10 computers in a hot-desking environment. Need to track ticket handling per agent.

### Setup
1. Create 10 Odoo accounts for support workstations
2. Create 15 support agent employee records
3. Agents know their Employee Codes by heart

### Workflow
```
Starting Work:
1. Agent Layla finds an available desk
2. Logs into the shared Odoo account
3. Enters her Employee Code: EMP-LA12-3456
4. Opens helpdesk module

Handling Tickets:
5. Layla picks up ticket #1234
6. System records: "Ticket #1234 assigned to Layla"
7. All messages, actions logged under Layla's name
8. Ticket resolved, next ticket picked up

Performance Review:
- Manager views "Tickets by Agent" report
- Layla: 45 tickets, avg resolution 2.5 hours
- Performance metrics accurate despite shared computers
```

### Benefits
- Hot-desking without losing accountability
- Individual KPI tracking
- Proper workload distribution visibility

---

## Use Case 6: Contractor/Temporary Worker Access

### Scenario
Company hires temporary workers during peak seasons. Don't want to create full user accounts for short-term workers.

### Setup
1. Create 1 "Temporary Worker" Odoo account
2. Create employee records for each temp worker
3. Generate Employee Codes valid for their contract period

### Workflow
```
Onboarding:
1. HR creates employee record for temp worker
2. System generates Employee Code
3. Temp worker receives code on first day

Daily Work:
4. Temp worker logs in with shared "Temporary Worker" account
5. Enters their unique Employee Code
6. Works on assigned tasks
7. All work tracked to their name

Contract End:
8. HR deactivates employee record
9. Employee Code no longer works
10. User account remains for next temp worker
```

### Benefits
- No license cost for temp workers
- Easy onboarding/offboarding
- Full activity tracking
- Quick access revocation

---

## Implementation Checklist

### Before Go-Live
- [ ] Install Employee Accountability module
- [ ] Create shared user accounts (by department/location)
- [ ] Generate Employee Codes for all employees
- [ ] Print/distribute codes securely
- [ ] Train employees on code entry process
- [ ] Configure session timeout (default 24h)
- [ ] Set up manager access for session monitoring

### Ongoing Maintenance
- [ ] Review session logs weekly
- [ ] Regenerate codes for terminated employees
- [ ] Monitor for unusual session patterns
- [ ] Update codes if security breach suspected
- [ ] Regular backup of session history

---

## Reporting Examples

### Employee Activity Report
```sql
-- Sessions per employee this month
SELECT 
    e.name as employee,
    COUNT(s.id) as sessions,
    SUM(EXTRACT(EPOCH FROM (s.end_date - s.start_date))/3600) as total_hours
FROM employee_session_context s
JOIN hr_employee e ON s.employee_id = e.id
WHERE s.start_date >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY e.name
ORDER BY sessions DESC;
```

### Task Completion by Employee
```sql
-- Tasks completed by each employee
SELECT 
    e.name as employee,
    e.employee_code,
    COUNT(t.id) as tasks_completed
FROM project_task t
JOIN hr_employee e ON t.employee_id = e.id
WHERE t.stage_id IN (SELECT id FROM project_task_type WHERE is_closed = true)
GROUP BY e.name, e.employee_code
ORDER BY tasks_completed DESC;
```

---

## FAQ

**Q: Can an employee have multiple active sessions?**
A: No, starting a new session automatically ends any existing session for that employee.

**Q: What happens if an employee forgets their code?**
A: Managers can view/regenerate codes from the employee record. The employee needs to contact their supervisor.

**Q: Is the Employee Code the same as a password?**
A: No, the Employee Code identifies WHO is using a shared account. The shared account still has its own password for initial login.

**Q: Can I use barcode scanners for code entry?**
A: Yes, Employee Codes can be printed as barcodes. The code entry field accepts keyboard/scanner input.

**Q: How long are sessions valid?**
A: Default is 24 hours. A scheduled job ends expired sessions daily. This can be customized.
