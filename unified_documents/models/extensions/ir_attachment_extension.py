# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class IrAttachmentExtension(models.Model):
    _inherit = 'ir.attachment'

    # Add folder field for document organization (optional)
    # Add folder field for document organization
    folder_id = fields.Many2one(
        'documents.document',
        string='Folder',
        domain=[('type', '=', 'folder')],
        help='Folder to organize this attachment in the Documents app',
        required=False
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to handle document uploads"""
        ctx = self.env.context
        
        # Check if this is an upload for a specific document
        upload_for_document = ctx.get('upload_for_document')
        if upload_for_document:
            # Update all attachments in this batch to link to the document
            for vals in vals_list:
                if not vals.get('res_model') and not vals.get('res_id'):
                    vals['res_model'] = 'documents.document'
                    vals['res_id'] = upload_for_document
        
        attachments = super().create(vals_list)
        
        # Update document status and refresh caches if needed
        if upload_for_document:
            try:
                document = self.env['documents.document'].browse(upload_for_document)
                if document.exists():
                    # Update document status if needed with preserve_linking context
                    if document.status == 'draft':
                        document.with_context(preserve_linking=True).write({'status': 'in_progress'})
                    
                    # Refresh parent caches
                    if document.linked_project_id:
                        document.linked_project_id._invalidate_cache([
                            'document_ids', 'document_count', 'required_document_count', 
                            'deliverable_document_count'
                        ])
                    
                    if document.linked_product_id:
                        document.linked_product_id._invalidate_cache([
                            'document_ids', 'document_count', 'required_document_count', 
                            'deliverable_document_count'
                        ])
                        
            except Exception as e:
                _logger.error("Error refreshing document after upload: %s", e)
        
        return attachments
