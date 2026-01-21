# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectProjectEmployeeAccountability(models.Model):
    """
    Extend project.project to add employee assignment preferences.
    This works with both regular projects and project templates.
    """
    _inherit = 'project.project'

    # ===========================================
    # Employee Assignment Preferences
    # ===========================================
    default_responsible_employee_id = fields.Many2one(
        'hr.employee',
        string='Default Responsible Employee',
        help='Default employee responsible for tasks in this project/template.',
    )
    default_department_id = fields.Many2one(
        'hr.department',
        string='Default Department',
        help='Default department for employee assignment suggestions.',
    )
    preferred_employee_tag_ids = fields.Many2many(
        'hr.employee.category',
        'project_preferred_employee_tags_rel',
        'project_id',
        'category_id',
        string='Preferred Employee Tags',
        help='Filter employees by these tags when suggesting assignments.',
    )
    
    # ===========================================
    # Project Manager Employee Link
    # ===========================================
    manager_employee_id = fields.Many2one(
        'hr.employee',
        string='Project Manager (Employee)',
        tracking=True,
        help='The employee who manages this project.',
    )

    # ===========================================
    # Team Assignment
    # ===========================================
    team_employee_ids = fields.Many2many(
        'hr.employee',
        'project_team_employee_rel',
        'project_id',
        'employee_id',
        string='Team Employees',
        help='Employees assigned to work on this project.',
    )

    # ===========================================
    # Helper Methods
    # ===========================================
    def get_suggested_employees(self, limit=10):
        """
        Get suggested employees for task assignment based on project preferences.
        
        Returns:
            recordset: hr.employee records
        """
        self.ensure_one()
        
        domain = [('active', '=', True)]
        
        # Filter by department
        if self.default_department_id:
            domain.append(('department_id', '=', self.default_department_id.id))
        
        # Filter by tags
        if self.preferred_employee_tag_ids:
            domain.append(('category_ids', 'in', self.preferred_employee_tag_ids.ids))
        
        # Prioritize team members
        if self.team_employee_ids:
            team_employees = self.team_employee_ids
            other_employees = self.env['hr.employee'].search(
                domain + [('id', 'not in', team_employees.ids)],
                limit=max(0, limit - len(team_employees))
            )
            return team_employees | other_employees
        
        return self.env['hr.employee'].search(domain, limit=limit)

    def action_view_team_employees(self):
        """Open team employees view."""
        self.ensure_one()
        return {
            'name': 'Team Employees',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.team_employee_ids.ids)],
        }
