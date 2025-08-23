from odoo import models, fields, api, _


class WorkflowAutomation(models.Model):
    _name = 'project.handover.auto'
    _description = 'Project Handover Workflow Automation'
    _order = 'sequence, name'

    name = fields.Char('Automation Name', required=True)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)
    
    # Trigger conditions
    trigger_type = fields.Selection([
        ('checkpoint_completion', 'Checkpoint Completion'),
        ('project_milestone', 'Project Milestone'),
        ('template_based', 'Template Based'),
    ], string='Trigger Type', required=True, default='checkpoint_completion')
    
    # Target configuration
    project_ids = fields.Many2many('project.project', string='Target Projects')
    checkpoint_type_selection = fields.Selection([
        ('task_template', 'Task Template'),
        ('document', 'Document'),
        ('compliance', 'Compliance'),
        ('partner', 'Partner'),
        ('milestone', 'Milestone'),
        ('custom', 'Custom'),
    ], string='Checkpoint Type Filter')
    template_id = fields.Many2one('project.project', string='Handover Template', domain=[('is_template', '=', True)])
    
    # Automation settings
    auto_create_handover = fields.Boolean('Auto Create Handover', default=True)
    auto_assign_template = fields.Boolean('Auto Assign Template', default=True)
    auto_copy_documents = fields.Boolean('Auto Copy Documents', default=True)
    
    # Document automation
    doc_auto_ids = fields.Many2many('unified.document.copy.automation', string='Document Automations')
    
    @api.model
    def trigger_handover_creation(self, trigger_type, record_id):
        """Trigger handover creation based on automation rules"""
        automations = self.search([
            ('active', '=', True),
            ('trigger_type', '=', trigger_type)
        ])
        
        for automation in automations:
            if trigger_type == 'checkpoint_completion':
                self._create_handover_from_checkpoint(record_id, automation)
            elif trigger_type == 'project_milestone':
                self._create_handover_from_milestone(record_id, automation)
            elif trigger_type == 'template_based':
                self._create_handover_from_template(record_id, automation)
    
    def _create_handover_from_checkpoint(self, checkpoint_id, automation):
        """Create handover from checkpoint completion"""
        checkpoint = self.env['project.task.checkpoint'].browse(checkpoint_id)
        
        # Check if automation applies to this checkpoint
        if not self._check_automation_applies(checkpoint, automation):
            return False
        
        # Create handover
        handover_vals = {
            'project_id': checkpoint.project_id.id,
            'template_id': automation.template_id.id if automation.auto_assign_template else False,
            'checkpoint_ids': [(4, checkpoint_id)],
            'automation_ids': [(6, 0, automation.doc_auto_ids.ids)] if automation.auto_copy_documents else False,
        }
        
        handover = self.env['project.handover.notes'].create(handover_vals)
        
        # Apply template if specified
        if automation.auto_assign_template and automation.template_id:
            handover.apply_handover_template()
        
        # Copy documents if enabled
        if automation.auto_copy_documents and automation.doc_auto_ids:
            handover.copy_documents_to_handover()
        
        return handover
    
    def _create_handover_from_milestone(self, milestone_id, automation):
        """Create handover from project milestone"""
        milestone = self.env['project.milestone'].browse(milestone_id)
        
        # Check if automation applies to this milestone
        if not self._check_automation_applies(milestone.project_id, automation):
            return False
        
        # Create handover
        handover_vals = {
            'project_id': milestone.project_id.id,
            'template_id': automation.template_id.id if automation.auto_assign_template else False,
            'automation_ids': [(6, 0, automation.doc_auto_ids.ids)] if automation.auto_copy_documents else False,
        }
        
        handover = self.env['project.handover.notes'].create(handover_vals)
        
        # Apply template if specified
        if automation.auto_assign_template and automation.template_id:
            handover.apply_handover_template()
        
        # Copy documents if enabled
        if automation.auto_copy_documents and automation.doc_auto_ids:
            handover.copy_documents_to_handover()
        
        return handover
    
    def _create_handover_from_template(self, project_id, automation):
        """Create handover from template"""
        project = self.env['project.project'].browse(project_id)
        
        # Check if automation applies to this project
        if not self._check_automation_applies(project, automation):
            return False
        
        # Create handover
        handover_vals = {
            'project_id': project.id,
            'template_id': automation.template_id.id if automation.auto_assign_template else False,
            'automation_ids': [(6, 0, automation.doc_auto_ids.ids)] if automation.auto_copy_documents else False,
        }
        
        handover = self.env['project.handover.notes'].create(handover_vals)
        
        # Apply template if specified
        if automation.auto_assign_template and automation.template_id:
            handover.apply_handover_template()
        
        # Copy documents if enabled
        if automation.auto_copy_documents and automation.doc_auto_ids:
            handover.copy_documents_to_handover()
        
        return handover
    
    def _check_automation_applies(self, record, automation):
        """Check if automation applies to the given record"""
        # Check project filter
        if automation.project_ids and record.project_id not in automation.project_ids:
            return False
        
        # Check checkpoint type filter
        if automation.checkpoint_type_selection and hasattr(record, 'checkpoint_type'):
            if record.checkpoint_type != automation.checkpoint_type_selection:
                return False
        
        return True


# Extend checkpoint model to trigger automation
class ProjectTaskCheckpoint(models.Model):
    _inherit = 'project.task.checkpoint'
    
    def action_mark_completed(self):
        """Override to trigger handover automation"""
        result = super().action_mark_completed()
        
        # Trigger handover automation if checkpoint requires handover
        if self.requires_handover:
            self.env['project.handover.auto'].trigger_handover_creation(
                'checkpoint_completion', self.id
            )
        
        return result


# Extend milestone model to trigger automation
class ProjectMilestone(models.Model):
    _inherit = 'project.milestone'
    
    def action_mark_completed(self):
        """Override to trigger handover automation"""
        result = super().action_mark_completed()
        
        # Trigger handover automation
        self.env['project.handover.auto'].trigger_handover_creation(
            'project_milestone', self.id
        )
        
        return result
