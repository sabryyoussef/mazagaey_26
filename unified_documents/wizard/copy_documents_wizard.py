# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class CopyDocumentsWizard(models.TransientModel):
    _name = 'copy.documents.wizard'
    _description = 'Copy Documents Wizard'

    source_model = fields.Char('Source Model', required=True)
    source_id = fields.Integer('Source ID', required=True)
    target_model = fields.Char('Target Model', required=True)
    target_id = fields.Integer('Target ID', required=True)
    
    # For product selection when copying from product to project
    source_product_id = fields.Many2one('product.template', string='Source Product')
    target_project_id = fields.Many2one('project.project', string='Target Project')
    
    # Enhanced fields for preview and results
    document_ids = fields.Many2many('documents.document', string='Documents to Copy')
    
    # Preview fields
    available_documents = fields.Text('Available Documents', readonly=True)
    preview_count = fields.Integer('Available Document Count', readonly=True)
    
    # Copy options
    copy_categories = fields.Selection([
        ('all', 'All Categories'),
        ('required', 'Required Only'),
        ('deliverable', 'Deliverable Only'),
        ('reference', 'Reference Only'),
        ('compliance', 'Compliance Only'),
    ], string='Copy Categories', default='all', required=True)
    
    # Method selection
    copy_method = fields.Selection([
        ('direct', 'Direct Copy (Fast & Simple)'),
        ('category', 'Category-Based Copy (Filtered)'),
        ('template', 'Template-Based Copy (Bulk)'),
        ('batch', 'Batch Copy (Progress Tracking)'),
        ('smart', 'Smart Copy (Intelligent)'),
        ('smart_linking', 'Smart Template Linking (Advanced)'),
        ('optimized', 'Optimized Copy (Performance)'),
    ], string='Copy Method', default='direct', required=True,
       help='Choose the copy method based on your needs')
    
    # Method-specific options
    batch_size = fields.Integer('Batch Size', default=10,
                               help='Number of documents to process in each batch')
    enable_recovery = fields.Boolean('Enable Recovery', default=True,
                                    help='Automatically try to recover failed copies')
    auto_categorize = fields.Boolean('Auto-Categorize', default=False,
                                    help='Automatically categorize documents using smart rules (Step 2.3)')
    
    copy_attachments = fields.Boolean('Copy Attachments', default=True)
    copy_tags = fields.Boolean('Copy Tags', default=True)
    copy_notes = fields.Boolean('Copy Notes', default=True)
    
    # Progress tracking fields
    progress_percentage = fields.Float('Progress (%)', readonly=True, default=0.0)
    progress_message = fields.Text('Progress Message', readonly=True)
    is_processing = fields.Boolean('Processing', readonly=True, default=False)
    
    # Results fields
    copied_documents = fields.Text('Copied Documents', readonly=True)
    copy_success = fields.Boolean('Copy Successful', readonly=True)
    copy_error = fields.Text('Copy Error', readonly=True)
    
    # Detailed results
    total_documents = fields.Integer('Total Documents', readonly=True)
    copied_count = fields.Integer('Copied Count', readonly=True)
    failed_count = fields.Integer('Failed Count', readonly=True)
    skipped_count = fields.Integer('Skipped Count', readonly=True)
    recovered_count = fields.Integer('Recovered Count', readonly=True)
    method_used = fields.Char('Method Used', readonly=True)
    processing_time = fields.Float('Processing Time (seconds)', readonly=True)
    
    @api.onchange('source_product_id')
    def _onchange_source_product_id(self):
        """Load documents when source product is selected"""
        if self.source_product_id:
            self._update_available_documents()
        else:
            self.document_ids = [(5, 0, 0)]
            self.available_documents = ''
            self.preview_count = 0
    
    @api.onchange('copy_categories')
    def _onchange_copy_categories(self):
        """Update available documents when category filter changes"""
        self._update_available_documents()
    
    @api.onchange('copy_method')
    def _onchange_copy_method(self):
        """Update options based on selected copy method"""
        if self.copy_method == 'batch':
            # Show batch size field for batch method
            self.batch_size = 10
        elif self.copy_method == 'smart':
            # Enable recovery for smart method
            self.enable_recovery = True
        elif self.copy_method == 'smart_linking':
            # Enable recovery and set small batch size for smart linking
            self.enable_recovery = True
            self.batch_size = 3  # Very small batches for smart linking
        elif self.copy_method == 'optimized':
            # Enable recovery and set optimized batch size
            self.enable_recovery = True
            self.batch_size = 20  # Optimized batch size for performance
        elif self.copy_method == 'category':
            # Ensure category is selected for category method
            if self.copy_categories == 'all':
                self.copy_categories = 'required'
        elif self.copy_method in ('smart', 'smart_linking'):
            # Offer auto-categorization for smart methods
            self.auto_categorize = True
    
    @api.onchange('batch_size')
    def _onchange_batch_size(self):
        """Validate batch size"""
        if self.batch_size and self.batch_size < 1:
            self.batch_size = 1
        elif self.batch_size and self.batch_size > 100:
            self.batch_size = 100
    
    @api.onchange('source_product_id', 'target_project_id')
    def _onchange_source_target(self):
        """Update available documents when source or target changes"""
        if self.source_product_id and self.target_project_id:
            self.source_model = 'product.template'
            self.source_id = self.source_product_id.id
            self.target_model = 'project.project'
            self.target_id = self.target_project_id.id
            self._update_available_documents()
    
    def action_preview_documents(self):
        """Manual preview action"""
        self._update_available_documents()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'copy.documents.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def _update_available_documents(self):
        """Update the preview of available documents"""
        if not (self.source_model and self.source_id):
            self.available_documents = ''
            self.preview_count = 0
            return
        
        try:
            # Get documents from source
            domain = [
                ('res_model', '=', self.source_model),
                ('res_id', '=', self.source_id),
                ('active', '=', True)
            ]
            
            # Apply category filter
            if self.copy_categories != 'all':
                domain.append(('category', '=', self.copy_categories))
            
            documents = self.env['documents.document'].search(domain)
            
            if documents:
                doc_list = []
                for doc in documents:
                    status_info = f" ({doc.status})" if doc.status != 'draft' else ""
                    doc_list.append(f"• {doc.name} - {doc.category}{status_info}")
                
                self.available_documents = '\n'.join(doc_list)
                self.preview_count = len(documents)
                
                # Update document_ids with filtered documents
                self.document_ids = [(6, 0, documents.ids)]
            else:
                self.available_documents = _('No documents found for the selected criteria')
                self.preview_count = 0
                self.document_ids = [(5, 0, 0)]
                
        except Exception as e:
            self.available_documents = f"Error: {str(e)}"
            self.preview_count = 0
            self.document_ids = [(5, 0, 0)]
    
    @api.model
    def default_get(self, fields_list):
        """Set default documents based on source"""
        res = super().default_get(fields_list)
        
        # Handle product to project copy (from project view)
        if (self.env.context.get('default_source_model') == 'product.template' and 
            self.env.context.get('default_target_model') == 'project.project' and
            self.env.context.get('default_target_id')):
            
            res.update({
                'source_model': 'product.template',
                'target_model': 'project.project',
                'target_id': self.env.context.get('default_target_id'),
            })
            return res
        
        # Handle direct source copy (from product view)
        if self.env.context.get('default_source_model') and self.env.context.get('default_source_id'):
            source_model = self.env.context.get('default_source_model')
            source_id = self.env.context.get('default_source_id')
            
            res.update({
                'source_model': source_model,
                'source_id': source_id,
            })
        
        return res
    
    def action_test_basic_functionality(self):
        """Test basic functionality without relying on the service model"""
        try:
            # Test basic Odoo functionality
            test_results = []
            
            # Test 1: Check if we can access basic models
            try:
                products = self.env['product.template'].search([], limit=1)
                test_results.append(f"✓ Product model accessible: {len(products)} products found")
            except Exception as e:
                test_results.append(f"✗ Product model error: {str(e)}")
            
            # Test 2: Check if we can access project model
            try:
                projects = self.env['project.project'].search([], limit=1)
                test_results.append(f"✓ Project model accessible: {len(projects)} projects found")
            except Exception as e:
                test_results.append(f"✗ Project model error: {str(e)}")
            
            # Test 3: Check if we can access document model
            try:
                documents = self.env['documents.document'].search([], limit=1)
                test_results.append(f"✓ Document model accessible: {len(documents)} documents found")
            except Exception as e:
                test_results.append(f"✗ Document model error: {str(e)}")
            
            # Test 4: Check service model registration
            try:
                if 'unified.document.service' in self.env.registry:
                    test_results.append("✓ Service model registered in registry")
                else:
                    test_results.append("✗ Service model not registered in registry")
            except Exception as e:
                test_results.append(f"✗ Registry check error: {str(e)}")
            
            # Test 5: Try to access service model
            try:
                service = self.env['unified.document.service']
                test_results.append("✓ Service model accessible")
                
                # Check available methods
                methods = [m for m in dir(service) if 'copy_documents' in m]
                test_results.append(f"✓ Available copy methods: {', '.join(methods)}")
            except Exception as e:
                test_results.append(f"✗ Service model access error: {str(e)}")
            
            message = "\n".join(test_results)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Basic Functionality Test'),
                    'message': message,
                    'type': 'info',
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Test Failed'),
                    'message': f"Test error: {str(e)}",
                    'type': 'danger',
                }
            }
    
    def action_test_service(self):
        """Test method to check if the service is working"""
        try:
            # Check if the service model exists in the registry
            if 'unified.document.service' not in self.env.registry:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Service Test Failed'),
                        'message': 'Service model not registered in Odoo registry',
                        'type': 'danger',
                    }
                }
            
            # Try to get the service model
            try:
                document_service = self.env['unified.document.service']
            except KeyError:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Service Test Failed'),
                        'message': 'Service model not accessible (KeyError)',
                        'type': 'danger',
                    }
                }
            
            # Check if we can access the model
            if not document_service:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Service Test Failed'),
                        'message': 'Service model is None',
                        'type': 'danger',
                    }
                }
            
            # Check available methods
            available_methods = [m for m in dir(document_service) if 'copy_documents' in m]
            
            # Try to call the test method if it exists
            if hasattr(document_service, 'test_method_availability'):
                try:
                    test_result = document_service.test_method_availability()
                    message = f"Service Status: {test_result['message']}\nAvailable Methods: {', '.join(test_result['available_methods'])}"
                except Exception as test_error:
                    message = f"Service is working but test method failed: {str(test_error)}\nAvailable Methods: {', '.join(available_methods)}"
            else:
                message = f"Service is working but test_method_availability not found.\nAvailable Methods: {', '.join(available_methods)}"
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Service Test'),
                    'message': message,
                    'type': 'info',
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Service Test Failed'),
                    'message': f"Error: {str(e)}",
                    'type': 'danger',
                }
            }
    
    def action_copy_documents(self):
        """Enhanced copy documents with method selection and progress tracking"""
        self.ensure_one()
        
        import time
        start_time = time.time()
        
        # Reset previous results and start processing
        self.write({
            'copy_success': False,
            'copied_documents': '',
            'copy_error': '',
            'is_processing': True,
            'progress_percentage': 0.0,
            'progress_message': _('Initializing copy operation...'),
            'total_documents': len(self.document_ids),
            'copied_count': 0,
            'failed_count': 0,
            'skipped_count': 0,
            'recovered_count': 0,
            'method_used': self.copy_method,
            'processing_time': 0.0,
        })
        
        try:
            # Validate inputs
            if not self.source_product_id or not self.target_project_id:
                raise ValidationError(_('Please select both source product and target project.'))
                
            if not self.document_ids:
                raise ValidationError(_('Please select at least one document to copy.'))
            
            # Update progress
            self.progress_percentage = 10.0
            self.progress_message = _('Validating documents and preparing copy operation...')
            
            # Get document service
            document_service = self.env['unified.document.service']
            
            # Execute copy based on selected method
            result = self._execute_copy_method(document_service)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Update final results
            self.write({
                'is_processing': False,
                'progress_percentage': 100.0,
                'progress_message': _('Copy operation completed successfully!'),
                'processing_time': processing_time,
                'copy_success': True,
            })
            
            # Show success notification
            return self._show_success_notification(result)
            
        except Exception as e:
            # Handle errors
            processing_time = time.time() - start_time
            error_msg = str(e)
            
            self.write({
                'is_processing': False,
                'progress_percentage': 0.0,
                'progress_message': _('Copy operation failed'),
                'copy_error': f"Error: {error_msg}",
                'copy_success': False,
                'processing_time': processing_time,
            })
            
            _logger.error(f"Document copy error: {error_msg}")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Copy Failed'),
                    'message': _('Failed to copy documents: {}').format(error_msg),
                    'type': 'danger',
                }
            }
    
    def _execute_copy_method(self, document_service):
        """Execute the selected copy method"""
        source_product = self.source_product_id
        target_project = self.target_project_id
        
        # Update progress
        self.progress_percentage = 20.0
        self.progress_message = _('Executing {} copy method...').format(self.copy_method)
        
        try:
            if self.copy_method == 'direct':
                # Try the main method first
                if hasattr(document_service, 'copy_documents_direct'):
                    result = document_service.copy_documents_direct(source_product, target_project)
                    return self._process_direct_result(result)
                else:
                    # Fallback to the basic method
                    _logger.warning("copy_documents_direct not found, using fallback method")
                    result = document_service.copy_product_documents_to_project(target_project, source_product)
                    return self._process_fallback_result(result)
                
            elif self.copy_method == 'category':
                categories = [self.copy_categories] if self.copy_categories != 'all' else None
                result = document_service.copy_documents_by_category(source_product, target_project, categories)
                return self._process_category_result(result)
                
            elif self.copy_method == 'template':
                result = document_service.copy_documents_from_template(source_product, target_project)
                return self._process_template_result(result)
                
            elif self.copy_method == 'batch':
                result = document_service.copy_documents_batch(source_product, target_project, self.batch_size)
                return self._process_batch_result(result)
                
            elif self.copy_method == 'smart':
                result = document_service.copy_documents_smart(source_product, target_project)
                return self._process_smart_result(result)
                
            elif self.copy_method == 'smart_linking':
                result = document_service.copy_documents_with_smart_linking(source_product, target_project)
                if self.auto_categorize:
                    # Auto-categorize project documents after linking
                    document_service.auto_categorize_project_documents(target_project)
                return self._process_smart_linking_result(result)
                
            elif self.copy_method == 'optimized':
                result = document_service.copy_documents_optimized(source_product, target_project)
                return self._process_optimized_result(result)
                
            else:
                raise ValidationError(_('Invalid copy method selected.'))
                
        except Exception as e:
            _logger.error(f"Error executing {self.copy_method} method: {e}")
            raise
    
    def _process_direct_result(self, result):
        """Process direct copy result"""
        self.write({
            'copied_count': result.get('copied_count', 0),
            'failed_count': len(result.get('errors', [])),
            'skipped_count': result.get('total_documents', 0) - result.get('copied_count', 0),
            'recovered_count': 0,
        })
        
        # Create document list for display
        if result.get('success', False):
            doc_list = []
            for doc in self.document_ids[:result.get('copied_count', 0)]:
                doc_list.append(f"• {doc.name} ({doc.category})")
            self.copied_documents = '\n'.join(doc_list)
        
        return result
    
    def _process_fallback_result(self, result):
        """Process fallback copy result"""
        total_copied = sum(len(docs) for docs in result.values())
        
        self.write({
            'copied_count': total_copied,
            'failed_count': 0,
            'skipped_count': len(self.document_ids) - total_copied,
            'recovered_count': 0,
        })
        
        # Create document list for display
        doc_list = []
        for category, docs in result.items():
            for doc in docs:
                doc_list.append(f"• {doc.name} ({category})")
        self.copied_documents = '\n'.join(doc_list)
        
        return result
    
    def _process_category_result(self, result):
        """Process category-based copy result"""
        total_copied = sum(len(docs) for docs in result.values())
        
        self.write({
            'copied_count': total_copied,
            'failed_count': 0,
            'skipped_count': len(self.document_ids) - total_copied,
            'recovered_count': 0,
        })
        
        # Create document list for display
        doc_list = []
        for category, docs in result.items():
            for doc in docs:
                doc_list.append(f"• {doc.name} ({category})")
        self.copied_documents = '\n'.join(doc_list)
        
        return result
    
    def _process_template_result(self, result):
        """Process template-based copy result"""
        self.write({
            'copied_count': len(result),
            'failed_count': 0,
            'skipped_count': len(self.document_ids) - len(result),
            'recovered_count': 0,
        })
        
        # Create document list for display
        doc_list = []
        for doc in result:
            doc_list.append(f"• {doc.name} ({doc.category})")
        self.copied_documents = '\n'.join(doc_list)
        
        return result
    
    def _process_batch_result(self, result):
        """Process batch copy result"""
        self.write({
            'copied_count': result.get('copied', 0),
            'failed_count': len(result.get('errors', [])),
            'skipped_count': result.get('total', 0) - result.get('copied', 0),
            'recovered_count': 0,
        })
        
        return result
    
    def _process_smart_result(self, result):
        """Process smart copy result"""
        self.write({
            'copied_count': len(result.get('copied', [])),
            'failed_count': len(result.get('invalid', [])),
            'skipped_count': 0,
            'recovered_count': 0,
        })
        
        # Create document list for display
        doc_list = []
        for doc in result.get('copied', []):
            doc_list.append(f"• {doc.name} ({doc.category})")
        self.copied_documents = '\n'.join(doc_list)
        
        return result
    
    def _process_smart_linking_result(self, result):
        """Process smart template linking result"""
        total_linked = len(result.get('linked', []))
        total_categorized = len(result.get('categorized', []))
        total_auto_created = len(result.get('auto_created', []))
        total_errors = len(result.get('errors', []))
        
        total_copied = total_linked + total_categorized + total_auto_created
        
        self.write({
            'copied_count': total_copied,
            'failed_count': total_errors,
            'skipped_count': len(self.document_ids) - total_copied - total_errors,
            'recovered_count': 0,
        })
        
        # Create detailed document list for display
        doc_list = []
        
        # Add linked documents
        if result.get('linked'):
            doc_list.append("🔗 LINKED DOCUMENTS:")
            for doc in result['linked']:
                doc_list.append(f"  • {doc.name} ({doc.category}) - Linked")
        
        # Add categorized documents
        if result.get('categorized'):
            doc_list.append("📂 CATEGORIZED DOCUMENTS:")
            for doc in result['categorized']:
                doc_list.append(f"  • {doc.name} ({doc.category}) - Smart Categorized")
        
        # Add auto-created documents
        if result.get('auto_created'):
            doc_list.append("✨ AUTO-CREATED DOCUMENTS:")
            for doc in result['auto_created']:
                doc_list.append(f"  • {doc.name} ({doc.category}) - Auto Created")
        
        # Add errors if any
        if result.get('errors'):
            doc_list.append("❌ ERRORS:")
            for error in result['errors']:
                doc_list.append(f"  • {error}")
        
        self.copied_documents = '\n'.join(doc_list)
        
        return result
    
    def _process_optimized_result(self, result):
        """Process optimized copy result with performance metrics"""
        self.write({
            'copied_count': len(result.get('copied', [])),
            'failed_count': len(result.get('errors', [])),
            'skipped_count': 0,
            'recovered_count': 0,
        })
        
        # Create detailed document list with performance info
        doc_list = []
        
        # Add performance metrics
        metrics = result.get('performance_metrics', {})
        if metrics:
            doc_list.append("🚀 PERFORMANCE METRICS:")
            if 'start_time' in metrics and 'end_time' in metrics:
                duration = metrics['end_time'] - metrics['start_time']
                doc_list.append(f"  • Duration: {duration}")
            doc_list.append(f"  • Total Copied: {metrics.get('total_copied', 0)}")
            doc_list.append(f"  • Total Errors: {metrics.get('total_errors', 0)}")
            doc_list.append("")
        
        # Add copied documents
        if result.get('copied'):
            doc_list.append("✅ COPIED DOCUMENTS:")
            for doc in result['copied']:
                doc_list.append(f"  • {doc.name} ({doc.category})")
        
        # Add errors if any
        if result.get('errors'):
            doc_list.append("❌ ERRORS:")
            for error in result['errors']:
                doc_list.append(f"  • {error}")
        
        self.copied_documents = '\n'.join(doc_list)
        
        return result
    
    def _show_success_notification(self, result):
        """Show success notification with detailed results"""
        message = _('Successfully copied {} documents using {} method.').format(
            self.copied_count, self.copy_method
        )
        
        if self.failed_count > 0:
            message += _(' {} documents failed.').format(self.failed_count)
        
        if self.skipped_count > 0:
            message += _(' {} documents were skipped.').format(self.skipped_count)
        
        if self.recovered_count > 0:
            message += _(' {} documents were recovered.').format(self.recovered_count)
        
        message += _(' Processing time: {:.2f} seconds.').format(self.processing_time)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Documents Copied Successfully'),
                'message': message,
                'type': 'success',
            }
        }
    
    def action_reset_form(self):
        """Reset the form to initial state"""
        self.ensure_one()
        
        # Clear all fields to reset state
        self.write({
            'source_model': 'product.template',
            'source_id': 0,
            'target_model': 'project.project',
            'target_id': 0,
            'source_product_id': False,
            'target_project_id': False,
            'document_ids': [(5, 0, 0)],
            'copy_categories': 'all',
            'copy_attachments': True,
            'copy_tags': True,
            'copy_notes': True,
            'available_documents': '',
            'preview_count': 0,
            'copied_documents': '',
            'copy_success': False,
            'copy_error': '',
        })
        
        # Return action to refresh the form
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
