# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestProjectTemplate(TransactionCase):
    """Test Project Template functionality"""

    def setUp(self):
        super().setUp()
        self.project_template = self.env['project.project'].create({
            'name': 'Test Template',
            'is_template': True,
            'template_category': 'general',
            'complexity_level': 'simple',
            'estimated_duration': 10,
            'template_description': 'Test template for unit tests',
        })

    def test_template_creation(self):
        """Test that templates are created correctly"""
        self.assertTrue(self.project_template.is_template)
        self.assertEqual(self.project_template.template_category, 'general')
        self.assertFalse(self.project_template.use_documents)  # Should be disabled for templates

    def test_create_from_template(self):
        """Test creating a new project from template"""
        # Create a task in the template
        task = self.env['project.task'].create({
            'name': 'Template Task',
            'project_id': self.project_template.id,
            'description': 'Test task in template',
        })

        # Create project from template
        action = self.project_template.action_create_from_template()
        
        # Verify action returns project view
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'project.project')
        self.assertTrue('res_id' in action)

        # Get the created project
        new_project = self.env['project.project'].browse(action['res_id'])
        
        # Verify project is not a template
        self.assertFalse(new_project.is_template)
        self.assertTrue(new_project.name.endswith(' - Copy'))
        
        # Verify task was copied
        self.assertEqual(len(new_project.task_ids), 1)
        self.assertEqual(new_project.task_ids[0].name, 'Template Task')

    def test_template_validation(self):
        """Test template validation"""
        # Non-template project should raise error when trying to create from template
        regular_project = self.env['project.project'].create({
            'name': 'Regular Project',
            'is_template': False,
        })
        
        with self.assertRaises(ValidationError):
            regular_project.action_create_from_template()

    def test_usage_count_tracking(self):
        """Test that usage count is tracked"""
        initial_count = self.project_template.usage_count
        
        # Create project from template
        self.project_template.action_create_from_template()
        
        # Usage count should increment
        self.assertEqual(self.project_template.usage_count, initial_count + 1)
        self.assertTrue(self.project_template.last_used_date)

    def test_documents_disabled_for_templates(self):
        """Test that documents are disabled for templates"""
        # Create a new template
        template = self.env['project.project'].create({
            'name': 'Test Template with Documents',
            'is_template': True,
            'template_category': 'company_formation',
        })
        
        # use_documents should be False for templates
        self.assertFalse(template.use_documents)
