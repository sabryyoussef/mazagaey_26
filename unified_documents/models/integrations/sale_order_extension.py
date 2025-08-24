# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_copy_documents_to_projects(self):
        """Copy documents from products to their respective projects"""
        self.ensure_one()
        
        copied_count = 0
        failed_count = 0
        
        for line in self.order_line:
            if line.product_id and line.product_id.document_ids and line.project_id:
                try:
                    if line.copy_documents_to_project():
                        copied_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    _logger.warning(f"Failed to copy documents for line {line.name}: {e}")
                    failed_count += 1
        
        # Show result notification
        if copied_count > 0:
            message = f"Successfully copied documents for {copied_count} order line(s)"
            if failed_count > 0:
                message += f". Failed for {failed_count} line(s)"
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Documents Copied'),
                    'message': message,
                    'type': 'success' if failed_count == 0 else 'warning',
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Documents Copied'),
                    'message': _('No documents were copied. Check if products have documents and projects are created.'),
                    'type': 'warning',
                }
            }
