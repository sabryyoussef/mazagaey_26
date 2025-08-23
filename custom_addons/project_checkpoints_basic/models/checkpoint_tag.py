# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProjectTaskCheckpointTag(models.Model):
    _name = 'project.task.checkpoint.tag'
    _description = 'Task Checkpoint Tag'
    _order = 'name'

    name = fields.Char(
        string='Tag Name',
        required=True,
        help='Name of the checkpoint tag'
    )
    
    color = fields.Integer(
        string='Color Index',
        help='Color index for the tag'
    )
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Tag name must be unique!')
    ]
