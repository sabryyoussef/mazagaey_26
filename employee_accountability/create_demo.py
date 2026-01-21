#!/usr/bin/env python3
"""
Demo Data Creation Script for Employee Accountability Module
Run this in Odoo shell: python3 odoo-bin shell -d odoo -c /etc/odoo/odoo.conf < /opt/odoo/extra-addons/employee_accountability/create_demo.py
Or import and call: exec(open('/opt/odoo/extra-addons/employee_accountability/create_demo.py').read())
"""

import hashlib
import os

def create_demo_data(env):
    """Create demo users and employees for testing the Employee Accountability module."""
    
    print("=" * 60)
    print("Creating Employee Accountability Demo Data")
    print("=" * 60)
    
    # Check if demo data already exists
    existing_user = env['res.users'].search([('login', '=', 'user.dept.ops')], limit=1)
    if existing_user:
        print("Demo data already exists! Skipping creation.")
        return
    
    # Get required references
    company = env.ref('base.main_company')
    partner_model = env['res.partner']
    user_model = env['res.users']
    employee_model = env['hr.employee']
    
    # Get user groups
    base_user_group = env.ref('base.group_user')
    employee_group = env.ref('hr.group_hr_user', raise_if_not_found=False)
    accountability_user_group = env.ref('employee_accountability.group_employee_accountability_user', raise_if_not_found=False)
    
    groups = [base_user_group.id]
    if employee_group:
        groups.append(employee_group.id)
    if accountability_user_group:
        groups.append(accountability_user_group.id)
    
    print(f"Using groups: {groups}")
    
    # Helper function to hash PIN
    def hash_pin(pin, salt=None):
        if salt is None:
            salt = os.urandom(32).hex()
        pin_hash = hashlib.sha256((pin + salt).encode()).hexdigest()
        return pin_hash, salt
    
    # ==========================================
    # Create User 1: Operations Department User
    # ==========================================
    print("\n--- Creating Operations Department User ---")
    
    ops_partner = partner_model.create({
        'name': 'Operations Department User',
        'email': 'ops.user@mazagawy.com',
        'company_id': company.id,
    })
    print(f"Created partner: {ops_partner.name} (ID: {ops_partner.id})")
    
    ops_user = user_model.with_context(no_reset_password=True).create({
        'name': 'Operations Department User',
        'login': 'user.dept.ops',
        'password': 'user.dept.ops',
        'partner_id': ops_partner.id,
        'company_id': company.id,
        'company_ids': [(6, 0, [company.id])],
        'groups_id': [(6, 0, groups)],
    })
    print(f"Created user: {ops_user.login} (ID: {ops_user.id})")
    
    # ==========================================
    # Create User 2: Operations Department Admin
    # ==========================================
    print("\n--- Creating Operations Department Admin ---")
    
    admin_partner = partner_model.create({
        'name': 'Operations Department Admin',
        'email': 'ops.admin@mazagawy.com',
        'company_id': company.id,
    })
    print(f"Created partner: {admin_partner.name} (ID: {admin_partner.id})")
    
    admin_user = user_model.with_context(no_reset_password=True).create({
        'name': 'Operations Department Admin',
        'login': 'admin.dept.ops',
        'password': 'admin.dept.ops',
        'partner_id': admin_partner.id,
        'company_id': company.id,
        'company_ids': [(6, 0, [company.id])],
        'groups_id': [(6, 0, groups)],
    })
    print(f"Created user: {admin_user.login} (ID: {admin_user.id})")
    
    # ==========================================
    # Create Employees
    # ==========================================
    employees_data = [
        # Employees sharing user.dept.ops
        {'name': 'Ahmed Ali', 'pin': '1234', 'user': ops_user, 'job': 'Field Technician'},
        {'name': 'Fatima Hassan', 'pin': '2345', 'user': ops_user, 'job': 'Service Engineer'},
        {'name': 'Omar Said', 'pin': '3456', 'user': ops_user, 'job': 'Maintenance Specialist'},
        {'name': 'Layla Mohamed', 'pin': '4567', 'user': ops_user, 'job': 'Quality Inspector'},
        # Employee using admin.dept.ops
        {'name': 'Hassan Ibrahim', 'pin': '5678', 'user': admin_user, 'job': 'Operations Supervisor'},
    ]
    
    print("\n--- Creating Employees ---")
    for emp_data in employees_data:
        # Create private address for employee
        private_address = partner_model.create({
            'name': emp_data['name'],
            'email': f"{emp_data['name'].lower().replace(' ', '.')}@mazagawy.com",
            'type': 'private',
            'company_id': company.id,
        })
        
        # Hash the PIN
        pin_hash, pin_salt = hash_pin(emp_data['pin'])
        
        # Create employee
        employee = employee_model.create({
            'name': emp_data['name'],
            'user_id': emp_data['user'].id,
            'company_id': company.id,
            'address_home_id': private_address.id,
            'job_title': emp_data['job'],
            'employee_pin': pin_hash,
            'employee_pin_salt': pin_salt,
            'pin_required': True,
            'pin_failed_attempts': 0,
        })
        print(f"Created employee: {employee.name} (ID: {employee.id}) - PIN: {emp_data['pin']} - User: {emp_data['user'].login}")
    
    # Commit the transaction
    env.cr.commit()
    
    print("\n" + "=" * 60)
    print("Demo Data Creation Complete!")
    print("=" * 60)
    print("\nTest Credentials:")
    print("-" * 40)
    print("User Login: user.dept.ops")
    print("Password: user.dept.ops")
    print("Employees: Ahmed Ali (1234), Fatima Hassan (2345), Omar Said (3456), Layla Mohamed (4567)")
    print("-" * 40)
    print("User Login: admin.dept.ops")
    print("Password: admin.dept.ops")
    print("Employee: Hassan Ibrahim (5678)")
    print("=" * 60)


# Auto-execute if running in Odoo shell
if 'env' in dir():
    create_demo_data(env)
else:
    print("This script should be run in Odoo shell.")
    print("Use: python3 odoo-bin shell -d odoo -c /etc/odoo/odoo.conf")
    print("Then: exec(open('/opt/odoo/extra-addons/employee_accountability/create_demo.py').read())")
