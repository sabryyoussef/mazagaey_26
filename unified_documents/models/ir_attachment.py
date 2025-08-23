# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import ValidationError
import logging
from odoo import fields

_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    # Add folder selection field
    folder_id = fields.Many2one(
        'documents.document',
        string='Documents Folder',
        domain=[('type', '=', 'folder')],
        help='Select a folder to organize this attachment in the Documents module'
    )
    
    # Computed field to show document category
    document_category = fields.Selection([
        ('required', 'Required'),
        ('deliverable', 'Deliverable'),
        ('reference', 'Reference'),
        ('compliance', 'Compliance')
    ], string='Document Category', compute='_compute_document_category', store=True)
    
    # Computed field to show the actual document name
    document_name = fields.Char(
        string='Document Name',
        compute='_compute_document_name',
        store=True
    )

    @api.model
    def create(self, vals):
        """Override create to ensure proper res_model/res_id persistence and folder assignment"""
        result = super().create(vals)
        
        # If this attachment is for a documents.document, ensure proper linking
        if result.res_model == 'documents.document' and result.res_id:
            try:
                document = self.env['documents.document'].browse(result.res_id)
                if document.exists():
                    # 🔹 Force re-link if missing res_model/res_id
                    if not document.res_model or not document.res_id:
                        document.write({
                            'res_model': vals.get('res_model') or document.res_model,
                            'res_id': vals.get('res_id') or document.res_id
                        })
                    
                    # 🔹 Assign folder if not already set
                    if not result.folder_id and document.folder_id:
                        result.folder_id = document.folder_id.id
                    
                    # 🔹 If folder is selected in upload form, assign it to the document too
                    if result.folder_id and not document.folder_id:
                        document.folder_id = result.folder_id.id
                        
            except Exception as e:
                _logger.warning(f"Could not process document attachment: {e}")
        
        return result

    def write(self, vals):
        """Override write to log attachment changes"""
        result = super().write(vals)
        

        
        return result

    def unlink(self):
        """Override unlink to handle document attachment deletion"""
        result = super().unlink()
        return result

    def action_download(self):
        """Download the attachment file"""
        self.ensure_one()
        if self.type == 'binary' and self.datas:
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{self._name}/{self.id}/datas?download=true',
                'target': 'self',
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('This file cannot be downloaded.'),
                    'type': 'warning',
                }
            }

    @api.depends('res_model', 'res_id')
    def _compute_document_category(self):
        """Compute the document category from the linked document"""
        for attachment in self:
            if attachment.res_model == 'documents.document' and attachment.res_id:
                try:
                    document = self.env['documents.document'].browse(attachment.res_id)
                    if document.exists():
                        attachment.document_category = document.category
                    else:
                        attachment.document_category = False
                except Exception as e:
                    _logger.warning(f"Could not get document category for attachment {attachment.name}: {e}")
                    attachment.document_category = False
            else:
                attachment.document_category = False

    @api.depends('res_model', 'res_id', 'res_name')
    def _compute_document_name(self):
        """Compute the actual document name from the linked document"""
        for attachment in self:
            if attachment.res_model == 'documents.document' and attachment.res_id:
                try:
                    document = self.env['documents.document'].browse(attachment.res_id)
                    if document.exists():
                        attachment.document_name = document.name
                    else:
                        attachment.document_name = False
                except Exception as e:
                    _logger.warning(f"Could not get document name for attachment {attachment.name}: {e}")
                    attachment.document_name = False
            else:
                attachment.document_name = False

    def action_recompute_document_name(self):
        """Manually recompute the document name field"""
        self.ensure_one()
        self._compute_document_name()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Field Recomputed'),
                'message': _('Document name has been recomputed.'),
                'type': 'success',
            }
        }
