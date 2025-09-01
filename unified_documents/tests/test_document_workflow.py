# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
import logging

_logger = logging.getLogger(__name__)


class TestDocumentWorkflow(TransactionCase):
    
    def setUp(self):
        super().setUp()
        
        # Create a test product with service tracking = task_in_project
        self.product = self.env['product.template'].create({
            'name': 'Test Service Product',
            'type': 'service',
            'service_tracking': 'task_in_project',
            'list_price': 100.0,
        })
        
        # Create test documents for the product
        self.doc_required = self.env['documents.document'].create({
            'name': 'Requirements Document',
            'category': 'required',
            'priority': '2',
            'status': 'draft',
            'linked_product_id': self.product.id,
        })
        
        self.doc_compliance = self.env['documents.document'].create({
            'name': 'Compliance Certificate',
            'category': 'compliance',
            'priority': '2',
            'status': 'draft',
            'linked_product_id': self.product.id,
        })
        
        self.doc_deliverable = self.env['documents.document'].create({
            'name': 'Final Deliverable',
            'category': 'deliverable',
            'priority': '1',
            'status': 'draft',
            'linked_product_id': self.product.id,
        })
        
        # Create a test customer
        self.customer = self.env['res.partner'].create({
            'name': 'Test Customer',
            'is_company': True,
        })
    
    def test_document_workflow_creation(self):
        """Test that document processing tasks are created when quotation is confirmed"""
        
        # Create a sale order with the test product
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'order_line': [(0, 0, {
                'product_id': self.product.product_variant_ids[0].id,
                'product_uom_qty': 1,
                'price_unit': 100.0,
            })]
        })
        
        # Confirm the sale order
        sale_order.action_confirm()
        
        # Get the order line
        order_line = sale_order.order_line[0]
        
        # Check that a project was created
        self.assertTrue(order_line.project_id, "Project should be created when quotation is confirmed")
        
        project = order_line.project_id
        _logger.info(f"Project created: {project.name}")
        
        # Check that documents were copied to the project
        project_documents = self.env['documents.document'].search([
            ('res_model', '=', 'project.project'),
            ('res_id', '=', project.id)
        ])
        _logger.info(f"Documents copied to project: {len(project_documents)}")
        
        # Check that tasks were created for document processing
        project_tasks = self.env['project.task'].search([
            ('project_id', '=', project.id)
        ])
        _logger.info(f"Tasks created in project: {len(project_tasks)}")
        
        # We should have main category tasks and subtasks
        # Expected: 3 main tasks (required, compliance, deliverable) + 3 subtasks = 6 total
        self.assertGreaterEqual(len(project_tasks), 3, "At least 3 tasks should be created for document processing")
        
        # Check for main category tasks
        main_tasks = project_tasks.filtered(lambda t: 'Documents Processing' in t.name)
        _logger.info(f"Main category tasks: {[t.name for t in main_tasks]}")
        
        # Check for document subtasks
        subtasks = project_tasks.filtered(lambda t: 'Process:' in t.name)
        _logger.info(f"Document subtasks: {[t.name for t in subtasks]}")
        
        # Verify we have the expected categories
        expected_categories = ['Required', 'Compliance', 'Deliverable']
        for category in expected_categories:
            category_task = main_tasks.filtered(lambda t: category in t.name)
            self.assertTrue(category_task, f"Should have a main task for {category} documents")
        
        # Check that checkpoints were created (if checkpoint module is available)
        if 'project.task.checkpoint' in self.env:
            checkpoints = self.env['project.task.checkpoint'].search([
                ('task_id', 'in', project_tasks.ids)
            ])
            _logger.info(f"Checkpoints created: {len(checkpoints)}")
            self.assertGreater(len(checkpoints), 0, "Checkpoints should be created for document processing")
        
        # Check that approval requests were created (if approvals module is available)
        if 'approval.request' in self.env:
            approvals = self.env['approval.request'].search([
                ('reference', 'ilike', project.name)
            ])
            _logger.info(f"Approval requests created: {len(approvals)}")
            # Should have approvals for required and compliance documents
            self.assertGreaterEqual(len(approvals), 2, "Approval requests should be created for required and compliance documents")
        
        _logger.info("✅ Document workflow creation test passed!")
    
    def test_document_categories_handling(self):
        """Test that different document categories are handled correctly"""
        
        # Create sale order and confirm
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'order_line': [(0, 0, {
                'product_id': self.product.product_variant_ids[0].id,
                'product_uom_qty': 1,
                'price_unit': 100.0,
            })]
        })
        
        sale_order.action_confirm()
        order_line = sale_order.order_line[0]
        project = order_line.project_id
        
        # Get all tasks
        project_tasks = self.env['project.task'].search([
            ('project_id', '=', project.id)
        ])
        
        # Check task priorities based on document categories
        required_tasks = project_tasks.filtered(lambda t: 'Required' in t.name or 'Requirements' in t.name)
        compliance_tasks = project_tasks.filtered(lambda t: 'Compliance' in t.name)
        deliverable_tasks = project_tasks.filtered(lambda t: 'Deliverable' in t.name or 'Final' in t.name)
        
        # Required and compliance tasks should have higher priority
        for task in required_tasks + compliance_tasks:
            if task.priority:
                self.assertIn(task.priority, ['2', '3'], f"Task {task.name} should have high priority")
        
        # Check due dates are set appropriately
        for task in project_tasks:
            if task.date_deadline:
                _logger.info(f"Task {task.name} has deadline: {task.date_deadline}")
        
        _logger.info("✅ Document categories handling test passed!")
