# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class DocumentsDocument(models.Model):
    _inherit = 'documents.document'

    # Additional field to link documents to projects
    linked_project_id = fields.Many2one(
        'project.project', 
        string='Linked Project',
        help='Project this document is specifically linked to'
    )

    def action_upload_complete(self):
        """Complete the upload process and close the dialog"""
        self.ensure_one()
        
        # Validate that file was uploaded
        if not self.datas and self.type == 'file':
            raise ValidationError(_("Please select a file to upload."))
        
        # Ensure proper linking if uploaded from project
        if self.linked_project_id and not self.res_id:
            self.write({
                'res_model': 'project.project',
                'res_id': self.linked_project_id.id,
            })
        
        # Return action to close dialog and refresh parent view
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Document "%s" has been uploaded successfully.') % self.name,
                'type': 'success',
                'sticky': False,
            }
        }

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to handle project folder assignment"""
        records = super().create(vals_list)
        
        for record in records:
            # If document is linked to a project and no folder is set, assign to project folder
            if record.linked_project_id and not record.folder_id:
                project = record.linked_project_id
                if project.documents_folder_id:
                    record.folder_id = project.documents_folder_id
                elif hasattr(project, '_ensure_project_folder'):
                    project._ensure_project_folder()
                    if project.documents_folder_id:
                        record.folder_id = project.documents_folder_id
        
        return records
