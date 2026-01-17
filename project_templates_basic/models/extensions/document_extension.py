# -*- coding: utf-8 -*-
from odoo import models, fields, api

class DocumentExtension(models.Model):
    _inherit = 'documents.document'
    
    # Source tracking fields
    source = fields.Selection([
        ('product', 'Product'),
        ('template', 'Template'),
        ('manual', 'Manual'),
    ], string='Document Source', default='manual', help='Source of this document')
    
    source_document_id = fields.Many2one(
        'documents.document', 
        string='Source Document', 
        help='Original document this was copied from (if from product)'
    )
    
    source_template_id = fields.Many2one(
        'project.document.template', 
        string='Source Template', 
        help='Document template this was created from'
    )
    
    # Additional metadata
    template_line_id = fields.Many2one(
        'project.document.template.line',
        string='Template Line',
        help='Specific template line this document was created from'
    )
