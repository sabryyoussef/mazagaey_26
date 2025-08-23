# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestTemplateIntegration(TransactionCase):
    """Test the integration between milestone templates and checkpoint templates"""

    def setUp(self):
        super().setUp()
        
        # Create test project
        self.project = self.env['project.project'].create({
            'name': 'Test Project',
        })
        
        # Create test task
        self.task = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.project.id,
        })
        
        # Create test checkpoint tag
        self.tag = self.env['project.task.checkpoint.tag'].create({
            'name': 'Test Tag',
        })

    def test_milestone_template_creation(self):
        """Test milestone template creation and application"""
        # Create milestone template
        milestone_template = self.env['project.milestone.template'].create({
            'name': 'Test Milestone Template',
            'milestone_name': 'Test Milestone',
            'milestone_deadline': '2025-12-31',
            'project_id': self.project.id,
        })
        
        # Add checkpoint definition
        checkpoint_line = self.env['project.milestone.template.checkpoint'].create({
            'template_id': milestone_template.id,
            'name': 'Test Checkpoint',
            'sequence': 10,
            'tag_ids': [(6, 0, [self.tag.id])],
        })
        
        # Verify template creation
        self.assertEqual(milestone_template.checkpoint_count, 1)
        self.assertEqual(milestone_template.milestone_name, 'Test Milestone')
        
        # Apply template
        milestone = milestone_template.apply_to_project(self.project)
        
        # Verify milestone creation
        self.assertEqual(milestone.name, 'Test Milestone')
        self.assertEqual(milestone.project_id, self.project)
        self.assertEqual(len(milestone.checkpoint_ids), 1)
        
        # Verify checkpoint creation
        checkpoint = milestone.checkpoint_ids[0]
        self.assertEqual(checkpoint.name, 'Test Checkpoint')
        self.assertEqual(checkpoint.milestone_id, milestone)
        self.assertEqual(checkpoint.tag_ids, self.tag)

    def test_checkpoint_template_with_milestone(self):
        """Test checkpoint template with milestone creation"""
        # Create checkpoint template with milestone enabled
        checkpoint_template = self.env['project.task.checkpoint.template'].create({
            'name': 'Test Checkpoint Template',
            'create_milestone': True,
            'milestone_name': 'Test Milestone from Checkpoint',
            'milestone_deadline': '2025-12-31',
        })
        
        # Add checkpoint line
        checkpoint_line = self.env['project.task.checkpoint.template.line'].create({
            'template_id': checkpoint_template.id,
            'name': 'Test Checkpoint',
            'sequence': 10,
            'tag_ids': [(6, 0, [self.tag.id])],
        })
        
        # Apply template to task
        self.task._instantiate_template_checkpoints(checkpoint_template)
        
        # Verify milestone creation
        milestones = self.env['project.milestone'].search([
            ('name', '=', 'Test Milestone from Checkpoint'),
            ('project_id', '=', self.project.id)
        ])
        self.assertEqual(len(milestones), 1)
        
        # Verify checkpoint creation and linking
        checkpoints = self.task.checkpoint_ids.filtered(
            lambda c: c.name == 'Test Checkpoint'
        )
        self.assertEqual(len(checkpoints), 1)
        self.assertEqual(checkpoints[0].milestone_id, milestones[0])

    def test_checkpoint_template_without_milestone(self):
        """Test checkpoint template without milestone creation"""
        # Create checkpoint template without milestone
        checkpoint_template = self.env['project.task.checkpoint.template'].create({
            'name': 'Test Checkpoint Template No Milestone',
            'create_milestone': False,
        })
        
        # Add checkpoint line
        checkpoint_line = self.env['project.task.checkpoint.template.line'].create({
            'template_id': checkpoint_template.id,
            'name': 'Test Checkpoint No Milestone',
            'sequence': 10,
        })
        
        # Apply template to task
        self.task._instantiate_template_checkpoints(checkpoint_template)
        
        # Verify checkpoint creation without milestone
        checkpoints = self.task.checkpoint_ids.filtered(
            lambda c: c.name == 'Test Checkpoint No Milestone'
        )
        self.assertEqual(len(checkpoints), 1)
        self.assertFalse(checkpoints[0].milestone_id)

    def test_template_selection_wizard(self):
        """Test template selection wizard functionality"""
        # Create milestone template
        milestone_template = self.env['project.milestone.template'].create({
            'name': 'Wizard Test Milestone Template',
            'milestone_name': 'Wizard Test Milestone',
            'project_id': self.project.id,
        })
        
        # Create wizard for milestone template
        wizard = self.env['template.selection.wizard'].create({
            'template_type': 'milestone',
            'project_id': self.project.id,
            'milestone_template_id': milestone_template.id,
        })
        
        # Verify wizard functionality
        self.assertEqual(wizard.template_name, 'Wizard Test Milestone Template')
        self.assertEqual(wizard.template_type, 'milestone')
        
        # Test milestone template application through wizard
        result = wizard.action_apply_template()
        self.assertEqual(result['res_model'], 'project.milestone')

    def test_milestone_auto_advancement(self):
        """Test milestone auto-advancement when all checkpoints are reached"""
        # Create milestone with checkpoints
        milestone = self.env['project.milestone'].create({
            'name': 'Auto Advance Test Milestone',
            'project_id': self.project.id,
        })
        
        # Create checkpoints
        checkpoint1 = self.env['project.task.checkpoint'].create({
            'name': 'Checkpoint 1',
            'milestone_id': milestone.id,
            'is_reached': False,
        })
        
        checkpoint2 = self.env['project.task.checkpoint'].create({
            'name': 'Checkpoint 2',
            'milestone_id': milestone.id,
            'is_reached': False,
        })
        
        # Verify initial state
        self.assertFalse(milestone.is_reached)
        self.assertEqual(milestone.checkpoint_count, 2)
        self.assertEqual(milestone.completed_checkpoint_count, 0)
        
        # Mark first checkpoint as reached
        checkpoint1.is_reached = True
        self.assertFalse(milestone.is_reached)  # Should still be False
        
        # Mark second checkpoint as reached
        checkpoint2.is_reached = True
        self.assertTrue(milestone.is_reached)  # Should now be True
        
        # Unmark one checkpoint
        checkpoint1.is_reached = False
        self.assertFalse(milestone.is_reached)  # Should be False again

    def test_template_validation(self):
        """Test template validation and error handling"""
        # Test milestone template without checkpoints
        milestone_template = self.env['project.milestone.template'].create({
            'name': 'Empty Template',
            'milestone_name': 'Empty Milestone',
        })
        
        # Should raise error when trying to apply template without checkpoints
        with self.assertRaises(ValidationError):
            milestone_template.apply_to_current_project()

    def test_backward_compatibility(self):
        """Test backward compatibility with existing checkpoint templates"""
        # Create checkpoint template without milestone fields (old style)
        checkpoint_template = self.env['project.task.checkpoint.template'].create({
            'name': 'Backward Compatible Template',
            'create_milestone': False,  # Default value
        })
        
        # Add checkpoint line
        checkpoint_line = self.env['project.task.checkpoint.template.line'].create({
            'template_id': checkpoint_template.id,
            'name': 'Backward Compatible Checkpoint',
            'sequence': 10,
        })
        
        # Apply template (should work without errors)
        self.task._instantiate_template_checkpoints(checkpoint_template)
        
        # Verify checkpoint creation
        checkpoints = self.task.checkpoint_ids.filtered(
            lambda c: c.name == 'Backward Compatible Checkpoint'
        )
        self.assertEqual(len(checkpoints), 1)
        self.assertFalse(checkpoints[0].milestone_id)
