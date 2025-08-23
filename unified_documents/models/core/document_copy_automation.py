from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)


class UnifiedDocumentCopyAutomation(models.Model):
    _name = 'unified.document.copy.automation'
    _description = 'Unified Document Copy Automation'
    _order = 'sequence, id'

    name = fields.Char('Automation Name', required=True)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)
    
    # Trigger configuration
    trigger_model = fields.Selection([
        ('project.project', 'Project'),
        ('sale.order', 'Sale Order'),
        ('purchase.order', 'Purchase Order'),
        ('product.template', 'Product'),
    ], string='Trigger Model', required=True)
    
    trigger_field = fields.Char('Trigger Field', 
                               help='Field that triggers the automation (e.g., state, stage_id)')
    trigger_value = fields.Char('Trigger Value', 
                               help='Value that triggers the automation (e.g., confirmed, done)')
    
    # Source configuration
    source_model = fields.Selection([
        ('product.template', 'Product'),
        ('project.project', 'Project'),
        ('sale.order', 'Sale Order'),
        ('purchase.order', 'Purchase Order'),
    ], string='Source Model', required=True)
    
    source_field = fields.Char('Source Field', 
                              help='Field to get source record (e.g., product_id, parent_id)')
    source_fallback = fields.Integer('Source Fallback ID', 
                                    help='Fallback source record ID if source field is empty')
    
    # Target configuration
    target_model = fields.Selection([
        ('project.project', 'Project'),
        ('product.template', 'Product'),
        ('sale.order', 'Sale Order'),
        ('purchase.order', 'Purchase Order'),
    ], string='Target Model', required=True)
    
    target_field = fields.Char('Target Field', 
                              help='Field to get target record (e.g., project_id, parent_id)')
    target_fallback = fields.Integer('Target Fallback ID', 
                                    help='Fallback target record ID if target field is empty')
    
    # Copy options
    copy_categories = fields.Selection([
        ('all', 'All Categories'),
        ('required', 'Required Only'),
        ('deliverable', 'Deliverable Only'),
        ('reference', 'Reference Only'),
        ('compliance', 'Compliance Only'),
    ], string='Copy Categories', default='all', required=True)
    
    copy_attachments = fields.Boolean('Copy Attachments', default=True)
    copy_tags = fields.Boolean('Copy Tags', default=True)
    copy_notes = fields.Boolean('Copy Notes', default=True)
    
    # Execution options
    execution_type = fields.Selection([
        ('on_write', 'On Record Update'),
        ('on_create', 'On Record Creation'),
        ('scheduled', 'Scheduled Action'),
    ], string='Execution Type', default='on_write', required=True)
    
    scheduled_interval = fields.Integer('Scheduled Interval (hours)', default=24,
                                       help='How often to run scheduled automation (in hours)')
    
    # Status and logging
    last_execution = fields.Datetime('Last Execution')
    execution_count = fields.Integer('Execution Count', default=0)
    success_count = fields.Integer('Success Count', default=0)
    error_count = fields.Integer('Error Count', default=0)
    
    # Advanced options
    condition_domain = fields.Text('Condition Domain', 
                                  help='Additional domain conditions for when to execute')
    error_notification = fields.Boolean('Send Error Notifications', default=True)
    log_executions = fields.Boolean('Log Executions', default=True)
    
    @api.model
    def _get_source_record(self, trigger_record):
        """Get source record based on configuration"""
        if not self.source_field and not self.source_fallback:
            return False
        
        # Try to get source from field
        if self.source_field:
            try:
                # Handle complex field paths (e.g., sale_line_id.product_id.product_tmpl_id)
                field_parts = self.source_field.split('.')
                current_record = trigger_record
                
                for field_part in field_parts:
                    if hasattr(current_record, field_part):
                        current_record = getattr(current_record, field_part)
                        if not current_record:
                            break
                    else:
                        current_record = None
                        break
                
                if current_record and hasattr(current_record, 'exists') and current_record.exists():
                    return current_record
            except Exception as e:
                _logger.warning(f"Error getting source record from field {self.source_field}: {e}")
                pass
        
        # Try fallback
        if self.source_fallback:
            try:
                source_record = self.env[self.source_model].browse(self.source_fallback)
                if source_record.exists():
                    return source_record
            except:
                pass
        
        return False
    
    @api.model
    def _get_target_record(self, trigger_record):
        """Get target record based on configuration"""
        if not self.target_field and not self.target_fallback:
            return False
        
        # Try to get target from field
        if self.target_field:
            try:
                # Handle complex field paths
                field_parts = self.target_field.split('.')
                current_record = trigger_record
                
                for field_part in field_parts:
                    if hasattr(current_record, field_part):
                        current_record = getattr(current_record, field_part)
                        if not current_record:
                            break
                    else:
                        current_record = None
                        break
                
                if current_record and hasattr(current_record, 'exists') and current_record.exists():
                    return current_record
            except Exception as e:
                _logger.warning(f"Error getting target record from field {self.target_field}: {e}")
                pass
        
        # Try fallback
        if self.target_fallback:
            try:
                target_record = self.env[self.target_model].browse(self.target_fallback)
                if target_record.exists():
                    return target_record
            except:
                pass
        
        return False
    
    @api.model
    def _should_execute(self, trigger_record):
        """Check if automation should execute based on trigger conditions"""
        # Check trigger field and value
        if self.trigger_field and self.trigger_value:
            if not hasattr(trigger_record, self.trigger_field):
                return False
            
            current_value = getattr(trigger_record, self.trigger_field)
            if isinstance(current_value, models.Model):
                current_value = current_value.name
            elif hasattr(current_value, 'display_name'):
                current_value = current_value.display_name
            
            if str(current_value) != str(self.trigger_value):
                return False
        
        # Check additional domain conditions
        if self.condition_domain:
            try:
                domain = eval(self.condition_domain)
                if not trigger_record.filtered_domain(domain):
                    return False
            except Exception as e:
                _logger.error(f"Error evaluating condition domain: {e}")
                return False
        
        return True
    
    def execute_automation(self, trigger_record=None):
        """Execute the document copy automation"""
        self.ensure_one()
        
        try:
            # Get source and target records
            source_record = self._get_source_record(trigger_record)
            target_record = self._get_target_record(trigger_record)
            
            if not source_record or not target_record:
                _logger.warning(f"Automation {self.name}: Missing source or target record")
                return False
            
            # Check if should execute
            if trigger_record and not self._should_execute(trigger_record):
                return False
            
            # Get document service
            document_service = self.env['unified.document.service']
            
            # Prepare category filter
            category_filter = None
            if self.copy_categories != 'all':
                category_filter = [self.copy_categories]
            
            # Execute document copying
            copied_docs = document_service.copy_documents_between_models(
                source_model=source_record._name,
                source_id=source_record.id,
                target_model=target_record._name,
                target_id=target_record.id,
                category_filter=category_filter
            )
            
            # Update statistics
            self.execution_count += 1
            if copied_docs:
                self.success_count += 1
            
            self.last_execution = fields.Datetime.now()
            
            return True
            
        except Exception as e:
            self.execution_count += 1
            self.error_count += 1
            self.last_execution = fields.Datetime.now()
            
            error_msg = f"Automation {self.name}: Error executing document copy - {str(e)}"
            _logger.error(error_msg)
            
            # Send error notification if enabled
            if self.error_notification:
                self._send_error_notification(error_msg)
            
            return False
    
    def _send_error_notification(self, error_msg):
        """Send error notification to administrators"""
        try:
            admin_users = self.env['res.users'].search([
                ('groups_id', 'in', self.env.ref('base.group_system').id)
            ])
            
            for user in admin_users:
                self.env['mail.message'].create({
                    'model': self._name,
                    'res_id': self.id,
                    'message_type': 'notification',
                    'subtype_id': self.env.ref('mail.mt_comment').id,
                    'body': f"<p><strong>Document Copy Automation Error:</strong></p><p>{error_msg}</p>",
                    'partner_ids': [(6, 0, [user.partner_id.id])],
                })
        except Exception as e:
            _logger.error(f"Failed to send error notification: {e}")
    
    @api.model
    def execute_scheduled_automations(self):
        """Execute all scheduled automations"""
        scheduled_automations = self.search([
            ('active', '=', True),
            ('execution_type', '=', 'scheduled')
        ])
        
        for automation in scheduled_automations:
            automation.execute_automation()
    
    @api.model
    def execute_on_record_update(self, record):
        """Execute automations triggered by record updates"""
        automations = self.search([
            ('active', '=', True),
            ('execution_type', '=', 'on_write'),
            ('trigger_model', '=', record._name)
        ])
        
        for automation in automations:
            automation.execute_automation(record)
    
    @api.model
    def execute_on_record_creation(self, record):
        """Execute automations triggered by record creation"""
        automations = self.search([
            ('active', '=', True),
            ('execution_type', '=', 'on_create'),
            ('trigger_model', '=', record._name)
        ])
        
        for automation in automations:
            automation.execute_automation(record)
    
    def action_test_automation(self):
        """Test the automation with sample data"""
        self.ensure_one()
        
        try:
            # Create test trigger record with basic fields
            test_data = {'name': f'Test Record for {self.name}'}
            
            # Add common fields that might be needed
            if self.trigger_model == 'project.project':
                test_data.update({
                    'partner_id': self.env['res.partner'].search([], limit=1).id,
                })
            elif self.trigger_model == 'sale.order':
                test_data.update({
                    'partner_id': self.env['res.partner'].search([], limit=1).id,
                    'state': 'draft',
                })
            elif self.trigger_model == 'purchase.order':
                test_data.update({
                    'partner_id': self.env['res.partner'].search([], limit=1).id,
                    'state': 'draft',
                })
            elif self.trigger_model == 'product.template':
                test_data.update({
                    'type': 'product',
                })
            
            test_record = self.env[self.trigger_model].create(test_data)
            
            # Execute automation
            success = self.execute_automation(test_record)
            
            # Clean up test record
            test_record.unlink()
            
            # Show result
            if success:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Test Successful'),
                        'message': _('Automation test completed successfully.'),
                        'type': 'success',
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Test Failed'),
                        'message': _('Automation test failed. Check logs for details.'),
                        'type': 'danger',
                    }
                }
                
        except Exception as e:
            _logger.error(f"Test automation failed: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Test Error'),
                    'message': _('Automation test encountered an error: %s') % str(e),
                    'type': 'danger',
                }
            }
    
    def action_reset_statistics(self):
        """Reset execution statistics"""
        self.ensure_one()
        self.write({
            'execution_count': 0,
            'success_count': 0,
            'error_count': 0,
            'last_execution': False,
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Statistics Reset'),
                'message': _('Execution statistics have been reset.'),
                'type': 'info',
            }
        }
