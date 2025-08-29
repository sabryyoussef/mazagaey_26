# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class WorkflowTemplateWizardExtension(models.TransientModel):
    _inherit = 'workflow.template.wizard'

    # FSM integration fields
    fsm_wizard_id = fields.Many2one(
        'fsm.workflow.create.wizard',
        string='FSM Wizard',
        help='Reference to the FSM wizard that called this workflow template wizard'
    )
    is_fsm_template = fields.Boolean(
        string='Is FSM Template',
        help='Flag to indicate this template is being created from FSM workflow'
    )

    def action_create_workflow(self):
        """Override to handle FSM callback after workflow creation"""
        # Call the original method
        result = super().action_create_workflow()
        
        # If this was called from FSM wizard, handle the callback
        if self.fsm_wizard_id and self.is_fsm_template:
            try:
                # Find the created workflow template
                # The workflow template should be the last one created
                workflow_template = self.env['workflow.template'].search([], order='id desc', limit=1)
                
                if workflow_template:
                    # Call the FSM wizard callback
                    callback_result = self.fsm_wizard_id.action_template_created_callback(workflow_template.id)
                    
                    # Return the callback result instead of the default notification
                    return callback_result
                else:
                    _logger.warning("Could not find created workflow template for FSM callback")
                    
            except Exception as e:
                _logger.error(f"Error in FSM workflow template callback: {e}")
                # Fall back to default behavior
                pass
        
        # Return the original result if no FSM callback or if callback failed
        return result

    @api.model
    def create(self, vals):
        """Override create to handle FSM context"""
        # Get FSM context from the environment context
        context = self.env.context
        if context.get('fsm_wizard_id'):
            vals['fsm_wizard_id'] = context.get('fsm_wizard_id')
        if context.get('is_fsm_template'):
            vals['is_fsm_template'] = context.get('is_fsm_template')
            
        return super().create(vals)
