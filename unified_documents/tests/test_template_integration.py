# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class TestTemplateIntegration(TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.product_template_model = self.env['unified.product.template']
        self.project_model = self.env['project.project']
        self.product_model = self.env['product.template']
        self.document_model = self.env['documents.document']
        
        # Create test data
        self.create_test_data()
    
    def create_test_data(self):
        """Create test data for template integration tests"""
        
        # Create a product template
        self.product_template = self.product_template_model.create({
            'name': 'Test Company Formation Template',
            'description': 'Test template for company formation services',
            'template_type': 'document_based',
            'service_tracking': 'task_in_project',
        })
        
        # Create document template lines
        self.document_line1 = self.env['unified.product.document.template.line'].create({
            'name': 'Company Formation Application',
            'description': 'Application form for company formation',
            'product_template_id': self.product_template.id,
            'category': 'required',
            'priority': '2',
            'notes': 'Required for all company formations',
        })
        
        self.document_line2 = self.env['unified.product.document.template.line'].create({
            'name': 'Business Plan Template',
            'description': 'Business plan template',
            'product_template_id': self.product_template.id,
            'category': 'reference',
            'priority': '1',
            'notes': 'Reference document for business planning',
        })
    
    def test_template_category_mapping(self):
        """Test template category mapping functionality"""
        
        # Test company formation category
        category = self.product_template._map_template_category()
        self.assertEqual(category, 'company_formation')
        
        # Test visa services category
        visa_template = self.product_template_model.create({
            'name': 'Visa Processing Template',
            'template_type': 'document_based',
        })
        category = visa_template._map_template_category()
        self.assertEqual(category, 'visa_services')
        
        # Test general category
        general_template = self.product_template_model.create({
            'name': 'General Service Template',
            'template_type': 'document_based',
        })
        category = general_template._map_template_category()
        self.assertEqual(category, 'general')
    
    def test_complexity_level_determination(self):
        """Test complexity level determination"""
        
        # Test simple complexity (few documents, no high priority)
        complexity = self.product_template._determine_complexity_level()
        self.assertEqual(complexity, 'simple')
        
        # Test medium complexity (more documents)
        for i in range(6):
            self.env['unified.product.document.template.line'].create({
                'name': f'Document {i}',
                'product_template_id': self.product_template.id,
                'category': 'required',
                'priority': '1',
            })
        
        complexity = self.product_template._determine_complexity_level()
        self.assertEqual(complexity, 'medium')
        
        # Test complex complexity (high priority document)
        high_priority_doc = self.env['unified.product.document.template.line'].create({
            'name': 'High Priority Document',
            'product_template_id': self.product_template.id,
            'category': 'required',
            'priority': '2',
        })
        
        complexity = self.product_template._determine_complexity_level()
        self.assertEqual(complexity, 'complex')
    
    def test_project_duration_estimation(self):
        """Test project duration estimation"""
        
        # Test base duration calculation
        duration = self.product_template._estimate_project_duration()
        expected_duration = 5 + (2 * 2) + 0  # base + (2 docs * 2 days) + complexity
        self.assertEqual(duration, expected_duration)
        
        # Test with more documents
        for i in range(5):
            self.env['unified.product.document.template.line'].create({
                'name': f'Document {i}',
                'product_template_id': self.product_template.id,
                'category': 'required',
                'priority': '1',
            })
        
        duration = self.product_template._estimate_project_duration()
        expected_duration = 5 + (7 * 2) + 5  # base + (7 docs * 2 days) + medium complexity
        self.assertEqual(duration, expected_duration)
    
    def test_project_template_creation(self):
        """Test project template creation from product template"""
        
        # Create project template
        result = self.product_template.action_create_project_template()
        
        # Verify project template was created
        self.assertTrue(self.product_template.project_template_id)
        self.assertTrue(self.product_template.project_template_id.is_template)
        self.assertEqual(self.product_template.project_template_id.template_category, 'company_formation')
        self.assertEqual(self.product_template.project_template_id.complexity_level, 'simple')
        
        # Verify template name and description
        self.assertIn('Project Template', self.product_template.project_template_id.name)
        self.assertIn('Auto-generated', self.product_template.project_template_id.description)
    
    def test_product_creation_from_template(self):
        """Test product creation from template with project"""
        
        # Create product from template
        product = self.product_template.create_product_from_template(
            product_name='Test Company Formation Service',
            create_documents=True,
            create_project=True
        )
        
        # Verify product was created
        self.assertTrue(product)
        self.assertEqual(product.name, 'Test Company Formation Service')
        self.assertEqual(product.type, 'service')
        self.assertEqual(product.service_tracking, 'task_in_project')
        
        # Verify documents were created
        self.assertEqual(len(product.document_ids), 2)
        document_names = [doc.name for doc in product.document_ids]
        self.assertIn('Company Formation Application', document_names)
        self.assertIn('Business Plan Template', document_names)
        
        # Verify project was created
        self.assertTrue(product.project_template_id)
        self.assertFalse(product.project_template_id.is_template)  # Should be a real project
    
    def test_document_copying_to_project(self):
        """Test document copying from product to project"""
        
        # Create product and project
        product = self.product_template.create_product_from_template(
            product_name='Test Service',
            create_documents=True,
            create_project=True
        )
        
        project = product.project_template_id
        
        # Verify documents were copied to project
        project_documents = self.document_model.search([
            ('res_model', '=', 'project.project'),
            ('res_id', '=', project.id)
        ])
        
        self.assertEqual(len(project_documents), 2)
        
        # Verify document properties
        for doc in project_documents:
            self.assertEqual(doc.linked_project_id, project)
            self.assertFalse(doc.linked_product_id)  # Should not be linked to product
    
    def test_template_auto_linking(self):
        """Test auto-linking of templates"""
        
        # Create a project template first
        project_template = self.project_model.create({
            'name': 'Company Formation Project Template',
            'is_template': True,
            'template_category': 'company_formation',
        })
        
        # Test auto-linking
        result = self.product_template.action_auto_link_templates()
        
        # Verify templates were linked
        self.assertEqual(self.product_template.project_template_id, project_template)
    
    def test_template_usage_tracking(self):
        """Test template usage tracking"""
        
        # Create product from template
        product = self.product_template.create_product_from_template(
            product_name='Test Service'
        )
        
        # Verify usage was recorded
        usage = self.env['unified.product.template.usage'].search([
            ('template_id', '=', self.product_template.id),
            ('product_id', '=', product.id)
        ])
        
        self.assertTrue(usage)
        self.assertEqual(usage.applied_by, self.env.user)
        self.assertIn('Product created from template', usage.notes)
    
    def test_template_domain_generation(self):
        """Test template domain generation for auto-linking"""
        
        # Test task template domain
        task_domain = self.product_template._get_task_template_domain('company_formation')
        expected_domain = [('template_type', 'in', ['company_setup', 'documentation', 'approval'])]
        self.assertEqual(task_domain, expected_domain)
        
        # Test checkpoint template domain
        checkpoint_domain = self.product_template._get_checkpoint_template_domain('visa_services')
        expected_domain = [('template_type', 'in', ['visa_application', 'documentation', 'approval'])]
        self.assertEqual(checkpoint_domain, expected_domain)
    
    def test_template_matching(self):
        """Test template matching functionality"""
        
        # Create a project template with similar name
        project_template = self.project_model.create({
            'name': 'Company Formation Services Project Template',
            'is_template': True,
            'template_category': 'company_formation',
        })
        
        # Test matching
        match = self.product_template._find_matching_project_template()
        self.assertEqual(match, project_template)
        
        # Test no match
        no_match_template = self.product_template_model.create({
            'name': 'Unrelated Template',
            'template_type': 'document_based',
        })
        match = no_match_template._find_matching_project_template()
        self.assertFalse(match)
    
    def test_error_handling(self):
        """Test error handling in template operations"""
        
        # Test creating project template when one already exists
        self.product_template.action_create_project_template()
        
        # Try to create another one
        result = self.product_template.action_create_project_template()
        self.assertEqual(result['params']['type'], 'warning')
    
    def test_template_integration_workflow(self):
        """Test complete template integration workflow"""
        
        # Step 1: Create product template
        self.assertTrue(self.product_template)
        self.assertEqual(len(self.product_template.document_template_line_ids), 2)
        
        # Step 2: Create project template
        self.product_template.action_create_project_template()
        self.assertTrue(self.product_template.project_template_id)
        self.assertTrue(self.product_template.project_template_id.is_template)
        
        # Step 3: Create product from template
        product = self.product_template.create_product_from_template(
            product_name='Integration Test Service',
            create_documents=True,
            create_project=True
        )
        
        # Step 4: Verify complete workflow
        self.assertTrue(product)
        self.assertEqual(len(product.document_ids), 2)
        self.assertTrue(product.project_template_id)
        self.assertFalse(product.project_template_id.is_template)  # Real project
        
        # Step 5: Verify project documents
        project_docs = self.document_model.search([
            ('res_model', '=', 'project.project'),
            ('res_id', '=', product.project_template_id.id)
        ])
        self.assertEqual(len(project_docs), 2)
        
        # Step 6: Verify usage tracking
        usage_count = self.product_template.usage_count
        self.assertEqual(usage_count, 1)
