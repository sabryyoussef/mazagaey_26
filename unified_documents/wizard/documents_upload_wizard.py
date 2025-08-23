# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class DocumentsUploadWizard(models.TransientModel):
    _name = 'documents.upload.wizard'
    _description = 'Documents Upload Wizard'

    document_id = fields.Many2one('documents.document', string='Document', required=True, readonly=True)
    attachment_file = fields.Binary(string='File', required=True, attachment=True)
    filename = fields.Char(string='Filename', required=True)
    folder_id = fields.Many2one('documents.folder', string='Folder', readonly=True)
    
    @api.model
    def default_get(self, fields_list):
        """Set default values from context"""
        defaults = super().default_get(fields_list)
        if self.env.context.get('default_document_id'):
            document = self.env['documents.document'].browse(self.env.context['default_document_id'])
            if document.exists():
                defaults['document_id'] = document.id
                defaults['folder_id'] = document.folder_id.id if document.folder_id else False
                defaults['filename'] = f"{document.name}_file"
        return defaults

    def action_upload(self):
        """Upload file and attach to document"""
        self.ensure_one()
        
        if not self.attachment_file or not self.filename:
            return {'type': 'ir.actions.act_window_close'}
        
        document = self.document_id
        ctx = self.env.context
        
        # Preserve original document linking
        original_res_model = ctx.get('original_res_model', document.res_model)
        original_res_id = ctx.get('original_res_id', document.res_id)
        
        # Create attachment linked to the document (not to project/product)
        attachment_vals = {
            'name': self.filename,
            'datas': self.attachment_file,
            'res_model': 'documents.document',
            'res_id': document.id,
            'folder_id': self.folder_id.id if self.folder_id else False,
        }
        
        # Create attachment WITHOUT triggering document res_model/res_id changes
        attachment = self.env['ir.attachment'].with_context(skip_document_write=True).create(attachment_vals)
        
        # Manually update document without changing res_model/res_id
        if document.status == 'draft':
            # Use write with specific context to avoid res_model/res_id override
            document.with_context(preserve_linking=True).write({'status': 'in_progress'})
        
        # Force refresh of parent record cache
        if document.linked_project_id:
            document.linked_project_id._invalidate_cache(['document_ids', 'document_count'])
        
        if document.linked_product_id:
            document.linked_product_id._invalidate_cache(['document_ids', 'document_count'])
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('File Uploaded'),
                'message': _('File "%s" uploaded successfully to document "%s"') % (self.filename, document.name),
                'type': 'success',
            }
        }
