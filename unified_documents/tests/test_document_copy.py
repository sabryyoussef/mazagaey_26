# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class TestDocumentCopy(TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.document_service = self.env['unified.document.service']
        
        # Create test product
        self.test_product = self.env['product.template'].create({
            'name': 'Test Product for Document Copy',
            'type': 'service',
            'service_tracking': 'task_in_project',
        })
        
        # Create test project
        self.test_project = self.env['project.project'].create({
            'name': 'Test Project for Document Copy',
        })
        
        # Create test documents
        self.test_documents = []
        for i, category in enumerate(['required', 'deliverable', 'reference']):
            doc = self.env['documents.document'].create({
                'name': f'Test Document {i+1} ({category})',
                'category': category,
                'res_model': 'product.template',
                'res_id': self.test_product.id,
                'linked_product_id': self.test_product.id,
            })
            self.test_documents.append(doc)
    
    def test_service_model_exists(self):
        """Test that the unified document service model exists"""
        self.assertTrue(self.document_service)
        self.assertEqual(self.document_service._name, 'unified.document.service')
    
    def test_copy_product_documents_to_project(self):
        """Test the main copy method"""
        # Copy documents from product to project
        result = self.document_service.copy_product_documents_to_project(
            self.test_project, self.test_product
        )
        
        # Verify results
        self.assertIsInstance(result, dict)
        self.assertIn('required', result)
        self.assertIn('deliverable', result)
        self.assertIn('reference', result)
        
        # Check that documents were copied
        total_copied = sum(len(docs) for docs in result.values())
        self.assertEqual(total_copied, 3)  # We created 3 documents
        
        # Verify documents exist in project
        project_docs = self.env['documents.document'].search([
            ('res_model', '=', 'project.project'),
            ('res_id', '=', self.test_project.id)
        ])
        self.assertEqual(len(project_docs), 3)
    
    def test_copy_documents_direct(self):
        """Test Method 1: Direct copy"""
        result = self.document_service.copy_documents_direct(
            self.test_product, self.test_project
        )
        
        # Verify result structure
        self.assertIn('copied_count', result)
        self.assertIn('errors', result)
        self.assertIn('success', result)
        self.assertIn('total_documents', result)
        
        # Check that documents were copied
        self.assertEqual(result['copied_count'], 3)
        self.assertEqual(result['total_documents'], 3)
        self.assertTrue(result['success'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_copy_documents_by_category(self):
        """Test Method 2: Category-based copy"""
        result = self.document_service.copy_documents_by_category(
            self.test_product, self.test_project, ['required', 'deliverable']
        )
        
        # Verify result structure
        self.assertIn('required', result)
        self.assertIn('deliverable', result)
        
        # Check that documents were copied
        self.assertEqual(len(result['required']), 1)
        self.assertEqual(len(result['deliverable']), 1)
        self.assertNotIn('reference', result)  # We didn't include reference
    
    def test_copy_documents_from_template(self):
        """Test Method 3: Template-based copy"""
        result = self.document_service.copy_documents_from_template(
            self.test_product, self.test_project
        )
        
        # Verify result
        self.assertIsInstance(result, self.env['documents.document'].__class__)
        self.assertEqual(len(result), 3)
    
    def test_copy_documents_batch(self):
        """Test Method 4: Batch copy"""
        result = self.document_service.copy_documents_batch(
            self.test_product, self.test_project, batch_size=2
        )
        
        # Verify result structure
        self.assertIn('total', result)
        self.assertIn('copied', result)
        self.assertIn('errors', result)
        self.assertIn('success_rate', result)
        
        # Check that documents were copied
        self.assertEqual(result['total'], 3)
        self.assertEqual(result['copied'], 3)
        self.assertEqual(result['success_rate'], 1.0)
        self.assertEqual(len(result['errors']), 0)
    
    def test_copy_documents_smart(self):
        """Test Method 5: Smart copy"""
        result = self.document_service.copy_documents_smart(
            self.test_product, self.test_project
        )
        
        # Verify result structure
        self.assertIn('copied', result)
        self.assertIn('invalid', result)
        self.assertIn('total_processed', result)
        self.assertIn('success_rate', result)
        
        # Check that documents were copied
        self.assertEqual(result['total_processed'], 3)
        self.assertEqual(len(result['copied']), 3)
        self.assertEqual(result['success_rate'], 1.0)
        self.assertEqual(len(result['invalid']), 0)
    
    def test_duplicate_prevention(self):
        """Test that duplicate documents are not created"""
        # Copy documents first time
        self.document_service.copy_documents_direct(
            self.test_product, self.test_project
        )
        
        # Try to copy again
        result = self.document_service.copy_documents_direct(
            self.test_product, self.test_project
        )
        
        # Should not copy duplicates
        self.assertEqual(result['copied_count'], 0)
        self.assertEqual(result['total_documents'], 3)
    
    def test_copy_specific_documents(self):
        """Test copying specific documents by IDs"""
        doc_ids = [self.test_documents[0].id, self.test_documents[1].id]
        
        result = self.document_service.copy_specific_documents(
            doc_ids, 'project.project', self.test_project.id
        )
        
        # Verify result
        self.assertEqual(len(result), 2)
        
        # Check that only specified documents were copied
        project_docs = self.env['documents.document'].search([
            ('res_model', '=', 'project.project'),
            ('res_id', '=', self.test_project.id)
        ])
        self.assertEqual(len(project_docs), 2)
    
    def test_copy_documents_between_models(self):
        """Test legacy method for backward compatibility"""
        result = self.document_service.copy_documents_between_models(
            'product.template', self.test_product.id,
            'project.project', self.test_project.id
        )
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('required', result)
        self.assertIn('deliverable', result)
        self.assertIn('reference', result)
    
    def test_recovery_methods(self):
        """Test document copy with recovery"""
        result = self.document_service.copy_documents_with_recovery(
            self.test_product, self.test_project
        )
        
        # Verify result structure
        self.assertIn('successful', result)
        self.assertIn('failed', result)
        self.assertIn('skipped', result)
        self.assertIn('recovered', result)
        
        # Check that documents were copied successfully
        self.assertEqual(len(result['successful']), 3)
        self.assertEqual(len(result['failed']), 0)
        self.assertEqual(len(result['recovered']), 0)
    
    def test_validation_methods(self):
        """Test document validation"""
        # Test valid document
        valid_doc = self.test_documents[0]
        is_valid = self.document_service._validate_document_for_copy(
            valid_doc, self.test_project
        )
        self.assertTrue(is_valid)
        
        # Test invalid document (already copied)
        self.document_service.copy_documents_direct(
            self.test_product, self.test_project
        )
        
        # Now the document should be invalid (duplicate)
        is_valid = self.document_service._validate_document_for_copy(
            valid_doc, self.test_project
        )
        self.assertFalse(is_valid)
