# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductBulkCategorize(models.TransientModel):
    """Bulk Categorization Wizard - Placeholder"""
    _name = 'product.bulk.categorize'
    _description = 'Product Bulk Categorize'
    
    name = fields.Char(string='Categorize')
