# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Template functionality moved to project_templates_basic module
    # This module now focuses only on core checkpoint management
