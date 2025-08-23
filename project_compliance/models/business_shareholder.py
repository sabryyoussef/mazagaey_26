from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BusinessRelationships(models.Model):
    _name = 'business.relationships'
    _description = 'Business Relationships'
    _order = 'name'

    name = fields.Char(string='Relationship Type', required=True)
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True, string='Active')


class PartnerUbo(models.Model):
    _name = 'res.partner.ubo'
    _description = 'Partner UBO'
    _order = 'name'

    name = fields.Char(string='UBO Name', required=True)
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True, string='Active')


class BusinessShareholderAddress(models.Model):
    _name = 'business.shareholder.address'
    _description = 'Business Shareholder Address'
    _order = 'is_primary desc, name'

    name = fields.Char(string='Address Name', required=True)
    shareholder_id = fields.Many2one('res.partner.business.shareholder', string='Shareholder', required=True, ondelete='cascade')
    
    type = fields.Selection([
        ('home', 'Home'),
        ('work', 'Work'),
        ('billing', 'Billing'),
        ('shipping', 'Shipping'),
        ('other', 'Other')
    ], string='Address Type', required=True, default='work')
    
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street 2')
    zip = fields.Char(string='ZIP')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')
    is_primary = fields.Boolean(string='Primary Address', default=False)
    active = fields.Boolean(default=True, string='Active')

    @api.onchange('country_id')
    def _onchange_country_id(self):
        """Reset state when country changes"""
        if self.country_id:
            self.state_id = False

    @api.onchange('is_primary')
    def _onchange_is_primary(self):
        """Ensure only one primary address per shareholder"""
        if self.is_primary and self.shareholder_id:
            # Unset primary flag for other addresses of the same shareholder
            other_addresses = self.shareholder_id.address_ids.filtered(lambda a: a.id != self.id)
            other_addresses.write({'is_primary': False})


class BusinessShareholder(models.Model):
    _name = 'res.partner.business.shareholder'
    _description = 'Business Shareholder'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Shareholder Name', required=True, tracking=True)
    
    # Project and partner relations
    project_id = fields.Many2one('project.project', string='Project', tracking=True, ondelete='set null')
    customer_id = fields.Many2one('res.partner', string='Customer', tracking=True, ondelete='set null')
    partner_id = fields.Many2one('res.partner', string='Partner', tracking=True, ondelete='set null')
    contact_id = fields.Many2one('res.partner', string='Contact Person', 
                                domain="[('is_company', '=', False)]", tracking=True, ondelete='set null')
    ubo_id = fields.Many2one('res.partner.ubo', string='UBO', tracking=True, ondelete='set null')

    # Shareholding information
    shareholding = fields.Float(string='Shareholding (%)', 
                               help='Percentage of shares owned', tracking=True)
    relationship_ids = fields.Many2many('business.relationships', string='Relationships', 
                                       widget='many2many_tags', tracking=True)

    # Contact information
    email = fields.Char(string='Email', tracking=True)
    mobile = fields.Char(string='Mobile', tracking=True)
    company_type = fields.Selection([
        ('person', 'Individual'),
        ('company', 'Company')
    ], string='Company Type', default='person', tracking=True)

    # Individual information
    nationality_id = fields.Many2one('res.country', string='Nationality', tracking=True, ondelete='set null')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender', tracking=True)

    # Corporate information
    license_authority_id = fields.Char(string='License Authority', tracking=True)
    incorporation_date = fields.Date(string='Incorporation Date', tracking=True)
    license_number = fields.Char(string='License Number', tracking=True)
    license_validity = fields.Selection([
        ('1', '1 Year'),
        ('2', '2 Years'),
        ('3', '3 Years'),
        ('4', '4 Years'),
        ('5', '5 Years'),
        ('6', '6 Years'),
        ('7', '7 Years'),
        ('8', '8 Years'),
        ('9', '9 Years'),
        ('10', '10 Years'),
    ], string='License Validity', tracking=True)

    # Address fields - One2many relationship for multiple addresses
    address_ids = fields.One2many('business.shareholder.address', 'shareholder_id', string='Addresses')

    # Document references (using project_documents_extension)
    passport = fields.Char(string='Passport Reference', tracking=True)
    uae_resident = fields.Boolean(string='UAE Resident', tracking=True)
    eid_copy = fields.Char(string='EID Copy Reference', tracking=True)
    residence_visa_copy = fields.Char(string='Residence Visa Copy Reference', tracking=True)
    current_visa = fields.Char(string='Current Visa Reference', tracking=True)
    entry_stamp = fields.Char(string='Entry Stamp Reference', tracking=True)
    trade_license = fields.Char(string='Trade License Reference', tracking=True)
    memorandum_association = fields.Char(string='Memorandum of Association Reference', tracking=True)
    apply_visa = fields.Boolean(string='Apply Visa', tracking=True)

    # Additional fields


    # Computed fields
    address_count = fields.Integer(compute="_compute_address_count", string="Address Count")

    notes = fields.Text(string='Notes', tracking=True)

    @api.constrains('shareholding')
    def _check_shareholding(self):
        for record in self:
            if record.shareholding and (record.shareholding < 0 or record.shareholding > 100):
                raise ValidationError(_('Shareholding percentage must be between 0 and 100.'))

    @api.depends("address_ids")
    def _compute_address_count(self):
        for record in self:
            record.address_count = len(record.address_ids)

    @api.onchange('company_type')
    def _onchange_company_type(self):
        if self.company_type == 'company':
            self.nationality_id = False
            self.gender = False
        else:
            self.license_authority_id = False
            self.incorporation_date = False
            self.license_number = False
            self.license_validity = False

    @api.model
    def _fix_dangling_foreign_keys(self):
        """Fix any dangling foreign keys that might cause read errors"""
        # Fix ubo_id references
        invalid_ubos = self.search([('ubo_id', '!=', False)])
        for shareholder in invalid_ubos:
            if not shareholder.ubo_id.exists():
                shareholder.ubo_id = False
        
        # Fix project_id references
        invalid_projects = self.search([('project_id', '!=', False)])
        for shareholder in invalid_projects:
            if not shareholder.project_id.exists():
                shareholder.project_id = False
        
        # Fix partner_id references
        invalid_partners = self.search([('partner_id', '!=', False)])
        for shareholder in invalid_partners:
            if not shareholder.partner_id.exists():
                shareholder.partner_id = False
        
        # Fix customer_id references
        invalid_customers = self.search([('customer_id', '!=', False)])
        for shareholder in invalid_customers:
            if not shareholder.customer_id.exists():
                shareholder.customer_id = False
        
        # Fix contact_id references
        invalid_contacts = self.search([('contact_id', '!=', False)])
        for shareholder in invalid_contacts:
            if not shareholder.contact_id.exists():
                shareholder.contact_id = False
        
        # Fix nationality_id references
        invalid_nationalities = self.search([('nationality_id', '!=', False)])
        for shareholder in invalid_nationalities:
            if not shareholder.nationality_id.exists():
                shareholder.nationality_id = False
