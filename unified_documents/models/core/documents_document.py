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
