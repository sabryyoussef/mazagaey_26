# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class TestSmartLinking(TransactionCase):
    """Test cases for Smart Template Linking functionality"""
    
    def setUp(self):
        super().setUp()
        
        # Create test products with different types
        self.company_formation_product = self.env['product.template'].create({
            'name': 'Company Formation Service',
            'type': 'service',
            'service_tracking': 'task_in_project',
        })
        
        self.visa_service_product = self.env['product.template'].create({
            'name': 'Visa Application Service',
            'type': 'service',
            'service_tracking': 'task_in_project',
        })
        
        self.general_service_product = self.env['product.template'].create({
            'name': 'General Consulting Service',
            'type': 'service',
            'service_tracking': 'task_in_project',
        })
        
        # Create test projects
        self.test_project = self.env['project.project'].create({
            'name': 'Test Project',
            'is_template': False,
        })
        
        # Create test documents for company formation
        self.company_docs = []
        doc_names = [
            'Company Registration Form',
            'Business License Application',
            'Tax Compliance Certificate',
            'Company Setup Guidelines',
            'Legal Requirements Document'
        ]
        
        for name in doc_names:
            doc = self.env['documents.document'].create({
                'name': name,
                'category': 'required',
                'res_model': 'product.template',
                'res_id': self.company_formation_product.id,
                'linked_product_id': self.company_formation_product.id,
            })
            self.company_docs.append(doc)
        
        # Create test documents for visa service
        self.visa_docs = []
        visa_doc_names = [
            'Visa Application Form',
            'Passport Copy',
            'Visa Approval Letter',
            'Immigration Guidelines',
            'Supporting Documents Checklist'
        ]
        
        for name in visa_doc_names:
            doc = self.env['documents.document'].create({
                'name': name,
                'category': 'required',
                'res_model': 'product.template',
                'res_id': self.visa_service_product.id,
                'linked_product_id': self.visa_service_product.id,
            })
            self.visa_docs.append(doc)
        
        # Link documents to products
        self.company_formation_product.document_ids = [(6, 0, [doc.id for doc in self.company_docs])]
        self.visa_service_product.document_ids = [(6, 0, [doc.id for doc in self.visa_docs])]
        
        # Get the document service
        self.document_service = self.env['unified.document.service']
    
    def test_smart_linking_method_exists(self):
        """Test that smart linking method exists"""
        self.assertTrue(hasattr(self.document_service, 'copy_documents_with_smart_linking'))
        self.assertTrue(callable(self.document_service.copy_documents_with_smart_linking))
    
    def test_product_type_detection_company_formation(self):
        """Test product type detection for company formation"""
        product_type = self.document_service._determine_product_type(self.company_formation_product)
        self.assertEqual(product_type, 'company_formation')
    
    def test_product_type_detection_visa_services(self):
        """Test product type detection for visa services"""
        product_type = self.document_service._determine_product_type(self.visa_service_product)
        self.assertEqual(product_type, 'visa_services')
    
    def test_product_type_detection_general(self):
        """Test product type detection for general services"""
        product_type = self.document_service._determine_product_type(self.general_service_product)
        self.assertEqual(product_type, 'general')
    
    def test_smart_category_mapping_company_formation(self):
        """Test smart category mapping for company formation"""
        mapping = self.document_service._get_smart_category_mapping(self.company_formation_product)
        
        # Should have company formation specific mappings
        self.assertIn('required', mapping)
        self.assertIn('deliverable', mapping)
        self.assertIn('reference', mapping)
        self.assertIn('compliance', mapping)
        
        # Check for company formation specific keywords
        self.assertIn('company_setup', mapping['required'])
        self.assertIn('certificate', mapping['deliverable'])
    
    def test_smart_category_mapping_visa_services(self):
        """Test smart category mapping for visa services"""
        mapping = self.document_service._get_smart_category_mapping(self.visa_service_product)
        
        # Should have visa service specific mappings
        self.assertIn('required', mapping)
        self.assertIn('deliverable', mapping)
        self.assertIn('reference', mapping)
        self.assertIn('compliance', mapping)
        
        # Check for visa service specific keywords
        self.assertIn('visa_application', mapping['required'])
        self.assertIn('visa_sticker', mapping['deliverable'])
    
    def test_template_linking_rules(self):
        """Test template linking rules generation"""
        rules = self.document_service._get_template_linking_rules(self.company_formation_product)
        
        # Should have all required rule components
        self.assertIn('name_patterns', rules)
        self.assertIn('tag_priorities', rules)
        self.assertIn('category_weights', rules)
        
        # Check name patterns
        self.assertIn('required', rules['name_patterns'])
        self.assertIn('deliverable', rules['name_patterns'])
        self.assertIn('reference', rules['name_patterns'])
        self.assertIn('compliance', rules['name_patterns'])
    
    def test_name_pattern_extraction(self):
        """Test name pattern extraction"""
        # Test with common prefixes
        pattern = self.document_service._extract_name_pattern('Document Company Registration Form')
        self.assertIn('company', pattern.lower())
        self.assertIn('registration', pattern.lower())
        
        # Test with short words
        pattern = self.document_service._extract_name_pattern('Visa Application')
        self.assertIn('visa', pattern.lower())
        self.assertIn('application', pattern.lower())
    
    def test_document_category_mapping(self):
        """Test document category mapping"""
        # Create a document with 'required' in name
        doc = self.env['documents.document'].create({
            'name': 'Required Business License',
            'category': 'reference',
            'res_model': 'product.template',
            'res_id': self.company_formation_product.id,
        })
        
        category_mapping = self.document_service._get_smart_category_mapping(self.company_formation_product)
        template_rules = self.document_service._get_template_linking_rules(self.company_formation_product)
        
        mapped_category = self.document_service._map_document_category(doc, category_mapping, template_rules)
        self.assertEqual(mapped_category, 'required')
    
    def test_smart_linking_basic_functionality(self):
        """Test basic smart linking functionality"""
        result = self.document_service.copy_documents_with_smart_linking(
            self.company_formation_product, self.test_project
        )
        
        # Should have result structure
        self.assertIn('linked', result)
        self.assertIn('categorized', result)
        self.assertIn('auto_created', result)
        self.assertIn('errors', result)
        
        # Should have copied documents
        total_copied = len(result['linked']) + len(result['categorized']) + len(result['auto_created'])
        self.assertGreater(total_copied, 0)
    
    def test_smart_linking_with_options(self):
        """Test smart linking with custom options"""
        link_options = {
            'auto_categorize': True,
            'link_by_category': True,
            'link_by_tags': False,
            'link_by_name_pattern': True,
            'priority_mapping': True
        }
        
        result = self.document_service.copy_documents_with_smart_linking(
            self.company_formation_product, self.test_project, link_options
        )
        
        # Should have result structure
        self.assertIn('linked', result)
        self.assertIn('categorized', result)
        self.assertIn('auto_created', result)
        self.assertIn('errors', result)
    
    def test_existing_document_linking(self):
        """Test linking to existing documents"""
        # Create a document in the target project first
        existing_doc = self.env['documents.document'].create({
            'name': 'Company Registration Form',
            'category': 'required',
            'res_model': 'project.project',
            'res_id': self.test_project.id,
            'linked_project_id': self.test_project.id,
        })
        
        result = self.document_service.copy_documents_with_smart_linking(
            self.company_formation_product, self.test_project
        )
        
        # Should find and link to existing document
        self.assertGreater(len(result['linked']), 0)
    
    def test_priority_mapping(self):
        """Test priority mapping functionality"""
        # Create a document with priority indicators
        doc = self.env['documents.document'].create({
            'name': 'Urgent Business License',
            'category': 'required',
            'priority': '1',
            'res_model': 'project.project',
            'res_id': self.test_project.id,
            'linked_project_id': self.test_project.id,
        })
        
        template_rules = self.document_service._get_template_linking_rules(self.company_formation_product)
        
        # Apply priority mapping
        self.document_service._apply_priority_mapping(doc, template_rules)
        
        # Should have high priority (3) due to 'urgent' in name
        self.assertEqual(doc.priority, '3')
    
    def test_tag_linking(self):
        """Test tag linking functionality"""
        # Create a document
        doc = self.env['documents.document'].create({
            'name': 'Test Document',
            'category': 'required',
            'res_model': 'project.project',
            'res_id': self.test_project.id,
            'linked_project_id': self.test_project.id,
        })
        
        original_doc = self.company_docs[0]
        template_rules = self.document_service._get_template_linking_rules(self.company_formation_product)
        
        # Apply tag linking
        self.document_service._apply_tag_linking(doc, original_doc, template_rules)
        
        # Should have category tag
        category_tags = [tag.name for tag in doc.tag_ids]
        self.assertIn('required_document', category_tags)
    
    def test_smart_linking_error_handling(self):
        """Test error handling in smart linking"""
        # Test with invalid product (no documents)
        result = self.document_service.copy_documents_with_smart_linking(
            self.general_service_product, self.test_project
        )
        
        # Should handle gracefully
        self.assertIn('linked', result)
        self.assertIn('categorized', result)
        self.assertIn('auto_created', result)
        self.assertIn('errors', result)
        
        # Should have no errors since no documents to process
        self.assertEqual(len(result['errors']), 0)
    
    def test_smart_linking_performance(self):
        """Test smart linking performance with multiple documents"""
        # Add more documents to test performance
        additional_docs = []
        for i in range(10):
            doc = self.env['documents.document'].create({
                'name': f'Additional Document {i}',
                'category': 'reference',
                'res_model': 'product.template',
                'res_id': self.company_formation_product.id,
                'linked_product_id': self.company_formation_product.id,
            })
            additional_docs.append(doc)
        
        # Link additional documents
        self.company_formation_product.document_ids = [(4, doc.id) for doc in additional_docs]
        
        # Test smart linking
        result = self.document_service.copy_documents_with_smart_linking(
            self.company_formation_product, self.test_project
        )
        
        # Should handle multiple documents
        total_copied = len(result['linked']) + len(result['categorized']) + len(result['auto_created'])
        self.assertGreaterEqual(total_copied, 5)  # At least some documents should be copied
    
    def test_optimized_copy_method_exists(self):
        """Test that optimized copy method exists"""
        self.assertTrue(hasattr(self.document_service, 'copy_documents_optimized'))
        self.assertTrue(callable(self.document_service.copy_documents_optimized))
    
    def test_optimized_document_query(self):
        """Test optimized document query"""
        documents = self.document_service._optimized_document_query(self.company_formation_product, {})
        self.assertIsInstance(documents, list)
        self.assertGreaterEqual(len(documents), 0)
    
    def test_bulk_document_creation(self):
        """Test bulk document creation functionality"""
        # Create test document data
        doc_data = [
            {'name': 'Test Doc 1', 'category': 'required', 'priority': '2', 'notes': '', 'tag_ids': [], 'attachment_ids': []},
            {'name': 'Test Doc 2', 'category': 'deliverable', 'priority': '2', 'notes': '', 'tag_ids': [], 'attachment_ids': []}
        ]
        
        batch_result = self.document_service._process_optimized_batch(doc_data, self.test_project, {'bulk_create': True})
        self.assertIn('copied', batch_result)
        self.assertIn('errors', batch_result)
    
    def test_progress_caching(self):
        """Test progress caching functionality"""
        progress_key = 'test_progress_key'
        total_docs = 10
        
        # Initialize cache
        self.document_service._init_progress_cache(progress_key, total_docs)
        
        # Update cache
        self.document_service._update_progress_cache(progress_key, 5, total_docs)
        
        # Retrieve cache
        cache_data = self.document_service._get_progress_cache(progress_key)
        self.assertIsNotNone(cache_data)
        self.assertEqual(cache_data['processed'], 5)
        self.assertEqual(cache_data['total'], total_docs)
    
    def test_memory_optimization(self):
        """Test memory optimization functionality"""
        results = {'copied': [self.company_docs[0]]}
        self.document_service._optimize_memory_usage(results)
        # Should complete without errors
        self.assertIn('copied', results)
    
    def test_resume_interrupted_copy(self):
        """Test resume interrupted copy functionality"""
        # First create some progress cache
        progress_key = f"copy_progress_{self.company_formation_product.id}_{self.test_project.id}"
        self.document_service._init_progress_cache(progress_key, 5)
        
        # Test resume
        result = self.document_service.resume_interrupted_copy(self.company_formation_product, self.test_project)
        self.assertIn('copied', result)
        self.assertIn('resumed', result)
        self.assertTrue(result['resumed'])

    def test_synonym_based_mapping(self):
        """Test synonym-based mapping falls back correctly"""
        doc = self.env['documents.document'].create({
            'name': 'Mandatory Identity Proof',
            'category': 'reference',
            'res_model': 'product.template',
            'res_id': self.company_formation_product.id,
        })
        mapping = self.document_service._get_smart_category_mapping(self.company_formation_product)
        rules = self.document_service._get_template_linking_rules(self.company_formation_product)
        new_category = self.document_service._map_document_category(doc, mapping, rules)
        self.assertEqual(new_category, 'required')

    def test_auto_categorize_product_documents(self):
        """Test bulk auto-categorization on product documents"""
        res = self.document_service.auto_categorize_product_documents(self.company_formation_product)
        self.assertIn('updated', res)
        self.assertIn('by_category', res)

    def test_auto_categorize_project_documents(self):
        """Test bulk auto-categorization on project documents"""
        # First copy some docs to project
        self.document_service.copy_documents_direct(self.company_formation_product, self.test_project)
        res = self.document_service.auto_categorize_project_documents(self.test_project)
        self.assertIn('updated', res)
        self.assertIn('by_category', res)
