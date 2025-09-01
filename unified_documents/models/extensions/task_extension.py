# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    # Document integration fields (keep these)
    # Note: Template functionality has been moved to project_templates_basic module
    
    # Approval integration fields (optional - only if approvals module is available)
    approval_request_id = fields.Many2one(
        'approval.request', 
        string='Approval Request',
        help='Linked approval request for this task'
    )
    
    # Document processing fields
    document_processing_stage = fields.Selection([
        ('upload', 'Upload'),
        ('review', 'Review'),
        ('approval', 'Approval'),
        ('delivery', 'Delivery'),
        ('completed', 'Completed')
    ], string='Document Stage', default='upload', tracking=True)
    
    document_upload_date = fields.Datetime('Upload Date', tracking=True)
    document_review_date = fields.Datetime('Review Date', tracking=True)
    document_approval_date = fields.Datetime('Approval Date', tracking=True)
    document_delivery_date = fields.Datetime('Delivery Date', tracking=True)
    
    # Document checklist fields
    document_uploaded = fields.Boolean('Document Uploaded', default=False)
    document_reviewed = fields.Boolean('Document Reviewed', default=False)
    document_approved = fields.Boolean('Document Approved', default=False)
    document_delivered = fields.Boolean('Document Delivered', default=False)
    
    # Document reference field
    document_id = fields.Many2one(
        'documents.document', 
        string='Related Document',
        help='Document that this task is processing'
    )
    
    document_category = fields.Selection(
        related='document_id.category', 
        string='Document Category',
        store=True,
        help='Category of the related document'
    )
    
    # Checkpoint integration fields
    document_checkpoint_ids = fields.One2many(
        'project.task.checkpoint', 'task_id',
        string='Document Checkpoints',
        help='Checkpoints for document processing stages'
    )
    
    document_checkpoint_count = fields.Integer(
        compute='_compute_document_checkpoint_stats',
        string='Document Checkpoints Count'
    )
    
    document_checkpoint_reached_count = fields.Integer(
        compute='_compute_document_checkpoint_stats',
        string='Reached Document Checkpoints Count'
    )
    
    document_checkpoint_progress = fields.Float(
        compute='_compute_document_checkpoint_stats',
        string='Document Checkpoint Progress (%)',
        store=True  # Store the computed value
    )
    
    # Enhanced document processing workflow fields
    def action_complete_upload(self):
        """Complete upload stage and move to review"""
        self.ensure_one()
        self.write({
            'document_uploaded': True,
            'document_upload_date': fields.Datetime.now(),
            'document_processing_stage': 'review'
        })
        self._advance_checkpoint('upload')
        self._update_document_status('uploaded')
        self._send_stage_notification('upload')
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Upload Completed'),
                'message': _('Document upload stage completed. Moving to review stage.'),
                'type': 'success',
            }
        }
    
    def action_complete_review(self):
        """Complete review stage and move to approval"""
        self.ensure_one()
        self.write({
            'document_reviewed': True,
            'document_review_date': fields.Datetime.now(),
            'document_processing_stage': 'approval'
        })
        self._advance_checkpoint('review')
        self._update_document_status('reviewed')
        self._send_stage_notification('review')
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Review Completed'),
                'message': _('Document review stage completed. Moving to approval stage.'),
                'type': 'success',
            }
        }
    
    def action_complete_approval(self):
        """Complete approval stage and move to delivery"""
        self.ensure_one()
        self.write({
            'document_approved': True,
            'document_approval_date': fields.Datetime.now(),
            'document_processing_stage': 'delivery'
        })
        self._advance_checkpoint('approval')
        self._update_document_status('approved')
        self._send_stage_notification('approval')
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Approval Completed'),
                'message': _('Document approval stage completed. Moving to delivery stage.'),
                'type': 'success',
            }
        }
    
    def action_complete_delivery(self):
        """Complete delivery stage and finish task"""
        self.ensure_one()
        
        # Get completed stage
        completed_stage = self._get_completed_stage()
        
        self.write({
            'document_delivered': True,
            'document_delivery_date': fields.Datetime.now(),
            'document_processing_stage': 'completed',
            'stage_id': completed_stage.id if completed_stage else self.stage_id.id
        })
        self._advance_checkpoint('delivery')
        self._update_document_status('delivered')
        self._send_stage_notification('delivery')
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Delivery Completed'),
                'message': _('Document delivery stage completed. Task is now complete!'),
                'type': 'success',
            }
        }
    
    def _advance_checkpoint(self, stage):
        """Advance the checkpoint for the given stage"""
        self.ensure_one()
        
        if 'project.task.checkpoint' not in self.env:
            return
        
        # Find checkpoint that matches the stage
        checkpoint = self.document_checkpoint_ids.filtered(
            lambda c: stage.lower() in c.name.lower()
        )
        
        if checkpoint and not checkpoint.is_reached:
            try:
                # Manual checkpoint advancement
                checkpoint.write({
                    'is_reached': True
                })
                _logger.info(f"Advanced checkpoint '{checkpoint.name}' for task '{self.name}'")
                
                # Force recomputation by writing to trigger field updates
                self.write({'document_checkpoint_count': self.document_checkpoint_count})
                
            except Exception as e:
                _logger.warning(f"Failed to advance checkpoint '{checkpoint.name}': {e}")
    
    def _update_document_status(self, status):
        """Update the linked document status"""
        self.ensure_one()
        
        if not self.document_id:
            return
        
        status_mapping = {
            'uploaded': 'pending',
            'reviewed': 'in_progress', 
            'approved': 'verified',
            'delivered': 'delivered'
        }
        
        new_status = status_mapping.get(status)
        if new_status:
            try:
                self.document_id.write({'status': new_status})
                _logger.info(f"Updated document '{self.document_id.name}' status to '{new_status}'")
            except Exception as e:
                _logger.warning(f"Failed to update document status: {e}")
    
    def _send_stage_notification(self, stage):
        """Send notification when stage is completed"""
        self.ensure_one()
        
        if not self.document_id:
            return
        
        stage_messages = {
            'upload': f'Document "{self.document_id.name}" has been uploaded and is ready for review.',
            'review': f'Document "{self.document_id.name}" has been reviewed and is pending approval.',
            'approval': f'Document "{self.document_id.name}" has been approved and is ready for delivery.',
            'delivery': f'Document "{self.document_id.name}" has been delivered and the task is complete.',
        }
        
        message = stage_messages.get(stage)
        if not message:
            return
        
        try:
            # Create activity for project manager
            if self.project_id and self.project_id.user_id:
                self.env['mail.activity'].create({
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'note': message,
                    'res_id': self.project_id.id,
                    'res_model': 'project.project',
                    'user_id': self.project_id.user_id.id,
                    'summary': f'Document Processing Update - {stage.title()}',
                })
            
            # Send message to project chatter
            if self.project_id:
                self.project_id.message_post(
                    body=message,
                    subject=f'Document Processing: {stage.title()} Stage Completed',
                    message_type='notification'
                )
            
            _logger.info(f"Sent stage notification for '{stage}' stage completion")
            
        except Exception as e:
            _logger.warning(f"Failed to send stage notification: {e}")
    
    def _get_completed_stage(self):
        """Get the completed stage for the project"""
        self.ensure_one()
        
        try:
            # Look for a stage marked as 'done' or 'completed'
            completed_stage = self.env['project.task.type'].search([
                ('project_ids', 'in', [self.project_id.id]),
                '|',
                ('name', 'ilike', 'done'),
                ('name', 'ilike', 'completed')
            ], limit=1)
            
            if not completed_stage:
                # Look for the last stage in the project
                completed_stage = self.env['project.task.type'].search([
                    ('project_ids', 'in', [self.project_id.id])
                ], order='sequence desc', limit=1)
            
            return completed_stage
            
        except Exception as e:
            _logger.warning(f"Failed to get completed stage: {e}")
            return False
    
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
    
    def action_mark_document_uploaded(self):
        """Mark document as uploaded"""
        self.ensure_one()
        self.write({
            'document_uploaded': True,
            'document_upload_date': fields.Datetime.now(),
            'document_processing_stage': 'review'
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Document Uploaded'),
                'message': _('Document has been marked as uploaded. Moving to review stage.'),
                'type': 'success',
            }
        }
    
    def action_mark_document_reviewed(self):
        """Mark document as reviewed"""
        self.ensure_one()
        self.write({
            'document_reviewed': True,
            'document_review_date': fields.Datetime.now(),
            'document_processing_stage': 'approval'
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Document Reviewed'),
                'message': _('Document has been reviewed. Moving to approval stage.'),
                'type': 'success',
            }
        }
    
    def action_mark_document_approved(self):
        """Mark document as approved"""
        self.ensure_one()
        self.write({
            'document_approved': True,
            'document_approval_date': fields.Datetime.now(),
            'document_processing_stage': 'delivery'
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Document Approved'),
                'message': _('Document has been approved. Moving to delivery stage.'),
                'type': 'success',
            }
        }
    
    def action_mark_document_delivered(self):
        """Mark document as delivered"""
        self.ensure_one()
        self.write({
            'document_delivered': True,
            'document_delivery_date': fields.Datetime.now(),
            'document_processing_stage': 'completed'
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Document Delivered'),
                'message': _('Document has been delivered. Task completed!'),
                'type': 'success',
            }
        }
    
    def action_view_approval_request(self):
        """Open linked approval request"""
        self.ensure_one()
        
        # Check if approvals module is available
        if 'approval.request' not in self.env:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Approvals Module Not Available'),
                    'message': _('The approvals module is not installed or available.'),
                    'type': 'warning',
                }
            }
        
        if not self.approval_request_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Approval Request'),
                    'message': _('No approval request linked to this task.'),
                    'type': 'warning',
                }
            }
        
        return {
            'name': _('Approval Request: %s') % self.approval_request_id.name,
            'type': 'ir.actions.act_window',
            'res_model': 'approval.request',
            'res_id': self.approval_request_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    @api.depends('document_checkpoint_ids', 'document_checkpoint_ids.is_reached', 'document_checkpoint_ids.sequence')
    def _compute_document_checkpoint_stats(self):
        """Compute document checkpoint statistics"""
        for task in self:
            total_checkpoints = len(task.document_checkpoint_ids)
            reached_checkpoints = len(task.document_checkpoint_ids.filtered(lambda c: c.is_reached))
            
            # Add logging for debugging
            _logger.info(f"Computing stats for task '{task.name}': total={total_checkpoints}, reached={reached_checkpoints}")
            
            task.document_checkpoint_count = total_checkpoints
            task.document_checkpoint_reached_count = reached_checkpoints
            
            if total_checkpoints > 0:
                progress = (reached_checkpoints / total_checkpoints) * 100
                # Ensure progress is within valid range (0-100)
                progress = max(0.0, min(100.0, progress))
                task.document_checkpoint_progress = progress
                _logger.info(f"Task '{task.name}' progress: {progress:.2f}%")
            else:
                task.document_checkpoint_progress = 0.0
                _logger.info(f"Task '{task.name}' progress: 0% (no checkpoints)")
    
    @api.constrains('document_checkpoint_progress')
    def _check_progress_range(self):
        """Ensure progress is within valid range"""
        for task in self:
            if task.document_checkpoint_progress < 0 or task.document_checkpoint_progress > 100:
                raise ValidationError(_('Document checkpoint progress must be between 0% and 100%. Current value: %.2f%%') % task.document_checkpoint_progress)
    
    def action_create_document_checkpoints(self):
        """Create checkpoints for document processing stages"""
        self.ensure_one()
        
        # Check if checkpoints already exist
        if self.document_checkpoint_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Checkpoints Already Exist'),
                    'message': _('Document checkpoints have already been created for this task.'),
                    'type': 'info',
                }
            }
        
        # Define checkpoint stages
        checkpoint_stages = [
            {
                'name': 'Document Upload',
                'sequence': 10,
                'notes': 'Document has been uploaded to the system and verified for format and completeness.',
                'checklist_items': [
                    'Document file uploaded successfully',
                    'Document format verified (PDF, DOC, etc.)',
                    'Document size within acceptable limits',
                    'Document content is readable and complete'
                ]
            },
            {
                'name': 'Document Review',
                'sequence': 20,
                'notes': 'Document has been reviewed by the team for content accuracy and compliance.',
                'checklist_items': [
                    'Document content reviewed by team member',
                    'Technical accuracy verified',
                    'Compliance requirements checked',
                    'Stakeholder feedback incorporated'
                ]
            },
            {
                'name': 'Document Approval',
                'sequence': 30,
                'notes': 'Document has been approved by authorized personnel through the approval workflow.',
                'checklist_items': [
                    'Approval request submitted',
                    'Approval workflow completed',
                    'All approvers have signed off',
                    'Approval documentation recorded'
                ]
            },
            {
                'name': 'Document Delivery',
                'sequence': 40,
                'notes': 'Document has been delivered to the client or stakeholder and receipt confirmed.',
                'checklist_items': [
                    'Final document version prepared',
                    'Document sent to client/stakeholder',
                    'Delivery receipt confirmed',
                    'Document archived for future reference'
                ]
            }
        ]
        
        created_checkpoints = []
        
        for stage in checkpoint_stages:
            # Create checkpoint
            checkpoint = self.env['project.task.checkpoint'].create({
                'name': stage['name'],
                'sequence': stage['sequence'],
                'task_id': self.id,
                'notes': stage['notes'],
                'auto_advance_stage': True,
            })
            created_checkpoints.append(checkpoint)
            
            # Create checklist items for this checkpoint
            for i, item_text in enumerate(stage['checklist_items']):
                self.env['project.checkpoint.checklist.item'].create({
                    'name': item_text,
                    'checkpoint_id': checkpoint.id,
                    'sequence': i + 1,
                })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Document Checkpoints Created'),
                'message': _('Successfully created %d document checkpoints with checklist items.') % len(created_checkpoints),
                'type': 'success',
            }
        }
    
    def action_view_document_checkpoints(self):
        """Open document checkpoints view"""
        self.ensure_one()
        return {
            'name': _('Document Checkpoints - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'project.task.checkpoint',
            'view_mode': 'list,form',
            'domain': [('task_id', '=', self.id)],
            'context': {
                'default_task_id': self.id,
                'default_name': f'Document Checkpoint - {self.name}',
            },
        }
    
    def action_create_approval_request(self):
        """Create approval request for this task"""
        self.ensure_one()
        
        # Check if approvals module is available
        if 'approval.request' not in self.env:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Approvals Module Not Available'),
                    'message': _('The approvals module is not installed or available.'),
                    'type': 'warning',
                }
            }
        
        if self.approval_request_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Approval Request Exists'),
                    'message': _('This task already has an approval request.'),
                    'type': 'warning',
                }
            }
        
        try:
            # Get document approval category
            category = self.env['approval.category'].search([
                ('name', 'ilike', 'document')
            ], limit=1)
            
            if not category:
                category = self.env['approval.category'].create({
                    'name': 'Document Approval',
                    'description': 'Document review and approval workflow',
                    'approval_minimum': 1,
                    'has_product': False,
                    'has_reference': True,
                    'has_date': True,
                    'has_period': False,
                    'has_quantity': False,
                    'has_amount': False,
                    'has_tax': False,
                    'has_partner': False,
                    'has_payment_method': False,
                    'has_location': False,
                    'has_delivery_address': False,
                })
            
            approval_request = self.env['approval.request'].create({
                'name': f'Task Approval - {self.name}',
                'category_id': category.id,
                'request_owner_id': self.user_ids[0].id if self.user_ids else self.env.user.id,
                'request_status': 'pending',
                'date_start': fields.Date.today(),
                'date_end': fields.Date.today() + relativedelta(days=7),
                'reference': f'Task: {self.name} | Project: {self.project_id.name}',
            })
            
            self.write({
                'approval_request_id': approval_request.id
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Approval Request Created'),
                    'message': _('Approval request has been created and linked to this task.'),
                    'type': 'success',
                }
            }
        except Exception as e:
            _logger.error(f"Error creating approval request: {e}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('Could not create approval request. Please check if the approvals module is properly configured.'),
                                    'type': 'danger',
            }
        }
    
    def action_refresh_checkpoint_stats(self):
        """Manually refresh checkpoint statistics - useful for debugging"""
        self.ensure_one()
        # Force recomputation by writing to trigger field updates
        self.write({'document_checkpoint_count': self.document_checkpoint_count})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Statistics Refreshed'),
                'message': _('Checkpoint statistics have been refreshed.'),
                'type': 'success',
            }
        }
    
    def action_force_refresh_all_stats(self):
        """Force refresh all computed fields for this task"""
        self.ensure_one()
        
        # Force recomputation by writing to trigger field updates
        self.write({
            'document_checkpoint_count': self.document_checkpoint_count,
            'document_checkpoint_reached_count': self.document_checkpoint_reached_count,
            'document_checkpoint_progress': self.document_checkpoint_progress
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('All Statistics Refreshed'),
                'message': _('All computed fields have been refreshed for this task.'),
                'type': 'success',
            }
        }
    
    def action_debug_checkpoint_stats(self):
        """Debug method to show current checkpoint statistics"""
        self.ensure_one()
        
        checkpoints = self.document_checkpoint_ids
        total = len(checkpoints)
        reached = len(checkpoints.filtered(lambda c: c.is_reached))
        progress = (reached / total * 100) if total > 0 else 0
        
        debug_info = f"""
        Task: {self.name}
        Total Checkpoints: {total}
        Reached Checkpoints: {reached}
        Progress: {progress:.1f}%
        
        Checkpoint Details:
        """
        
        for cp in checkpoints:
            debug_info += f"\n- {cp.name}: {'✓' if cp.is_reached else '✗'}"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Checkpoint Debug Info'),
                'message': debug_info,
                'type': 'info',
            }
        }
    
    def action_fix_checkpoint_data(self):
        """Fix any data inconsistencies in checkpoint data"""
        self.ensure_one()
        
        fixed_issues = []
        
        # Check for invalid progress values
        if self.document_checkpoint_progress > 100:
            old_value = self.document_checkpoint_progress
            # Force recomputation by writing to trigger field updates
            self.write({'document_checkpoint_count': self.document_checkpoint_count})
            fixed_issues.append(f"Fixed invalid progress: {old_value}% → {self.document_checkpoint_progress:.2f}%")
        
        # Check for checkpoint count mismatches
        actual_count = len(self.document_checkpoint_ids)
        if self.document_checkpoint_count != actual_count:
            old_count = self.document_checkpoint_count
            # Force recomputation by writing to trigger field updates
            self.write({'document_checkpoint_reached_count': self.document_checkpoint_reached_count})
            fixed_issues.append(f"Fixed count mismatch: {old_count} → {actual_count}")
        
        # Check for reached count mismatches
        actual_reached = len(self.document_checkpoint_ids.filtered(lambda c: c.is_reached))
        if self.document_checkpoint_reached_count != actual_reached:
            old_reached = self.document_checkpoint_reached_count
            # Force recomputation by writing to trigger field updates
            self.write({'document_checkpoint_progress': self.document_checkpoint_progress})
            fixed_issues.append(f"Fixed reached count: {old_reached} → {actual_reached}")
        
        if fixed_issues:
            message = "Fixed data inconsistencies:\n" + "\n".join(f"• {issue}" for issue in fixed_issues)
        else:
            message = "No data inconsistencies found. All checkpoint data is correct."
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Data Consistency Check'),
                'message': message,
                'type': 'success' if fixed_issues else 'info',
            }
        }
    
    def action_fix_all_invalid_progress(self):
        """Fix all tasks with invalid progress values in the database"""
        invalid_tasks = self.search([
            '|',
            ('document_checkpoint_progress', '<', 0),
            ('document_checkpoint_progress', '>', 100)
        ])
        
        if not invalid_tasks:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Invalid Data Found'),
                    'message': _('All tasks have valid progress values.'),
                    'type': 'info',
                }
            }
        
        fixed_count = 0
        for task in invalid_tasks:
            try:
                # Force recomputation by writing to trigger field updates
                task.write({'document_checkpoint_count': task.document_checkpoint_count})
                fixed_count += 1
                _logger.info(f"Fixed invalid progress for task '{task.name}'")
            except Exception as e:
                _logger.error(f"Failed to fix task '{task.name}': {e}")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk Fix Complete'),
                'message': _('Fixed %d tasks with invalid progress values.') % fixed_count,
                'type': 'success',
            }
        }
