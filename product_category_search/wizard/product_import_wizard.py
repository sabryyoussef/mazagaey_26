# -*- coding: utf-8 -*-
import base64
import csv
import io
import re
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ProductImportWizard(models.TransientModel):
    """
    CSV Import Wizard for Bulk Product Loading
    
    Features:
    - Upload CSV with product data
    - Auto-detect and map columns to fields
    - Preview before import
    - Auto-categorize products (service types, departments)
    - Import progress tracking
    """
    _name = 'product.import.wizard'
    _description = 'Product Import Wizard'
    
    # === Step Control ===
    state = fields.Selection([
        ('upload', 'Upload File'),
        ('mapping', 'Map Columns'),
        ('preview', 'Preview Data'),
        ('import', 'Import Results'),
    ], default='upload', string='Step')
    
    # === Upload Step ===
    name = fields.Char(
        string='Import Name',
        default=lambda self: _('Product Import - %s') % fields.Date.today(),
    )
    file_data = fields.Binary(
        string='CSV File',
        help='Upload a CSV file with product data',
    )
    file_name = fields.Char(string='File Name')
    delimiter = fields.Selection([
        (',', 'Comma (,)'),
        (';', 'Semicolon (;)'),
        ('\t', 'Tab'),
        ('|', 'Pipe (|)'),
    ], default=',', string='Delimiter')
    encoding = fields.Selection([
        ('utf-8', 'UTF-8'),
        ('latin-1', 'Latin-1'),
        ('cp1252', 'Windows-1252'),
    ], default='utf-8', string='Encoding')
    has_header = fields.Boolean(
        string='File Has Header Row',
        default=True,
    )
    
    # === Mapping Step ===
    column_mapping_ids = fields.One2many(
        'product.import.column.mapping',
        'wizard_id',
        string='Column Mappings',
    )
    detected_columns = fields.Text(
        string='Detected Columns',
        help='JSON list of column names from CSV',
    )
    row_count = fields.Integer(
        string='Total Rows',
        readonly=True,
    )
    
    # === Auto-Categorization Options ===
    auto_detect_service_type = fields.Boolean(
        string='Auto-Detect Service Type',
        default=True,
        help='Automatically assign service types based on product name patterns',
    )
    auto_detect_department = fields.Boolean(
        string='Auto-Detect Department',
        default=True,
        help='Automatically assign department based on product name patterns',
    )
    default_service_type_id = fields.Many2one(
        'product.service.type',
        string='Default Service Type',
        help='Use this if auto-detection fails',
    )
    default_department_id = fields.Many2one(
        'product.department',
        string='Default Department',
        help='Use this if auto-detection fails',
    )
    product_type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Storable'),
    ], default='service', string='Product Type')
    
    # === Preview Step ===
    preview_line_ids = fields.One2many(
        'product.import.preview.line',
        'wizard_id',
        string='Preview Lines',
    )
    preview_limit = fields.Integer(
        string='Preview Limit',
        default=20,
    )
    
    # === Import Results ===
    import_log = fields.Text(
        string='Import Log',
        readonly=True,
    )
    imported_count = fields.Integer(
        string='Products Imported',
        readonly=True,
    )
    updated_count = fields.Integer(
        string='Products Updated',
        readonly=True,
    )
    error_count = fields.Integer(
        string='Errors',
        readonly=True,
    )
    duplicate_action = fields.Selection([
        ('skip', 'Skip Duplicates'),
        ('update', 'Update Existing'),
        ('create', 'Create New (Allow Duplicates)'),
    ], default='skip', string='Duplicate Handling')
    
    # === Column Mapping Keywords for Auto-Detection ===
    COLUMN_PATTERNS = {
        'name': ['name', 'product', 'service', 'title', 'description'],
        'default_code': ['code', 'sku', 'reference', 'ref', 'internal_reference'],
        'list_price': ['price', 'sale_price', 'list_price', 'amount', 'cost', 'fee'],
        'description': ['description', 'desc', 'details', 'notes'],
        'category': ['category', 'categ', 'type', 'group'],
        'department': ['department', 'dept', 'team', 'division'],
        'service_type': ['service_type', 'service', 'type'],
    }
    
    @api.onchange('file_data')
    def _onchange_file_data(self):
        """Reset wizard when new file is uploaded"""
        if self.file_data:
            self.column_mapping_ids = [(5, 0, 0)]
            self.preview_line_ids = [(5, 0, 0)]
            self.state = 'upload'
    
    def _parse_csv_file(self):
        """Parse CSV file and return rows"""
        if not self.file_data:
            raise UserError(_('Please upload a CSV file first.'))
        
        try:
            file_content = base64.b64decode(self.file_data)
            file_content = file_content.decode(self.encoding)
            
            # Handle different line endings
            file_content = file_content.replace('\r\n', '\n').replace('\r', '\n')
            
            reader = csv.reader(
                io.StringIO(file_content),
                delimiter=self.delimiter,
            )
            rows = list(reader)
            
            if not rows:
                raise UserError(_('The CSV file is empty.'))
            
            return rows
            
        except UnicodeDecodeError:
            raise UserError(_(
                'Could not decode file with %s encoding. '
                'Please try a different encoding.'
            ) % self.encoding)
        except csv.Error as e:
            raise UserError(_('CSV parsing error: %s') % str(e))
    
    def _auto_detect_column_mapping(self, headers):
        """Auto-detect column to field mappings based on header names"""
        mappings = []
        
        for idx, header in enumerate(headers):
            header_lower = header.lower().strip()
            field_name = False
            
            # Check against known patterns
            for field, patterns in self.COLUMN_PATTERNS.items():
                for pattern in patterns:
                    if pattern in header_lower:
                        field_name = field
                        break
                if field_name:
                    break
            
            mappings.append({
                'column_index': idx,
                'column_name': header,
                'field_name': field_name,
                'is_mapped': bool(field_name),
            })
        
        return mappings
    
    def action_analyze_file(self):
        """Analyze uploaded file and detect columns"""
        self.ensure_one()
        
        rows = self._parse_csv_file()
        
        # Get headers
        headers = rows[0] if self.has_header else [f'Column {i+1}' for i in range(len(rows[0]))]
        data_start = 1 if self.has_header else 0
        
        self.row_count = len(rows) - data_start
        self.detected_columns = ','.join(headers)
        
        # Create column mappings
        mappings = self._auto_detect_column_mapping(headers)
        
        # Clear existing mappings
        self.column_mapping_ids = [(5, 0, 0)]
        
        # Create new mapping records
        mapping_vals = []
        for m in mappings:
            mapping_vals.append((0, 0, {
                'column_index': m['column_index'],
                'column_name': m['column_name'],
                'field_name': m['field_name'],
                'is_mapped': m['is_mapped'],
            }))
        
        self.column_mapping_ids = mapping_vals
        self.state = 'mapping'
        
        return self._reopen_wizard()
    
    def action_generate_preview(self):
        """Generate preview of import data"""
        self.ensure_one()
        
        rows = self._parse_csv_file()
        data_start = 1 if self.has_header else 0
        data_rows = rows[data_start:data_start + self.preview_limit]
        
        # Get mappings
        name_idx = self._get_mapped_column_index('name')
        code_idx = self._get_mapped_column_index('default_code')
        price_idx = self._get_mapped_column_index('list_price')
        category_idx = self._get_mapped_column_index('category')
        
        if name_idx is None:
            raise UserError(_('Please map the "Name" column - it is required.'))
        
        # Clear existing preview
        self.preview_line_ids = [(5, 0, 0)]
        
        preview_vals = []
        for row_num, row in enumerate(data_rows, start=1):
            # Get values from mapped columns
            name = row[name_idx].strip() if len(row) > name_idx else ''
            code = row[code_idx].strip() if code_idx and len(row) > code_idx else ''
            
            # Parse price
            price = 0.0
            if price_idx and len(row) > price_idx:
                price_str = row[price_idx].strip()
                # Remove currency symbols and commas
                price_str = re.sub(r'[^\d.]', '', price_str)
                try:
                    price = float(price_str) if price_str else 0.0
                except ValueError:
                    price = 0.0
            
            category_name = row[category_idx].strip() if category_idx and len(row) > category_idx else ''
            
            # Auto-detect service type and department
            detected_service_type = self._detect_service_type(name, category_name) if self.auto_detect_service_type else False
            detected_department = self._detect_department(name, category_name) if self.auto_detect_department else False
            
            # Check for existing product
            existing_product = self.env['product.template'].search([
                '|',
                ('name', '=ilike', name),
                ('default_code', '=', code) if code else ('id', '=', False),
            ], limit=1)
            
            status = 'duplicate' if existing_product else 'new'
            
            preview_vals.append((0, 0, {
                'row_number': row_num,
                'name': name,
                'default_code': code,
                'list_price': price,
                'category_name': category_name,
                'detected_service_type_id': detected_service_type.id if detected_service_type else False,
                'detected_department_id': detected_department.id if detected_department else False,
                'existing_product_id': existing_product.id if existing_product else False,
                'status': status,
                'include': status == 'new' or self.duplicate_action != 'skip',
            }))
        
        self.preview_line_ids = preview_vals
        self.state = 'preview'
        
        return self._reopen_wizard()
    
    def _get_mapped_column_index(self, field_name):
        """Get the column index for a mapped field"""
        mapping = self.column_mapping_ids.filtered(lambda m: m.field_name == field_name)
        return mapping.column_index if mapping else None
    
    def _detect_service_type(self, product_name, category_name=''):
        """Auto-detect service type based on product name patterns"""
        name_lower = (product_name + ' ' + category_name).lower()
        
        # Service type detection patterns
        patterns = {
            'VISA': ['visa', 'employment visa', 'investor visa', 'golden visa', 'dependent visa', 'maid visa'],
            'ACCT': ['accounting', 'bookkeeping', 'audit', 'tax', 'vat', 'corporate tax', 'ct registration', 'ct filing'],
            'BANK': ['banking', 'bank account', 'mortgage', 'digital banking'],
            'SETUP': ['business setup', 'company formation', 'license issuance', 'pre-approval', 'fzco'],
            'RENEW': ['renewal', 'license renewal', 'renew'],
            'LIQUID': ['liquidation', 'cancellation', 'cancel license', 'wind up'],
            'ADMIN': ['amendment', 'add activity', 'remove activity', 'shareholder', 'management change', 'name change'],
            'VALUE': ['pro', 'ejari', 'attestation', 'notary', 'medical', 'emirates id', 'eid', 'typing'],
            'DOCUMENT': ['certificate', 'letter', 'clearance', 'approval', 'permit'],
        }
        
        ServiceType = self.env['product.service.type']
        
        for code, keywords in patterns.items():
            for keyword in keywords:
                if keyword in name_lower:
                    service_type = ServiceType.search([('code', '=like', code + '%')], limit=1, order='sequence')
                    if service_type:
                        return service_type
        
        return self.default_service_type_id or False
    
    def _detect_department(self, product_name, category_name=''):
        """Auto-detect department based on product name patterns"""
        name_lower = (product_name + ' ' + category_name).lower()
        
        Department = self.env['product.department']
        
        # Check for explicit department markers
        if any(x in name_lower for x in ['accounts', 'accounting', '- accounts', 'finance']):
            dept = Department.search([('code', '=', 'ACCT')], limit=1)
            if dept:
                return dept
        
        if any(x in name_lower for x in ['operations', '- operations', 'ops']):
            dept = Department.search([('code', '=', 'OPS')], limit=1)
            if dept:
                return dept
        
        if any(x in name_lower for x in ['sales', '- sales', 'sale']):
            dept = Department.search([('code', '=', 'SALES')], limit=1)
            if dept:
                return dept
        
        if any(x in name_lower for x in ['pro', 'typing', 'admin', 'administration']):
            dept = Department.search([('code', '=', 'PRO')], limit=1)
            if dept:
                return dept
        
        return self.default_department_id or False
    
    def action_execute_import(self):
        """Execute the actual product import"""
        self.ensure_one()
        
        rows = self._parse_csv_file()
        data_start = 1 if self.has_header else 0
        data_rows = rows[data_start:]
        
        # Get column mappings
        name_idx = self._get_mapped_column_index('name')
        code_idx = self._get_mapped_column_index('default_code')
        price_idx = self._get_mapped_column_index('list_price')
        desc_idx = self._get_mapped_column_index('description')
        category_idx = self._get_mapped_column_index('category')
        
        if name_idx is None:
            raise UserError(_('Please map the "Name" column - it is required.'))
        
        imported = 0
        updated = 0
        errors = 0
        log_lines = []
        
        ProductTemplate = self.env['product.template']
        
        for row_num, row in enumerate(data_rows, start=1):
            try:
                # Parse row data
                name = row[name_idx].strip() if len(row) > name_idx else ''
                if not name:
                    log_lines.append(f'Row {row_num}: Skipped - Empty name')
                    continue
                
                code = row[code_idx].strip() if code_idx is not None and len(row) > code_idx else ''
                
                # Parse price
                price = 0.0
                if price_idx is not None and len(row) > price_idx:
                    price_str = row[price_idx].strip()
                    price_str = re.sub(r'[^\d.]', '', price_str)
                    try:
                        price = float(price_str) if price_str else 0.0
                    except ValueError:
                        price = 0.0
                
                description = row[desc_idx].strip() if desc_idx is not None and len(row) > desc_idx else ''
                category_name = row[category_idx].strip() if category_idx is not None and len(row) > category_idx else ''
                
                # Check for existing product
                domain = [('name', '=ilike', name)]
                if code:
                    domain = ['|', ('default_code', '=', code)] + domain
                existing_product = ProductTemplate.search(domain, limit=1)
                
                # Auto-detect categorization
                service_type = self._detect_service_type(name, category_name) if self.auto_detect_service_type else self.default_service_type_id
                department = self._detect_department(name, category_name) if self.auto_detect_department else self.default_department_id
                
                # Prepare values
                vals = {
                    'name': name,
                    'detailed_type': self.product_type,
                    'list_price': price,
                    'sale_ok': True,
                    'purchase_ok': False,
                }
                
                if code:
                    vals['default_code'] = code
                if description:
                    vals['description'] = description
                if service_type:
                    vals['service_type_id'] = service_type.id
                if department:
                    vals['product_department_id'] = department.id
                
                # Handle duplicates
                if existing_product:
                    if self.duplicate_action == 'skip':
                        log_lines.append(f'Row {row_num}: Skipped duplicate - {name}')
                        continue
                    elif self.duplicate_action == 'update':
                        existing_product.write(vals)
                        updated += 1
                        log_lines.append(f'Row {row_num}: Updated - {name}')
                        continue
                    # else: create new (allow duplicates)
                
                # Create product
                ProductTemplate.create(vals)
                imported += 1
                log_lines.append(f'Row {row_num}: Created - {name}')
                
            except Exception as e:
                errors += 1
                log_lines.append(f'Row {row_num}: ERROR - {str(e)}')
        
        # Update wizard with results
        self.imported_count = imported
        self.updated_count = updated
        self.error_count = errors
        self.import_log = '\n'.join(log_lines[-100:])  # Keep last 100 lines
        self.state = 'import'
        
        return self._reopen_wizard()
    
    def action_back_to_upload(self):
        """Go back to upload step"""
        self.state = 'upload'
        return self._reopen_wizard()
    
    def action_back_to_mapping(self):
        """Go back to mapping step"""
        self.state = 'mapping'
        return self._reopen_wizard()
    
    def action_back_to_preview(self):
        """Go back to preview step"""
        self.state = 'preview'
        return self._reopen_wizard()
    
    def _reopen_wizard(self):
        """Reopen wizard to refresh view"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.import.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_view_imported_products(self):
        """View all imported products"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Imported Products'),
            'res_model': 'product.template',
            'view_mode': 'list,form',
            'domain': [],
            'context': {'search_default_filter_service_type': 1},
        }


class ProductImportColumnMapping(models.TransientModel):
    """Column mapping for product import"""
    _name = 'product.import.column.mapping'
    _description = 'Product Import Column Mapping'
    _order = 'column_index'
    
    wizard_id = fields.Many2one(
        'product.import.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade',
    )
    column_index = fields.Integer(
        string='Column #',
        required=True,
    )
    column_name = fields.Char(
        string='CSV Column',
        required=True,
    )
    field_name = fields.Selection([
        ('name', 'Product Name'),
        ('default_code', 'Internal Reference / SKU'),
        ('list_price', 'Sale Price'),
        ('description', 'Description'),
        ('category', 'Category (for auto-detect)'),
        ('department', 'Department (for auto-detect)'),
        ('service_type', 'Service Type (for auto-detect)'),
        (False, '-- Do Not Import --'),
    ], string='Map to Field')
    is_mapped = fields.Boolean(
        string='Is Mapped',
        compute='_compute_is_mapped',
        store=True,
    )
    sample_values = fields.Char(
        string='Sample Values',
        help='First few values from this column',
    )
    
    @api.depends('field_name')
    def _compute_is_mapped(self):
        for rec in self:
            rec.is_mapped = bool(rec.field_name)


class ProductImportPreviewLine(models.TransientModel):
    """Preview line for product import"""
    _name = 'product.import.preview.line'
    _description = 'Product Import Preview Line'
    _order = 'row_number'
    
    wizard_id = fields.Many2one(
        'product.import.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade',
    )
    row_number = fields.Integer(
        string='Row #',
        readonly=True,
    )
    name = fields.Char(
        string='Product Name',
        readonly=True,
    )
    default_code = fields.Char(
        string='Reference',
        readonly=True,
    )
    list_price = fields.Float(
        string='Price',
        readonly=True,
    )
    category_name = fields.Char(
        string='Category (CSV)',
        readonly=True,
    )
    detected_service_type_id = fields.Many2one(
        'product.service.type',
        string='Auto-Detected Service Type',
        readonly=True,
    )
    detected_department_id = fields.Many2one(
        'product.department',
        string='Auto-Detected Department',
        readonly=True,
    )
    existing_product_id = fields.Many2one(
        'product.template',
        string='Existing Product',
        readonly=True,
    )
    status = fields.Selection([
        ('new', 'New'),
        ('duplicate', 'Duplicate'),
        ('error', 'Error'),
    ], string='Status', readonly=True)
    include = fields.Boolean(
        string='Import',
        default=True,
        help='Include this row in import',
    )
