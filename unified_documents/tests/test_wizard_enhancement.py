# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class TestWizardEnhancement(TransactionCase):
    
    def setUp(self):
        super().setUp()
        
        # Create test product
        self.test_product = self.env['product.template'].create({
            'name': 'Test Product for Wizard',
            'type': 'service',
            'service_tracking': 'task_in_project',
        })
        
        # Create test project
        self.test_project = self.env['project.project'].create({
            'name': 'Test Project for Wizard',
        })
        
        # Create test documents
        self.test_documents = []
        for i, category in enumerate(['required', 'deliverable', 'reference']):
            doc = self.env['documents.document'].create({
                'name': f'Wizard Test Document {i+1} ({category})',
                'category': category,
                'res_model': 'product.template',
                'res_id': self.test_product.id,
                'linked_product_id': self.test_product.id,
            })
            self.test_documents.append(doc)
    
    def test_wizard_creation(self):
        """Test that wizard can be created with enhanced fields"""
        wizard = self.env['copy.documents.wizard'].create({
            'source_product_id': self.test_product.id,
            'target_project_id': self.test_project.id,
            'copy_method': 'direct',
            'copy_categories': 'all',
        })
        
        self.assertTrue(wizard)
        self.assertEqual(wizard.copy_method, 'direct')
        self.assertEqual(wizard.copy_categories, 'all')
        self.assertEqual(wizard.batch_size, 10)  # Default value
        self.assertTrue(wizard.enable_recovery)  # Default value
    
    def test_method_selection_onchange(self):
        """Test method selection onchange behavior"""
        wizard = self.env['copy.documents.wizard'].create({
            'source_product_id': self.test_product.id,
            'target_project_id': self.test_project.id,
            'copy_method': 'direct',
        })
        
        # Test batch method onchange
        wizard.copy_method = 'batch'
        wizard._onchange_copy_method()
        self.assertEqual(wizard.batch_size, 10)
        
        # Test smart method onchange
        wizard.copy_method = 'smart'
        wizard._onchange_copy_method()
        self.assertTrue(wizard.enable_recovery)
        
        # Test category method onchange
        wizard.copy_method = 'category'
        wizard.copy_categories = 'all'
        wizard._onchange_copy_method()
        self.assertEqual(wizard.copy_categories, 'required')
    
    def test_batch_size_validation(self):
        """Test batch size validation"""
        wizard = self.env['copy.documents.wizard'].create({
            'source_product_id': self.test_product.id,
            'target_project_id': self.test_project.id,
            'copy_method': 'batch',
        })
        
        # Test minimum value
        wizard.batch_size = 0
        wizard._onchange_batch_size()
        self.assertEqual(wizard.batch_size, 1)
        
        # Test maximum value
        wizard.batch_size = 200
        wizard._onchange_batch_size()
        self.assertEqual(wizard.batch_size, 100)
        
        # Test valid value
        wizard.batch_size = 25
        wizard._onchange_batch_size()
        self.assertEqual(wizard.batch_size, 25)
    
    def test_direct_copy_method(self):
        """Test direct copy method execution"""
        wizard = self.env['copy.documents.wizard'].create({
            'source_product_id': self.test_product.id,
            'target_project_id': self.test_project.id,
            'copy_method': 'direct',
            'copy_categories': 'all',
            'document_ids': [(6, 0, [self.test_documents[0].id])],
        })
        
        # Execute copy
        result = wizard.action_copy_documents()
        
        # Verify results
        self.assertTrue(wizard.copy_success)
        self.assertEqual(wizard.copied_count, 1)
        self.assertEqual(wizard.method_used, 'direct')
        self.assertGreater(wizard.processing_time, 0)
    
    def test_category_copy_method(self):
        """Test category-based copy method execution"""
        wizard = self.env['copy.documents.wizard'].create({
            'source_product_id': self.test_product.id,
            'target_project_id': self.test_project.id,
            'copy_method': 'category',
            'copy_categories': 'required',
            'document_ids': [(6, 0, [self.test_documents[0].id])],
        })
        
        # Execute copy
        result = wizard.action_copy_documents()
        
        # Verify results
        self.assertTrue(wizard.copy_success)
        self.assertEqual(wizard.copied_count, 1)
        self.assertEqual(wizard.method_used, 'category')
    
    def test_template_copy_method(self):
        """Test template-based copy method execution"""
        wizard = self.env['copy.documents.wizard'].create({
            'source_product_id': self.test_product.id,
            'target_project_id': self.test_project.id,
            'copy_method': 'template',
            'copy_categories': 'all',
            'document_ids': [(6, 0, [self.test_documents[0].id])],
        })
        
        # Execute copy
        result = wizard.action_copy_documents()
        
        # Verify results
        self.assertTrue(wizard.copy_success)
        self.assertEqual(wizard.copied_count, 1)
        self.assertEqual(wizard.method_used, 'template')
    
    def test_batch_copy_method(self):
        """Test batch copy method execution"""
        wizard = self.env['copy.documents.wizard'].create({
            'source_product_id': self.test_product.id,
            'target_project_id': self.test_project.id,
            'copy_method': 'batch',
            'copy_categories': 'all',
            'batch_size': 5,
            'document_ids': [(6, 0, [self.test_documents[0].id])],
        })
        
        # Execute copy
        result = wizard.action_copy_documents()
        
        # Verify results
        self.assertTrue(wizard.copy_success)
        self.assertEqual(wizard.copied_count, 1)
        self.assertEqual(wizard.method_used, 'batch')
    
    def test_smart_copy_method(self):
        """Test smart copy method execution"""
        wizard = self.env['copy.documents.wizard'].create({
            'source_product_id': self.test_product.id,
            'target_project_id': self.test_project.id,
            'copy_method': 'smart',
            'copy_categories': 'all',
            'document_ids': [(6, 0, [self.test_documents[0].id])],
        })
        
        # Execute copy
        result = wizard.action_copy_documents()
        
        # Verify results
        self.assertTrue(wizard.copy_success)
        self.assertEqual(wizard.copied_count, 1)
        self.assertEqual(wizard.method_used, 'smart')
    
    def test_progress_tracking(self):
        """Test progress tracking during copy operation"""
        wizard = self.env['copy.documents.wizard'].create({
            'source_product_id': self.test_product.id,
            'target_project_id': self.test_project.id,
            'copy_method': 'direct',
            'copy_categories': 'all',
            'document_ids': [(6, 0, [self.test_documents[0].id])],
        })
        
        # Check initial state
        self.assertFalse(wizard.is_processing)
        self.assertEqual(wizard.progress_percentage, 0.0)
        
        # Execute copy
        result = wizard.action_copy_documents()
        
        # Check final state
        self.assertFalse(wizard.is_processing)
        self.assertEqual(wizard.progress_percentage, 100.0)
        self.assertIn('completed successfully', wizard.progress_message)
    
    def test_error_handling(self):
        """Test error handling in wizard"""
        # Create wizard without required fields
        wizard = self.env['copy.documents.wizard'].create({
            'copy_method': 'direct',
            'copy_categories': 'all',
        })
        
        # Try to execute copy without source/target
        result = wizard.action_copy_documents()
        
        # Verify error handling
        self.assertFalse(wizard.copy_success)
        self.assertIn('Error:', wizard.copy_error)
        self.assertEqual(wizard.progress_percentage, 0.0)
    
    def test_detailed_results(self):
        """Test detailed results tracking"""
        wizard = self.env['copy.documents.wizard'].create({
            'source_product_id': self.test_product.id,
            'target_project_id': self.test_project.id,
            'copy_method': 'direct',
            'copy_categories': 'all',
            'document_ids': [(6, 0, [self.test_documents[0].id])],
        })
        
        # Execute copy
        result = wizard.action_copy_documents()
        
        # Verify detailed results
        self.assertEqual(wizard.total_documents, 1)
        self.assertEqual(wizard.copied_count, 1)
        self.assertEqual(wizard.failed_count, 0)
        self.assertEqual(wizard.skipped_count, 0)
        self.assertEqual(wizard.recovered_count, 0)
        self.assertIsNotNone(wizard.copied_documents)
    
    def test_method_specific_configuration(self):
        """Test method-specific configuration options"""
        # Test batch method configuration
        wizard = self.env['copy.documents.wizard'].create({
            'source_product_id': self.test_product.id,
            'target_project_id': self.test_project.id,
            'copy_method': 'batch',
            'batch_size': 15,
            'enable_recovery': False,
        })
        
        self.assertEqual(wizard.batch_size, 15)
        self.assertFalse(wizard.enable_recovery)
        
        # Test smart method configuration
        wizard.copy_method = 'smart'
        wizard._onchange_copy_method()
        self.assertTrue(wizard.enable_recovery)  # Should be enabled for smart method
