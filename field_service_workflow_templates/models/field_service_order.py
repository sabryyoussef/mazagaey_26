# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FieldServiceOrder(models.Model):
    _name = 'field.service.order'
    _description = 'Field Service Order'
    _order = 'create_date desc'

    name = fields.Char('Order Name', required=True)
    description = fields.Text('Description')
    active = fields.Boolean('Active', default=True)
