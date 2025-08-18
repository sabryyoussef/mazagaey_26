# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    checkpoint_template_ids = fields.Many2many(
        'project.task.checkpoint.template',
        string='Checkpoint Templates',
        help='Checkpoint templates to apply when creating tasks from this product'
    )

    auto_apply_checkpoint_templates = fields.Boolean(
        string='Auto Apply Checkpoint Templates',
        default=True,
        help='Automatically apply checkpoint templates when creating tasks'
    )

    @api.constrains('type', 'service_tracking')
    def _check_checkpoint_template_constraints(self):
        """Ensure checkpoint templates are only for service products that generate tasks"""
        for product in self:
            if product.checkpoint_template_ids and product.type != 'service':
                raise ValidationError(_('Checkpoint templates can only be applied to service products'))
            if product.checkpoint_template_ids and product.service_tracking not in ['task_in_project', 'project_only']:
                raise ValidationError(_('Checkpoint templates can only be applied to products that generate tasks or projects'))
