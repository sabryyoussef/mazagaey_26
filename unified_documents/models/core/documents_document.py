# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class DocumentsDocument(models.Model):
    _inherit = 'documents.document'
    _description = 'Document with Extended Fields'

    category = fields.Selection([
        ('required', 'Required'),
        ('deliverable', 'Deliverable'),
        ('reference', 'Reference'),
        ('compliance', 'Compliance')
    ], string='Category', required=True, default='required', tracking=True)

    status = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('verified', 'Verified'),
        ('delivered', 'Delivered'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    expiry_date = fields.Date('Expiry Date', tracking=True)
    reminder_days = fields.Integer('Reminder Days', default=30,
                                   help='Days before expiry to send reminder')
    is_expired = fields.Boolean('Is Expired', compute='_compute_is_expired', store=True, tracking=True)
    is_verified = fields.Boolean('Verified', default=False, tracking=True)
    verification_date = fields.Date('Verification Date', readonly=True, tracking=True)
    verified_by = fields.Many2one('res.users', string='Verified By', readonly=True, tracking=True)

    priority = fields.Selection([
        ('0', 'Low'), ('1', 'Normal'), ('2', 'High'), ('3', 'Critical')
    ], string='Priority', default='1', tracking=True)

    notes = fields.Text('Notes', tracking=True)

    # Use unique field names to avoid conflicts with documents_product module
    linked_product_id = fields.Many2one('product.template', string='Linked Product', ondelete='cascade', index=True)
    linked_project_id = fields.Many2one('project.project', string='Linked Project', ondelete='cascade', index=True)
    
    # Project template relationships (using existing project.project as template)
    linked_project_template_id = fields.Many2one('project.project', string='Linked Project Template', ondelete='cascade', index=True)
    
    # Folder contents fields (only for folder type documents)
    folder_document_ids = fields.One2many(
        'documents.document', 'folder_id',
        string='Folder Documents',
        domain=[('type', '!=', 'folder')],
        help='Documents inside this folder'
    )
    
    folder_document_count = fields.Integer(
        compute='_compute_folder_counts',
        string='Document Count',
        help='Number of documents in this folder'
    )
    
    folder_subfolder_count = fields.Integer(
        compute='_compute_folder_counts',
        string='Subfolder Count',
        help='Number of subfolders in this folder'
    )
    
    folder_size_total = fields.Float(
        compute='_compute_folder_size',
        string='Total Size (MB)',
        help='Total size of all documents in this folder'
    )
    
    last_modified_date = fields.Datetime(
        compute='_compute_last_modified',
        string='Last Modified',
        help='Last modification date of any document in this folder'
    )
    
    # Computed fields for folder summary statistics
    folder_category_summary = fields.Char(
        compute='_compute_folder_summary',
        string='Category Summary',
        help='Summary of categories in this folder'
    )
    
    folder_status_summary = fields.Char(
        compute='_compute_folder_summary',
        string='Status Summary',
        help='Summary of statuses in this folder'
    )
    
    folder_expired_summary = fields.Char(
        compute='_compute_folder_summary',
        string='Expired Summary',
        help='Summary of expired documents in this folder'
    )
    
    folder_verified_summary = fields.Char(
        compute='_compute_folder_summary',
        string='Verified Summary',
        help='Summary of verified documents in this folder'
    )
    
    # Document preview fields
    selected_document_id = fields.Many2one(
        'documents.document',
        string='Selected Document',
        help='Currently selected document for preview'
    )
    
    document_preview = fields.Binary(
        compute='_compute_document_preview',
        string='Document Preview',
        help='Preview of the selected document (thumbnail for images, content for text/PDF)'
    )
    
    document_preview_text = fields.Char(
        related='selected_document_id.name',
        string='Document Name',
        help='Name of the selected document'
    )
    
    document_preview_content = fields.Text(
        compute='_compute_document_preview_content',
        string='Document Content',
        help='Content of the selected document (for text/PDF files)'
    )
    
    document_preview_metadata = fields.Text(
        compute='_compute_document_preview_metadata',
        string='Document Metadata',
        help='Document metadata (type, size, dates)'
    )

    @api.depends('expiry_date')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for rec in self:
            rec.is_expired = bool(rec.expiry_date and rec.expiry_date < today)

    @api.constrains('expiry_date', 'status')
    def _check_expiry_date(self):
        today = fields.Date.today()
        for rec in self:
            if rec.expiry_date and rec.expiry_date < today and rec.status in ('draft', 'pending'):
                raise ValidationError(_("Expiry date cannot be in the past for documents in draft or pending status."))

    def action_mark_verified(self):
        self.ensure_one()
        self.write({
            'is_verified': True,
            'verification_date': fields.Date.today(),
            'verified_by': self.env.user.id,
            'status': 'verified',
        })
        return True

    def action_mark_completed(self):
        self.ensure_one()
        self.write({'status': 'completed'})
        return True

    def action_mark_delivered(self):
        self.ensure_one()
        if self.category == 'deliverable':
            self.write({'status': 'delivered'})
        return True

    def action_reset_to_draft(self):
        self.ensure_one()
        self.write({
            'status': 'draft',
            'is_verified': False,
            'verification_date': False,
            'verified_by': False,
        })
        return True

    @api.depends('folder_document_ids', 'folder_document_ids.type')
    def _compute_folder_counts(self):
        """Compute document and subfolder counts for folders"""
        for record in self:
            if record.type == 'folder':
                documents = record.folder_document_ids
                record.folder_document_count = len(documents.filtered(lambda d: d.type != 'folder'))
                record.folder_subfolder_count = len(documents.filtered(lambda d: d.type == 'folder'))
            else:
                record.folder_document_count = 0
                record.folder_subfolder_count = 0
    
    @api.depends('folder_document_ids', 'folder_document_ids.file_size')
    def _compute_folder_size(self):
        """Compute total size of all documents in folder"""
        for record in self:
            if record.type == 'folder':
                total_size = sum(record.folder_document_ids.mapped('file_size') or [0])
                record.folder_size_total = total_size / (1024 * 1024)  # Convert to MB
            else:
                record.folder_size_total = 0.0
    
    @api.depends('folder_document_ids', 'folder_document_ids.write_date')
    def _compute_last_modified(self):
        """Compute last modification date of any document in folder"""
        for record in self:
            if record.type == 'folder' and record.folder_document_ids:
                last_modified = max(record.folder_document_ids.mapped('write_date'))
                record.last_modified_date = last_modified
            else:
                record.last_modified_date = False
    
    @api.depends('selected_document_id', 'selected_document_id.thumbnail', 'selected_document_id.datas')
    def _compute_document_preview(self):
        """Compute document preview based on type"""
        for record in self:
            if record.selected_document_id:
                doc = record.selected_document_id
                if doc.type == 'binary' and doc.thumbnail:
                    # Show thumbnail for images
                    record.document_preview = doc.thumbnail
                else:
                    record.document_preview = False
            else:
                record.document_preview = False
    
    @api.depends('selected_document_id', 'selected_document_id.datas', 'selected_document_id.mimetype')
    def _compute_document_preview_content(self):
        """Compute document content for text/PDF files"""
        for record in self:
            if record.selected_document_id:
                doc = record.selected_document_id
                if doc.type == 'binary' and doc.datas:
                    # For text files, try to decode content
                    if doc.mimetype and ('text/' in doc.mimetype or 'pdf' in doc.mimetype):
                        try:
                            import base64
                            content = base64.b64decode(doc.datas).decode('utf-8', errors='ignore')
                            # Limit content length for preview
                            record.document_preview_content = content[:1000] + '...' if len(content) > 1000 else content
                        except:
                            record.document_preview_content = "Unable to preview file content"
                    else:
                        record.document_preview_content = f"File type: {doc.mimetype or 'Unknown'}"
                else:
                    record.document_preview_content = doc.notes or "No content available"
            else:
                record.document_preview_content = ""
    
    @api.depends('selected_document_id')
    def _compute_document_preview_metadata(self):
        """Compute document metadata"""
        for record in self:
            if record.selected_document_id:
                doc = record.selected_document_id
                metadata = []
                metadata.append(f"Type: {doc.type or 'Unknown'}")
                if doc.file_size:
                    metadata.append(f"Size: {doc.file_size} bytes")
                if doc.create_date:
                    metadata.append(f"Created: {doc.create_date.strftime('%Y-%m-%d %H:%M')}")
                if doc.owner_id:
                    metadata.append(f"Owner: {doc.owner_id.name}")
                if doc.category:
                    metadata.append(f"Category: {doc.category}")
                if doc.status:
                    metadata.append(f"Status: {doc.status}")
                
                record.document_preview_metadata = "\n".join(metadata)
            else:
                record.document_preview_metadata = ""
    
    @api.depends('folder_document_ids', 'folder_document_ids.category', 'folder_document_ids.status', 'folder_document_ids.is_expired', 'folder_document_ids.is_verified')
    def _compute_folder_summary(self):
        """Compute folder summary statistics"""
        for record in self:
            if record.type == 'folder' and record.folder_document_ids:
                # Category summary
                categories = record.folder_document_ids.mapped('category')
                unique_categories = list(set(categories))
                if len(unique_categories) == 1:
                    record.folder_category_summary = unique_categories[0]
                else:
                    record.folder_category_summary = f"Mixed ({', '.join(unique_categories)})"
                
                # Status summary
                statuses = record.folder_document_ids.mapped('status')
                unique_statuses = list(set(statuses))
                if len(unique_statuses) == 1:
                    record.folder_status_summary = unique_statuses[0]
                else:
                    record.folder_status_summary = f"Mixed ({', '.join(unique_statuses)})"
                
                # Expired summary (Option A: Summary statistics)
                expired_count = len(record.folder_document_ids.filtered(lambda d: d.is_expired))
                total_count = len(record.folder_document_ids)
                active_count = total_count - expired_count
                
                if expired_count == 0:
                    record.folder_expired_summary = f"All active ({active_count} documents)"
                elif active_count == 0:
                    record.folder_expired_summary = f"All expired ({expired_count} documents)"
                else:
                    record.folder_expired_summary = f"Mixed ({active_count} active, {expired_count} expired)"
                
                # Verified summary (Option C: Count-based display)
                verified_count = len(record.folder_document_ids.filtered(lambda d: d.is_verified))
                record.folder_verified_summary = f"{verified_count}/{total_count} verified"
                
            else:
                record.folder_category_summary = ""
                record.folder_status_summary = ""
                record.folder_expired_summary = ""
                record.folder_verified_summary = ""
    
    def action_refresh_folder_contents(self):
        """Refresh folder contents"""
        self.ensure_one()
        if self.type == 'folder':
            self._compute_folder_counts()
            self._compute_folder_size()
            self._compute_last_modified()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Folder Refreshed'),
                'message': _('Folder contents have been refreshed.'),
                'type': 'success',
            }
        }
    
    def action_upload_to_folder(self):
        """Open upload dialog for folder"""
        self.ensure_one()
        if self.type != 'folder':
            return False
        
        return {
            'name': _('Upload Document to Folder'),
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_folder_id': self.id,
                'default_type': 'binary',
            }
        }
    
    def action_create_subfolder(self):
        """Create a new subfolder"""
        self.ensure_one()
        if self.type != 'folder':
            return False
        
        return {
            'name': _('Create Subfolder'),
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_folder_id': self.id,
                'default_type': 'folder',
            }
        }
    
    def action_upload_attachment(self):
        """Upload attachment to this document"""
        self.ensure_one()
        
        return {
            'name': _('Upload Attachment'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_res_model': 'documents.document',
                'default_res_id': self.id,
                'default_name': self.name,
            }
        }
    
    def action_upload_attachment_to_document(self):
        """Upload attachment to a specific document in the list"""
        self.ensure_one()
        
        return {
            'name': _('Upload Attachment to Document'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_res_model': 'documents.document',
                'default_res_id': self.id,
                'default_name': f'Attachment for {self.name}',
            }
        }
    
    def action_clear_preview(self):
        """Clear the document preview"""
        self.ensure_one()
        self.selected_document_id = False
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Preview Cleared'),
                'message': _('Document preview has been cleared.'),
                'type': 'info',
            }
        }
    
    def action_refresh_preview(self):
        """Refresh the preview computed fields"""
        self.ensure_one()
        if self.selected_document_id:
            # Force recompute of preview fields
            self._compute_document_preview()
            self._compute_document_preview_content()
            self._compute_document_preview_metadata()
        
        return True
    
    def action_preview_document(self):
        """Preview the selected document within the form"""
        self.ensure_one()
        
        # Find the parent folder document that contains this document
        parent_document = self.env['documents.document'].search([
            ('type', '=', 'folder'),
            ('folder_document_ids', 'in', self.id)
        ], limit=1)
        
        if parent_document:
            # Set the selected document for preview
            parent_document.write({'selected_document_id': self.id})
            
            # Return action to refresh the form and show notification
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Document Preview'),
                    'message': _('Document preview is now displayed below.'),
                    'type': 'success',
                }
            }
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Preview Error'),
                'message': _('Could not load document preview.'),
                'type': 'warning',
            }
        }
    
    def action_download_document(self):
        """Download the document"""
        self.ensure_one()
        if self.type != 'binary':
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Download Not Available'),
                    'message': _('Download is only available for binary documents.'),
                    'type': 'warning',
                }
            }
        
        # Check if attachment exists and has data
        if not self.attachment_id or not self.attachment_id.datas:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Content Available'),
                    'message': _('This document has no content to download.'),
                    'type': 'warning',
                }
            }
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/documents.document/{self.id}/datas?download=true',
            'target': 'self',
        }
    
    def action_open_document(self):
        """Open the document in a new window"""
        self.ensure_one()
        
        if self.type == 'binary':
            return self.action_download_document()
        elif self.type == 'url':
            return {
                'type': 'ir.actions.act_url',
                'url': self.url,
                'target': 'new',
            }
        elif self.type == 'folder':
            return {
                'name': self.name,
                'type': 'ir.actions.act_window',
                'res_model': 'documents.document',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'current',
            }
        
        return False

    def _default_upload_context(self):
        self.ensure_one()
        ctx = {
            'default_res_model': 'documents.document',
            'default_res_id': self.id,
        }
        # if linked to a project, default the folder
        if self.res_model == 'project.project' and self.res_id:
            project = self.env['project.project'].browse(self.res_id)
            if project.exists() and project.documents_folder_id:
                ctx['default_folder_id'] = project.documents_folder_id.id
        return ctx

    def action_upload_file(self):
        self.ensure_one()
        
        # Simple direct attachment approach
        return {
            'name': _('Upload File for %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name': f"{self.name}_attachment",
                'default_folder_id': self.folder_id.id if self.folder_id else False,
                # Store document info in context but don't set as default
                'upload_for_document': self.id,
                'document_original_res_model': self.res_model,
                'document_original_res_id': self.res_id,
            },
        }

    def action_view_document(self):
        self.ensure_one()
        return {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model
    def _get_or_create_folder(self, folder_name, parent_folder=None):
        try:
            domain = [('name', '=', folder_name),
                      ('parent_folder_id', '=', parent_folder.id if parent_folder else False)]
            folder = self.env['documents.folder'].search(domain, limit=1)
            if not folder:
                folder = self.env['documents.folder'].create({
                    'name': folder_name,
                    'parent_folder_id': parent_folder.id if parent_folder else False,
                })
            return folder
        except Exception as e:
            _logger.warning("Could not create folder '%s': %s", folder_name, e)
            return False

    @api.model
    def _get_project_folder(self, project):
        if not project:
            return False
        return self._get_or_create_folder(project.name, self._get_or_create_folder('Projects'))

    @api.model
    def _get_product_folder(self, product):
        if not product:
            return False
        return self._get_or_create_folder(product.name, self._get_or_create_folder('Products'))

    def _auto_assign_to_project_folder(self):
        for doc in self:
            if doc.res_model == 'project.project' and doc.res_id:
                try:
                    project = self.env['project.project'].browse(doc.res_id)
                    if project.exists():
                        if hasattr(project, '_ensure_project_folder'):
                            project._ensure_project_folder()
                        if project.documents_folder_id and doc.folder_id != project.documents_folder_id:
                            doc.folder_id = project.documents_folder_id.id
                except Exception as e:
                    _logger.error("Failed to assign doc '%s' to project folder: %s", doc.name, e)

    @api.model
    def default_get(self, fields_list):
        """Override default_get to ensure proper linking from context"""
        defaults = super().default_get(fields_list)
        ctx = self.env.context
        
        # ALWAYS set these fields from context if available, regardless of fields_list
        if ctx.get('default_product_id'):
            defaults['linked_product_id'] = ctx.get('default_product_id')
            
        if ctx.get('default_project_id'):
            defaults['linked_project_id'] = ctx.get('default_project_id')
            
        if ctx.get('default_res_model'):
            defaults['res_model'] = ctx.get('default_res_model')
            
        if ctx.get('default_res_id'):
            defaults['res_id'] = ctx.get('default_res_id')
            
        return defaults

    @api.model_create_multi
    def create(self, vals_list):
        ctx = dict(self.env.context or {})
        processed = []
        for vals in vals_list:
            v = dict(vals)

            # Normalize tag_ids input
            if 'tag_ids' in v and isinstance(v['tag_ids'], list) and v['tag_ids'] == []:
                v['tag_ids'] = [(6, 0, [])]

            # 1) Prefer explicit product_id/project_id if provided
            product_id = v.get('linked_product_id') or ctx.get('default_product_id')
            project_id = v.get('linked_project_id') or ctx.get('default_project_id')

            # 2) Set the Many2one fields explicitly if not already set
            if product_id and not v.get('linked_product_id'):
                v['linked_product_id'] = product_id
            if project_id and not v.get('linked_project_id'):
                v['linked_project_id'] = project_id

            # 3) Backfill res_model/res_id for linkage (even if context is empty)
            if not v.get('res_model') and not v.get('res_id'):
                if product_id:
                    v['res_model'] = 'product.template'
                    v['res_id'] = product_id
                elif project_id:
                    v['res_model'] = 'project.project'
                    v['res_id'] = project_id

            processed.append(v)

        docs = super().create(processed)
        docs._auto_assign_to_project_folder()
        return docs

    def write(self, vals):
        # CRITICAL FIX: Prevent res_model/res_id changes during file upload
        # This was causing documents to disappear from project/product lists
        if self.env.context.get('preserve_linking') or vals.get('attachment_id'):
            # If we're preserving linking or this is an attachment update, 
            # don't allow res_model/res_id to be changed
            if 'res_model' in vals or 'res_id' in vals:
                _logger.warning("BLOCKING res_model/res_id change during upload to preserve document linking")
                # Remove the problematic fields from vals
                vals.pop('res_model', None)
                vals.pop('res_id', None)

        res = super().write(vals)

        if 'res_model' in vals or 'res_id' in vals:
            self._auto_assign_to_project_folder()
        return res
