# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class ProjectMilestone(models.Model):
    _inherit = 'project.milestone'

    checkpoint_ids = fields.One2many(
        'project.task.checkpoint',
        'milestone_id',
        string='Checkpoints',
        help='Checkpoints for this milestone'
    )
    
    # Computed fields for checkpoint statistics
    checkpoint_count = fields.Integer(
        string='Total Checkpoints',
        compute='_compute_checkpoint_counts',
        store=False,
        help='Total number of checkpoints for this milestone'
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
    create_quotation_on_reach = fields.Boolean(
        string='Create Quotation on Reach',
        default=False,
        help='Automatically create a quotation when this milestone is reached'
    )
    
    quotation_template_id = fields.Many2one(
        'sale.order.template',
        string='Quotation Template',
        help='Template to use when creating quotation from this milestone',
        ondelete='set null',
        required=False
    )
    
    quotation_notes = fields.Text(
        string='Quotation Notes',
        help='Additional notes to include in the quotation'
    )
    
    @api.depends('checkpoint_ids', 'checkpoint_ids.is_reached')
    def _compute_checkpoint_counts(self):
        """Compute checkpoint counts and progress"""
        for milestone in self:
            total_checkpoints = len(milestone.checkpoint_ids)
            completed_checkpoints = len(milestone.checkpoint_ids.filtered(lambda c: c.is_reached))
            
            milestone.checkpoint_count = total_checkpoints
            milestone.completed_checkpoint_count = completed_checkpoints
            
            if total_checkpoints > 0:
                milestone.checkpoint_progress = (completed_checkpoints / total_checkpoints) * 100
            else:
                milestone.checkpoint_progress = 0.0
    
    def _advance_milestone_on_checkpoint(self, checkpoint):
        """Mark milestone as reached when all checkpoints are reached"""
        if all(self.checkpoint_ids.mapped('is_reached')):
            if not self.is_reached:
                self.is_reached = True
                # Create quotation if configured
                if self.create_quotation_on_reach:
                    self._create_quotation_on_reach()
                return True
        else:
            # If not all checkpoints are reached, milestone should not be reached
            if self.is_reached:
                self.is_reached = False
                return True
        return False
    
    def write(self, vals):
        """Override write to handle checkpoint milestone advancement"""
        result = super().write(vals)
        
        # Check if any checkpoints were marked as reached
        if 'checkpoint_ids' in vals:
            for milestone in self:
                for checkpoint in milestone.checkpoint_ids:
                    if checkpoint.is_reached:
                        milestone._advance_milestone_on_checkpoint(checkpoint)
        
        return result
    
    def _create_quotation_on_reach(self):
        """Create quotation when milestone is reached"""
        self.ensure_one()
        
        # Find the workflow instance through the project
        workflow_instance = None
        if self.project_id:
            workflow_instance = self.env['fsm.workflow.instance'].search([
                ('project_id', '=', self.project_id.id)
            ], limit=1)
        
        if not workflow_instance:
            _logger.warning(f"No workflow instance found for milestone {self.name}")
            return False
        
        # Create quotation with milestone context
        context = {
            'default_workflow_instance_id': workflow_instance.id,
            'milestone_trigger': True,
            'milestone_name': self.name,
        }
        
        # Create the quotation
        sale_order = workflow_instance.with_context(context).create_milestone_quotation(
            milestone_name=self.name
        )
        
        if sale_order:
            # Add quotation notes if provided
            if self.quotation_notes:
                sale_order.message_post(
                    body=f"📝 **Milestone Notes**: {self.quotation_notes}",
                    subject=f"Milestone Notes - {self.name}"
                )
            
            # Apply template if specified
            if self.quotation_template_id and 'sale.order.template' in self.env:
                try:
                    # Use the correct method for applying sale order templates
                    if hasattr(self.quotation_template_id, '_generate_quotation_lines'):
                        self.quotation_template_id._generate_quotation_lines(sale_order)
                    else:
                        # Fallback: manually add template lines
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
                    # Final fallback: create basic line
                    try:
                        self.env['sale.order.line'].create({
                            'order_id': sale_order.id,
                            'name': f'Milestone: {self.name}',
                            'product_uom_qty': 1.0,
                            'price_unit': 1000.0,
                        })
                    except Exception as fallback_error:
                        _logger.error(f"Error in final fallback template application: {fallback_error}")
            
            _logger.info(f"Quotation created for milestone {self.name}: {sale_order.name}")
            return sale_order
        
        return False
    
    def apply_milestone_template(self, template):
        """Apply milestone template to create milestone with checkpoints"""
        self.ensure_one()
        
        # Create milestone
        milestone_vals = {
            'name': template.milestone_name,
            'project_id': self.project_id.id,
            'deadline': template.milestone_deadline,
        }
        milestone = self.env['project.milestone'].create(milestone_vals)
        
        # Create checkpoints
        for line in template.checkpoint_line_ids:
            checkpoint_vals = {
                'name': line.name,
                'sequence': line.sequence,
                'milestone_id': milestone.id,
                'tag_ids': [(6, 0, line.tag_ids.ids)],
                'auto_advance_stage': line.auto_advance_stage,
                'target_stage_id': line.target_stage_id.id if line.target_stage_id else False,
                'notes': line.notes,
            }
            self.env['project.task.checkpoint'].create(checkpoint_vals)
        
        return milestone
    
    def apply_milestone_template_from_project(self, template):
        """Apply milestone template from project context"""
        if not self.project_id:
            raise ValidationError(_("No project associated with this milestone"))
        
        return self.apply_milestone_template(template)
