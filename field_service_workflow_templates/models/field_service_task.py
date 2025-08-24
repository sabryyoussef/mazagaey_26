# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FieldServiceTask(models.Model):
    _name = 'field.service.task'
    _description = 'Field Service Task'
    _order = 'create_date desc'

    name = fields.Char('Task Name', required=True)
    description = fields.Text('Description')
    active = fields.Boolean('Active', default=True)
