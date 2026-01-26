# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ProjectProject(models.Model):
    _inherit = 'project.project'
    
    # Manager employee (for accountability)
    manager_employee_id = fields.Many2one(
        'hr.employee',
        string='Manager Employee',
        help='Employee record of the project manager (for accountability)'
    )
    
    # Portal collaborators
    portal_collaborator_ids = fields.Many2many(
        'res.partner',
        'project_portal_collaborator_rel',
        string='Portal Collaborators',
        help='Portal users who can view all tasks in this project'
    )
