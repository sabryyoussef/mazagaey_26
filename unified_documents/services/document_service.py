from odoo import models, api, _
import logging

_logger = logging.getLogger(__name__)


class UnifiedDocumentService(models.AbstractModel):
    _name = 'unified.document.service'
    _description = 'Unified Document Copy Service'

    @api.model
    def copy_product_documents_to_project(self, project, product):
        """
        Copy documents from product to project using unified documents
        Returns: dict with created document records
        """
        if not project or not product:
            return {'required': [], 'deliverable': []}
        
        # Use the generic copy method with full options
        copy_options = {
            'copy_attachments': True,
            'copy_tags': True,
            'copy_notes': True,
        }
        
        # Get documents from product using unified documents
        # Check both res_model/res_id and linked_product_id
        
        # Search by res_model/res_id
        docs_by_res = self.env['documents.document'].search([
            ('res_model', '=', 'product.template'),
            ('res_id', '=', product.id)
        ])
        
        # Search by linked_product_id
        docs_by_linked = self.env['documents.document'].search([
            ('linked_product_id', '=', product.id)
        ])
        
        # Combine both searches
        product_documents = docs_by_res | docs_by_linked
        
        if not product_documents:
            return {'required': [], 'deliverable': []}
        
        # Use the generic copy method with elevated privileges
        created_docs = self.sudo().copy_documents_between_models(
            'product.template', 
            product.id, 
            'project.project', 
            project.id, 
            copy_options=copy_options
        )
        
        # Categorize the created documents
        categorized_docs = {
            'required': [],
            'deliverable': []
        }
        
        for doc in created_docs:
            if doc.category == 'required':
                categorized_docs['required'].append(doc)
            else:
                categorized_docs['deliverable'].append(doc)
        
        return categorized_docs

    @api.model
    def copy_documents_between_models(self, source_model, source_id, target_model, target_id, category_filter=None, copy_options=None):
        """
        Generic method to copy documents between any models
        Args:
            source_model: Source model name (e.g., 'product.template')
            source_id: Source record ID
            target_model: Target model name (e.g., 'project.project')
            target_id: Target record ID
            category_filter: Optional filter for document categories
            copy_options: Optional dict with copy options (attachments, tags, notes)
        Returns: list of created documents
        """
        if not all([source_model, source_id, target_model, target_id]):
            return []
        

        
        # Default copy options
        if copy_options is None:
            copy_options = {
                'copy_attachments': True,
                'copy_tags': True,
                'copy_notes': True,
            }
        
        # Get source documents
        domain = [
            ('active', '=', True)
        ]
        
        # For product.template, check both res_model/res_id and linked_product_id
        if source_model == 'product.template':
            domain.extend([
                '|',
                ('res_model', '=', source_model),
                ('res_id', '=', source_id),
                ('linked_product_id', '=', source_id)
            ])
        else:
            domain.extend([
                ('res_model', '=', source_model),
                ('res_id', '=', source_id)
            ])
        
        if category_filter:
            domain.append(('category', 'in', category_filter))
        
        source_documents = self.env['documents.document'].search(domain)
        
        created_docs = []
        
        for doc in source_documents:
            # Check if document already exists in target
            existing_doc = self.env['documents.document'].search([
                ('res_model', '=', target_model),
                ('res_id', '=', target_id),
                ('name', '=', doc.name),
                ('category', '=', doc.category),
                ('active', '=', True)
            ], limit=1)
            
            if existing_doc:
                created_docs.append(existing_doc)
            else:
                # Create new document in target
                new_doc_vals = {
                    'name': doc.name,
                    'res_model': target_model,
                    'res_id': target_id,
                    'category': doc.category,
                    'status': 'draft',  # Reset status for copied documents
                    'priority': doc.priority,
                    'description': doc.description or '',
                    'notes': f"Copied from {source_model}",
                    'is_verified': False,
                    'verification_date': False,
                    'verified_by': False,
                }
                
                # Apply copy options
                if copy_options.get('copy_tags') and hasattr(doc, 'tag_ids') and doc.tag_ids:
                    new_doc_vals['tag_ids'] = [(6, 0, doc.tag_ids.ids)]
                
                if copy_options.get('copy_notes') and doc.notes:
                    new_doc_vals['notes'] = f"Copied from {source_model}: {doc.notes}"
                
                # Handle attachments separately (they need special handling)
                if copy_options.get('copy_attachments') and hasattr(doc, 'attachment_ids') and doc.attachment_ids:
                    # We'll handle attachments after document creation
                    pass
                
                # Get or create project folder and set linked_project_id if target is a project
                if target_model == 'project.project':
                    target_project = self.env['project.project'].browse(target_id)
                    project_folder = self.env['documents.document']._get_project_folder(target_project)
                    if project_folder:
                        new_doc_vals['folder_id'] = project_folder.id
                    # Set linked_project_id for project documents
                    new_doc_vals['linked_project_id'] = target_id
                
                new_doc = self.env['documents.document'].create(new_doc_vals)
                
                # Force recomputation of project document fields if target is a project
                if target_model == 'project.project':
                    target_project = self.env['project.project'].browse(target_id)
                    target_project._invalidate_cache(['document_ids', 'document_count', 'required_document_count', 'deliverable_document_count'])
                
                # Handle attachments after document creation
                if copy_options.get('copy_attachments') and hasattr(doc, 'attachment_ids') and doc.attachment_ids:
                    try:
                        # Copy attachments
                        for attachment in doc.attachment_ids:
                            new_attachment = attachment.copy({
                                'res_model': target_model,
                                'res_id': target_id,
                                'res_name': new_doc.name,
                            })
                    except Exception as e:
                        _logger.error(f"Error copying attachments for document {doc.name}: {e}")
                
                created_docs.append(new_doc)
        
        return created_docs

    @api.model
    def copy_specific_documents(self, document_ids, target_model, target_id, copy_options=None):
        """
        Copy specific documents to target
        Args:
            document_ids: List of document IDs to copy
            target_model: Target model name
            target_id: Target record ID
            copy_options: Optional dict with copy options
        Returns: list of created documents
        """
        if not document_ids:
            return []
        

        
        # Default copy options
        if copy_options is None:
            copy_options = {
                'copy_attachments': True,
                'copy_tags': True,
                'copy_notes': True,
            }
        
        created_docs = []
        
        for doc_id in document_ids:
            doc = self.env['documents.document'].browse(doc_id)
            if not doc.exists():
                continue
            
            # Check if document already exists in target
            existing_doc = self.env['documents.document'].search([
                ('res_model', '=', target_model),
                ('res_id', '=', target_id),
                ('name', '=', doc.name),
                ('category', '=', doc.category),
                ('active', '=', True)
            ], limit=1)
            
            if existing_doc:
                created_docs.append(existing_doc)
            else:
                # Create new document in target
                new_doc_vals = {
                    'name': doc.name,
                    'res_model': target_model,
                    'res_id': target_id,
                    'category': doc.category,
                    'status': 'draft',
                    'priority': doc.priority,
                    'description': doc.description or '',
                    'notes': f"Copied from {doc.res_model}",
                    'is_verified': False,
                    'verification_date': False,
                    'verified_by': False,
                }
                
                # Apply copy options
                if copy_options.get('copy_tags') and hasattr(doc, 'tag_ids') and doc.tag_ids:
                    new_doc_vals['tag_ids'] = [(6, 0, doc.tag_ids.ids)]
                
                if copy_options.get('copy_notes') and doc.notes:
                    new_doc_vals['notes'] = f"Copied from {doc.res_model}: {doc.notes}"
                
                # Get or create project folder and set linked_project_id if target is a project
                if target_model == 'project.project':
                    target_project = self.env['project.project'].browse(target_id)
                    project_folder = self.env['documents.document']._get_project_folder(target_project)
                    if project_folder:
                        new_doc_vals['folder_id'] = project_folder.id
                    # Set linked_project_id for project documents
                    new_doc_vals['linked_project_id'] = target_id
                
                new_doc = self.env['documents.document'].create(new_doc_vals)
                
                # Handle attachments after document creation
                if copy_options.get('copy_attachments') and hasattr(doc, 'attachment_ids') and doc.attachment_ids:
                    try:
                        for attachment in doc.attachment_ids:
                            new_attachment = attachment.copy({
                                'res_model': target_model,
                                'res_id': target_id,
                                'res_name': new_doc.name,
                            })
                    except Exception as e:
                        _logger.error(f"Error copying attachments for document {doc.name}: {e}")
                
                created_docs.append(new_doc)
        
        return created_docs

    @api.model
    def get_document_service_methods(self):
        """
        Return available document service methods
        """
        return {
            'copy_product_documents_to_project': {
                'name': 'Copy Product Documents to Project',
                'description': 'Copy documents from product to project using unified documents',
                'params': ['project', 'product'],
                'returns': 'dict with created document records'
            },
            'copy_documents_between_models': {
                'name': 'Copy Documents Between Models',
                'description': 'Generic method to copy documents between any models',
                'params': ['source_model', 'source_id', 'target_model', 'target_id', 'category_filter'],
                'returns': 'list of created documents'
            }
        }

    @api.model
    def execute_document_service(self, service_name, **kwargs):
        """
        Generic method to execute any document service
        """
        if hasattr(self, service_name):
            method = getattr(self, service_name)
            return method(**kwargs)
        else:
            raise ValueError(f"Document service '{service_name}' not found")
