from odoo import api, fields, models, _


class SaleOrderExtension(models.Model):
    _inherit = 'sale.order'

    workflow_instance_id = fields.Many2one(
        'fsm.workflow.instance', 
        string='Workflow Instance', 
        copy=False,
        help='Link to the FSM Workflow Instance that created this quotation'
    )
    
    is_workflow_quotation = fields.Boolean(
        string='Is Workflow Quotation',
        compute='_compute_is_workflow_quotation',
        store=True,
        help='Indicates if this quotation was created from a workflow instance'
    )
    
    workflow_trigger_type = fields.Selection([
        ('manual', 'Manual'),
        ('milestone', 'Milestone Reached'),
        ('checkpoint', 'Checkpoint Reached'),
        ('task', 'Task Completed'),
        ('project', 'Project Completed'),
        ('automatic', 'Automatic'),
    ], string='Workflow Trigger', default='manual', copy=False,
       help='Type of trigger that created this quotation')
    
    workflow_trigger_name = fields.Char(
        string='Trigger Name',
        copy=False,
        help='Name of the milestone or checkpoint that triggered this quotation'
    )

    @api.depends('workflow_instance_id')
    def _compute_is_workflow_quotation(self):
        for order in self:
            order.is_workflow_quotation = bool(order.workflow_instance_id)

    def action_open_workflow_instance(self):
        """Open the related workflow instance"""
        self.ensure_one()
        if not self.workflow_instance_id:
            return {}
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fsm.workflow.instance',
            'res_id': self.workflow_instance_id.id,
            'view_mode': 'form',
        }

    @api.model
    def create(self, vals):
        """Override create to handle workflow instance context"""
        # Check if we're creating from a workflow instance context
        if self.env.context.get('default_workflow_instance_id'):
            vals['workflow_instance_id'] = self.env.context.get('default_workflow_instance_id')
            vals['is_workflow_quotation'] = True
            
            # Set trigger type based on context
            if self.env.context.get('milestone_trigger'):
                vals['workflow_trigger_type'] = 'milestone'
                vals['workflow_trigger_name'] = self.env.context.get('milestone_name')
            elif self.env.context.get('checkpoint_trigger'):
                vals['workflow_trigger_type'] = 'checkpoint'
                vals['workflow_trigger_name'] = self.env.context.get('checkpoint_name')
            elif self.env.context.get('task_trigger'):
                vals['workflow_trigger_type'] = 'task'
                vals['workflow_trigger_name'] = self.env.context.get('task_name')
            elif self.env.context.get('project_trigger'):
                vals['workflow_trigger_type'] = 'project'
                vals['workflow_trigger_name'] = self.env.context.get('project_name')
            else:
                vals['workflow_trigger_type'] = 'manual'
        
        return super().create(vals)
