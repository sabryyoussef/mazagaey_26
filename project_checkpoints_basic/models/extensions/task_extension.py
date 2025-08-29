# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    checkpoint_ids = fields.One2many(
        'project.task.checkpoint',
        'task_id',
        string='Checkpoints',
        help='Checkpoints for this task'
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
    
    # Quotation Integration
    create_quotation_on_completion = fields.Boolean(
        string='Create Quotation on Completion',
        default=False,
        help='Automatically create a quotation when this task is completed'
    )
    quotation_template_id = fields.Many2one(
        'sale.order.template',
        string='Quotation Template',
        help='Template to use when creating quotation from this task',
        ondelete='set null',
        required=False
    )
    quotation_notes = fields.Text(
        string='Quotation Notes',
        help='Additional notes to include in the quotation'
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

    def _evaluate_checkpoint_rules(self):
        """Evaluate checkpoint rules and advance stages if conditions are met"""
        # This method is called when checkpoints change to evaluate any template rules
        # For now, we'll implement basic functionality and can be extended later
        
        # Check if all checkpoints are reached and advance to final stage if configured
        total_checkpoints = len(self.checkpoint_ids)
        reached_checkpoints = len(self.checkpoint_ids.filtered(lambda c: c.is_reached))
        
        if total_checkpoints > 0 and reached_checkpoints == total_checkpoints:
            # All checkpoints reached - check if there's a completion stage to advance to
            project_stages = self.project_id.type_ids
            if project_stages:
                # Find a completion/done stage (usually the last one)
                completion_stages = project_stages.filtered(lambda s: s.name.lower() in ['done', 'completed', 'finished'])
                if completion_stages:
                    # Only advance if current stage is before completion stage
                    completion_stage = completion_stages[0]
                    if self.stage_id.sequence < completion_stage.sequence:
                        self.stage_id = completion_stage.id
        
        return True
    
    def write(self, vals):
        """Override write to handle checkpoint stage advancement and quotation creation"""
        result = super().write(vals)
        
        # Check if any checkpoints were marked as reached
        if 'checkpoint_ids' in vals:
            for checkpoint in self.checkpoint_ids:
                if checkpoint.is_reached and checkpoint.auto_advance_stage:
                    self._advance_stage_on_checkpoint(checkpoint)
        
        # Check if task was completed and quotation should be created
        if 'stage_id' in vals:
            self._check_task_completion_quotation()
        
        return result
    
    def _check_task_completion_quotation(self):
        """Check if task completion should trigger quotation creation"""
        self.ensure_one()
        
        # Check if task is in a completion stage
        completion_stages = ['done', 'completed', 'finished', 'closed']
        if self.stage_id.name.lower() in completion_stages:
            if self.create_quotation_on_completion:
                self._create_quotation_on_completion()
    
    def _create_quotation_on_completion(self):
        """Create quotation when task is completed"""
        self.ensure_one()
        
        # Find the workflow instance for this task's project
        workflow_instance = None
        if self.project_id and 'fsm.workflow.instance' in self.env:
            workflow_instance = self.env['fsm.workflow.instance'].search([
                ('project_id', '=', self.project_id.id)
            ], limit=1)
        
        if not workflow_instance:
            _logger.warning(f"No workflow instance found for task {self.name} - FSM workflow module may not be installed")
            return False
        
        # Create context for quotation creation
        context = {
            'default_workflow_instance_id': workflow_instance.id,
            'task_trigger': True,
            'task_name': self.name,
        }
        
        # Create quotation using workflow instance method
        sale_order = workflow_instance.with_context(context).create_milestone_quotation(
            milestone_name=None,
            checkpoint_name=None
        )
        
        if sale_order:
            # Update quotation name to reflect task completion
            sale_order.name = f'Task Quotation - {self.name} - {workflow_instance.name}'
            
            # Add task notes if available
            if self.quotation_notes:
                sale_order.message_post(
                    body=f"📝 **Task Notes**: {self.quotation_notes}",
                    subject=f"Task Notes - {self.name}"
                )
            
            # Apply quotation template if available
            if self.quotation_template_id and 'sale.order.template' in self.env:
                try:
                    if hasattr(self.quotation_template_id, '_generate_quotation_lines'):
                        self.quotation_template_id._generate_quotation_lines(sale_order)
                    else:
                        for line in self.quotation_template_id.sale_order_template_line_ids:
                            self.env['sale.order.line'].create({
                                'order_id': sale_order.id,
                                'name': line.name,
                                'product_id': line.product_id.id if line.product_id else False,
                                'product_uom_qty': line.product_uom_qty,
                                'price_unit': line.price_unit,
                            })
                except Exception as e:
                    _logger.error(f"Error applying quotation template: {e}")
                    # Fallback: create a basic line
                    try:
                        self.env['sale.order.line'].create({
                            'order_id': sale_order.id,
                            'name': f'Task: {self.name}',
                            'product_uom_qty': 1.0,
                            'price_unit': 500.0,
                        })
                    except Exception as fallback_error:
                        _logger.error(f"Error in fallback template application: {fallback_error}")
            
            _logger.info(f"Quotation created for task {self.name}: {sale_order.name}")
            return sale_order
        
        return False
