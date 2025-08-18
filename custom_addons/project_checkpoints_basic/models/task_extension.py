# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    checkpoint_ids = fields.One2many(
        'project.task.checkpoint',
        'task_id',
        string='Checkpoints',
        help='Checkpoints for this task'
    )
    
    # Template-related fields
    applied_checkpoint_template_ids = fields.Many2many(
        'project.task.checkpoint.template',
        string='Applied Checkpoint Templates',
        readonly=True,
        help='Checkpoint templates that have been applied to this task'
    )

    checkpoint_reached_count = fields.Integer(
        string='Reached Checkpoints',
        compute='_compute_checkpoint_reached_count',
        store=False,
        help='Number of reached checkpoints'
    )

    checkpoint_reached_by_tag_json = fields.Text(
        string='Reached Checkpoints by Tag',
        compute='_compute_checkpoint_reached_by_tag_json',
        store=False,
        help='JSON representation of reached checkpoints by tag'
    )
    
    # Computed fields for checkpoint progress
    checkpoint_count = fields.Integer(
        string='Total Checkpoints',
        compute='_compute_checkpoint_counts',
        store=False,
        help='Total number of checkpoints for this task'
    )
    
    completed_checkpoint_count = fields.Integer(
        string='Completed Checkpoints',
        compute='_compute_checkpoint_counts',
        store=False,
        help='Number of completed checkpoints'
    )
    
    checkpoint_progress = fields.Float(
        string='Checkpoint Progress',
        compute='_compute_checkpoint_counts',
        store=False,
        help='Progress percentage of completed checkpoints'
    )
    
    @api.depends('checkpoint_ids', 'checkpoint_ids.is_reached')
    def _compute_checkpoint_reached_count(self):
        """Compute the number of reached checkpoints"""
        for task in self:
            task.checkpoint_reached_count = len(task.checkpoint_ids.filtered(lambda c: c.is_reached))

    @api.depends('checkpoint_ids', 'checkpoint_ids.is_reached', 'checkpoint_ids.tag_ids')
    def _compute_checkpoint_reached_by_tag_json(self):
        """Compute reached checkpoints by tag as JSON"""
        import json
        for task in self:
            tag_counts = {}
            for checkpoint in task.checkpoint_ids.filtered(lambda c: c.is_reached):
                for tag in checkpoint.tag_ids:
                    tag_counts[tag.name] = tag_counts.get(tag.name, 0) + 1
            task.checkpoint_reached_by_tag_json = json.dumps(tag_counts)
    
    @api.depends('checkpoint_ids', 'checkpoint_ids.is_reached')
    def _compute_checkpoint_counts(self):
        """Compute checkpoint counts and progress"""
        for task in self:
            total_checkpoints = len(task.checkpoint_ids)
            completed_checkpoints = len(task.checkpoint_ids.filtered(lambda c: c.is_reached))
            
            task.checkpoint_count = total_checkpoints
            task.completed_checkpoint_count = completed_checkpoints
            
            if total_checkpoints > 0:
                task.checkpoint_progress = (completed_checkpoints / total_checkpoints) * 100
            else:
                task.checkpoint_progress = 0.0
    
    def _apply_checkpoint_templates_from_products(self, products=None):
        """Apply checkpoint templates from products to this task"""
        if not products:
            # Try to get product from sale line
            if hasattr(self, 'sale_line_id') and self.sale_line_id:
                products = [self.sale_line_id.product_id]
            else:
                return False
        
        applied_templates = []
        for product in products:
            if (product.type == 'service' and 
                product.auto_apply_checkpoint_templates and 
                product.checkpoint_template_ids):
                
                for template in product.checkpoint_template_ids:
                    if template not in self.applied_checkpoint_template_ids:
                        self._instantiate_template_checkpoints(template)
                        applied_templates.append(template)
        
        if applied_templates:
            self.applied_checkpoint_template_ids = [(4, template.id) for template in applied_templates]
            return True
        return False

    def _instantiate_template_checkpoints(self, template):
        """Instantiate checkpoints from a template with milestone support"""
        # Create milestone if requested
        milestone = None
        if template.create_milestone:
            milestone_vals = {
                'name': template.milestone_name or template.name,
                'project_id': self.project_id.id,
                'deadline': template.milestone_deadline,
            }
            milestone = self.env['project.milestone'].create(milestone_vals)
        
        # Create checkpoints
        for line in template.line_ids:
            checkpoint_vals = {
                'name': line.name,
                'sequence': line.sequence,
                'task_id': self.id,
                'milestone_id': milestone.id if milestone else False,
                'tag_ids': [(6, 0, line.tag_ids.ids)],
                'auto_advance_stage': line.auto_advance_stage,
                'target_stage_id': line.target_stage_id.id if line.target_stage_id else False,
                'notes': line.notes,
            }
            self.env['project.task.checkpoint'].create(checkpoint_vals)

    def _evaluate_checkpoint_rules(self):
        """Evaluate checkpoint rules and advance stages if conditions are met"""
        if not self.applied_checkpoint_template_ids:
            return
        
        # Get all rules from applied templates
        all_rules = self.env['project.task.checkpoint.rule'].search([
            ('template_id', 'in', self.applied_checkpoint_template_ids.ids),
            ('active', '=', True)
        ], order='sequence desc')
        
        for rule in all_rules:
            if self._check_rule_condition(rule):
                self._apply_rule_advancement(rule)
                break  # Only apply the highest priority rule

    def _check_rule_condition(self, rule):
        """Check if a rule condition is met"""
        total_checkpoints = len(self.checkpoint_ids)
        reached_checkpoints = len(self.checkpoint_ids.filtered(lambda c: c.is_reached))
        
        if rule.condition_type == 'all':
            return reached_checkpoints == total_checkpoints and total_checkpoints > 0
        
        elif rule.condition_type == 'min_count':
            return reached_checkpoints >= rule.min_count
        
        elif rule.condition_type == 'by_tag_count':
            for tag in rule.tag_ids:
                tag_checkpoints = self.checkpoint_ids.filtered(lambda c: tag in c.tag_ids)
                tag_reached = len(tag_checkpoints.filtered(lambda c: c.is_reached))
                if tag_reached < rule.min_count:
                    return False
            return True
        
        elif rule.condition_type == 'percentage':
            if total_checkpoints == 0:
                return False
            percentage = (reached_checkpoints / total_checkpoints) * 100
            return percentage >= rule.percentage
        
        return False

    def _apply_rule_advancement(self, rule):
        """Apply stage advancement based on rule"""
        if not rule.target_stage_id:
            return
        
        # Check if target stage is ahead of current stage
        current_stage = self.stage_id
        target_stage = rule.target_stage_id
        
        if current_stage.sequence < target_stage.sequence:
            self.stage_id = target_stage.id
    
    def _advance_stage_on_checkpoint(self, checkpoint):
        """Advance task stage when a checkpoint is reached"""
        if checkpoint.auto_advance_stage and checkpoint.target_stage_id:
            if self.stage_id != checkpoint.target_stage_id:
                self.stage_id = checkpoint.target_stage_id
                return True
        return False
    
    def write(self, vals):
        """Override write to handle checkpoint stage advancement"""
        result = super().write(vals)
        
        # Check if any checkpoints were marked as reached
        if 'checkpoint_ids' in vals:
            for checkpoint in self.checkpoint_ids:
                if checkpoint.is_reached and checkpoint.auto_advance_stage:
                    self._advance_stage_on_checkpoint(checkpoint)
        
        return result
