# -*- coding: utf-8 -*-
from odoo import models, fields, api

class WorkflowServiceProduct(models.Model):
    _name = 'workflow.service.product'
    _description = 'Workflow Service Product'
    _order = 'name'

    name = fields.Char('Product Name', required=True)
    description = fields.Text('Description')
    active = fields.Boolean('Active', default=True)
