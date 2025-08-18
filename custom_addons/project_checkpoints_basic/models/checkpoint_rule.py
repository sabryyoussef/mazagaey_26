# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectTaskCheckpointRule(models.Model):
    _name = 'project.task.checkpoint.rule'
    _description = 'Task Checkpoint Rule'
    _order = 'sequence, id'

    name = fields.Char(
        string='Rule Name',
        required=True,
        help='Name of the rule'
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Priority order of the rule'
    )
    
    template_id = fields.Many2one(
        'project.task.checkpoint.template',
        string='Template',
        required=True,
        ondelete='cascade'
    )
    
    condition_type = fields.Selection([
        ('all', 'All Checkpoints Reached'),
        ('min_count', 'Minimum Count'),
        ('by_tag_count', 'By Tag Count'),
        ('percentage', 'Percentage')
    ], string='Condition Type', required=True, default='all')
    
    min_count = fields.Integer(
        string='Minimum Count',
        help='Minimum number of checkpoints that must be reached'
    )
    
    percentage = fields.Float(
        string='Percentage',
        help='Percentage of checkpoints that must be reached (0-100)'
    )
    
    tag_ids = fields.Many2many(
        'project.task.checkpoint.tag',
        'checkpoint_rule_tag_rel',
        'rule_id',
        'tag_id',
        string='Tags',
        help='Tags to count when condition_type is by_tag_count'
    )
    
    target_stage_id = fields.Many2one(
        'project.task.type',
        string='Target Stage',
        required=False,
        help='Target stage to advance to when rule condition is met'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Whether this rule is active'
    )
    
    @api.constrains('condition_type', 'min_count', 'percentage', 'tag_ids')
    def _check_rule_conditions(self):
        """Validate rule conditions based on condition type"""
        for rule in self:
            if rule.condition_type == 'min_count' and not rule.min_count:
                raise ValidationError(_('Minimum count is required for min_count condition type'))
            elif rule.condition_type == 'percentage' and not rule.percentage:
                raise ValidationError(_('Percentage is required for percentage condition type'))
            elif rule.condition_type == 'by_tag_count' and not rule.tag_ids:
                raise ValidationError(_('Tags are required for by_tag_count condition type'))
