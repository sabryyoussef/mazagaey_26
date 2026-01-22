#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to install the employee_accountability module.
Run this in Odoo shell context.
"""
import odoo
from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry

db_name = "odoo"
with Registry(db_name).cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    module = env['ir.module.module'].search([('name', '=', 'employee_accountability')])
    print(f"Module: {module.name}, State: {module.state}")
    if module.state != 'installed':
        print("Installing module...")
        module.button_immediate_install()
        cr.commit()
        print("Module installed successfully!")
    else:
        print("Module already installed.")
