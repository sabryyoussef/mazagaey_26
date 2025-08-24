# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    # Document relationships (One2many fields)
    document_ids = fields.One2many(
        'documents.document', 'linked_project_id',
        string='Documents'
    )
    required_document_ids = fields.One2many(
        'documents.document', 'linked_project_id',
        domain=[('category', '=', 'required')],
        string='Required Documents'
    )
    deliverable_document_ids = fields.One2many(
        'documents.document', 'linked_project_id',
        domain=[('category', '=', 'deliverable')],
        string='Deliverable Documents'
    )

    # Document count fields
    document_count = fields.Integer(
        compute='_compute_document_counts', 
        store=True,
        string='Total Documents'
    )
    required_document_count = fields.Integer(
        compute='_compute_document_counts', 
        store=True,
        string='Required Document Count'
    )
    deliverable_document_count = fields.Integer(
        compute='_compute_document_counts', 
        store=True,
        string='Deliverable Document Count'
    )

    # Temporary fields for document creation
    new_document_name = fields.Char('Document Name')
    new_document_category = fields.Selection([
        ('required', 'Required'),
        ('deliverable', 'Deliverable'),
        ('reference', 'Reference'),
        ('compliance', 'Compliance')
    ], string='Category', default='required')
    new_document_priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Critical')
    ], string='Priority', default='1')
    new_document_status = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('verified', 'Verified'),
        ('delivered', 'Delivered'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')
    new_document_expiry_date = fields.Date('Expiry Date')
    new_document_notes = fields.Text('Notes')
    new_document_tag_ids = fields.Many2many('documents.tag', string='Document Tags')
    


    documents_folder_id = fields.Many2one(
        'documents.document', 
        string='Documents Folder',
        help='Documents folder for this project in the Documents module'
    )
    
    project_files_count = fields.Integer(
        compute='_compute_project_files_count',
        string='Project Files',
        help='Number of files in the project folder'
    )
    
    project_folder_files = fields.Many2many(
        'ir.attachment',
        compute='_compute_project_folder_files',
        string='Project Folder Files',
        help='Files in the project documents folder'
    )
    
    # Note: Template functionality has been moved to project_templates_basic module

    @api.depends('document_ids', 'required_document_ids', 'deliverable_document_ids')
    def _compute_document_counts(self):
        """Compute document counts for projects"""
        for project in self:
            project.document_count = len(project.document_ids)
            project.required_document_count = len(project.required_document_ids)
            project.deliverable_document_count = len(project.deliverable_document_ids)



    @api.depends('documents_folder_id')
    def _compute_project_files_count(self):
        """Compute the number of files in the project folder"""
        for project in self:
            if project.documents_folder_id:
                # Count attachments in the project folder
                file_count = self.env['ir.attachment'].search_count([
                    ('folder_id', '=', project.documents_folder_id.id),
                    ('res_model', '=', 'documents.document')
                ])
                project.project_files_count = file_count
            else:
                project.project_files_count = 0

    @api.depends('documents_folder_id')
    def _compute_project_folder_files(self):
        """Compute the files in the project folder"""
        for project in self:
            if project.documents_folder_id:
                # Get attachments in the project folder (both linked to documents and directly to project)
                files = self.env['ir.attachment'].search([
                    '|',
                    ('folder_id', '=', project.documents_folder_id.id),
                    '&',
                    ('res_model', '=', 'project.project'),
                    ('res_id', '=', project.id)
                ])
                # Force recomputation of computed fields on attachments
                files._invalidate_cache(['document_name', 'document_category'])
                project.project_folder_files = files
            else:
                project.project_folder_files = self.env['ir.attachment']

    def action_refresh_project_files(self):
        """Refresh the project files list and recompute fields"""
        self.ensure_one()
        if self.documents_folder_id:
            # Force recomputation of the project folder files
            self._invalidate_cache(['project_folder_files'])
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Files Refreshed'),
                    'message': _('Project files list has been refreshed.'),
                    'type': 'success',
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Folder'),
                    'message': _('This project does not have a documents folder.'),
                    'type': 'warning',
                }
            }

    def _invalidate_document_fields(self):
        """Invalidate all document-related computed fields"""
        self._invalidate_cache(['document_count', 'required_document_count', 'deliverable_document_count'])

    def action_view_documents(self):
        """Open documents view for this project"""
        self.ensure_one()
        return {
            'name': _('Project Documents'),
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'list,form',
            'domain': [
                ('res_model', '=', 'project.project'),
                ('res_id', '=', self.id)
            ],
            'context': {
                'default_res_model': 'project.project',
                'default_res_id': self.id,
            },
        }

    def action_create_document(self):
        """Create a new document record for this project"""
        self.ensure_one()
        
        if not self.new_document_name:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Missing Information'),
                    'message': _('Please enter a document name.'),
                    'type': 'warning',
                }
            }
        
        # Ensure project has a folder
        self._ensure_project_folder()
        
        # Create the document record
        document_vals = {
            'name': self.new_document_name,
            'category': self.new_document_category,
            'priority': self.new_document_priority,
            'status': self.new_document_status,
            'expiry_date': self.new_document_expiry_date,
            'notes': self.new_document_notes,
            'tag_ids': [(6, 0, self.new_document_tag_ids.ids)] if self.new_document_tag_ids else False,
            'res_model': 'project.project',
            'res_id': self.id,
        }
        
        # Add folder_id if project has a documents folder
        if self.documents_folder_id:
            document_vals['folder_id'] = self.documents_folder_id.id
        
        new_document = self.env['documents.document'].create(document_vals)
        
        # Clear the temporary fields
        self.write({
            'new_document_name': False,
            'new_document_category': 'required',
            'new_document_priority': '1',
            'new_document_status': 'draft',
            'new_document_expiry_date': False,
            'new_document_notes': False,
            'new_document_tag_ids': [(5, 0, 0)],
        })
        
        # Refresh the document counts
        self.invalidate_recordset(['document_count', 'required_document_count', 'deliverable_document_count'])
        
        folder_name = self.documents_folder_id.name if self.documents_folder_id else 'Default'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Document Created'),
                'message': _('Document "%s" has been created in folder "%s". Use the Upload button to add the file.') % (new_document.name, folder_name),
                'type': 'success',
            }
        }

    def action_refresh_documents(self):
        """Force refresh of the document list in the UI"""
        self.ensure_one()
        
        # Force recomputation of all document-related fields
        self._invalidate_cache(['document_ids', 'document_count', 'required_document_count', 'deliverable_document_count'])
        
        # Force a complete page reload to refresh the view
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def _force_document_ui_refresh(self):
        """Force UI refresh after document creation"""
        self.ensure_one()
        
        # Force recomputation
        self._invalidate_cache(['document_ids', 'document_count', 'required_document_count', 'deliverable_document_count'])
        
        # Trigger a client action to refresh the view
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Documents Updated',
                'message': f'Documents have been updated for project {self.name}. Please refresh the page to see the changes.',
                'type': 'info',
                'sticky': False,
            }
        }

    def action_fix_document_tags(self):
        """Fix existing documents that might not have tag_ids field properly initialized"""
        self.ensure_one()
        documents = self.env['documents.document'].search([
            ('res_model', '=', 'project.project'),
            ('res_id', '=', self.id),
            ('active', '=', True)
        ])
        
        fixed_count = 0
        for doc in documents:
            # Force recomputation of tag_ids field
            doc._invalidate_cache(['tag_ids'])
            fixed_count += 1
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Tags Fixed'),
                'message': _('Fixed tag display for %d documents.') % fixed_count,
                'type': 'success',
            }
        }

    def action_copy_product_documents(self, product):
        """Copy documents from a product to this project"""
        self.ensure_one()
        
        # Get documents from the product
        product_documents = self.env['documents.document'].search([
            ('res_model', '=', 'product.template'),
            ('res_id', '=', product.id),
            ('active', '=', True)
        ])
        
        if not product_documents:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Documents'),
                    'message': _('No documents found in the selected product.'),
                    'type': 'warning',
                }
            }
        
        copied_count = 0
        for doc in product_documents:
            try:
                # Check if document already exists in project
                existing_doc = self.env['documents.document'].search([
                    ('res_model', '=', 'project.project'),
                    ('res_id', '=', self.id),
                    ('name', '=', doc.name),
                    ('category', '=', doc.category),
                    ('active', '=', True)
                ], limit=1)
                
                if existing_doc:
                    continue  # Skip if already exists
                
                # Get or create project folder (optional)
                project_folder = self.env['documents.document']._get_project_folder(self)
                
                # Create copy for project
                new_doc_vals = {
                    'name': doc.name,
                    'description': doc.description,
                    'tag_ids': [(6, 0, doc.tag_ids.ids)] if doc.tag_ids else False,  # Copy tags
                    'category': doc.category,
                    'status': 'draft',  # Reset status for new context
                    'expiry_date': doc.expiry_date,
                    'priority': doc.priority,
                    'notes': doc.notes,
                    'res_model': 'project.project',
                    'res_id': self.id,
                }
                
                # Add folder_id only if folder was created successfully
                if project_folder:
                    new_doc_vals['folder_id'] = project_folder.id
                
                self.env['documents.document'].create(new_doc_vals)
                copied_count += 1
                    
            except Exception as e:
                _logger.error(f"Error copying document {doc.name}: {e}")
        
        if copied_count > 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Documents Copied'),
                    'message': _('%d documents copied from product.') % copied_count,
                    'type': 'success',
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Documents Copied'),
                    'message': _('All documents already exist in the project.'),
                                    'type': 'info',
            }
        }

    def action_copy_from_product(self):
        """Open wizard to copy documents from a selected product to this project"""
        self.ensure_one()
        
        # Find products that have documents
        products_with_documents = self.env['product.template'].search([
            ('id', 'in', self.env['documents.document'].search([
                ('res_model', '=', 'product.template'),
                ('active', '=', True)
            ]).mapped('res_id'))
        ])
        
        if not products_with_documents:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Products with Documents'),
                    'message': _('No products found with documents to copy.'),
                    'type': 'warning',
                }
            }
        
        # If only one product, use it directly
        if len(products_with_documents) == 1:
            return {
                'name': _('Copy Documents from Product'),
                'type': 'ir.actions.act_window',
                'res_model': 'copy.documents.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_source_model': 'product.template',
                    'default_source_id': products_with_documents.id,
                    'default_source_product_id': products_with_documents.id,
                    'default_target_model': 'project.project',
                    'default_target_id': self.id,
                    'default_target_project_id': self.id,
                }
            }
        
        # If multiple products, show selection dialog
        return {
            'name': _('Select Product to Copy Documents From'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'list',
            'view_id': self.env.ref('unified_documents.view_product_template_list_copy_selection').id,
            'target': 'new',
            'domain': [('id', 'in', products_with_documents.ids)],
            'context': {
                'default_target_project_id': self.id,
            }
        }

    def _ensure_project_folder(self):
        """Ensure the project has a documents folder"""
        
        if not self.documents_folder_id:
            try:
                # Look for existing folder
                existing_folder = self.env['documents.document'].search([
                    ('name', '=', self.name),
                    ('type', '=', 'folder')
                ], limit=1)
                
                if existing_folder:
                    self.documents_folder_id = existing_folder.id
                else:
                    # Create new folder
                    new_folder = self.env['documents.document'].create({
                        'name': self.name,
                        'type': 'folder',
                        'company_id': self.company_id.id if self.company_id else False,
                    })
                    self.documents_folder_id = new_folder.id
            except Exception as e:
                _logger.error(f"Failed to create documents folder for project {self.name}: {e}")

    def action_create_project_folder(self):
        """Create or assign documents folder for this project"""
        self.ensure_one()
        self._ensure_project_folder()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Folder Created'),
                'message': _('Documents folder "%s" has been created/assigned to this project.') % (self.documents_folder_id.name if self.documents_folder_id else self.name),
                'type': 'success',
            }
        }

    def action_view_project_folder(self):
        """Open the project's documents folder"""
        self.ensure_one()
        if self.documents_folder_id:
            return {
                'name': _('Project Documents Folder'),
                'type': 'ir.actions.act_window',
                'res_model': 'documents.document',
                'res_id': self.documents_folder_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Folder'),
                    'message': _('This project does not have a documents folder yet. Create one first.'),
                    'type': 'warning',
                }
            }

    def action_view_project_files(self):
        """View all files in the project's documents folder"""
        self.ensure_one()
        if self.documents_folder_id:
            return {
                'name': _('Project Files - %s') % self.name,
                'type': 'ir.actions.act_window',
                'res_model': 'ir.attachment',
                'view_mode': 'list',
                'view_id': self.env.ref('unified_documents.view_ir_attachment_tree_project_files').id,
                'domain': [
                    '|',
                    ('folder_id', '=', self.documents_folder_id.id),
                    '&',
                    ('res_model', '=', 'project.project'),
                    ('res_id', '=', self.id)
                ],
                'context': {
                    'default_folder_id': self.documents_folder_id.id,
                    'default_res_model': 'documents.document',
                },
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Folder'),
                    'message': _('This project does not have a documents folder yet. Create one first.'),
                    'type': 'warning',
                }
            }

    def action_view_required_documents(self):
        """Open required documents view for this project"""
        self.ensure_one()
        return {
            'name': _('Required Documents - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'list,form',
            'domain': [
                ('res_model', '=', 'project.project'),
                ('res_id', '=', self.id),
                ('category', '=', 'required')
            ],
            'context': {
                'default_res_model': 'project.project',
                'default_res_id': self.id,
                'default_category': 'required',
            },
        }

    def action_view_deliverable_documents(self):
        """Open deliverable documents view for this project"""
        self.ensure_one()
        return {
            'name': _('Deliverable Documents - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'list,form',
            'domain': [
                ('res_model', '=', 'project.project'),
                ('res_id', '=', self.id),
                ('category', '=', 'deliverable')
            ],
            'context': {
                'default_res_model': 'project.project',
                'default_res_id': self.id,
                'default_category': 'deliverable',
            },
        }

    def action_upload_project_document(self):
        """Upload a new document for this project"""
        self.ensure_one()
        return {
            'name': _('Upload Document for %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_res_model': 'project.project',
                'default_res_id': self.id,
                'default_linked_project_id': self.id,
                'default_name': 'New Document',
                'default_category': 'required',
                'form_view_initial_mode': 'edit',
            }
        }

    def action_test_document_linking(self):
        """Test action to verify document linking - can be called from project form"""
        self.ensure_one()
        
        _logger.info(f"🧪 Testing document linking for project {self.name} (ID: {self.id})")
        
        # Check documents linked to this project
        docs_linked = self.env['documents.document'].search([('linked_project_id', '=', self.id)])
        _logger.info(f"📋 Documents with linked_project_id={self.id}: {[(d.id, d.name, d.category) for d in docs_linked]}")
        
        # Check documents with res_model and res_id
        docs_res = self.env['documents.document'].search([
            ('res_model', '=', 'project.project'),
            ('res_id', '=', self.id)
        ])
        _logger.info(f"📋 Documents with res_model='project.project' and res_id={self.id}: {[(d.id, d.name, d.category) for d in docs_res]}")
        
        # Check project's document_ids field
        self._invalidate_cache(['document_ids', 'document_count', 'required_document_count', 'deliverable_document_count'])
        _logger.info(f"📋 Project document_ids count: {len(self.document_ids)}")
        _logger.info(f"📋 Project document_ids: {[(d.id, d.name, d.category) for d in self.document_ids]}")
        
        # Check project's computed counts
        _logger.info(f"📊 Project document_count: {self.document_count}")
        _logger.info(f"📊 Project required_document_count: {self.required_document_count}")
        _logger.info(f"📊 Project deliverable_document_count: {self.deliverable_document_count}")
        
        # Create a test document if none exist
        if not docs_linked and not docs_res:
            _logger.info(f"🧪 No documents found, creating test document")
            test_doc = self.env['documents.document'].create({
                'name': f"TEST DOC - {self.name}",
                'res_model': 'project.project',
                'res_id': self.id,
                'linked_project_id': self.id,
                'category': 'required',
                'status': 'draft',
                'priority': '1',
                'description': 'Test document for debugging',
                'notes': f"Test document from project: {self.name}",
            })
            _logger.info(f"🧪 Created test document: {test_doc.name} (ID: {test_doc.id})")
            
            # Force recomputation
            self._invalidate_cache(['document_ids', 'document_count', 'required_document_count', 'deliverable_document_count'])
            
            message = f"Test Document Created!\n\nProject: {self.name} (ID: {self.id})\n"
            message += f"Test Document: {test_doc.name} (ID: {test_doc.id})\n"
            message += f"Document linked_project_id: {test_doc.linked_project_id.id if test_doc.linked_project_id else 'None'}\n"
            message += f"Document res_model: {test_doc.res_model}, res_id: {test_doc.res_id}\n"
            message += f"Project document_ids count after creation: {len(self.document_ids)}\n"
            message += f"Project document_count after creation: {self.document_count}"
        else:
            message = f"Document Linking Test Results for {self.name}:\n\n"
            message += f"Project ID: {self.id}\n"
            message += f"Documents with linked_project_id: {len(docs_linked)}\n"
            message += f"Documents with res_model/res_id: {len(docs_res)}\n"
            message += f"Project document_ids count: {len(self.document_ids)}\n"
            message += f"Project document_count: {self.document_count}\n"
            message += f"Project required_document_count: {self.required_document_count}\n"
            message += f"Project deliverable_document_count: {self.deliverable_document_count}\n\n"
            
            if docs_linked:
                message += "Documents with linked_project_id:\n"
                for doc in docs_linked:
                    message += f"  - {doc.name} (ID: {doc.id}, Category: {doc.category})\n"
            
            if docs_res:
                message += "Documents with res_model/res_id:\n"
                for doc in docs_res:
                    message += f"  - {doc.name} (ID: {doc.id}, Category: {doc.category})\n"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Document Linking Test',
                'message': message,
                'type': 'info',
            }
        }
