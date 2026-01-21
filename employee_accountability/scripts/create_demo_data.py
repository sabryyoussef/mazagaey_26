# -*- coding: utf-8 -*-
# Script to create demo data for employee_accountability module
# Run with: docker exec mazagawy-odoo-1 odoo shell -c /etc/odoo/odoo.conf -d mazagawy < /opt/odoo/extra-addons/employee_accountability/scripts/create_demo_data.py

import hashlib

def hash_pin(pin, salt):
    """Hash the PIN with salt using SHA-256."""
    return hashlib.sha256((pin + salt).encode()).hexdigest()

# Get models
User = env['res.users']
Employee = env['hr.employee']

print("=" * 50)
print("Creating Employee Accountability Demo Data")
print("=" * 50)

# Create shared users
print("\n[1] Creating Users...")

user_ops = User.search([('login', '=', 'user.dept.ops')], limit=1)
if not user_ops:
    user_ops = User.create({
        'name': 'Operations Department User',
        'login': 'user.dept.ops',
        'password': 'user.dept.ops',
        'groups_id': [(4, env.ref('base.group_user').id), (4, env.ref('hr.group_hr_user').id)],
    })
    print(f"  ✓ Created: user.dept.ops (ID: {user_ops.id})")
else:
    print(f"  - Exists: user.dept.ops (ID: {user_ops.id})")

admin_ops = User.search([('login', '=', 'admin.dept.ops')], limit=1)
if not admin_ops:
    admin_ops = User.create({
        'name': 'Operations Admin User',
        'login': 'admin.dept.ops',
        'password': 'admin.dept.ops',
        'groups_id': [(4, env.ref('base.group_user').id), (4, env.ref('hr.group_hr_manager').id)],
    })
    print(f"  ✓ Created: admin.dept.ops (ID: {admin_ops.id})")
else:
    print(f"  - Exists: admin.dept.ops (ID: {admin_ops.id})")

env.cr.commit()

# Create employees
print("\n[2] Creating Employees...")

employees_data = [
    {'name': 'Ahmed Ali', 'job_title': 'Operations Senior Specialist', 'email': 'ahmed.ali@example.com', 'user_id': user_ops.id, 'pin': '1234', 'salt': 'demo_salt_ahmed_001'},
    {'name': 'Fatima Hassan', 'job_title': 'Operations Junior Specialist', 'email': 'fatima.hassan@example.com', 'user_id': user_ops.id, 'pin': '2345', 'salt': 'demo_salt_fatima_002'},
    {'name': 'Omar Said', 'job_title': 'Operations Senior Specialist', 'email': 'omar.said@example.com', 'user_id': user_ops.id, 'pin': '3456', 'salt': 'demo_salt_omar_003'},
    {'name': 'Layla Mohamed', 'job_title': 'Operations Junior Specialist', 'email': 'layla.mohamed@example.com', 'user_id': user_ops.id, 'pin': '4567', 'salt': 'demo_salt_layla_004'},
    {'name': 'Hassan Ibrahim', 'job_title': 'Operations Manager', 'email': 'hassan.ibrahim@example.com', 'user_id': admin_ops.id, 'pin': '5678', 'salt': 'demo_salt_hassan_005'},
]

for emp_data in employees_data:
    existing = Employee.search([('name', '=', emp_data['name'])], limit=1)
    if not existing:
        pin_hash = hash_pin(emp_data['pin'], emp_data['salt'])
        emp = Employee.create({
            'name': emp_data['name'],
            'job_title': emp_data['job_title'],
            'work_email': emp_data['email'],
            'user_id': emp_data['user_id'],
            'pin_required': True,
            'employee_pin': pin_hash,
            'employee_pin_salt': emp_data['salt'],
        })
        print(f"  ✓ Created: {emp.name} (ID: {emp.id}, PIN: {emp_data['pin']})")
    else:
        # Update user_id and PIN if employee exists
        pin_hash = hash_pin(emp_data['pin'], emp_data['salt'])
        existing.write({
            'user_id': emp_data['user_id'],
            'pin_required': True,
            'employee_pin': pin_hash,
            'employee_pin_salt': emp_data['salt'],
        })
        print(f"  ↻ Updated: {existing.name} (ID: {existing.id}, PIN: {emp_data['pin']})")

env.cr.commit()

print("\n" + "=" * 50)
print("Demo Data Creation Complete!")
print("=" * 50)
print("\nTest Credentials:")
print("  Login: user.dept.ops / Password: user.dept.ops")
print("  Login: admin.dept.ops / Password: admin.dept.ops")
print("\nEmployee PINs:")
print("  Ahmed Ali:      1234")
print("  Fatima Hassan:  2345")
print("  Omar Said:      3456")
print("  Layla Mohamed:  4567")
print("  Hassan Ibrahim: 5678")
print("")
