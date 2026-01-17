# -*- coding: utf-8 -*-

import base64
import csv
import io
import logging
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class IntakeBatch(models.Model):
    _name = 'gr.intake.batch'
    _description = 'Grants Training Intake Batch'
    _order = 'create_date desc'

    # Basic Fields
    name = fields.Char(
        string='Batch Name',
        required=True,
        default=lambda self: _('New'),
        copy=False
    )
    
    filename = fields.Char(
        string='File Name',
        help='Name of the uploaded file'
    )
    
    file_data = fields.Binary(
        string='File',
        help='Upload CSV or Excel file with student data'
    )
    
    file_type = fields.Selection([
        ('csv', 'CSV File'),
        ('xlsx', 'Excel File'),
    ], string='File Type', compute='_compute_file_type', store=True)
    
    # Status Fields
    state = fields.Selection([
        ('draft', 'Draft'),
        ('uploaded', 'File Uploaded'),
        ('validated', 'Validated'),
        ('processed', 'Processed'),
        ('error', 'Error'),
    ], string='Status', default='draft')
    
    # Processing Fields
    total_records = fields.Integer(
        string='Total Records',
        help='Total number of records in the file'
    )
    
    processed_records = fields.Integer(
        string='Processed Records',
        default=0,
        help='Number of records successfully processed'
    )
    
    error_records = fields.Integer(
        string='Error Records',
        default=0,
        help='Number of records with errors'
    )
    
    validation_errors = fields.Text(
        string='Validation Errors',
        help='Details of validation errors'
    )
    
    # Timestamps
    upload_date = fields.Datetime(
        string='Upload Date',
        default=fields.Datetime.now
    )
    
    validation_date = fields.Datetime(
        string='Validation Date',
        help='Date when the file was validated'
    )
    
    processing_date = fields.Datetime(
        string='Processing Date',
        help='Date when the file was processed'
    )
    
    # Related Records
    student_ids = fields.One2many(
        'gr.student',
        'intake_batch_id',
        string='Students',
        help='Students created from this batch'
    )
    
    # Computed Fields
    success_rate = fields.Float(
        string='Success Rate (%)',
        compute='_compute_success_rate',
        store=True,
        help='Percentage of successfully processed records'
    )
    
    @api.depends('filename', 'file_data')
    def _compute_file_type(self):
        """Compute file type based on filename extension."""
        for record in self:
            if record.filename:
                if record.filename.lower().endswith('.csv'):
                    record.file_type = 'csv'
                elif record.filename.lower().endswith(('.xlsx', '.xls')):
                    record.file_type = 'xlsx'
                else:
                    record.file_type = False
            else:
                record.file_type = False
    
    @api.depends('total_records', 'processed_records')
    def _compute_success_rate(self):
        """Compute success rate percentage."""
        for record in self:
            if record.total_records > 0:
                record.success_rate = (record.processed_records / record.total_records) * 100
            else:
                record.success_rate = 0.0
    
    
    @api.model
    def create(self, vals):
        """Override create to generate sequence number."""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('gr.intake.batch') or _('New')
        return super(IntakeBatch, self).create(vals)
    
    def action_upload_file(self):
        """Action to upload and validate file."""
        self.ensure_one()
        
        if not self.file_data:
            raise UserError(_('Please upload a file first.'))
        
        if not self.filename:
            raise UserError(_('File name is required.'))
        
        try:
            # Parse file and count records
            records = self._parse_file()
            self.total_records = len(records)
            
            # Update state
            self.state = 'uploaded'
            self.upload_date = fields.Datetime.now()
            
            # Log the action
            _logger.info('File uploaded for batch %s: %s - %d records found', self.name, self.filename, self.total_records)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('File Uploaded'),
                    'message': _('File has been uploaded successfully. %d records found. You can now validate it.') % self.total_records,
                    'type': 'success',
                }
            }
            
        except Exception as e:
            _logger.error('Error uploading file for batch %s: %s', self.name, str(e))
            self.state = 'error'
            self.validation_errors = str(e)
            raise UserError(_('Error uploading file: %s') % str(e))
    
    def action_validate_file(self):
        """Action to validate the uploaded file."""
        self.ensure_one()
        
        if self.state != 'uploaded':
            raise UserError(_('Please upload a file first.'))
        
        try:
            # Parse file and count records
            records = self._parse_file()
            self.total_records = len(records)
            
            # Validate records
            errors = self._validate_records(records)
            
            if errors:
                self.validation_errors = '\n'.join(errors)
                self.state = 'error'
                self.error_records = len(errors)
            else:
                self.validation_errors = False
                self.state = 'validated'
                self.error_records = 0
            
            self.validation_date = fields.Datetime.now()
            
            # Log the validation
            _logger.info('File validated for batch %s: %d records, %d errors', 
                        self.name, self.total_records, self.error_records)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('File Validated'),
                    'message': _('File validation completed. %d records found, %d errors.') % 
                              (self.total_records, self.error_records),
                    'type': 'success' if not errors else 'warning',
                }
            }
            
        except Exception as e:
            _logger.error('Error validating batch %s: %s', self.name, str(e))
            self.state = 'error'
            self.validation_errors = str(e)
            raise UserError(_('Error validating file: %s') % str(e))
    
    def action_process_file(self):
        """Action to process the validated file and create students."""
        self.ensure_one()
        
        _logger.info('Starting file processing for batch %s (state: %s)', self.name, self.state)
        
        if self.state != 'validated':
            raise UserError(_('Please validate the file first.'))
        
        try:
            # Parse file again
            _logger.info('Parsing file for batch %s', self.name)
            records = self._parse_file()
            _logger.info('File parsed successfully: %d records found', len(records))
            
            # Create students
            _logger.info('Creating students for batch %s', self.name)
            created_students = self._create_students(records)
            
            # Update counters
            self.processed_records = len(created_students)
            self.processing_date = fields.Datetime.now()
            self.state = 'processed'
            
            # Log the processing
            _logger.info('File processed for batch %s: %d students created', 
                        self.name, self.processed_records)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('File Processed'),
                    'message': _('File processing completed. %d students created.') % 
                              self.processed_records,
                    'type': 'success',
                }
            }
            
        except Exception as e:
            _logger.error('Error processing batch %s: %s', self.name, str(e))
            self.state = 'error'
            self.validation_errors = str(e)
            raise UserError(_('Error processing file: %s') % str(e))
    
    def _parse_file(self):
        """Parse the uploaded file and return records."""
        if not self.file_data:
            return []
        
        try:
            # Decode file data
            file_data = base64.b64decode(self.file_data)
            
            _logger.info('Parsing file: filename=%s, file_type=%s', self.filename, self.file_type)
            
            if self.file_type == 'csv':
                return self._parse_csv(file_data)
            elif self.file_type == 'xlsx':
                return self._parse_excel(file_data)
            else:
                _logger.error('Unsupported file type: %s (filename: %s)', self.file_type, self.filename)
                raise UserError(_('Unsupported file type: %s') % self.file_type)
                
        except Exception as e:
            _logger.error('Error parsing file: %s', str(e))
            raise UserError(_('Error parsing file: %s') % str(e))
    
    def _parse_csv(self, file_data):
        """Parse CSV file and return records."""
        try:
            # Convert bytes to string
            file_content = file_data.decode('utf-8')
            _logger.info('CSV content length: %d characters', len(file_content))
            
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(file_content))
            records = list(csv_reader)
            
            _logger.info('CSV parsed successfully: %d records found', len(records))
            if records:
                _logger.info('CSV headers: %s', list(records[0].keys()))
                # Debug: Log the first record to see what data is being parsed
                _logger.info('First record data: %s', records[0])
            
            return records
            
        except Exception as e:
            _logger.error('Error parsing CSV: %s', str(e))
            raise UserError(_('Error parsing CSV file: %s') % str(e))
    
    def _parse_excel(self, file_data):
        """Parse Excel file and return records."""
        try:
            # For now, return empty list - Excel parsing will be implemented later
            _logger.warning('Excel parsing not yet implemented')
            return []
            
        except Exception as e:
            _logger.error('Error parsing Excel: %s', str(e))
            raise UserError(_('Error parsing Excel file: %s') % str(e))
    
    def _validate_records(self, records):
        """Validate records and return list of errors."""
        errors = []
        
        # Required fields
        required_fields = ['name', 'email', 'phone']
        
        for i, record in enumerate(records, 1):
            # Check required fields
            for field in required_fields:
                if not record.get(field):
                    errors.append(f'Row {i}: Missing required field "{field}"')
            
            # Validate email format
            email = record.get('email', '')
            if email and '@' not in email:
                errors.append(f'Row {i}: Invalid email format "{email}"')
        
        return errors
    
    def _create_students(self, records):
        """Create student records from validated data."""
        created_students = []
        
        _logger.info('Starting to create students from %d records', len(records))
        
        for i, record in enumerate(records, 1):
            try:
                # Parse birth_date if provided
                birth_date = None
                if record.get('birth_date'):
                    try:
                        birth_date = datetime.strptime(record.get('birth_date'), '%Y-%m-%d').date()
                    except ValueError:
                        _logger.warning('Invalid birth_date format for student %d: %s', i, record.get('birth_date'))
                
                # Parse certificate_date if provided
                certificate_date = None
                if record.get('certificate_date'):
                    try:
                        certificate_date = datetime.strptime(record.get('certificate_date'), '%Y-%m-%d').date()
                    except ValueError:
                        _logger.warning('Invalid certificate_date format for student %d: %s', i, record.get('certificate_date'))
                
                # Parse has_certificate boolean
                has_certificate = False
                if record.get('has_certificate'):
                    has_cert_str = record.get('has_certificate').lower().strip()
                    has_certificate = has_cert_str in ['true', '1', 'yes', 'y']
                
                # Create student record with all fields
                student_vals = {
                    'name': record.get('name'),
                    'email': record.get('email'),
                    'phone': record.get('phone'),
                    'birth_date': birth_date,
                    'gender': record.get('gender'),
                    'nationality': record.get('nationality'),
                    'native_language': record.get('native_language'),
                    'english_level': record.get('english_level'),
                    'has_certificate': has_certificate,
                    'certificate_type': record.get('certificate_type'),
                    'certificate_date': certificate_date,
                    'intake_batch_id': self.id,
                    'state': 'draft',
                }
                
                _logger.info('Creating student %d: %s with birth_date=%s, has_certificate=%s, english_level=%s', 
                           i, student_vals['name'], birth_date, has_certificate, record.get('english_level'))
                _logger.info('Full student_vals for student %d: %s', i, student_vals)
                student = self.env['gr.student'].create(student_vals)
                created_students.append(student)
                _logger.info('Student %d created successfully with ID: %s', i, student.id)
                _logger.info('Student %d actual values after creation: birth_date=%s, has_certificate=%s, english_level=%s, age=%s', 
                           i, student.birth_date, student.has_certificate, student.english_level, student.age)
                
            except Exception as e:
                _logger.error('Error creating student %d from record %s: %s', i, record, str(e))
                continue
        
        _logger.info('Student creation completed: %d students created out of %d records', 
                    len(created_students), len(records))
        return created_students
    
    def action_reset(self):
        """Reset batch to draft state."""
        self.ensure_one()
        self.state = 'draft'
        self.total_records = 0
        self.processed_records = 0
        self.error_records = 0
        self.validation_errors = False
        self.upload_date = False
        self.validation_date = False
        self.processing_date = False
