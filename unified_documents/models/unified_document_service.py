# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class UnifiedDocumentService(models.Model):
    _name = 'unified.document.service'
    _description = 'Unified Document Service'
    
    # Synonym map for Step 2.3 Category Mapping
    CATEGORY_SYNONYMS = {
        'required': {
            'name': ['required', 'mandatory', 'must have', 'must_have', 'compulsory', 'obligatory', 'prerequisite'],
            'context': ['requirement', 'pre-requisite', 'pre requisite', 'needed', 'essential']
        },
        'deliverable': {
            'name': ['deliverable', 'output', 'result', 'final', 'certificate', 'license', 'report'],
            'context': ['to be delivered', 'delivery', 'handover', 'submission']
        },
        'reference': {
            'name': ['reference', 'guide', 'manual', 'info', 'information', 'help', 'specification'],
            'context': ['for reference', 'example', 'sample', 'template']
        },
        'compliance': {
            'name': ['compliance', 'regulatory', 'legal', 'audit', 'policy', 'gdpr'],
            'context': ['regulation', 'law', 'standard', 'iso', 'sox']
        },
    }
    
    def copy_product_documents_to_project(self, project, product):
        """Copy documents from product to project with duplicate prevention"""
        _logger.info(f"Starting document copy from product {product.name} to project {project.name}")
        
        copied_docs = {
            'required': [],
            'deliverable': [],
            'reference': [],
            'compliance': []
        }
        
        # Deduplication sets
        document_keys = set()
        
        for document in product.document_ids:
            # Create unique key for deduplication
            key = (project.id, document.name, document.category)
            
            if key not in document_keys:
                document_keys.add(key)
                
                try:
                    new_document = self._copy_single_document(document, project)
                    if new_document:
                        copied_docs[document.category].append(new_document)
                        _logger.info(f"Successfully copied document {document.name} ({document.category})")
                except Exception as e:
                    _logger.error(f"Failed to copy document {document.name}: {e}")
                    continue
            else:
                _logger.info(f"Skipping duplicate document {document.name}")
        
        _logger.info(f"Document copy completed. Copied: {sum(len(docs) for docs in copied_docs.values())} documents")
        return copied_docs
    
    def _copy_single_document(self, document, target_project):
        """Copy a single document to the target project"""
        try:
            # Check if document already exists
            existing = self.env['documents.document'].search([
                ('res_model', '=', 'project.project'),
                ('res_id', '=', target_project.id),
                ('name', '=', document.name),
                ('category', '=', document.category)
            ])
            
            if existing:
                _logger.info(f"Document {document.name} already exists in project {target_project.name}")
                return existing[0]
            
            # Create new document
            new_document_vals = {
                'name': document.name,
                'category': document.category,
                'priority': document.priority,
                'notes': document.notes,
                'tag_ids': [(6, 0, document.tag_ids.ids)],
                'res_model': 'project.project',
                'res_id': target_project.id,
                'linked_project_id': target_project.id,
                'linked_product_id': False,  # Remove product link
            }
            
            new_document = self.env['documents.document'].create(new_document_vals)
            
            # Copy attachments if any
            if document.attachment_ids:
                new_document.attachment_ids = [(6, 0, document.attachment_ids.ids)]
                _logger.info(f"Copied {len(document.attachment_ids)} attachments for document {document.name}")
            
            return new_document
            
        except Exception as e:
            _logger.error(f"Error copying document {document.name}: {e}")
            raise
    
    def copy_documents_direct(self, source_product, target_project):
        """Method 1: Direct copy with duplicate prevention"""
        _logger.info(f"Starting direct copy from product {source_product.name} to project {target_project.name}")
        
        copied_count = 0
        errors = []
        
        for doc in source_product.document_ids:
            try:
                # Check for existing document
                existing = self.env['documents.document'].search([
                    ('res_model', '=', 'project.project'),
                    ('res_id', '=', target_project.id),
                    ('name', '=', doc.name),
                    ('category', '=', doc.category)
                ])
                
                if not existing:
                    new_doc = doc.copy({
                        'res_model': 'project.project',
                        'res_id': target_project.id,
                        'linked_project_id': target_project.id,
                        'linked_product_id': False,  # Remove product link
                    })
                    copied_count += 1
                    _logger.info(f"Direct copy: Successfully copied document {doc.name}")
                else:
                    _logger.info(f"Direct copy: Document {doc.name} already exists in project")
                    
            except Exception as e:
                error_msg = f"Document {doc.name}: {str(e)}"
                errors.append(error_msg)
                _logger.error(f"Direct copy error: {error_msg}")
        
        result = {
            'copied_count': copied_count,
            'errors': errors,
            'success': len(errors) == 0,
            'total_documents': len(source_product.document_ids)
        }
        
        _logger.info(f"Direct copy completed: {copied_count} copied, {len(errors)} errors")
        return result
    
    def test_method_availability(self):
        """Test method to verify the service is working"""
        return {
            'status': 'success',
            'message': 'Service is working correctly',
            'available_methods': [m for m in dir(self) if 'copy_documents' in m]
        }
    
    def copy_documents_by_category(self, source_product, target_project, categories=None):
        """Method 2: Category-based copy"""
        if categories is None:
            categories = ['required', 'deliverable']
        
        _logger.info(f"Starting category-based copy for categories: {categories}")
        
        copied_docs = {}
        
        for category in categories:
            category_docs = source_product.document_ids.filtered(
                lambda d: d.category == category
            )
            
            copied_docs[category] = []
            for doc in category_docs:
                try:
                    new_doc = self._copy_document_with_attachments(doc, target_project)
                    copied_docs[category].append(new_doc)
                    _logger.info(f"Category copy: Successfully copied {category} document {doc.name}")
                except Exception as e:
                    _logger.error(f"Category copy: Failed to copy {category} document {doc.name}: {e}")
        
        total_copied = sum(len(docs) for docs in copied_docs.values())
        _logger.info(f"Category-based copy completed: {total_copied} documents copied")
        return copied_docs
    
    def _copy_document_with_attachments(self, document, target_project):
        """Copy document with attachments handling"""
        try:
            # Create document template
            doc_vals = {
                'name': document.name,
                'category': document.category,
                'priority': document.priority,
                'notes': document.notes,
                'tag_ids': [(6, 0, document.tag_ids.ids)],
                'res_model': 'project.project',
                'res_id': target_project.id,
                'linked_project_id': target_project.id,
            }
            
            new_doc = self.env['documents.document'].create(doc_vals)
            
            # Copy attachments separately to avoid issues
            if document.attachment_ids:
                new_doc.attachment_ids = [(6, 0, document.attachment_ids.ids)]
            
            return new_doc
            
        except Exception as e:
            _logger.error(f"Error in _copy_document_with_attachments: {e}")
            raise
    
    def copy_documents_from_template(self, source_product, target_project):
        """Method 3: Template-based copy"""
        _logger.info(f"Starting template-based copy from product {source_product.name}")
        
        # Create document template records
        template_docs = []
        
        for doc in source_product.document_ids:
            template_doc = {
                'name': doc.name,
                'category': doc.category,
                'priority': doc.priority,
                'notes': doc.notes,
                'tag_ids': [(6, 0, doc.tag_ids.ids)],
                'res_model': 'project.project',
                'res_id': target_project.id,
                'linked_project_id': target_project.id,
            }
            template_docs.append(template_doc)
        
        try:
            # Bulk create documents
            created_docs = self.env['documents.document'].create(template_docs)
            
            # Copy attachments separately
            for i, doc in enumerate(source_product.document_ids):
                if doc.attachment_ids:
                    created_docs[i].attachment_ids = [(6, 0, doc.attachment_ids.ids)]
            
            _logger.info(f"Template-based copy completed: {len(created_docs)} documents created")
            return created_docs
            
        except Exception as e:
            _logger.error(f"Template-based copy failed: {e}")
            raise
    
    def copy_documents_batch(self, source_product, target_project, batch_size=10):
        """Method 4: Batch copy with progress tracking"""
        _logger.info(f"Starting batch copy with batch size {batch_size}")
        
        total_docs = len(source_product.document_ids)
        copied_count = 0
        errors = []
        
        for i in range(0, total_docs, batch_size):
            batch = source_product.document_ids[i:i + batch_size]
            
            for doc in batch:
                try:
                    self._copy_single_document(doc, target_project)
                    copied_count += 1
                except Exception as e:
                    errors.append(f"Document {doc.name}: {str(e)}")
            
            # Log progress
            progress = min((i + batch_size) / total_docs * 100, 100)
            _logger.info(f"Batch copy progress: {progress:.1f}% ({copied_count}/{total_docs})")
        
        result = {
            'total': total_docs,
            'copied': copied_count,
            'errors': errors,
            'success_rate': copied_count / total_docs if total_docs > 0 else 0
        }
        
        _logger.info(f"Batch copy completed: {copied_count}/{total_docs} documents copied")
        return result
    
    def copy_documents_smart(self, source_product, target_project):
        """Method 5: Smart copy with validation and optimization"""
        _logger.info(f"Starting smart copy from product {source_product.name}")
        
        # Pre-validate documents
        valid_docs = []
        invalid_docs = []
        
        for doc in source_product.document_ids:
            if self._validate_document_for_copy(doc, target_project):
                valid_docs.append(doc)
            else:
                invalid_docs.append(doc)
        
        _logger.info(f"Smart copy validation: {len(valid_docs)} valid, {len(invalid_docs)} invalid documents")
        
        # Copy valid documents
        copied_docs = []
        for doc in valid_docs:
            try:
                new_doc = self._copy_document_optimized(doc, target_project)
                copied_docs.append(new_doc)
            except Exception as e:
                _logger.error(f"Smart copy failed for {doc.name}: {e}")
        
        result = {
            'copied': copied_docs,
            'invalid': invalid_docs,
            'total_processed': len(valid_docs) + len(invalid_docs),
            'success_rate': len(copied_docs) / len(valid_docs) if valid_docs else 0
        }
        
        _logger.info(f"Smart copy completed: {len(copied_docs)} documents copied successfully")
        return result
    
    def _validate_document_for_copy(self, document, target_project):
        """Validate if document can be copied to project"""
        # Check if document is active
        if not document.active:
            return False
        
        # Check if document already exists
        existing = self.env['documents.document'].search([
            ('res_model', '=', 'project.project'),
            ('res_id', '=', target_project.id),
            ('name', '=', document.name),
            ('category', '=', document.category)
        ])
        
        if existing:
            return False
        
        # Check if project can accept documents
        if not hasattr(target_project, 'document_ids'):
            return False
        
        return True
    
    def _copy_document_optimized(self, document, target_project):
        """Optimized document copy with minimal database operations"""
        try:
            # Create document with minimal fields first
            basic_vals = {
                'name': document.name,
                'category': document.category,
                'res_model': 'project.project',
                'res_id': target_project.id,
                'linked_project_id': target_project.id,
            }
            
            new_doc = self.env['documents.document'].create(basic_vals)
            
            # Update with additional fields in a second operation
            additional_vals = {
                'priority': document.priority,
                'notes': document.notes,
                'tag_ids': [(6, 0, document.tag_ids.ids)],
            }
            new_doc.write(additional_vals)
            
            # Copy attachments in final operation
            if document.attachment_ids:
                new_doc.attachment_ids = [(6, 0, document.attachment_ids.ids)]
            
            return new_doc
            
        except Exception as e:
            _logger.error(f"Optimized copy failed for {document.name}: {e}")
            raise
    
    def copy_documents_with_recovery(self, source_product, target_project):
        """Copy documents with comprehensive error handling and recovery"""
        _logger.info(f"Starting copy with recovery from product {source_product.name}")
        
        results = {
            'successful': [],
            'failed': [],
            'skipped': [],
            'recovered': []
        }
        
        for doc in source_product.document_ids:
            try:
                # Primary copy attempt
                new_doc = self._copy_single_document(doc, target_project)
                results['successful'].append(new_doc)
                
            except ValidationError as e:
                # Handle validation errors
                results['failed'].append({
                    'document': doc.name,
                    'error': str(e),
                    'type': 'validation'
                })
                
            except Exception as e:
                # Try recovery methods
                recovered_doc = self._recover_document_copy(doc, target_project)
                if recovered_doc:
                    results['recovered'].append(recovered_doc)
                else:
                    results['failed'].append({
                        'document': doc.name,
                        'error': str(e),
                        'type': 'unrecoverable'
                    })
        
        _logger.info(f"Copy with recovery completed: {len(results['successful'])} successful, "
                    f"{len(results['recovered'])} recovered, {len(results['failed'])} failed")
        return results
    
    def _recover_document_copy(self, document, target_project):
        """Attempt to recover failed document copy"""
        recovery_methods = [
            self._recover_without_attachments,
            self._recover_with_basic_fields,
            self._recover_as_reference
        ]
        
        for method in recovery_methods:
            try:
                recovered_doc = method(document, target_project)
                if recovered_doc:
                    _logger.info(f"Recovered document {document.name} using {method.__name__}")
                    return recovered_doc
            except Exception as e:
                _logger.warning(f"Recovery method {method.__name__} failed: {e}")
                continue
        
        return False
    
    def _recover_without_attachments(self, document, target_project):
        """Recovery method 1: Copy without attachments"""
        try:
            doc_vals = {
                'name': f"{document.name} (Recovered)",
                'category': document.category,
                'res_model': 'project.project',
                'res_id': target_project.id,
                'linked_project_id': target_project.id,
            }
            return self.env['documents.document'].create(doc_vals)
        except Exception as e:
            _logger.error(f"Recovery without attachments failed: {e}")
            return False
    
    def _recover_with_basic_fields(self, document, target_project):
        """Recovery method 2: Copy with only basic fields"""
        try:
            doc_vals = {
                'name': document.name,
                'category': 'reference',  # Change to reference category
                'res_model': 'project.project',
                'res_id': target_project.id,
                'linked_project_id': target_project.id,
            }
            return self.env['documents.document'].create(doc_vals)
        except Exception as e:
            _logger.error(f"Recovery with basic fields failed: {e}")
            return False
    
    def _recover_as_reference(self, document, target_project):
        """Recovery method 3: Create as reference document"""
        try:
            doc_vals = {
                'name': f"Reference: {document.name}",
                'category': 'reference',
                'notes': f"Recovered from product document: {document.name}",
                'res_model': 'project.project',
                'res_id': target_project.id,
                'linked_project_id': target_project.id,
            }
            return self.env['documents.document'].create(doc_vals)
        except Exception as e:
            _logger.error(f"Recovery as reference failed: {e}")
            return False
    
    def copy_specific_documents(self, document_ids, target_model, target_id, copy_options=None):
        """Copy specific documents by IDs to target model"""
        _logger.info(f"Copying specific documents {document_ids} to {target_model} {target_id}")
        
        if copy_options is None:
            copy_options = {}
        
        copied_docs = []
        
        for doc_id in document_ids:
            try:
                document = self.env['documents.document'].browse(doc_id)
                if not document.exists():
                    _logger.warning(f"Document {doc_id} does not exist")
                    continue
                
                # Get target record
                target_record = self.env[target_model].browse(target_id)
                if not target_record.exists():
                    raise ValidationError(f"Target {target_model} {target_id} does not exist")
                
                # Copy document
                new_doc = self._copy_single_document(document, target_record)
                if new_doc:
                    copied_docs.append(new_doc)
                    
            except Exception as e:
                _logger.error(f"Failed to copy document {doc_id}: {e}")
                continue
        
        _logger.info(f"Specific document copy completed: {len(copied_docs)} documents copied")
        return copied_docs
    
    def copy_documents_between_models(self, source_model, source_id, target_model, target_id, category_filter=None, copy_options=None):
        """Legacy method for backward compatibility"""
        _logger.info(f"Legacy copy between models: {source_model} {source_id} -> {target_model} {target_id}")
        
        try:
            # Get source and target records
            source_record = self.env[source_model].browse(source_id)
            target_record = self.env[target_model].browse(target_id)
            
            if not source_record.exists() or not target_record.exists():
                raise ValidationError("Source or target record does not exist")
            
            # Handle different source models
            if source_model == 'product.template':
                return self.copy_product_documents_to_project(target_record, source_record)
            elif source_model == 'documents.document':
                return [self._copy_single_document(source_record, target_record)]
            else:
                raise ValidationError(f"Unsupported source model: {source_model}")
                
        except Exception as e:
            _logger.error(f"Legacy copy failed: {e}")
            return []
    
    # ============================================================================
    # STEP 2.2: SMART TEMPLATE LINKING METHODS
    # ============================================================================
    
    def copy_documents_with_smart_linking(self, source_product, target_project, link_options=None):
        """Method 6: Smart copy with intelligent template linking"""
        _logger.info(f"Starting smart template linking from {source_product.name} to {target_project.name}")
        
        # Default link options
        default_options = {
            'auto_categorize': True,
            'link_by_category': True,
            'link_by_tags': True,
            'link_by_name_pattern': True,
            'create_missing_categories': False,
            'priority_mapping': True
        }
        
        if link_options:
            default_options.update(link_options)
        
        # Get smart category mapping
        category_mapping = self._get_smart_category_mapping(source_product)
        
        # Get template linking rules
        template_rules = self._get_template_linking_rules(source_product)
        
        copied_docs = {
            'linked': [],
            'categorized': [],
            'auto_created': [],
            'errors': []
        }
        
        for document in source_product.document_ids:
            try:
                # Apply smart linking
                linked_doc = self._apply_smart_linking(
                    document, target_project, category_mapping, template_rules, default_options
                )
                
                if linked_doc:
                    if linked_doc.get('is_linked'):
                        copied_docs['linked'].append(linked_doc['document'])
                    elif linked_doc.get('is_categorized'):
                        copied_docs['categorized'].append(linked_doc['document'])
                    else:
                        copied_docs['auto_created'].append(linked_doc['document'])
                        
            except Exception as e:
                error_msg = f"Smart linking failed for {document.name}: {str(e)}"
                copied_docs['errors'].append(error_msg)
                _logger.error(error_msg)
        
        _logger.info(f"Smart template linking completed. Results: {len(copied_docs['linked'])} linked, "
                    f"{len(copied_docs['categorized'])} categorized, {len(copied_docs['auto_created'])} auto-created")
        
        return copied_docs
    
    def _get_smart_category_mapping(self, source_product):
        """Get intelligent category mapping based on product type"""
        _logger.info(f"Generating smart category mapping for product {source_product.name}")
        
        # Base category mapping
        base_mapping = {
            'required': ['required', 'mandatory', 'essential', 'must_have'],
            'deliverable': ['deliverable', 'output', 'result', 'final'],
            'reference': ['reference', 'supporting', 'background', 'info'],
            'compliance': ['compliance', 'regulatory', 'legal', 'audit']
        }
        
        # Product-specific mappings
        product_mappings = {
            'company_formation': {
                'required': ['company_setup', 'registration', 'approval', 'legal'],
                'deliverable': ['certificate', 'license', 'registration_doc'],
                'reference': ['guidelines', 'requirements', 'process'],
                'compliance': ['tax_compliance', 'regulatory_compliance']
            },
            'visa_services': {
                'required': ['visa_application', 'passport', 'supporting_docs'],
                'deliverable': ['visa_sticker', 'approval_letter', 'entry_permit'],
                'reference': ['visa_guidelines', 'requirements', 'checklist'],
                'compliance': ['immigration_compliance', 'document_verification']
            },
            'government_services': {
                'required': ['application_form', 'identity_docs', 'proof_docs'],
                'deliverable': ['service_certificate', 'approval_document', 'result'],
                'reference': ['service_guidelines', 'process_info', 'requirements'],
                'compliance': ['government_compliance', 'regulatory_requirements']
            }
        }
        
        # Determine product type from name or tags
        product_type = self._determine_product_type(source_product)
        
        if product_type in product_mappings:
            return product_mappings[product_type]
        else:
            return base_mapping
    
    def _determine_product_type(self, product):
        """Determine product type based on name, tags, or category"""
        product_name = product.name.lower()
        product_tags = [tag.name.lower() for tag in product.tag_ids]
        
        # Check for product type indicators
        if any(keyword in product_name for keyword in ['company', 'formation', 'registration', 'setup']):
            return 'company_formation'
        elif any(keyword in product_name for keyword in ['visa', 'immigration', 'permit', 'entry']):
            return 'visa_services'
        elif any(keyword in product_name for keyword in ['government', 'service', 'official', 'public']):
            return 'government_services'
        elif any(keyword in product_tags for keyword in ['company', 'formation']):
            return 'company_formation'
        elif any(keyword in product_tags for keyword in ['visa', 'immigration']):
            return 'visa_services'
        elif any(keyword in product_tags for keyword in ['government', 'official']):
            return 'government_services'
        else:
            return 'general'
    
    def _get_template_linking_rules(self, source_product):
        """Get template linking rules based on product characteristics"""
        _logger.info(f"Generating template linking rules for product {source_product.name}")
        
        rules = {
            'name_patterns': {
                'required': ['required', 'mandatory', 'must', 'essential'],
                'deliverable': ['deliverable', 'output', 'result', 'final', 'certificate'],
                'reference': ['reference', 'guide', 'manual', 'info', 'help'],
                'compliance': ['compliance', 'regulatory', 'legal', 'audit', 'certification']
            },
            'tag_priorities': {
                'high': ['urgent', 'critical', 'important'],
                'medium': ['standard', 'normal', 'regular'],
                'low': ['optional', 'nice_to_have', 'additional']
            },
            'category_weights': {
                'required': 1.0,
                'deliverable': 0.9,
                'compliance': 0.8,
                'reference': 0.6
            }
        }
        
        return rules
    
    def _apply_smart_linking(self, document, target_project, category_mapping, template_rules, options):
        """Apply smart linking to a single document"""
        _logger.info(f"Applying smart linking to document {document.name}")
        
        # Step 1: Check for existing linked documents
        existing_linked = self._find_existing_linked_document(document, target_project)
        if existing_linked:
            _logger.info(f"Found existing linked document: {existing_linked.name}")
            return {'document': existing_linked, 'is_linked': True}
        
        # Step 2: Apply category mapping
        mapped_category = self._map_document_category(document, category_mapping, template_rules)
        
        # Step 3: Create new document with smart linking
        new_document = self._create_smart_linked_document(document, target_project, mapped_category, options)
        
        # Step 4: Apply priority mapping
        if options.get('priority_mapping'):
            self._apply_priority_mapping(new_document, template_rules)
        
        # Step 5: Apply tag linking
        if options.get('link_by_tags'):
            self._apply_tag_linking(new_document, document, template_rules)
        
        return {'document': new_document, 'is_categorized': True}
    
    def _find_existing_linked_document(self, document, target_project):
        """Find existing linked document in target project"""
        # Check by name and category
        existing = self.env['documents.document'].search([
            ('res_model', '=', 'project.project'),
            ('res_id', '=', target_project.id),
            ('name', '=', document.name),
            ('category', '=', document.category)
        ])
        
        if existing:
            return existing[0]
        
        # Check by name pattern
        name_pattern = self._extract_name_pattern(document.name)
        if name_pattern:
            existing = self.env['documents.document'].search([
                ('res_model', '=', 'project.project'),
                ('res_id', '=', target_project.id),
                ('name', 'ilike', f'%{name_pattern}%')
            ])
            
            if existing:
                return existing[0]
        
        return False
    
    def _extract_name_pattern(self, document_name):
        """Extract key pattern from document name for matching"""
        # Remove common prefixes/suffixes
        patterns_to_remove = ['document', 'doc', 'file', 'form', 'template']
        name_lower = document_name.lower()
        
        for pattern in patterns_to_remove:
            name_lower = name_lower.replace(pattern, '').strip()
        
        # Extract meaningful words (3+ characters)
        words = [word for word in name_lower.split() if len(word) >= 3]
        
        if words:
            return ' '.join(words[:3])  # Return first 3 meaningful words
        else:
            return document_name
    
    def _map_document_category(self, document, category_mapping, template_rules):
        """Map document to appropriate category using smart rules"""
        document_name = document.name.lower()
        document_notes = (document.notes or '').lower()
        
        # Check name patterns first
        for category, patterns in template_rules['name_patterns'].items():
            for pattern in patterns:
                if pattern in document_name:
                    _logger.info(f"Mapped document {document.name} to category {category} by name pattern")
                    return category
        
        # Check notes content
        for category, patterns in template_rules['name_patterns'].items():
            for pattern in patterns:
                if pattern in document_notes:
                    _logger.info(f"Mapped document {document.name} to category {category} by notes pattern")
                    return category
        
        # Check existing category mapping
        if document.category in category_mapping:
            return document.category
        
        # Step 2.3: Synonym-based mapping fallback
        synonym_category = self._map_category_by_synonyms(document_name, document_notes)
        if synonym_category:
            _logger.info(f"Synonym mapping categorized {document.name} as {synonym_category}")
            return synonym_category
        
        # Default to reference if no match found
        _logger.info(f"No specific mapping found for {document.name}, defaulting to reference")
        return 'reference'

    # ============================================================================
    # STEP 2.3: CATEGORY MAPPING (Synonym-based + Auto-categorization helpers)
    # ============================================================================
    def _map_category_by_synonyms(self, name_text: str, notes_text: str):
        """Return category based on synonym lookup in name or notes."""
        for category, buckets in self.CATEGORY_SYNONYMS.items():
            for token in buckets.get('name', []):
                if token in name_text:
                    return category
            for token in buckets.get('context', []):
                if token in notes_text:
                    return category
        return None

    def auto_categorize_product_documents(self, product):
        """Auto-categorize all product documents using synonym and smart rules.
        Returns dict with counts per category and changed records.
        """
        results = {
            'updated': 0,
            'unchanged': 0,
            'by_category': {'required': 0, 'deliverable': 0, 'reference': 0, 'compliance': 0}
        }
        category_mapping = self._get_smart_category_mapping(product)
        template_rules = self._get_template_linking_rules(product)
        
        for doc in product.document_ids:
            target_category = self._map_document_category(doc, category_mapping, template_rules)
            if target_category and doc.category != target_category:
                doc.category = target_category
                results['updated'] += 1
                results['by_category'][target_category] = results['by_category'].get(target_category, 0) + 1
            else:
                results['unchanged'] += 1
        return results

    def auto_categorize_project_documents(self, project):
        """Auto-categorize all project documents using synonym and smart rules."""
        results = {
            'updated': 0,
            'unchanged': 0,
            'by_category': {'required': 0, 'deliverable': 0, 'reference': 0, 'compliance': 0}
        }
        # Use a temporary product-like wrapper: rely on smart rules with general mapping
        dummy_product = models.NewId()  # placeholder not used directly
        category_mapping = self._get_smart_category_mapping(project)
        template_rules = self._get_template_linking_rules(project)
        
        documents = self.env['documents.document'].search([
            ('res_model', '=', 'project.project'),
            ('res_id', '=', project.id),
        ])
        for doc in documents:
            target_category = self._map_document_category(doc, category_mapping, template_rules)
            if target_category and doc.category != target_category:
                doc.category = target_category
                results['updated'] += 1
                results['by_category'][target_category] = results['by_category'].get(target_category, 0) + 1
            else:
                results['unchanged'] += 1
        return results
    
    def _create_smart_linked_document(self, document, target_project, mapped_category, options):
        """Create new document with smart linking applied"""
        try:
            # Check if document already exists
            existing = self.env['documents.document'].search([
                ('res_model', '=', 'project.project'),
                ('res_id', '=', target_project.id),
                ('name', '=', document.name),
                ('category', '=', mapped_category)
            ])
            
            if existing:
                _logger.info(f"Document {document.name} already exists in project {target_project.name}")
                return existing[0]
            
            # Create new document with smart linking
            new_document_vals = {
                'name': document.name,
                'category': mapped_category,
                'priority': document.priority,
                'notes': document.notes,
                'tag_ids': [(6, 0, document.tag_ids.ids)],
                'res_model': 'project.project',
                'res_id': target_project.id,
                'linked_project_id': target_project.id,
                'linked_product_id': False,
            }
            
            new_document = self.env['documents.document'].create(new_document_vals)
            
            # Copy attachments if any
            if document.attachment_ids:
                new_document.attachment_ids = [(6, 0, document.attachment_ids.ids)]
                _logger.info(f"Copied {len(document.attachment_ids)} attachments for document {document.name}")
            
            return new_document
            
        except Exception as e:
            _logger.error(f"Error creating smart linked document {document.name}: {e}")
            raise
    
    def _apply_priority_mapping(self, document, template_rules):
        """Apply priority mapping based on template rules"""
        document_name = document.name.lower()
        document_tags = [tag.name.lower() for tag in document.tag_ids]
        
        # Check for priority indicators in name
        for priority, keywords in template_rules['tag_priorities'].items():
            for keyword in keywords:
                if keyword in document_name:
                    priority_value = {'high': '3', 'medium': '2', 'low': '1'}.get(priority, '2')
                    document.priority = priority_value
                    _logger.info(f"Applied priority {priority} to document {document.name}")
                    return
        
        # Check for priority indicators in tags
        for priority, keywords in template_rules['tag_priorities'].items():
            for keyword in keywords:
                if any(keyword in tag for tag in document_tags):
                    priority_value = {'high': '3', 'medium': '2', 'low': '1'}.get(priority, '2')
                    document.priority = priority_value
                    _logger.info(f"Applied priority {priority} to document {document.name}")
                    return
    
    def _apply_tag_linking(self, new_document, original_document, template_rules):
        """Apply intelligent tag linking"""
        # Copy original tags
        new_document.tag_ids = [(6, 0, original_document.tag_ids.ids)]
        
        # Add category-based tags
        category_tag_map = {
            'required': 'required_document',
            'deliverable': 'deliverable_document',
            'reference': 'reference_document',
            'compliance': 'compliance_document'
        }
        
        if new_document.category in category_tag_map:
            category_tag_name = category_tag_map[new_document.category]
            category_tag = self.env['documents.tag'].search([('name', '=', category_tag_name)], limit=1)
            
            if not category_tag:
                category_tag = self.env['documents.tag'].create({'name': category_tag_name})
            
            if category_tag not in new_document.tag_ids:
                new_document.tag_ids = [(4, category_tag.id)]
                _logger.info(f"Added category tag {category_tag_name} to document {new_document.name}")
    
    # ============================================================================
    # STEP 2.4: PERFORMANCE OPTIMIZATION METHODS
    # ============================================================================
    
    def copy_documents_optimized(self, source_product, target_project, optimization_options=None):
        """Method 7: Optimized copy with performance enhancements"""
        _logger.info(f"Starting optimized copy from {source_product.name} to {target_project.name}")
        
        # Default optimization options
        default_options = {
            'use_async': True,
            'batch_size': 20,
            'memory_limit': 1000,  # Max documents in memory
            'query_optimization': True,
            'progress_caching': True,
            'bulk_create': True
        }
        
        if optimization_options:
            default_options.update(optimization_options)
        
        # Pre-load documents with optimized query
        documents = self._optimized_document_query(source_product, default_options)
        
        # Initialize progress tracking
        progress_key = f"copy_progress_{source_product.id}_{target_project.id}"
        if default_options.get('progress_caching'):
            self._init_progress_cache(progress_key, len(documents))
        
        results = {
            'copied': [],
            'errors': [],
            'performance_metrics': {
                'start_time': fields.Datetime.now(),
                'memory_usage': 0,
                'query_count': 0
            }
        }
        
        # Process in optimized batches
        for i in range(0, len(documents), default_options['batch_size']):
            batch = documents[i:i + default_options['batch_size']]
            
            try:
                batch_result = self._process_optimized_batch(
                    batch, target_project, default_options
                )
                
                results['copied'].extend(batch_result['copied'])
                results['errors'].extend(batch_result['errors'])
                
                # Update progress cache
                if default_options.get('progress_caching'):
                    self._update_progress_cache(progress_key, i + len(batch), len(documents))
                
                # Memory management
                if len(results['copied']) > default_options['memory_limit']:
                    self._optimize_memory_usage(results)
                
            except Exception as e:
                _logger.error(f"Batch processing failed: {e}")
                results['errors'].append(f"Batch {i//default_options['batch_size']}: {str(e)}")
        
        # Final performance metrics
        results['performance_metrics']['end_time'] = fields.Datetime.now()
        results['performance_metrics']['total_copied'] = len(results['copied'])
        results['performance_metrics']['total_errors'] = len(results['errors'])
        
        _logger.info(f"Optimized copy completed: {len(results['copied'])} copied, {len(results['errors'])} errors")
        return results
    
    def _optimized_document_query(self, source_product, options):
        """Optimized query to fetch documents with minimal database load"""
        _logger.info("Executing optimized document query")
        
        # Use select_related to reduce queries
        domain = [
            ('res_model', '=', 'product.template'),
            ('res_id', '=', source_product.id),
            ('active', '=', True)
        ]
        
        # Optimize field selection
        fields_to_fetch = ['name', 'category', 'priority', 'notes', 'tag_ids', 'attachment_ids']
        
        documents = self.env['documents.document'].search_read(
            domain, fields_to_fetch, order='id'
        )
        
        _logger.info(f"Optimized query fetched {len(documents)} documents")
        return documents
    
    def _process_optimized_batch(self, batch, target_project, options):
        """Process a batch of documents with optimization"""
        batch_result = {'copied': [], 'errors': []}
        
        # Bulk create preparation
        if options.get('bulk_create'):
            bulk_vals = []
            for doc_data in batch:
                try:
                    doc_vals = self._prepare_document_vals(doc_data, target_project)
                    bulk_vals.append(doc_vals)
                except Exception as e:
                    batch_result['errors'].append(f"Document {doc_data.get('name', 'Unknown')}: {str(e)}")
            
            # Bulk create documents
            if bulk_vals:
                try:
                    created_docs = self.env['documents.document'].create(bulk_vals)
                    batch_result['copied'].extend(created_docs)
                    _logger.info(f"Bulk created {len(created_docs)} documents")
                except Exception as e:
                    _logger.error(f"Bulk create failed: {e}")
                    # Fallback to individual creation
                    for doc_data in batch:
                        try:
                            new_doc = self._create_single_optimized_document(doc_data, target_project)
                            if new_doc:
                                batch_result['copied'].append(new_doc)
                        except Exception as e:
                            batch_result['errors'].append(f"Document {doc_data.get('name', 'Unknown')}: {str(e)}")
        else:
            # Individual processing
            for doc_data in batch:
                try:
                    new_doc = self._create_single_optimized_document(doc_data, target_project)
                    if new_doc:
                        batch_result['copied'].append(new_doc)
                except Exception as e:
                    batch_result['errors'].append(f"Document {doc_data.get('name', 'Unknown')}: {str(e)}")
        
        return batch_result
    
    def _prepare_document_vals(self, doc_data, target_project):
        """Prepare document values for bulk creation"""
        return {
            'name': doc_data.get('name', ''),
            'category': doc_data.get('category', 'reference'),
            'priority': doc_data.get('priority', '2'),
            'notes': doc_data.get('notes', ''),
            'tag_ids': [(6, 0, doc_data.get('tag_ids', []))],
            'res_model': 'project.project',
            'res_id': target_project.id,
            'linked_project_id': target_project.id,
            'linked_product_id': False,
        }
    
    def _create_single_optimized_document(self, doc_data, target_project):
        """Create single document with optimization"""
        try:
            # Check for existing document with optimized query
            existing = self.env['documents.document'].search([
                ('res_model', '=', 'project.project'),
                ('res_id', '=', target_project.id),
                ('name', '=', doc_data.get('name', '')),
                ('category', '=', doc_data.get('category', 'reference'))
            ], limit=1)
            
            if existing:
                return existing[0]
            
            # Create new document
            doc_vals = self._prepare_document_vals(doc_data, target_project)
            new_doc = self.env['documents.document'].create(doc_vals)
            
            # Handle attachments separately to avoid bulk issues
            if doc_data.get('attachment_ids'):
                new_doc.attachment_ids = [(6, 0, doc_data['attachment_ids'])]
            
            return new_doc
            
        except Exception as e:
            _logger.error(f"Error creating optimized document: {e}")
            raise
    
    def _optimize_memory_usage(self, results):
        """Optimize memory usage by clearing unnecessary data"""
        # Clear detailed document data, keep only essential info
        for doc in results['copied']:
            if hasattr(doc, '_prefetch_ids'):
                doc._prefetch_ids = None
        
        # Force garbage collection if available
        try:
            import gc
            gc.collect()
        except ImportError:
            pass
        
        _logger.info("Memory optimization completed")
    
    def _init_progress_cache(self, progress_key, total_documents):
        """Initialize progress cache for resumable operations"""
        cache_data = {
            'total': total_documents,
            'processed': 0,
            'start_time': fields.Datetime.now(),
            'status': 'in_progress'
        }
        
        # Store in ir.config_parameter for persistence
        self.env['ir.config_parameter'].set_param(
            f'unified_documents.{progress_key}', str(cache_data)
        )
        
        _logger.info(f"Progress cache initialized: {progress_key}")
    
    def _update_progress_cache(self, progress_key, processed_count, total_documents):
        """Update progress cache with current status"""
        cache_data = {
            'total': total_documents,
            'processed': processed_count,
            'last_update': fields.Datetime.now(),
            'status': 'in_progress'
        }
        
        self.env['ir.config_parameter'].set_param(
            f'unified_documents.{progress_key}', str(cache_data)
        )
    
    def _get_progress_cache(self, progress_key):
        """Retrieve progress cache data"""
        cache_param = self.env['ir.config_parameter'].get_param(f'unified_documents.{progress_key}')
        if cache_param:
            try:
                import ast
                return ast.literal_eval(cache_param)
            except:
                return None
        return None
    
    def resume_interrupted_copy(self, source_product, target_project):
        """Resume interrupted copy operation using cached progress"""
        progress_key = f"copy_progress_{source_product.id}_{target_project.id}"
        cache_data = self._get_progress_cache(progress_key)
        
        if not cache_data:
            _logger.warning("No progress cache found for resumption")
            return self.copy_documents_optimized(source_product, target_project)
        
        _logger.info(f"Resuming copy operation from {cache_data['processed']}/{cache_data['total']}")
        
        # Continue from where we left off
        documents = self._optimized_document_query(source_product, {})
        remaining_docs = documents[cache_data['processed']:]
        
        # Process remaining documents
        results = {
            'copied': [],
            'errors': [],
            'resumed': True,
            'original_progress': cache_data
        }
        
        for doc_data in remaining_docs:
            try:
                new_doc = self._create_single_optimized_document(doc_data, target_project)
                if new_doc:
                    results['copied'].append(new_doc)
            except Exception as e:
                results['errors'].append(f"Document {doc_data.get('name', 'Unknown')}: {str(e)}")
        
        # Clear progress cache
        self.env['ir.config_parameter'].set_param(f'unified_documents.{progress_key}', '')
        
        _logger.info(f"Resumed copy completed: {len(results['copied'])} additional documents copied")
        return results
