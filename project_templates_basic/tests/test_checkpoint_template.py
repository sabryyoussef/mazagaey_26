# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestCheckpointTemplate(TransactionCase):
    """Test Checkpoint Template functionality"""

    def setUp(self):
        super().setUp()
        self.checkpoint_template = self.env['project.checkpoint.template'].create({
            'name': 'Test Checkpoint Template',
            'sequence': 10,
            'notes': 'Test checkpoint template for unit tests',
        })

    def test_checkpoint_template_creation(self):
        """Test that checkpoint templates are created correctly"""
        self.assertEqual(self.checkpoint_template.name, 'Test Checkpoint Template')
        self.assertEqual(self.checkpoint_template.sequence, 10)
        self.assertTrue(self.checkpoint_template.active)

    def test_milestone_configuration(self):
        """Test milestone configuration in checkpoint templates"""
        # Test with milestone creation disabled
        self.assertFalse(self.checkpoint_template.create_milestone)
        
        # Enable milestone creation
        self.checkpoint_template.write({
            'create_milestone': True,
            'milestone_name': 'Test Milestone',
            'milestone_deadline': 30,
            'milestone_notes': 'Test milestone notes',
        })
        
        self.assertTrue(self.checkpoint_template.create_milestone)
        self.assertEqual(self.checkpoint_template.milestone_name, 'Test Milestone')
        self.assertEqual(self.checkpoint_template.milestone_deadline, 30)

    def test_checkpoint_lines(self):
        """Test checkpoint template lines"""
        # Create checkpoint lines
        line1 = self.env['project.checkpoint.template.line'].create({
            'template_id': self.checkpoint_template.id,
            'name': 'Checkpoint Line 1',
            'sequence': 1,
            'auto_advance_stage': True,
            'notes': 'First checkpoint line',
        })
        
        line2 = self.env['project.checkpoint.template.line'].create({
            'template_id': self.checkpoint_template.id,
            'name': 'Checkpoint Line 2',
            'sequence': 2,
            'auto_advance_stage': False,
            'notes': 'Second checkpoint line',
        })
        
        # Verify lines are created
        self.assertEqual(len(self.checkpoint_template.line_ids), 2)
        self.assertEqual(self.checkpoint_template.line_count, 2)
        
        # Verify line properties
        self.assertEqual(line1.name, 'Checkpoint Line 1')
        self.assertTrue(line1.auto_advance_stage)
        self.assertFalse(line2.auto_advance_stage)

    def test_template_display_name(self):
        """Test template display names"""
        # Test without milestone
        self.assertEqual(self.checkpoint_template.display_milestone_name, self.checkpoint_template.name)
        
        # Test with milestone
        self.checkpoint_template.write({
            'create_milestone': True,
            'milestone_name': 'Custom Milestone',
        })
        
        # Display name should include milestone info
        self.assertIn('Custom Milestone', self.checkpoint_template.display_milestone_name)
