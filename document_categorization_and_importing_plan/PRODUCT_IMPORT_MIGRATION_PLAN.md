# Product Import & Migration Plan
## Freezoner to Mazagawy Module Enhancement Strategy

**Source Database:** Odoo 19 Freezoner (odoo19_restore)  
**Target System:** Mazagawy Odoo 18 Custom Modules  
**Total Products:** 250+ Service Products  
**Migration Date:** January 19, 2026

---

## Executive Summary

This document provides a comprehensive plan for migrating 250+ Freezoner products into the Mazagawy module system with full enhancement including:
- Required document configuration per product
- Deliverable document configuration per product
- Partner required fields per service type
- Project template linkage
- Checkpoint and milestone automation
- Compliance requirements
- Pricing structure preservation

---

## Table of Contents

1. [Product Categories & Count](#product-categories--count)
2. [Enhancement Requirements](#enhancement-requirements)
3. [Product Configuration Template](#product-configuration-template)
4. [Category-Specific Configurations](#category-specific-configurations)
5. [Import Workflow](#import-workflow)
6. [Data Migration Scripts](#data-migration-scripts)
7. [Testing & Validation](#testing--validation)
8. [Rollout Plan](#rollout-plan)

---

## 1. Product Categories & Count

### 1.1 Accounting Services (46 products)
**Departments:** Accounts (19) | Operations (20) | Sales (7)

**Service Types:**
- Tax Services (CT, VAT) - 12 products
- Accounting & Bookkeeping - 6 products
- Compliance (GoAML, Customs) - 4 products
- Specialized Reports - 8 products
- Other Services - 16 products

**Price Range:** AED 0 - AED 6,000

---

### 1.2 Banking & Accounts Opening (12 products)
**Departments:** Accounts (4) | Operations (4) | Sales (4)

**Service Types:**
- Corporate Banking - 3 products
- Personal Banking - 3 products
- Digital Banking - 3 products
- Mortgage Assistance - 3 products

**Price Range:** AED 1

---

### 1.3 Business Administration Services (24 products)
**Departments:** Accounts (8) | Operations (8) | Sales (8)

**Service Types:**
- Company Amendments - 21 products
  - Activity Changes
  - Shareholder Changes
  - Management Changes
  - Name Changes
  - Structure Changes
  - Visa Quota Changes
  - Salary Amendments
- General Amendments - 3 products

**Price Range:** AED 1

---

### 1.4 Business Setup (5 products)
**Departments:** Operations (2) | Sales (3)

**Service Types:**
- 1 Year Setup - 2 products
- Multiyear Setup - 2 products
- Pre-Approval - 1 product

**Price Range:** AED 1

---

### 1.5 Company Liquidation (6 products)
**Departments:** Accounts (2) | Operations (2) | Sales (2)

**Service Types:**
- With Visa - 3 products
- Without Visa - 3 products

**Price Range:** AED 1

---

### 1.6 Company Renewal (6 products)
**Departments:** Accounts (2) | Operations (2) | Sales (2)

**Service Types:**
- 1 Year Renewal - 3 products
- Multiyear Renewal - 3 products

**Price Range:** AED 1

---

### 1.7 Value Added Services (85+ products)
**Departments:** Accounts (18) | Operations (35) | Sales (20+)

**Service Types:**
- Certificates & Letters - 9 products
- Corporate Services - 12 products
- Visa Support Services - 15 products
- Legal Services (POA, Wills) - 8 products
- Document Services (Attestation, Translation) - 10 products
- Real Estate Services - 6 products
- Insurance Services - 4 products
- Compliance Services - 8 products
- VIP Services - 6 products
- Logistics (Courier, Delivery) - 7 products

**Price Range:** AED 1 - AED 6,000

---

### 1.8 Visa Services (60+ products)
**Departments:** Accounts (14) | Operations (20+) | Sales (14)

**Service Types:**
- Employment Visa - 9 products
- Investor Visa - 9 products
- Property Visa - 6 products
- Golden Visa (10 years) - 12 products
- Retirement Visa - 3 products
- Dependent Visa - 6 products
- Special Visas (Maid, Nomad) - 6 products
- Visa Administration - 9+ products

**Price Range:** AED 1 - AED 600

---

### 1.9 Service Fees (5 products)

**Service Types:**
- Freezoner Service Fees - 3 products
- Payment Processing - 1 product
- Down Payment - 1 product

**Price Range:** AED 1 - AED 20

---

### 1.10 Miscellaneous Services (40+ products)

**Service Types:**
- Operational Costs - 10 products
- Marketing Services - 4 products
- License Services - 4 products
- Commission/Referral - 4 products
- Odoo Standard Services - 4 products
- Other - 14+ products

**Price Range:** AED 0 - AED 5,000

---

## 2. Enhancement Requirements

### 2.1 Required Documents Configuration

Each product must specify documents **required from client** before service execution:

**Document Categories:**
1. **Identity Documents**
   - Passport copy (all shareholders)
   - Emirates ID (UAE residents)
   - Visa page
   - Photographs (passport size)

2. **Proof Documents**
   - Proof of address (utility bill, bank statement)
   - Bank reference letter
   - Source of funds declaration
   - Bank statements (3-6 months)

3. **Business Documents**
   - Business plan
   - Financial statements
   - Audit reports
   - Trade license (for renewals/amendments)
   - MOA/AOA
   - Share certificates

4. **Legal Documents**
   - NOC from sponsor (if applicable)
   - Power of Attorney
   - Board resolution
   - Tenancy contract

5. **Specialized Documents**
   - Educational certificates (attested)
   - CV/Resume
   - Medical fitness certificate
   - Police clearance certificate
   - Marriage certificate (for dependents)

### 2.2 Deliverable Documents Configuration

Each product must specify documents **to be delivered to client** upon completion:

**Document Categories:**
1. **License Documents**
   - Trade license (original + copies)
   - License renewal certificate
   - License cancellation certificate
   - Amendment certificate

2. **Corporate Documents**
   - Certificate of Incorporation
   - Memorandum of Association (MOA)
   - Articles of Association (AOA)
   - Share certificates
   - Establishment card
   - Company stamp

3. **Visa Documents**
   - Entry permit
   - Emirates ID
   - Visa page (stamped passport)
   - Work permit
   - Labor card
   - Residence visa

4. **Tax Documents**
   - Tax Registration Number (TRN) certificate
   - VAT certificate
   - Corporate Tax certificate
   - Tax residency certificate
   - Filing confirmation

5. **Banking Documents**
   - Bank account opening documents
   - Signatory authorization
   - Account cards
   - Online banking credentials

6. **Compliance Documents**
   - GoAML certificate
   - Customs registration
   - AML compliance certificate
   - UBO declaration

7. **Value Added Documents**
   - Attestation certificates
   - Translation documents
   - POA documents
   - Tenancy agreement
   - PO Box documents
   - Trademark certificate

### 2.3 Partner Required Fields

**Partner fields needed before SO confirmation per service type:**

**Business Formation Services:**
- Nationality (all shareholders)
- Business structure (FZCO/FZE/LLC)
- License authority (DMCC, DAFZA, RAKEZ, etc.)
- Proposed company names (3 options)
- Business activities
- Visa eligibility requirements

**Visa Services:**
- Nationality
- Visa type required
- Dependent relationship (if applicable)
- Current visa status
- Sponsor information

**Tax Services:**
- Business legal entity
- Financial year end
- Previous tax registration status
- Accounting method

**Banking Services:**
- Business turnover
- Banking requirements
- Number of signatories
- Expected transaction volume

**Compliance Services:**
- Business activity risk level
- Source of funds
- PEP status
- Sanctions screening

### 2.4 Project Template Linkage

Each product category maps to specific project template:

| Category | Template | Service Tracking |
|----------|----------|------------------|
| Business Setup | `template_business_formation` | new_workflow |
| Company Renewal | `template_license_renewal` | new_workflow |
| Company Liquidation | `template_company_liquidation` | new_workflow |
| Business Amendment | `template_company_amendment` | new_workflow |
| Visa Services | `template_visa_processing` | new_workflow |
| Tax Services | `template_tax_compliance` | new_workflow |
| Banking Services | `template_bank_assistance` | new_workflow |
| Value Added Services | `template_value_added_services` | new_workflow |
| Accounting Services | `template_accounting_services` | new_workflow |

### 2.5 Compliance Requirements

**Products requiring compliance onboarding:**

**High Compliance:**
- All Business Formation products
- All Banking Services
- Corporate Tax services
- Company Amendment (ownership/shareholding)
- Golden Visa services

**Medium Compliance:**
- Value Added Tax services
- Accounting & Bookkeeping
- Audit services
- Property Visa services

**Low/No Compliance:**
- Service fees
- Operational costs
- Simple certificate services
- Delivery services

---

## 3. Product Configuration Template

### 3.1 Mazagawy Product Structure

```python
{
    # Basic Product Information
    'name': 'Business Formation - FZCO 1 Year',
    'default_code': 'BF-FZCO-1Y',
    'type': 'service',
    'categ_id': category_business_setup.id,
    
    # Service Configuration
    'service_tracking': 'new_workflow',  # Mazagawy enhanced tracking
    'project_template_id': template_business_formation.id,
    
    # Pricing
    'list_price': 15000.00,
    'standard_price': 8000.00,
    'pricing_tiers': {
        '1_year': 15000,
        '3_year': 40000,
        '5_year': 65000
    },
    
    # Document Configuration
    'document_required_type_ids': [
        # From client
        (4, doc_type_passport.id),
        (4, doc_type_emirates_id.id),
        (4, doc_type_proof_address.id),
        (4, doc_type_business_plan.id),
        (4, doc_type_bank_statement.id),
        (4, doc_type_cv.id),
        (4, doc_type_noc.id),
    ],
    
    'document_deliverable_type_ids': [
        # To client
        (4, doc_type_trade_license.id),
        (4, doc_type_moa.id),
        (4, doc_type_aoa.id),
        (4, doc_type_share_certificate.id),
        (4, doc_type_establishment_card.id),
        (4, doc_type_company_stamp.id),
        (4, doc_type_initial_approval.id),
    ],
    
    # Partner Required Fields
    'partner_required_fields': [
        'nationality',
        'company_type',
        'license_authority',
        'proposed_company_names',
        'business_activities',
        'visa_eligibility',
        'number_of_shareholders',
        'share_capital_amount',
    ],
    
    # Compliance Configuration
    'compliance_required': True,
    'risk_level': 'medium',
    'ubo_required': True,
    'kyc_level': 'enhanced',
    
    # Workflow Configuration
    'default_checkpoints': [
        'collect_client_documents',
        'verify_documents',
        'name_reservation_submission',
        'name_approval_received',
        'license_application_prepared',
        'license_application_submitted',
        'initial_approval_received',
        'license_issued',
        'documents_prepared_for_handover',
        'client_handover_completed',
    ],
    
    'default_milestones': [
        ('Contract Signed', 0),
        ('Documents Collected', 5),
        ('Name Approved', 10),
        ('License Submitted', 15),
        ('License Issued', 25),
        ('Handover Complete', 30),
    ],
    
    # Task Configuration
    'auto_create_tasks': True,
    'task_templates': [
        'initial_consultation',
        'document_collection',
        'name_reservation',
        'license_preparation',
        'license_submission',
        'license_collection',
        'handover_preparation',
    ],
    
    # Invoice Configuration
    'invoice_policy': 'order',  # or 'delivery' or 'milestone'
    'payment_terms': 'prepayment_50',
    'milestone_invoicing': [
        ('Contract Signed', 50),
        ('License Issued', 50),
    ],
    
    # Department Access
    'department_tags': ['sales', 'operations', 'accounts'],
}
```

---

## 4. Category-Specific Configurations

### 4.1 Business Formation Products

**Example: FZCO Formation - 1 Year**

```xml
<record id="product_business_formation_fzco_1y" model="product.template">
    <field name="name">Business Formation - FZCO 1 Year</field>
    <field name="default_code">BF-FZCO-1Y</field>
    <field name="type">service</field>
    <field name="categ_id" ref="category_business_setup"/>
    <field name="list_price">15000.00</field>
    
    <!-- Service Tracking -->
    <field name="service_tracking">new_workflow</field>
    <field name="project_template_id" ref="template_business_formation"/>
    
    <!-- Required Documents (From Client) -->
    <field name="document_required_type_ids" eval="[
        (4, ref('doc_type_passport_all_shareholders')),
        (4, ref('doc_type_emirates_id_uae_residents')),
        (4, ref('doc_type_proof_address')),
        (4, ref('doc_type_business_plan')),
        (4, ref('doc_type_bank_statement_6months')),
        (4, ref('doc_type_cv_all_shareholders')),
        (4, ref('doc_type_educational_certificates')),
        (4, ref('doc_type_noc_if_applicable')),
        (4, ref('doc_type_source_of_funds')),
    ]"/>
    
    <!-- Deliverable Documents (To Client) -->
    <field name="document_deliverable_type_ids" eval="[
        (4, ref('doc_type_trade_license_original')),
        (4, ref('doc_type_trade_license_copy')),
        (4, ref('doc_type_moa')),
        (4, ref('doc_type_aoa')),
        (4, ref('doc_type_share_certificates')),
        (4, ref('doc_type_establishment_card')),
        (4, ref('doc_type_initial_approval_certificate')),
        (4, ref('doc_type_company_stamp')),
        (4, ref('doc_type_signatory_authorization')),
    ]"/>
    
    <!-- Partner Required Fields -->
    <field name="partner_required_fields">nationality,company_type,license_authority,proposed_company_names,business_activities,visa_eligibility,number_of_shareholders,share_capital</field>
    
    <!-- Compliance -->
    <field name="compliance_required">True</field>
    <field name="ubo_tracking_required">True</field>
</record>
```

**Required Documents:**
1. Passport copies (all shareholders)
2. Emirates ID copies (UAE residents)
3. Proof of address (utility bill, bank statement)
4. Business plan (detailed)
5. Bank statements (6 months)
6. CV/Resume (all shareholders)
7. Educational certificates (attested)
8. NOC from sponsor (if applicable)
9. Source of funds declaration

**Deliverable Documents:**
1. Trade License (original)
2. Trade License (certified copies)
3. Memorandum of Association (MOA)
4. Articles of Association (AOA)
5. Share Certificates
6. Establishment Card
7. Initial Approval Certificate
8. Company Stamp
9. Signatory Authorization

**Partner Required Fields:**
- Nationality
- Company type preference (FZCO/FZE)
- License authority (DMCC, DAFZA, RAKEZ, etc.)
- Proposed company names (3 options)
- Business activities (up to 3)
- Visa eligibility requirements
- Number of shareholders
- Share capital amount

**Checkpoints:**
1. Client consultation completed
2. Service agreement signed
3. All required documents collected
4. Documents verified and complete
5. Name reservation submitted
6. Name approved by authority
7. License application prepared
8. License fees calculated
9. Client approval obtained
10. License application submitted
11. Initial approval received
12. License issued by authority
13. Documents prepared for handover
14. Client handover appointment scheduled
15. Documents handed over to client
16. Client sign-off obtained

---

### 4.2 Visa Services Products

**Example: Employment Visa - 2 Years**

**Required Documents:**
1. Passport copy (employee)
2. Passport size photographs (2)
3. Emirates ID copy (if renewal)
4. Educational certificates (attested)
5. CV/Resume
6. Employment contract
7. Medical fitness certificate
8. Company trade license copy
9. Establishment card copy

**Deliverable Documents:**
1. Entry permit
2. Emirates ID (original)
3. Visa page (stamped in passport)
4. Work permit
5. Labor card
6. Residence visa sticker

**Partner Required Fields:**
- Employee nationality
- Visa type (Employment, Investor, etc.)
- Designation/job title
- Salary details
- Qualification level
- Previous visa status
- Sponsor company details

**Checkpoints:**
1. Visa application form completed
2. Medical test scheduled
3. Medical test passed
4. Entry permit applied
5. Entry permit received
6. Visa stamping appointment scheduled
7. Visa stamped
8. Emirates ID application submitted
9. Emirates ID collected
10. Labor card issued

---

### 4.3 Tax Services Products

**Example: VAT Registration**

**Required Documents:**
1. Trade license copy
2. MOA/AOA
3. Passport copies (all shareholders/partners)
4. Emirates ID copies
5. Bank statements (6 months)
6. Tenancy contract
7. EJARI certificate
8. Utility bill (DEWA/FEWA)
9. Business activity description

**Deliverable Documents:**
1. TRN Certificate
2. VAT Registration Certificate
3. FTA Portal Login Credentials
4. VAT Filing Schedule
5. Compliance Guidelines

**Partner Required Fields:**
- Legal entity type
- Expected annual turnover
- Main business activity
- Voluntary or mandatory registration
- Financial year end date
- Accounting method (cash/accrual)

**Checkpoints:**
1. Registration documents collected
2. Documents verified
3. Application prepared
4. Client review and approval
5. Application submitted to FTA
6. TRN issued
7. Portal credentials created
8. Client training completed

---

### 4.4 Banking Services Products

**Example: Corporate Banking Assistance**

**Required Documents:**
1. Trade license (original + copy)
2. MOA/AOA
3. Share certificates
4. Passport copies (all signatories)
5. Emirates ID copies (all signatories)
6. Proof of address (all signatories)
7. Business plan
8. Bank statements (6 months - if existing business)
9. Source of funds declaration
10. CV of all signatories
11. Company profile

**Deliverable Documents:**
1. Bank account opening confirmation
2. Account number details
3. Debit/credit cards
4. Online banking credentials
5. Checkbook
6. Signatory authorization cards

**Partner Required Fields:**
- Expected monthly turnover
- Number of signatories required
- Banking services needed (current, savings, trade finance)
- Expected transaction volume
- Countries of operation
- Industry sector

**Checkpoints:**
1. Bank selection consultation
2. Required documents collected
3. Bank appointment scheduled
4. Bank application submitted
5. Due diligence completed
6. Account approved
7. Account activated
8. Banking kit delivered

---

### 4.5 Company Amendment Products

**Example: Add/Remove Activity**

**Required Documents:**
1. Current trade license
2. Amendment application form
3. Board resolution
4. Amended MOA (if applicable)
5. Passport copies (authorized signatories)
6. Emirates ID copies
7. Payment receipt

**Deliverable Documents:**
1. Amended trade license
2. Amendment certificate
3. Updated establishment card (if applicable)

**Partner Required Fields:**
- Current business activities
- Activities to add/remove
- Reason for amendment
- Effective date required

**Checkpoints:**
1. Amendment request received
2. Documents collected
3. Application prepared
4. Authority approval obtained
5. Fees paid
6. Amended license issued
7. Updated documents delivered

---

### 4.6 Accounting Services Products

**Example: Accounting & Bookkeeping (Monthly)**

**Required Documents:**
1. Previous financial statements
2. Bank statements
3. Purchase invoices
4. Sales invoices
5. Expense receipts
6. Salary details
7. VAT returns (if registered)

**Deliverable Documents:**
1. Monthly financial statements
2. Profit & loss statement
3. Balance sheet
4. Cash flow statement
5. Management reports
6. Reconciliation reports

**Partner Required Fields:**
- Accounting software used
- Financial year end
- Number of transactions/month
- VAT registered (yes/no)
- Previous accountant (if any)

**Checkpoints:**
1. Previous records reviewed
2. Chart of accounts set up
3. Opening balances entered
4. Monthly transactions recorded
5. Bank reconciliation completed
6. Financial statements prepared
7. Reports delivered to client

---

### 4.7 Value Added Services Products

**Example: POA Drafting (Remote & Physical)**

**Required Documents:**
1. Passport copy (principal)
2. Passport copy (attorney)
3. Emirates ID copies
4. Specific authority requirements
5. Company documents (if corporate POA)

**Deliverable Documents:**
1. Drafted POA document
2. Attested POA (if required)
3. Translated POA (if required)

**Partner Required Fields:**
- POA type (general/specific)
- Scope of authority
- Duration of POA
- Attestation required (yes/no)

**Checkpoints:**
1. POA requirements discussed
2. Draft prepared
3. Client review
4. Final POA prepared
5. Attestation (if required)
6. POA delivered

---

## 5. Import Workflow

### 5.1 Pre-Import Preparation

**Step 1: Create Document Types**
```python
# Create all required document types first
document_types = [
    # Identity Documents
    ('Passport Copy', 'identity', 'required'),
    ('Emirates ID', 'identity', 'required'),
    ('Visa Page', 'identity', 'optional'),
    ('Photographs', 'identity', 'required'),
    
    # Proof Documents
    ('Proof of Address', 'proof', 'required'),
    ('Bank Statements', 'proof', 'required'),
    ('Source of Funds', 'proof', 'required'),
    
    # Business Documents
    ('Business Plan', 'business', 'required'),
    ('Trade License', 'business', 'required'),
    ('MOA', 'business', 'deliverable'),
    ('AOA', 'business', 'deliverable'),
    
    # ... (continue for all document types)
]
```

**Step 2: Create Project Templates**
```python
# Create project templates with tasks
templates = [
    'Business Formation',
    'License Renewal',
    'Company Liquidation',
    'Company Amendment',
    'Visa Processing',
    'Tax Compliance',
    'Bank Assistance',
    'Value Added Services',
    'Accounting Services',
]
```

**Step 3: Create Product Categories**
```python
categories = {
    'Business Setup': 'business_setup',
    'Company Renewal': 'company_renewal',
    'Company Liquidation': 'company_liquidation',
    'Business Administration': 'business_admin',
    'Visa Services': 'visa_services',
    'Tax Services': 'tax_services',
    'Banking Services': 'banking_services',
    'Value Added Services': 'value_added',
    'Accounting Services': 'accounting',
}
```

### 5.2 Product Import Script

**Python Migration Script:**

```python
# product_migration.py
import psycopg2
from odoo import api, fields, models, SUPERUSER_ID

class ProductMigration:
    def __init__(self, source_db, target_db):
        self.source_conn = psycopg2.connect(source_db)
        self.target_env = api.Environment(target_db, SUPERUSER_ID, {})
    
    def migrate_products(self):
        """Migrate products from Freezoner to Mazagawy"""
        
        # Step 1: Extract products from source
        products = self.extract_freezoner_products()
        
        # Step 2: Transform to Mazagawy structure
        transformed = self.transform_products(products)
        
        # Step 3: Load into Mazagawy
        self.load_products(transformed)
    
    def extract_freezoner_products(self):
        """Extract products from Freezoner database"""
        cursor = self.source_conn.cursor()
        
        query = """
            SELECT 
                pt.id,
                pt.name,
                pt.default_code,
                pc.name as category,
                pt.type,
                pt.service_tracking,
                pt.list_price,
                pt.description_sale
            FROM product_template pt
            LEFT JOIN product_category pc ON pt.categ_id = pc.id
            WHERE pt.type = 'service'
            AND pt.active = true
            AND pt.service_tracking = 'new_workflow'
            ORDER BY pc.name, pt.name
        """
        
        cursor.execute(query)
        return cursor.fetchall()
    
    def transform_products(self, products):
        """Transform products with Mazagawy enhancements"""
        transformed = []
        
        for product in products:
            # Determine category
            category = self.map_category(product['category'])
            
            # Get document requirements
            required_docs = self.get_required_documents(category)
            deliverable_docs = self.get_deliverable_documents(category)
            
            # Get partner fields
            partner_fields = self.get_partner_fields(category)
            
            # Get project template
            template = self.get_project_template(category)
            
            # Build enhanced product
            enhanced = {
                'name': self.clean_product_name(product['name']),
                'default_code': product['default_code'] or self.generate_code(product['name']),
                'categ_id': category.id,
                'type': 'service',
                'service_tracking': 'new_workflow',
                'project_template_id': template.id,
                'list_price': product['list_price'],
                'document_required_type_ids': [(6, 0, required_docs)],
                'document_deliverable_type_ids': [(6, 0, deliverable_docs)],
                'partner_required_fields': ','.join(partner_fields),
                'compliance_required': self.is_compliance_required(category),
                'description_sale': product['description_sale'],
            }
            
            transformed.append(enhanced)
        
        return transformed
    
    def load_products(self, products):
        """Load products into Mazagawy"""
        ProductTemplate = self.target_env['product.template']
        
        for product_data in products:
            try:
                product = ProductTemplate.create(product_data)
                print(f"✓ Created: {product.name}")
            except Exception as e:
                print(f"✗ Failed: {product_data['name']} - {str(e)}")
    
    def clean_product_name(self, name):
        """Remove department prefixes [A], [O], [S]"""
        import re
        # Remove [A], [O], [S] prefixes
        clean = re.sub(r'^\[.\]\s*', '', name)
        return clean.strip()
    
    def map_category(self, freezoner_category):
        """Map Freezoner category to Mazagawy category"""
        mapping = {
            'Accounting Services - Accounts': 'accounting',
            'Accounting Services - Operations': 'accounting',
            'Accounting Services - Sales': 'accounting',
            'Banking & Accounts Opening - Accounts': 'banking',
            'Banking & Accounts Opening - Operations': 'banking',
            'Banking & Accounts Opening - Sales': 'banking',
            'Business Administration Services - Accounts': 'business_admin',
            'Business Administration Services - Operations': 'business_admin',
            'Business Administration Services - Sales': 'business_admin',
            'Business Setup - Operations': 'business_setup',
            'Business Setup - Sales': 'business_setup',
            'Company Liquidation - Accounts': 'company_liquidation',
            'Company Liquidation - Operations': 'company_liquidation',
            'Company Liquidation - Sales': 'company_liquidation',
            'Company Renewal - Accounts': 'company_renewal',
            'Company Renewal - Operations': 'company_renewal',
            'Company Renewal - Sales': 'company_renewal',
            'Value Added Services - Accounts': 'value_added',
            'Value Added Services - Operations': 'value_added',
            'Value Added Services - Sales': 'value_added',
            'Visa Services - Accounts': 'visa_services',
            'Visa Services - Operations': 'visa_services',
            'Visa Services - Sales': 'visa_services',
        }
        
        category_code = mapping.get(freezoner_category, 'other')
        return self.target_env.ref(f'mazagawy.category_{category_code}')
    
    def get_required_documents(self, category):
        """Get required document IDs for category"""
        # Map category to required documents
        doc_mapping = {
            'business_setup': [
                'doc_type_passport',
                'doc_type_emirates_id',
                'doc_type_proof_address',
                'doc_type_business_plan',
                'doc_type_bank_statement',
                'doc_type_cv',
                'doc_type_educational_cert',
                'doc_type_noc',
                'doc_type_source_funds',
            ],
            'visa_services': [
                'doc_type_passport',
                'doc_type_photographs',
                'doc_type_educational_cert',
                'doc_type_cv',
                'doc_type_medical_fitness',
                'doc_type_employment_contract',
            ],
            # ... add mappings for all categories
        }
        
        doc_refs = doc_mapping.get(category.code, [])
        return [self.target_env.ref(f'mazagawy.{ref}').id for ref in doc_refs]
    
    def get_deliverable_documents(self, category):
        """Get deliverable document IDs for category"""
        # Similar to get_required_documents but for deliverables
        pass
    
    def get_partner_fields(self, category):
        """Get required partner fields for category"""
        field_mapping = {
            'business_setup': [
                'nationality',
                'company_type',
                'license_authority',
                'proposed_company_names',
                'business_activities',
                'visa_eligibility',
            ],
            'visa_services': [
                'nationality',
                'visa_type',
                'qualification_level',
                'job_title',
            ],
            # ... add mappings for all categories
        }
        
        return field_mapping.get(category.code, [])
    
    def get_project_template(self, category):
        """Get project template for category"""
        template_mapping = {
            'business_setup': 'template_business_formation',
            'company_renewal': 'template_license_renewal',
            'company_liquidation': 'template_company_liquidation',
            'business_admin': 'template_company_amendment',
            'visa_services': 'template_visa_processing',
            'accounting': 'template_accounting_services',
            'banking': 'template_bank_assistance',
            'value_added': 'template_value_added_services',
        }
        
        template_ref = template_mapping.get(category.code, 'template_default')
        return self.target_env.ref(f'mazagawy.{template_ref}')
    
    def is_compliance_required(self, category):
        """Determine if compliance is required for category"""
        high_compliance = ['business_setup', 'banking', 'accounting']
        return category.code in high_compliance
    
    def generate_code(self, name):
        """Generate product code from name"""
        # Take first letter of each word
        words = name.split()
        code = ''.join([w[0].upper() for w in words[:3]])
        return code

# Usage
if __name__ == '__main__':
    source_db = "host=localhost port=5433 dbname=odoo19_restore user=postgres"
    target_db = odoorpc.ODOO('localhost', port=8069)
    target_db.login('mazagawy_db', 'admin', 'admin')
    
    migrator = ProductMigration(source_db, target_db)
    migrator.migrate_products()
```

### 5.3 Deduplication Strategy

**Problem:** Freezoner has 3 products per service ([A], [O], [S])

**Solution:** Consolidate to single product with department tagging

```python
def deduplicate_products(products):
    """Consolidate department-specific products into one"""
    
    deduplicated = {}
    
    for product in products:
        # Remove department prefix
        clean_name = re.sub(r'^\[.\]\s*', '', product['name'])
        
        # Use clean name as key
        if clean_name not in deduplicated:
            deduplicated[clean_name] = {
                **product,
                'name': clean_name,
                'departments': []
            }
        
        # Add department tag
        if '[A]' in product['name']:
            deduplicated[clean_name]['departments'].append('accounts')
        elif '[O]' in product['name']:
            deduplicated[clean_name]['departments'].append('operations')
        elif '[S]' in product['name']:
            deduplicated[clean_name]['departments'].append('sales')
    
    return list(deduplicated.values())
```

---

## 6. Data Migration Scripts

### 6.1 Document Type Creation Script

```python
# create_document_types.py

document_types = [
    # Identity Documents
    {
        'name': 'Passport Copy',
        'code': 'PASSPORT',
        'category': 'identity',
        'mandatory': True,
        'expiry_tracking': True,
        'attestation_required': False,
    },
    {
        'name': 'Emirates ID',
        'code': 'EID',
        'category': 'identity',
        'mandatory': True,
        'expiry_tracking': True,
        'attestation_required': False,
    },
    # ... continue for all document types
]

def create_document_types(env):
    DocumentType = env['documents.type']
    
    for doc_data in document_types:
        existing = DocumentType.search([('code', '=', doc_data['code'])])
        if not existing:
            DocumentType.create(doc_data)
            print(f"✓ Created document type: {doc_data['name']}")
        else:
            print(f"⊗ Skipped (exists): {doc_data['name']}")
```

### 6.2 Project Template Creation Script

```python
# create_project_templates.py

templates = [
    {
        'name': 'Business Formation - FZCO/FZE',
        'code': 'BF_FZCO',
        'is_template': True,
        'task_templates': [
            {'name': 'Initial Consultation', 'sequence': 1},
            {'name': 'Document Collection', 'sequence': 2},
            {'name': 'Name Reservation', 'sequence': 3},
            {'name': 'License Application', 'sequence': 4},
            {'name': 'License Collection', 'sequence': 5},
            {'name': 'Handover Preparation', 'sequence': 6},
        ],
        'milestones': [
            {'name': 'Contract Signed', 'days': 0},
            {'name': 'Documents Collected', 'days': 5},
            {'name': 'Name Approved', 'days': 10},
            {'name': 'License Issued', 'days': 25},
            {'name': 'Handover Complete', 'days': 30},
        ]
    },
    # ... continue for all templates
]

def create_project_templates(env):
    Project = env['project.project']
    Task = env['project.task']
    Milestone = env['project.milestone']
    
    for template_data in templates:
        # Create project template
        project = Project.create({
            'name': template_data['name'],
            'is_template': True,
        })
        
        # Create task templates
        for task_data in template_data['task_templates']:
            Task.create({
                **task_data,
                'project_id': project.id,
            })
        
        # Create milestones
        for milestone_data in template_data['milestones']:
            Milestone.create({
                **milestone_data,
                'project_id': project.id,
            })
        
        print(f"✓ Created template: {template_data['name']}")
```

---

## 7. Testing & Validation

### 7.1 Import Validation Checklist

**Pre-Import Validation:**
- [ ] All document types created
- [ ] All project templates created
- [ ] All product categories created
- [ ] Compliance workflows configured
- [ ] Partner fields defined

**Post-Import Validation:**
- [ ] Product count matches (after deduplication)
- [ ] All products have project templates
- [ ] All products have required documents
- [ ] All products have deliverable documents
- [ ] All products have partner required fields
- [ ] Pricing preserved correctly
- [ ] Product codes unique
- [ ] Categories assigned correctly

### 7.2 Test Scenarios

**Test Case 1: Business Formation Product**
1. Create SO with Business Formation product
2. Verify required documents auto-created
3. Verify partner required fields wizard appears
4. Confirm SO creates project from template
5. Verify deliverable documents created
6. Complete workflow end-to-end
7. Verify handover process

**Test Case 2: Visa Services Product**
1. Create SO with Employment Visa product
2. Verify visa-specific documents requested
3. Verify partner fields (nationality, etc.)
4. Confirm project created with visa workflow
5. Complete visa processing
6. Verify deliverables

**Test Case 3: Multi-Product SO**
1. Add multiple products to SO
2. Verify consolidation logic
3. Verify document deduplication
4. Verify project handling

---

## 8. Rollout Plan

### Phase 1: Foundation (Week 1-2)
- [ ] Create all document types (100+)
- [ ] Create project templates (9 core templates)
- [ ] Create product categories
- [ ] Configure compliance workflows

### Phase 2: Data Migration (Week 3)
- [ ] Run product extraction from Freezoner
- [ ] Transform products with enhancements
- [ ] Deduplicate products
- [ ] Load products into Mazagawy

### Phase 3: Configuration (Week 4)
- [ ] Assign documents to products
- [ ] Configure partner required fields
- [ ] Set up pricing tiers
- [ ] Configure compliance rules

### Phase 4: Testing (Week 5)
- [ ] Unit testing (per product category)
- [ ] Integration testing (workflows)
- [ ] User acceptance testing
- [ ] Performance testing

### Phase 5: Training (Week 6)
- [ ] Train sales team on new products
- [ ] Train operations on workflows
- [ ] Train accounts on compliance
- [ ] Create user documentation

### Phase 6: Go-Live (Week 7)
- [ ] Soft launch (limited products)
- [ ] Monitor and fix issues
- [ ] Full rollout
- [ ] Post-launch support

---

## Summary

This migration plan transforms 250+ Freezoner products into 80-90 enhanced Mazagawy products by:

1. **Deduplicating** department-specific variants ([A], [O], [S])
2. **Enriching** with required/deliverable documents
3. **Enhancing** with partner required fields
4. **Linking** to project templates
5. **Enabling** compliance workflows
6. **Automating** document and task creation

**Expected Outcomes:**
- ✅ Reduced product count (250+ → 80-90)
- ✅ Enhanced automation (document auto-creation)
- ✅ Better compliance tracking (UBO, KYC)
- ✅ Improved user experience (guided workflows)
- ✅ Consistent service delivery (templates)

**Timeline:** 7 weeks from start to full rollout

---

**Document Version:** 1.0  
**Last Updated:** January 19, 2026  
**Status:** Ready for Implementation
