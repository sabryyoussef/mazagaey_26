# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestTemplateApplication(TransactionCase):
    """Test Template Application tracking functionality"""

    def setUp(self):
        super().setUp()
        self.template = self.env['project.checkpoint.template'].create({
            'name': 'Test Template for Application',
            'sequence': 10,
        })

    def test_template_application_creation(self):
        """Test template application record creation"""
        application = self.env['project.template.application'].create({
            'template_id': self.template.id,
            'applied_to_model': 'project.task',
            'applied_to_id': 1,
            'status': 'applied',
            'total_items': 5,
            'completed_items': 0,
        })
        
        self.assertEqual(application.template_id, self.template)
        self.assertEqual(application.applied_to_model, 'project.task')
        self.assertEqual(application.status, 'applied')
        self.assertEqual(application.completion_percentage, 0.0)

    def test_completion_percentage_calculation(self):
        """Test completion percentage calculation"""
        application = self.env['project.template.application'].create({
            'template_id': self.template.id,
            'applied_to_model': 'project.task',
            'applied_to_id': 1,
            'status': 'in_progress',
            'total_items': 10,
            'completed_items': 3,
        })
        
        # Update completion
        application._compute_completion_percentage()
        self.assertEqual(application.completion_percentage, 30.0)
        
        # Complete all items
        application.write({'completed_items': 10})
        application._compute_completion_percentage()
        self.assertEqual(application.completion_percentage, 100.0)

    def test_application_progress_tracking(self):
        """Test application progress tracking"""
        application = self.env['project.template.application'].create({
            'template_id': self.template.id,
            'applied_to_model': 'project.project',
            'applied_to_id': 1,
            'status': 'applied',
            'total_items': 8,
            'completed_items': 0,
        })
        
        # Progress through application
        application.write({
            'status': 'in_progress',
            'completed_items': 4,
        })
        self.assertEqual(application.status, 'in_progress')
        self.assertEqual(application.completion_percentage, 50.0)
        
        # Complete application
        application.write({
            'status': 'completed',
            'completed_items': 8,
        })
        self.assertEqual(application.status, 'completed')
        self.assertEqual(application.completion_percentage, 100.0)

    def test_template_usage_statistics(self):
        """Test template usage statistics computation"""
        # Create multiple applications
        app1 = self.env['project.template.application'].create({
            'template_id': self.template.id,
            'applied_to_model': 'project.task',
            'applied_to_id': 1,
            'status': 'completed',
        })
        
        app2 = self.env['project.template.application'].create({
            'template_id': self.template.id,
            'applied_to_model': 'project.task',
            'applied_to_id': 2,
            'status': 'in_progress',
        })
        
        # Refresh template to compute usage stats
        self.template._compute_usage_stats()
        
        # Should have 2 applications
        self.assertEqual(self.template.usage_count, 2)
        self.assertTrue(self.template.last_used)
