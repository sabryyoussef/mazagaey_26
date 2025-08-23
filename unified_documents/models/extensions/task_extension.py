# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    # Document integration fields (keep these)
    # Note: Template functionality has been moved to project_templates_basic module
    
    def action_view_documents(self):
        """Open documents view for this task"""
        self.ensure_one()
        return {
            'name': _('Task Documents: %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'list,form',
            'domain': [('res_model', '=', 'project.task'), ('res_id', '=', self.id)],
            'context': {
                'default_res_model': 'project.task',
                'default_res_id': self.id,
            },
            'target': 'current',
        }
