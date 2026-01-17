# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging
from datetime import datetime, timedelta
from collections import defaultdict

_logger = logging.getLogger(__name__)


class SmartTemplateSuggestionEngine(models.AbstractModel):
    """
    Smart Template Suggestion Engine
    
    Provides intelligent template recommendations based on:
    - User preferences and behavior
    - Context analysis
    - Template compatibility
    - Usage patterns and frequency
    - Learning from user interactions
    """
    _name = 'smart.template.suggestion.engine'
    _description = 'Smart Template Suggestion Engine'
    
    @api.model
    def get_suggestions(self, context=None, limit=5, user_id=None):
        """
        Get intelligent template suggestions based on context and user behavior
        
        Args:
            context (dict): Current context (project_type, complexity, etc.)
            limit (int): Maximum number of suggestions to return
            user_id (int): User ID for personalized suggestions
            
        Returns:
            list: List of suggested templates with scores
        """
        try:
            # Get user preferences
            user_prefs = self._get_user_preferences(user_id)
            
            # Analyze context
            context_analysis = self._analyze_context(context or {})
            
            # Get candidate templates
            candidates = self._get_candidate_templates(context_analysis)
            
            # Score and rank templates
            scored_templates = self._score_templates(candidates, user_prefs, context_analysis)
            
            # Apply learning adjustments
            learned_suggestions = self._apply_learning_adjustments(scored_templates, user_id)
            
            # Return top suggestions
            return learned_suggestions[:limit]
            
        except Exception as e:
            _logger.error(f"Error generating suggestions: {str(e)}")
            return self._get_fallback_suggestions(limit)
    
    def _get_user_preferences(self, user_id=None):
        """Get user preferences for personalized suggestions"""
        if not user_id:
            user_id = self.env.user.id
            
        prefs = self.env['smart.template.user.preferences'].search([
            ('user_id', '=', user_id)
        ], limit=1)
        
        if not prefs:
            # Return default preferences
            return {
                'suggestion_level': 'active',
                'trigger_behavior': 'on_demand',
                'preferred_start_template': 'project',
                'enable_learning': True,
                'show_compatibility_warnings': True,
            }
        
        return {
            'suggestion_level': prefs.suggestion_level,
            'trigger_behavior': prefs.trigger_behavior,
            'preferred_start_template': prefs.preferred_start_template,
            'enable_learning': prefs.enable_learning,
            'show_compatibility_warnings': prefs.show_compatibility_warnings,
        }
    
    def _analyze_context(self, context):
        """Analyze current context to understand user needs"""
        analysis = {
            'project_type': context.get('project_type', 'general'),
            'complexity_level': context.get('complexity_level', 'medium'),
            'template_type': context.get('template_type', 'project'),
            'user_role': context.get('user_role', 'user'),
            'time_of_day': datetime.now().hour,
            'day_of_week': datetime.now().weekday(),
            'recent_activity': self._get_recent_activity(context.get('user_id')),
        }
        
        return analysis
    
    def _get_candidate_templates(self, context_analysis):
        """Get candidate templates based on context analysis"""
        domain = [('is_active', '=', True)]
        
        # Filter by template type
        if context_analysis['template_type'] == 'project':
            domain.append(('_name', '=', 'smart.project.template'))
        elif context_analysis['template_type'] == 'task':
            domain.append(('_name', '=', 'smart.task.template'))
        elif context_analysis['template_type'] == 'document':
            domain.append(('_name', '=', 'smart.document.template'))
        elif context_analysis['template_type'] == 'checkpoint':
            domain.append(('_name', '=', 'smart.checkpoint.template'))
        elif context_analysis['template_type'] == 'milestone':
            domain.append(('_name', '=', 'smart.milestone.template'))
        
        # Filter by complexity level
        if context_analysis['complexity_level'] in ['simple', 'medium', 'complex']:
            domain.append(('complexity_level', '=', context_analysis['complexity_level']))
        
        # Get templates from all relevant models
        candidates = []
        template_models = [
            'smart.project.template',
            'smart.task.template', 
            'smart.document.template',
            'smart.checkpoint.template',
            'smart.milestone.template'
        ]
        
        for model_name in template_models:
            if context_analysis['template_type'] == 'all' or model_name == f"smart.{context_analysis['template_type']}.template":
                templates = self.env[model_name].search(domain)
                for template in templates:
                    candidates.append({
                        'id': template.id,
                        'name': template.name,
                        'model': model_name,
                        'template': template,
                        'complexity_level': getattr(template, 'complexity_level', 'medium'),
                        'usage_count': getattr(template, 'usage_count', 0),
                        'last_used': getattr(template, 'last_used', False),
                        'compatibility_score': getattr(template, 'compatibility_score', 0.0),
                    })
        
        return candidates
    
    def _score_templates(self, candidates, user_prefs, context_analysis):
        """Score templates based on multiple factors"""
        scored_templates = []
        
        for candidate in candidates:
            score = 0.0
            template = candidate['template']
            
            # Base score from compatibility
            score += candidate['compatibility_score'] * 0.3
            
            # Usage frequency score
            usage_score = min(candidate['usage_count'] / 10.0, 1.0) * 0.2
            score += usage_score
            
            # Recency score (recently used templates get higher scores)
            if candidate['last_used']:
                days_since_used = (datetime.now() - candidate['last_used']).days
                recency_score = max(0, (30 - days_since_used) / 30.0) * 0.2
                score += recency_score
            
            # Complexity matching score
            if candidate['complexity_level'] == context_analysis['complexity_level']:
                score += 0.2
            
            # User preference matching
            if user_prefs['suggestion_level'] == 'smart':
                score += 0.1
            
            scored_templates.append({
                'template': template,
                'score': min(score, 1.0),  # Cap at 1.0
                'candidate': candidate,
            })
        
        # Sort by score (highest first)
        scored_templates.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_templates
    
    def _apply_learning_adjustments(self, scored_templates, user_id):
        """Apply learning adjustments based on user behavior patterns"""
        if not user_id:
            return scored_templates
        
        # Get user's historical preferences
        learning_data = self._get_learning_data(user_id)
        
        # Adjust scores based on learning
        for suggestion in scored_templates:
            template_id = suggestion['template'].id
            
            # Boost score for frequently used templates
            if template_id in learning_data.get('frequently_used', []):
                suggestion['score'] *= 1.2
            
            # Reduce score for rarely used templates
            if template_id in learning_data.get('rarely_used', []):
                suggestion['score'] *= 0.8
        
        # Re-sort after learning adjustments
        scored_templates.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_templates
    
    def _get_learning_data(self, user_id):
        """Get learning data for user behavior patterns"""
        # This would typically come from a learning data model
        # For now, return empty data structure
        return {
            'frequently_used': [],
            'rarely_used': [],
            'recently_successful': [],
        }
    
    def _get_recent_activity(self, user_id):
        """Get recent user activity for context analysis"""
        if not user_id:
            return []
        
        # Get recent template usage
        recent_usage = []
        template_models = [
            'smart.project.template',
            'smart.task.template',
            'smart.document.template',
            'smart.checkpoint.template',
            'smart.milestone.template'
        ]
        
        for model_name in template_models:
            templates = self.env[model_name].search([
                ('last_used', '>=', datetime.now() - timedelta(days=7))
            ], limit=5)
            recent_usage.extend(templates.mapped('id'))
        
        return recent_usage
    
    def _get_fallback_suggestions(self, limit):
        """Get fallback suggestions when main engine fails"""
        fallback_templates = []
        
        # Get most popular templates as fallback
        template_models = [
            'smart.project.template',
            'smart.task.template',
            'smart.document.template',
            'smart.checkpoint.template',
            'smart.milestone.template'
        ]
        
        for model_name in template_models:
            templates = self.env[model_name].search([
                ('is_active', '=', True)
            ], limit=2, order='usage_count desc')
            
            for template in templates:
                fallback_templates.append({
                    'template': template,
                    'score': 0.5,  # Default fallback score
                    'candidate': {
                        'id': template.id,
                        'name': template.name,
                        'model': model_name,
                        'template': template,
                    }
                })
        
        return fallback_templates[:limit]
    
    @api.model
    def check_template_compatibility(self, template_ids, context=None):
        """
        Check compatibility between templates
        
        Args:
            template_ids (list): List of template IDs to check
            context (dict): Context for compatibility checking
            
        Returns:
            dict: Compatibility analysis results
        """
        try:
            compatibility_results = {
                'compatible': True,
                'warnings': [],
                'conflicts': [],
                'suggestions': [],
                'compatibility_score': 1.0
            }
            
            if len(template_ids) < 2:
                return compatibility_results
            
            # Get templates
            templates = []
            for template_id in template_ids:
                # Find template in any model
                for model_name in ['smart.project.template', 'smart.task.template', 
                                 'smart.document.template', 'smart.checkpoint.template', 
                                 'smart.milestone.template']:
                    template = self.env[model_name].browse(template_id)
                    if template.exists():
                        templates.append(template)
                        break
            
            if len(templates) < 2:
                return compatibility_results
            
            # Check for conflicts
            conflicts = self._check_template_conflicts(templates)
            if conflicts:
                compatibility_results['compatible'] = False
                compatibility_results['conflicts'] = conflicts
                compatibility_results['compatibility_score'] = 0.0
            
            # Check for warnings
            warnings = self._check_template_warnings(templates, context)
            compatibility_results['warnings'] = warnings
            
            # Generate suggestions
            suggestions = self._generate_compatibility_suggestions(templates, context)
            compatibility_results['suggestions'] = suggestions
            
            # Calculate overall compatibility score
            if compatibility_results['compatible']:
                compatibility_results['compatibility_score'] = self._calculate_compatibility_score(templates)
            
            return compatibility_results
            
        except Exception as e:
            _logger.error(f"Error checking template compatibility: {str(e)}")
            return {
                'compatible': False,
                'warnings': [f"Error checking compatibility: {str(e)}"],
                'conflicts': [],
                'suggestions': [],
                'compatibility_score': 0.0
            }
    
    def _check_template_conflicts(self, templates):
        """Check for conflicts between templates"""
        conflicts = []
        
        # Check for duplicate template types
        template_types = defaultdict(list)
        for template in templates:
            if hasattr(template, 'template_type'):
                template_types[template.template_type].append(template.name)
        
        for template_type, names in template_types.items():
            if len(names) > 1:
                conflicts.append(f"Multiple {template_type} templates selected: {', '.join(names)}")
        
        # Check for complexity mismatches
        complexity_levels = [getattr(t, 'complexity_level', 'medium') for t in templates]
        if len(set(complexity_levels)) > 1:
            conflicts.append(f"Complexity level mismatch: {', '.join(set(complexity_levels))}")
        
        return conflicts
    
    def _check_template_warnings(self, templates, context):
        """Check for warnings between templates"""
        warnings = []
        
        # Check for missing relationships
        project_templates = [t for t in templates if t._name == 'smart.project.template']
        other_templates = [t for t in templates if t._name != 'smart.project.template']
        
        if project_templates and other_templates:
            for project_template in project_templates:
                for other_template in other_templates:
                    if not self._templates_are_related(project_template, other_template):
                        warnings.append(f"Template '{other_template.name}' is not linked to project template '{project_template.name}'")
        
        return warnings
    
    def _templates_are_related(self, project_template, other_template):
        """Check if templates are related"""
        try:
            if other_template._name == 'smart.task.template':
                return other_template in project_template.task_template_ids
            elif other_template._name == 'smart.document.template':
                return other_template in project_template.document_template_ids
            elif other_template._name == 'smart.checkpoint.template':
                return other_template in project_template.checkpoint_template_ids
            elif other_template._name == 'smart.milestone.template':
                return other_template in project_template.milestone_template_ids
        except:
            pass
        return False
    
    def _generate_compatibility_suggestions(self, templates, context):
        """Generate suggestions for improving template compatibility"""
        suggestions = []
        
        # Suggest linking unlinked templates
        project_templates = [t for t in templates if t._name == 'smart.project.template']
        other_templates = [t for t in templates if t._name != 'smart.project.template']
        
        if project_templates and other_templates:
            for project_template in project_templates:
                for other_template in other_templates:
                    if not self._templates_are_related(project_template, other_template):
                        suggestions.append(f"Link '{other_template.name}' to project template '{project_template.name}' for better integration")
        
        return suggestions
    
    def _calculate_compatibility_score(self, templates):
        """Calculate overall compatibility score"""
        if not templates:
            return 0.0
        
        # Base score
        score = 1.0
        
        # Reduce score for complexity mismatches
        complexity_levels = [getattr(t, 'complexity_level', 'medium') for t in templates]
        if len(set(complexity_levels)) > 1:
            score -= 0.2
        
        # Reduce score for missing relationships
        project_templates = [t for t in templates if t._name == 'smart.project.template']
        other_templates = [t for t in templates if t._name != 'smart.project.template']
        
        if project_templates and other_templates:
            linked_count = 0
            total_links = len(project_templates) * len(other_templates)
            
            for project_template in project_templates:
                for other_template in other_templates:
                    if self._templates_are_related(project_template, other_template):
                        linked_count += 1
            
            if total_links > 0:
                link_ratio = linked_count / total_links
                score *= link_ratio
        
        return max(0.0, min(1.0, score))
    
    @api.model
    def learn_from_user_action(self, template_id, action, user_id=None, context=None):
        """
        Learn from user actions to improve future suggestions
        
        Args:
            template_id (int): ID of the template
            action (str): Action taken ('selected', 'ignored', 'applied', etc.)
            user_id (int): User ID
            context (dict): Context of the action
        """
        try:
            if not user_id:
                user_id = self.env.user.id
            
            # This would typically store learning data in a dedicated model
            # For now, we'll just log the learning event
            _logger.info(f"Learning from user action: User {user_id} {action} template {template_id}")
            
            # Update template usage statistics
            self._update_template_usage_stats(template_id, action)
            
        except Exception as e:
            _logger.error(f"Error learning from user action: {str(e)}")
    
    def _update_template_usage_stats(self, template_id, action):
        """Update template usage statistics"""
        try:
            # Find template in any model
            for model_name in ['smart.project.template', 'smart.task.template', 
                             'smart.document.template', 'smart.checkpoint.template', 
                             'smart.milestone.template']:
                template = self.env[model_name].browse(template_id)
                if template.exists():
                    if action in ['selected', 'applied']:
                        template.update_usage()
                    break
        except Exception as e:
            _logger.error(f"Error updating template usage stats: {str(e)}")