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

    # Document category counts
    required_document_count = fields.Integer(
        compute='_compute_document_category_counts',
        string='Required Documents'
    )
    deliverable_document_count = fields.Integer(
        compute='_compute_document_category_counts',
        string='Deliverable Documents'
    )
    reference_document_count = fields.Integer(
        compute='_compute_document_category_counts',
        string='Reference Documents'
    )
    compliance_document_count = fields.Integer(
        compute='_compute_document_category_counts',
        string='Compliance Documents'
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

    @api.depends('document_ids')
    def _compute_document_category_counts(self):
        """Compute document counts by category"""
        for project in self:
            project.required_document_count = len(project.document_ids.filtered(lambda d: d.category == 'required'))
            project.deliverable_document_count = len(project.document_ids.filtered(lambda d: d.category == 'deliverable'))
            project.reference_document_count = len(project.document_ids.filtered(lambda d: d.category == 'reference'))
            project.compliance_document_count = len(project.document_ids.filtered(lambda d: d.category == 'compliance'))

    def action_copy_product_documents_and_create_tasks(self):
        """Manual action to copy documents from product and create document category tasks"""
        self.ensure_one()
        
        # Find sale order lines for this project
        sale_lines = self.env['sale.order.line'].search([
            ('project_id', '=', self.id),
            ('product_id.document_ids', '!=', False)
        ])
        
        if not sale_lines:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Documents Found',
                    'message': 'No products with documents found for this project.',
                    'type': 'warning',
                }
            }
        
        created_tasks = []
        for line in sale_lines:
            # Copy documents
            if line.copy_documents_to_project():
                # Create tasks (this will be called automatically by copy_documents_to_project)
                pass
        
        # Force recomputation of document counts
        self._invalidate_cache(['document_ids', 'required_document_count', 'deliverable_document_count', 'reference_document_count', 'compliance_document_count'])
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Documents Copied & Tasks Created',
                'message': f'Documents copied and document category tasks created for project {self.name}.',
                'type': 'success',
            }
        }

    def create_document_category_tasks(self):
        """Create tasks for each document category that has documents"""
        self.ensure_one()
        
        # Get document counts by category
        required_count = len(self.document_ids.filtered(lambda d: d.category == 'required'))
        deliverable_count = len(self.document_ids.filtered(lambda d: d.category == 'deliverable'))
        reference_count = len(self.document_ids.filtered(lambda d: d.category == 'reference'))
        compliance_count = len(self.document_ids.filtered(lambda d: d.category == 'compliance'))
        
        created_tasks = []
        
        # Create task for Required Documents
        if required_count > 0:
            task_vals = {
                'name': f'Required Documents ({required_count})',
                'description': f'Process {required_count} required documents for project {self.name}',
                'project_id': self.id,
                'allocated_hours': required_count * 0.5,  # 30 min per document
            }
            task = self.env['project.task'].create(task_vals)
            created_tasks.append(task)
        
        # Create task for Deliverable Documents
        if deliverable_count > 0:
            task_vals = {
                'name': f'Deliverable Documents ({deliverable_count})',
                'description': f'Prepare {deliverable_count} deliverable documents for project {self.name}',
                'project_id': self.id,
                'allocated_hours': deliverable_count * 1.0,  # 1 hour per document
            }
            task = self.env['project.task'].create(task_vals)
            created_tasks.append(task)
        
        # Create task for Reference Documents
        if reference_count > 0:
            task_vals = {
                'name': f'Reference Documents ({reference_count})',
                'description': f'Review {reference_count} reference documents for project {self.name}',
                'project_id': self.id,
                'allocated_hours': reference_count * 0.25,  # 15 min per document
            }
            task = self.env['project.task'].create(task_vals)
            created_tasks.append(task)
        
        # Create task for Compliance Documents
        if compliance_count > 0:
            task_vals = {
                'name': f'Compliance Documents ({compliance_count})',
                'description': f'Process {compliance_count} compliance documents for project {self.name}',
                'project_id': self.id,
                'allocated_hours': compliance_count * 1.5,  # 1.5 hours per document
            }
            task = self.env['project.task'].create(task_vals)
            created_tasks.append(task)
        
        return created_tasks

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
                # Get attachments in the project folder
                files = self.env['ir.attachment'].search([
                    ('folder_id', '=', project.documents_folder_id.id),
                    ('res_model', '=', 'documents.document')
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

    def action_direct_copy_documents(self):
        """Directly copy all documents from products linked to this project's sales orders"""
        self.ensure_one()
        
        _logger.info(f"Starting direct copy for project: {self.name} (ID: {self.id})")
        
        # Get products from sales order lines linked to this project
        sale_order_lines = self.env['sale.order.line'].search([
            ('project_id', '=', self.id)
        ])
        
        _logger.info(f"Found {len(sale_order_lines)} sale order lines for project {self.name}")
        
        if not sale_order_lines:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Sales Orders'),
                    'message': _('This project is not linked to any sales orders. Please link it to a sales order first.'),
                    'type': 'warning',
                }
            }
        
        # Get products from the sales order lines
        products = sale_order_lines.mapped('product_id.product_tmpl_id')
        _logger.info(f"Found {len(products)} products from sale order lines")
        
        # Filter products that have documents
        products_with_documents = products.filtered(lambda p: p.document_ids)
        _logger.info(f"Found {len(products_with_documents)} products with documents")
        
        if not products_with_documents:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Products with Documents'),
                    'message': _('None of the products in this project\'s sales orders have documents to copy.'),
                    'type': 'warning',
                }
            }
        
        # Copy documents from each product
        total_copied = 0
        total_documents = 0
        
        for product in products_with_documents:
            _logger.info(f"Processing product: {product.name} with {len(product.document_ids)} documents")
            total_documents += len(product.document_ids)
            
            try:
                # Use the unified document service to copy documents
                service = self.env['unified.document.service']
                _logger.info(f"Calling copy_product_documents_to_project for product {product.name}")
                
                copied_docs = service.copy_product_documents_to_project(self, product)
                _logger.info(f"Service returned: {copied_docs} (type: {type(copied_docs)})")
                
                # Count the total documents copied from the returned dictionary
                if copied_docs and isinstance(copied_docs, dict):
                    docs_copied = sum(len(docs) for docs in copied_docs.values())
                    total_copied += docs_copied
                    _logger.info(f"Copied {docs_copied} documents from product {product.name}")
                elif copied_docs:
                    # If it's a number, use it directly
                    total_copied += copied_docs
                    _logger.info(f"Copied {copied_docs} documents from product {product.name}")
                else:
                    _logger.warning(f"No documents copied from product {product.name}")
                    
            except Exception as e:
                _logger.error(f"Failed to copy documents from product {product.name}: {e}")
                import traceback
                _logger.error(f"Traceback: {traceback.format_exc()}")
        
        _logger.info(f"Final result: {total_copied} documents copied from {len(products_with_documents)} products")
        
        if total_copied > 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Documents Copied'),
                    'message': f"Successfully copied {total_copied} documents from {len(products_with_documents)} products.",
                    'type': 'success',
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Copy Failed'),
                    'message': _('Failed to copy documents. Please check if documents exist and try again.'),
                    'type': 'error',
                }
            }

    def action_copy_from_product(self):
        """Open wizard to copy documents from products linked to this project's sales orders"""
        self.ensure_one()
        
        # Get products from sales order lines linked to this project
        sale_order_lines = self.env['sale.order.line'].search([
            ('project_id', '=', self.id)
        ])
        
        if not sale_order_lines:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Sales Orders'),
                    'message': _('This project is not linked to any sales orders. Please link it to a sales order first.'),
                    'type': 'warning',
                }
            }
        
        # Get products from the sales order lines
        products = sale_order_lines.mapped('product_id.product_tmpl_id')
        
        # Filter products that have documents
        products_with_documents = products.filtered(lambda p: p.document_ids)
        
        if not products_with_documents:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Products with Documents'),
                    'message': _('None of the products in this project\'s sales orders have documents to copy.'),
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
        
        # If multiple products, show selection dialog with filtered products
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
                    ('folder_id', '=', self.documents_folder_id.id),
                    ('res_model', '=', 'documents.document')
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
