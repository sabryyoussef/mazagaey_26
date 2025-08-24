# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class ProjectTaskGenerationService(models.Model):
    _name = 'project.task.generation.service'
    _description = 'Project Task Generation Service'

    def generate_tasks_from_project_template(self, project_template, task_templates=None, options=None):
        """
        Generate tasks from project template documents and requirements
        
        Args:
            project_template: project.project record (template)
            task_templates: list of project.task.template records (optional)
            options: dict with generation options (optional)
        
        Returns:
            dict: {'success': bool, 'tasks_created': int, 'message': str}
        """
        try:
            if not project_template:
                return {'success': False, 'tasks_created': 0, 'message': 'No project template provided'}
            
            if not task_templates:
                # Get default task templates based on project template
                task_templates = self._get_default_task_templates(project_template)
            
            if not options:
                options = self._get_default_options()
            
            tasks_created = 0
            created_tasks = []
            
            # Generate tasks based on template types
            for task_template in task_templates:
                if task_template.template_type == 'document_based':
                    tasks = self.generate_document_based_tasks(project_template, task_template, options)
                elif task_template.template_type == 'progress_tracking':
                    tasks = self.generate_progress_tracking_tasks(project_template, task_template, options)
                elif task_template.template_type == 'milestone':
                    tasks = self.generate_milestone_tasks(project_template, task_template, options)
                else:
                    tasks = self.generate_custom_tasks(project_template, task_template, options)
                
                created_tasks.extend(tasks)
                tasks_created += len(tasks)
            
            # Set task dependencies
            self._set_task_dependencies(created_tasks, task_templates)
            
            # Record usage
            self._record_template_usage(project_template, task_templates, created_tasks)
            
            return {
                'success': True,
                'tasks_created': tasks_created,
                'message': f'Successfully created {tasks_created} tasks from {len(task_templates)} templates',
                'tasks': created_tasks
            }
            
        except Exception as e:
            _logger.error(f"Error generating tasks from project template: {e}")
            return {'success': False, 'tasks_created': 0, 'message': f'Error: {str(e)}'}

    def generate_document_based_tasks(self, project_template, task_template, options):
        """Generate tasks based on document categories"""
        tasks = []
        
        # Get documents from project template
        documents = self._get_project_documents(project_template)
        
        if not documents:
            _logger.info(f"No documents found in project template {project_template.name}")
            return tasks
        
        # Group documents by category
        documents_by_category = self._group_documents_by_category(documents)
        
        # Generate tasks for each category
        for category, docs in documents_by_category.items():
            if task_template.document_category == 'all' or task_template.document_category == category:
                task = self._create_task_from_template(
                    project_template, task_template, {
                        'category': category,
                        'count': len(docs),
                        'project_name': project_template.name,
                        'documents': docs
                    }
                )
                if task:
                    tasks.append(task)
        
        return tasks

    def generate_progress_tracking_tasks(self, project_template, task_template, options):
        """Generate progress tracking tasks"""
        tasks = []
        
        # Get documents from project template
        documents = self._get_project_documents(project_template)
        
        if not documents:
            return tasks
        
        # Create overall progress tracking task
        if options.get('generate_overall_progress', True):
            task = self._create_task_from_template(
                project_template, task_template, {
                    'category': 'Overall Progress',
                    'count': len(documents),
                    'project_name': project_template.name,
                    'documents': documents
                }
            )
            if task:
                tasks.append(task)
        
        # Create category-specific progress tracking tasks
        if options.get('generate_category_progress', True):
            documents_by_category = self._group_documents_by_category(documents)
            for category, docs in documents_by_category.items():
                task = self._create_task_from_template(
                    project_template, task_template, {
                        'category': f'{category.title()} Progress',
                        'count': len(docs),
                        'project_name': project_template.name,
                        'documents': docs
                    }
                )
                if task:
                    tasks.append(task)
        
        return tasks

    def generate_milestone_tasks(self, project_template, task_template, options):
        """Generate milestone tasks"""
        tasks = []
        
        # Get documents from project template
        documents = self._get_project_documents(project_template)
        
        if not documents:
            return tasks
        
        # Create milestone tasks based on document completion stages
        milestones = [
            {
                'name': 'Document Collection Complete',
                'description': 'All required documents have been collected',
                'trigger': 'required_complete'
            },
            {
                'name': 'Document Review Complete',
                'description': 'All documents have been reviewed and approved',
                'trigger': 'review_complete'
            },
            {
                'name': 'Document Submission Complete',
                'description': 'All documents have been submitted to relevant authorities',
                'trigger': 'submission_complete'
            }
        ]
        
        for milestone in milestones:
            task = self._create_task_from_template(
                project_template, task_template, {
                    'category': 'Milestone',
                    'count': len(documents),
                    'project_name': project_template.name,
                    'milestone_name': milestone['name'],
                    'milestone_description': milestone['description']
                }
            )
            if task:
                tasks.append(task)
        
        return tasks

    def generate_custom_tasks(self, project_template, task_template, options):
        """Generate custom tasks"""
        tasks = []
        
        # Create a single custom task
        task = self._create_task_from_template(
            project_template, task_template, {
                'category': 'Custom',
                'count': 1,
                'project_name': project_template.name
            }
        )
        if task:
            tasks.append(task)
        
        return tasks

    def _get_project_documents(self, project_template):
        """Get documents from project template"""
        documents = []
        
        # Check if project template has documents
        if hasattr(project_template, 'document_ids') and project_template.document_ids:
            documents = project_template.document_ids
        
        # If no documents in template, check linked documents
        elif hasattr(project_template, 'linked_document_ids') and project_template.linked_document_ids:
            documents = project_template.linked_document_ids
        
        return documents

    def _group_documents_by_category(self, documents):
        """Group documents by category"""
        grouped = {}
        for doc in documents:
            category = doc.category or 'reference'
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(doc)
        return grouped

    def _create_task_from_template(self, project_template, task_template, context_data):
        """Create a task from template with context data"""
        try:
            # Generate task name and description
            task_name = task_template.get_task_name(context_data)
            task_description = task_template.get_task_description(context_data)
            
            # Create task
            task_vals = {
                'name': task_name,
                'description': task_description,
                'project_id': project_template.id,
                'priority': task_template.priority,
                'allocated_hours': task_template.estimated_hours,
                'user_ids': [],  # No assignment by default
                'tag_ids': [],   # No tags by default
                'is_generated_from_template': True,
                'source_task_template_id': task_template.id,
                'template_generation_date': fields.Datetime.now(),
                'template_context_data': str(context_data),
            }
            
            task = self.env['project.task'].create(task_vals)
            
            _logger.info(f"Created task '{task_name}' from template '{task_template.name}'")
            return task
            
        except Exception as e:
            _logger.error(f"Error creating task from template: {e}")
            return None

    def _set_task_dependencies(self, tasks, task_templates):
        """Set dependencies between tasks based on template prerequisites"""
        for task_template in task_templates:
            if task_template.prerequisite_task_ids:
                # Find corresponding tasks for this template
                template_tasks = [t for t in tasks if t.name == task_template.get_task_name()]
                prerequisite_tasks = []
                
                for prereq_template in task_template.prerequisite_task_ids:
                    prereq_tasks = [t for t in tasks if t.name == prereq_template.get_task_name()]
                    prerequisite_tasks.extend(prereq_tasks)
                
                # Set dependencies
                for task in template_tasks:
                    if prerequisite_tasks:
                        task.depend_on_ids = [(6, 0, [t.id for t in prerequisite_tasks])]

    def _record_template_usage(self, project_template, task_templates, created_tasks):
        """Record usage of task templates"""
        for task_template in task_templates:
            for task in created_tasks:
                if task.name == task_template.get_task_name():
                    self.env['project.task.template.usage'].create({
                        'task_template_id': task_template.id,
                        'project_template_id': project_template.id,
                        'task_id': task.id,
                        'applied_by': self.env.user.id,
                        'document_category': task_template.document_category,
                        'document_count': len(self._get_project_documents(project_template)),
                        'project_name': project_template.name,
                    })

    def _get_default_task_templates(self, project_template):
        """Get default task templates based on project template"""
        # Get document-based templates
        document_templates = self.env['project.task.template'].search([
            ('template_type', '=', 'document_based'),
            ('active', '=', True)
        ])
        
        # Get progress tracking templates
        progress_templates = self.env['project.task.template'].search([
            ('template_type', '=', 'progress_tracking'),
            ('active', '=', True)
        ])
        
        # Get milestone templates
        milestone_templates = self.env['project.task.template'].search([
            ('template_type', '=', 'milestone'),
            ('active', '=', True)
        ])
        
        return document_templates + progress_templates + milestone_templates

    def _get_default_options(self):
        """Get default generation options"""
        return {
            'generate_document_tasks': True,
            'generate_progress_tasks': True,
            'generate_milestone_tasks': True,
            'generate_overall_progress': True,
            'generate_category_progress': True,
            'set_dependencies': True,
            'assign_users': False,
        }

    def apply_task_template_to_project(self, project, task_template):
        """Apply a single task template to an existing project"""
        try:
            context_data = {
                'category': task_template.document_category,
                'count': 1,
                'project_name': project.name,
            }
            
            task = self._create_task_from_template(project, task_template, context_data)
            
            if task:
                # Record usage
                self.env['project.task.template.usage'].create({
                    'task_template_id': task_template.id,
                    'project_id': project.id,
                    'task_id': task.id,
                    'applied_by': self.env.user.id,
                    'document_category': task_template.document_category,
                    'project_name': project.name,
                })
                
                return {'success': True, 'task': task, 'message': 'Task created successfully'}
            else:
                return {'success': False, 'task': None, 'message': 'Failed to create task'}
                
        except Exception as e:
            _logger.error(f"Error applying task template to project: {e}")
            return {'success': False, 'task': None, 'message': f'Error: {str(e)}'}
