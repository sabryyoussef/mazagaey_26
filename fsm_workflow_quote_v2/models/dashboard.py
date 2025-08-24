# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import safe_eval
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """Post-install hook to create dashboard view"""
    try:
        # Create the dashboard view
        cr.execute("""
            DROP VIEW IF EXISTS fsm_workflow_dashboard
        """)
        
        cr.execute("""
            CREATE OR REPLACE VIEW fsm_workflow_dashboard AS (
                SELECT 
                    row_number() OVER () as id,
                    COUNT(*) as total_workflows,
                    COUNT(CASE WHEN state = 'in_progress' THEN 1 END) as active_workflows,
                    COUNT(CASE WHEN state = 'completed' THEN 1 END) as completed_workflows,
                    COALESCE(SUM(quotation_amount), 0) as total_revenue,
                    AVG(EXTRACT(EPOCH FROM (write_date - create_date))/86400) as avg_completion_time,
                    COUNT(DISTINCT partner_id) as customer_count,
                    COUNT(CASE WHEN sale_order_id IS NOT NULL THEN 1 END) as total_quotations,
                    COUNT(CASE WHEN quotation_state = 'sent' THEN 1 END) as sent_quotations,
                    COUNT(CASE WHEN quotation_state = 'sale' THEN 1 END) as confirmed_quotations,
                    COALESCE(SUM(estimated_hours), 0) as total_hours,
                    AVG(estimated_hours) as avg_hours_per_workflow,
                    (SELECT currency_id FROM res_company WHERE id = 1) as currency_id,
                    '' as top_customers,
                    0 as total_checkpoints,
                    0 as completed_checkpoints,
                    0.0 as checkpoint_completion_rate
                FROM fsm_workflow_instance
                WHERE active = true
            )
        """)
    except Exception as e:
        _logger.error(f"Error creating dashboard view: {e}")


class FSMWorkflowDashboard(models.Model):
    """Dashboard model for FSM Workflow statistics and analytics"""
    _name = 'fsm.workflow.dashboard'
    _description = 'FSM Workflow Dashboard'
    _auto = False
    _table = 'fsm_workflow_dashboard'

    # Dashboard fields
    total_workflows = fields.Integer(string='Total Workflows', readonly=True)
    active_workflows = fields.Integer(string='Active Workflows', readonly=True)
    completed_workflows = fields.Integer(string='Completed Workflows', readonly=True)
    total_revenue = fields.Monetary(string='Total Revenue', currency_field='currency_id', readonly=True)
    avg_completion_time = fields.Float(string='Avg Completion Time (Days)', readonly=True)
    total_checkpoints = fields.Integer(string='Total Checkpoints', readonly=True)
    completed_checkpoints = fields.Integer(string='Completed Checkpoints', readonly=True)
    checkpoint_completion_rate = fields.Float(string='Checkpoint Completion Rate (%)', readonly=True)
    
    # Customer analytics
    top_customers = fields.Text(string='Top Customers', readonly=True)
    customer_count = fields.Integer(string='Total Customers', readonly=True)
    
    # Quotation analytics
    total_quotations = fields.Integer(string='Total Quotations', readonly=True)
    sent_quotations = fields.Integer(string='Sent Quotations', readonly=True)
    confirmed_quotations = fields.Integer(string='Confirmed Quotations', readonly=True)
    quotation_conversion_rate = fields.Float(string='Quotation Conversion Rate (%)', readonly=True)
    
    # Time tracking
    total_hours = fields.Float(string='Total Hours', readonly=True)
    avg_hours_per_workflow = fields.Float(string='Avg Hours per Workflow', readonly=True)
    
    # Currency
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)

    def create(self, vals):
        """Prevent creation of dashboard records"""
        raise UserError(_("Cannot create dashboard records manually. This is a read-only view."))

    def write(self, vals):
        """Prevent writing to dashboard records"""
        raise UserError(_("Cannot modify dashboard records. This is a read-only view."))

    def unlink(self):
        """Prevent deletion of dashboard records"""
        raise UserError(_("Cannot delete dashboard records. This is a read-only view."))

    def init(self):
        """Initialize the dashboard view"""
        # Drop existing view if it exists
        self.env.cr.execute("""
            DROP VIEW IF EXISTS fsm_workflow_dashboard
        """)
        
        # Create the dashboard view
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW fsm_workflow_dashboard AS (
                SELECT 
                    row_number() OVER () as id,
                    COUNT(*) as total_workflows,
                    COUNT(CASE WHEN state = 'in_progress' THEN 1 END) as active_workflows,
                    COUNT(CASE WHEN state = 'completed' THEN 1 END) as completed_workflows,
                    COALESCE(SUM(quotation_amount), 0) as total_revenue,
                    AVG(EXTRACT(EPOCH FROM (write_date - create_date))/86400) as avg_completion_time,
                    COUNT(DISTINCT partner_id) as customer_count,
                    COUNT(CASE WHEN sale_order_id IS NOT NULL THEN 1 END) as total_quotations,
                    COUNT(CASE WHEN quotation_state = 'sent' THEN 1 END) as sent_quotations,
                    COUNT(CASE WHEN quotation_state = 'sale' THEN 1 END) as confirmed_quotations,
                    COALESCE(SUM(estimated_hours), 0) as total_hours,
                    AVG(estimated_hours) as avg_hours_per_workflow,
                    (SELECT currency_id FROM res_company WHERE id = 1) as currency_id,
                    '' as top_customers,
                    0 as total_checkpoints,
                    0 as completed_checkpoints,
                    0.0 as checkpoint_completion_rate
                FROM fsm_workflow_instance
                WHERE active = true
                
                UNION ALL
                
                SELECT 
                    999999 as id,
                    0 as total_workflows,
                    0 as active_workflows,
                    0 as completed_workflows,
                    0 as total_revenue,
                    0 as avg_completion_time,
                    0 as customer_count,
                    0 as total_quotations,
                    0 as sent_quotations,
                    0 as confirmed_quotations,
                    0 as total_hours,
                    0 as avg_hours_per_workflow,
                    (SELECT currency_id FROM res_company WHERE id = 1) as currency_id,
                    '' as top_customers,
                    0 as total_checkpoints,
                    0 as completed_checkpoints,
                    0.0 as checkpoint_completion_rate
                WHERE NOT EXISTS (
                    SELECT 1 FROM fsm_workflow_instance WHERE active = true
                )
            )
        """)

    @api.model
    def get_dashboard_data(self):
        """Get dashboard data for display"""
        try:
            # Get basic statistics
            dashboard = self.search([])
            if not dashboard:
                return self._get_empty_dashboard()
            
            data = dashboard[0]
            
            # Get checkpoint statistics
            checkpoint_stats = self._get_checkpoint_stats()
            
            # Get top customers
            top_customers = self._get_top_customers()
            
            # Calculate rates
            quotation_rate = (data.confirmed_quotations / data.total_quotations * 100) if data.total_quotations > 0 else 0
            checkpoint_rate = checkpoint_stats['completion_rate']
            
            return {
                'total_workflows': data.total_workflows,
                'active_workflows': data.active_workflows,
                'completed_workflows': data.completed_workflows,
                'total_revenue': data.total_revenue,
                'avg_completion_time': round(data.avg_completion_time or 0, 1),
                'customer_count': data.customer_count,
                'total_quotations': data.total_quotations,
                'sent_quotations': data.sent_quotations,
                'confirmed_quotations': data.confirmed_quotations,
                'quotation_conversion_rate': round(quotation_rate, 1),
                'total_hours': data.total_hours,
                'avg_hours_per_workflow': round(data.avg_hours_per_workflow or 0, 1),
                'checkpoint_stats': checkpoint_stats,
                'top_customers': top_customers,
                'currency_symbol': data.currency_id.symbol if data.currency_id else '$',
            }
        except Exception as e:
            _logger.error(f"Error getting dashboard data: {e}")
            return self._get_empty_dashboard()

    def _get_checkpoint_stats(self):
        """Get checkpoint statistics"""
        try:
            if 'project.task.checkpoint' not in self.env:
                return {'total': 0, 'completed': 0, 'completion_rate': 0}
            
            checkpoints = self.env['project.task.checkpoint'].search([])
            total = len(checkpoints)
            completed = len(checkpoints.filtered(lambda c: c.is_reached))
            rate = (completed / total * 100) if total > 0 else 0
            
            return {
                'total': total,
                'completed': completed,
                'completion_rate': round(rate, 1)
            }
        except Exception as e:
            _logger.error(f"Error getting checkpoint stats: {e}")
            return {'total': 0, 'completed': 0, 'completion_rate': 0}

    def _get_top_customers(self):
        """Get top customers by workflow count"""
        try:
            workflows = self.env['fsm.workflow.instance'].search([])
            customer_counts = {}
            
            for workflow in workflows:
                if workflow.partner_id:
                    customer_name = workflow.partner_id.name
                    customer_counts[customer_name] = customer_counts.get(customer_name, 0) + 1
            
            # Sort by count and get top 5
            top_customers = sorted(customer_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return [{'name': name, 'count': count} for name, count in top_customers]
        except Exception as e:
            _logger.error(f"Error getting top customers: {e}")
            return []

    def _get_empty_dashboard(self):
        """Return empty dashboard data"""
        return {
            'total_workflows': 0,
            'active_workflows': 0,
            'completed_workflows': 0,
            'total_revenue': 0,
            'avg_completion_time': 0,
            'customer_count': 0,
            'total_quotations': 0,
            'sent_quotations': 0,
            'confirmed_quotations': 0,
            'quotation_conversion_rate': 0,
            'total_hours': 0,
            'avg_hours_per_workflow': 0,
            'checkpoint_stats': {'total': 0, 'completed': 0, 'completion_rate': 0},
            'top_customers': [],
            'currency_symbol': '$',
        }

    def action_refresh_dashboard(self):
        """Refresh dashboard data"""
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_view_workflows(self):
        """Open workflows list view"""
        return {
            'name': _('FSM Workflows'),
            'type': 'ir.actions.act_window',
            'res_model': 'fsm.workflow.instance',
            'view_mode': 'list,form',
            'domain': [],
            'context': {},
        }

    def action_view_quotations(self):
        """Open quotations list view"""
        return {
            'name': _('Quotations'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('fsm_workflow_instance_ids', '!=', False)],
            'context': {},
        }
