# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductImportWizard(models.TransientModel):
    """Product Import Wizard - Placeholder"""
    _name = 'product.import.wizard'
    _description = 'Product Import Wizard'
    
    name = fields.Char(string='Import')
