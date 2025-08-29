# Dynamic Quotation System - Use Case Examples

## 🏗️ **Construction Project Management**

### **Scenario: Building Construction Project**

**Project**: 3-story office building construction
**Client**: ABC Corporation
**Workflow**: Multi-phase construction with milestone-based billing

#### **Phase 1: Foundation & Structure**
```python
# Milestone 1: Foundation Complete
milestone_foundation = {
    'name': 'Foundation Complete',
    'create_quotation_on_reach': True,
    'quotation_template_id': foundation_template.id,
    'quotation_notes': 'Foundation work completed - ready for structural work'
}

# Checkpoints for Foundation
checkpoints = [
    {
        'name': 'Site Preparation',
        'create_quotation_on_reach': False,  # No billing for prep work
    },
    {
        'name': 'Excavation Complete',
        'create_quotation_on_reach': False,
    },
    {
        'name': 'Foundation Poured',
        'create_quotation_on_reach': True,
        'quotation_template_id': foundation_pour_template.id,
        'quotation_notes': 'Concrete foundation poured and cured'
    },
    {
        'name': 'Foundation Inspection Passed',
        'create_quotation_on_reach': True,
        'quotation_template_id': inspection_template.id,
        'quotation_notes': 'Foundation inspection passed by city inspector'
    }
]
```

**Result**: When all foundation checkpoints are reached, a quotation for $150,000 is automatically created.

#### **Phase 2: Structural Framework**
```python
# Milestone 2: Structural Framework Complete
milestone_structure = {
    'name': 'Structural Framework Complete',
    'create_quotation_on_reach': True,
    'quotation_template_id': structural_template.id,
    'quotation_notes': 'Steel framework erected and secured'
}

# Checkpoints for Structure
checkpoints = [
    {
        'name': 'Steel Delivery',
        'create_quotation_on_reach': True,
        'quotation_template_id': materials_template.id,
        'quotation_notes': 'Steel materials delivered and inspected'
    },
    {
        'name': 'Steel Erection',
        'create_quotation_on_reach': False,
    },
    {
        'name': 'Structural Welding',
        'create_quotation_on_reach': True,
        'quotation_template_id': welding_template.id,
        'quotation_notes': 'All structural welding completed and inspected'
    },
    {
        'name': 'Structural Inspection',
        'create_quotation_on_reach': True,
        'quotation_template_id': final_inspection_template.id,
        'quotation_notes': 'Structural inspection passed by engineer'
    }
]
```

**Result**: Multiple quotations created during the process:
- Materials quotation: $75,000
- Welding work quotation: $45,000
- Final structural quotation: $200,000

---

## 🖥️ **Software Development Project**

### **Scenario: E-commerce Platform Development**

**Project**: Custom e-commerce platform
**Client**: Fashion Retailer XYZ
**Workflow**: Agile development with sprint-based billing

#### **Sprint 1: User Authentication**
```python
# Milestone: Authentication System Complete
milestone_auth = {
    'name': 'Authentication System Complete',
    'create_quotation_on_reach': True,
    'quotation_template_id': sprint_template.id,
    'quotation_notes': 'User registration, login, and password recovery completed'
}

# Checkpoints for Authentication
checkpoints = [
    {
        'name': 'Database Schema Design',
        'create_quotation_on_reach': True,
        'quotation_template_id': design_template.id,
        'quotation_notes': 'User database schema designed and implemented'
    },
    {
        'name': 'Registration System',
        'create_quotation_on_reach': True,
        'quotation_template_id': feature_template.id,
        'quotation_notes': 'User registration with email verification completed'
    },
    {
        'name': 'Login System',
        'create_quotation_on_reach': True,
        'quotation_template_id': feature_template.id,
        'quotation_notes': 'Secure login system with session management'
    },
    {
        'name': 'Password Recovery',
        'create_quotation_on_reach': True,
        'quotation_template_id': feature_template.id,
        'quotation_notes': 'Password reset functionality implemented'
    },
    {
        'name': 'Security Testing',
        'create_quotation_on_reach': True,
        'quotation_template_id': testing_template.id,
        'quotation_notes': 'Security testing completed - no vulnerabilities found'
    }
]
```

**Result**: Progressive billing throughout the sprint:
- Design quotation: $5,000
- Registration feature: $8,000
- Login feature: $6,000
- Password recovery: $4,000
- Security testing: $3,000
- **Total Sprint 1**: $26,000

#### **Sprint 2: Product Catalog**
```python
# Milestone: Product Catalog Complete
milestone_catalog = {
    'name': 'Product Catalog Complete',
    'create_quotation_on_reach': True,
    'quotation_template_id': sprint_template.id,
    'quotation_notes': 'Complete product management system ready'
}

# Checkpoints for Product Catalog
checkpoints = [
    {
        'name': 'Product Database Design',
        'create_quotation_on_reach': True,
        'quotation_template_id': design_template.id,
        'quotation_notes': 'Product database schema with categories and attributes'
    },
    {
        'name': 'Product Management Interface',
        'create_quotation_on_reach': True,
        'quotation_template_id': admin_template.id,
        'quotation_notes': 'Admin interface for adding/editing products'
    },
    {
        'name': 'Product Display Frontend',
        'create_quotation_on_reach': True,
        'quotation_template_id': frontend_template.id,
        'quotation_notes': 'Customer-facing product catalog with search and filters'
    },
    {
        'name': 'Image Upload System',
        'create_quotation_on_reach': True,
        'quotation_template_id': feature_template.id,
        'quotation_notes': 'Product image upload and management system'
    }
]
```

---

## 🏥 **Healthcare Facility Setup**

### **Scenario: Medical Clinic Setup**

**Project**: New medical clinic setup
**Client**: Healthcare Provider ABC
**Workflow**: Regulatory compliance with milestone billing

#### **Phase 1: Facility Preparation**
```python
# Milestone: Facility Ready for Equipment
milestone_facility = {
    'name': 'Facility Ready for Equipment',
    'create_quotation_on_reach': True,
    'quotation_template_id': facility_template.id,
    'quotation_notes': 'Facility prepared according to healthcare standards'
}

# Checkpoints for Facility
checkpoints = [
    {
        'name': 'Building Permit Obtained',
        'create_quotation_on_reach': True,
        'quotation_template_id': permit_template.id,
        'quotation_notes': 'All building permits and approvals received'
    },
    {
        'name': 'Electrical Installation',
        'create_quotation_on_reach': True,
        'quotation_template_id': electrical_template.id,
        'quotation_notes': 'Electrical system installed to medical standards'
    },
    {
        'name': 'HVAC Installation',
        'create_quotation_on_reach': True,
        'quotation_template_id': hvac_template.id,
        'quotation_notes': 'HVAC system installed with medical-grade air filtration'
    },
    {
        'name': 'Plumbing Installation',
        'create_quotation_on_reach': True,
        'quotation_template_id': plumbing_template.id,
        'quotation_notes': 'Plumbing system installed with medical waste handling'
    },
    {
        'name': 'Safety Inspection Passed',
        'create_quotation_on_reach': True,
        'quotation_template_id': inspection_template.id,
        'quotation_notes': 'All safety inspections passed by health department'
    }
]
```

#### **Phase 2: Medical Equipment Installation**
```python
# Milestone: Medical Equipment Operational
milestone_equipment = {
    'name': 'Medical Equipment Operational',
    'create_quotation_on_reach': True,
    'quotation_template_id': equipment_template.id,
    'quotation_notes': 'All medical equipment installed and operational'
}

# Checkpoints for Equipment
checkpoints = [
    {
        'name': 'X-Ray Machine Installation',
        'create_quotation_on_reach': True,
        'quotation_template_id': xray_template.id,
        'quotation_notes': 'X-Ray machine installed and calibrated'
    },
    {
        'name': 'Laboratory Equipment Setup',
        'create_quotation_on_reach': True,
        'quotation_template_id': lab_template.id,
        'quotation_notes': 'Laboratory equipment installed and tested'
    },
    {
        'name': 'Patient Monitoring Systems',
        'create_quotation_on_reach': True,
        'quotation_template_id': monitoring_template.id,
        'quotation_notes': 'Patient monitoring systems installed and operational'
    }
]
```

---

## 🚗 **Automotive Service Center**

### **Scenario: Service Center Renovation**

**Project**: Automotive service center renovation
**Client**: AutoCare Plus
**Workflow**: Service-based billing with quality checkpoints

#### **Phase 1: Workshop Setup**
```python
# Milestone: Workshop Operational
milestone_workshop = {
    'name': 'Workshop Operational',
    'create_quotation_on_reach': True,
    'quotation_template_id': workshop_template.id,
    'quotation_notes': 'Workshop fully operational and ready for business'
}

# Checkpoints for Workshop
checkpoints = [
    {
        'name': 'Lift Installation',
        'create_quotation_on_reach': True,
        'quotation_template_id': lift_template.id,
        'quotation_notes': 'Automotive lifts installed and safety tested'
    },
    {
        'name': 'Tool Installation',
        'create_quotation_on_reach': True,
        'quotation_template_id': tools_template.id,
        'quotation_notes': 'Professional automotive tools installed and organized'
    },
    {
        'name': 'Safety Equipment',
        'create_quotation_on_reach': True,
        'quotation_template_id': safety_template.id,
        'quotation_notes': 'Safety equipment installed and staff trained'
    },
    {
        'name': 'Quality Control Station',
        'create_quotation_on_reach': True,
        'quotation_template_id': qc_template.id,
        'quotation_notes': 'Quality control station set up with testing equipment'
    }
]
```

---

## 📊 **Financial Services Implementation**

### **Scenario: Banking System Integration**

**Project**: Core banking system integration
**Client**: Regional Bank XYZ
**Workflow**: Compliance-driven with regulatory checkpoints

#### **Phase 1: Core System Integration**
```python
# Milestone: Core Banking System Live
milestone_core = {
    'name': 'Core Banking System Live',
    'create_quotation_on_reach': True,
    'quotation_template_id': core_banking_template.id,
    'quotation_notes': 'Core banking system successfully integrated and operational'
}

# Checkpoints for Core System
checkpoints = [
    {
        'name': 'Data Migration Complete',
        'create_quotation_on_reach': True,
        'quotation_template_id': migration_template.id,
        'quotation_notes': 'All customer data successfully migrated to new system'
    },
    {
        'name': 'Security Audit Passed',
        'create_quotation_on_reach': True,
        'quotation_template_id': security_template.id,
        'quotation_notes': 'Security audit passed by regulatory authority'
    },
    {
        'name': 'Staff Training Complete',
        'create_quotation_on_reach': True,
        'quotation_template_id': training_template.id,
        'quotation_notes': 'All staff trained on new banking system'
    },
    {
        'name': 'Go-Live Testing',
        'create_quotation_on_reach': True,
        'quotation_template_id': testing_template.id,
        'quotation_notes': 'System go-live testing completed successfully'
    }
]
```

---

## 🎯 **How to Implement These Use Cases**

### **Step 1: Create Quotation Templates**

```python
# Example: Foundation Template
foundation_template = {
    'name': 'Foundation Work Template',
    'sale_order_template_line_ids': [
        (0, 0, {
            'name': 'Site Preparation',
            'product_id': site_prep_product.id,
            'product_uom_qty': 1.0,
            'price_unit': 25000.0
        }),
        (0, 0, {
            'name': 'Excavation',
            'product_id': excavation_product.id,
            'product_uom_qty': 1.0,
            'price_unit': 35000.0
        }),
        (0, 0, {
            'name': 'Foundation Concrete',
            'product_id': concrete_product.id,
            'product_uom_qty': 1.0,
            'price_unit': 90000.0
        })
    ]
}
```

### **Step 2: Configure Workflow Instance**

```python
# Create workflow instance
workflow = self.env['fsm.workflow.instance'].create({
    'name': 'ABC Corporation Building Project',
    'partner_id': abc_corp.id,
    'pricing_policy': 'fixed_price',
    'template_id': construction_template.id,
})
```

### **Step 3: Set Up Milestones and Checkpoints**

```python
# Create milestone with quotation trigger
milestone = self.env['project.milestone'].create({
    'name': 'Foundation Complete',
    'project_id': workflow.project_id.id,
    'create_quotation_on_reach': True,
    'quotation_template_id': foundation_template.id,
    'quotation_notes': 'Foundation work completed - ready for structural work'
})

# Create checkpoints
for checkpoint_data in foundation_checkpoints:
    self.env['project.task.checkpoint'].create({
        'name': checkpoint_data['name'],
        'milestone_id': milestone.id,
        'create_quotation_on_reach': checkpoint_data.get('create_quotation_on_reach', False),
        'quotation_template_id': checkpoint_data.get('quotation_template_id', False),
        'quotation_notes': checkpoint_data.get('quotation_notes', ''),
    })
```

### **Step 4: Monitor and Manage**

```python
# Check workflow quotations
quotations = self.env['sale.order'].search([
    ('workflow_instance_id', '=', workflow.id)
])

# Filter by trigger type
milestone_quotations = quotations.filtered(lambda q: q.workflow_trigger_type == 'milestone')
checkpoint_quotations = quotations.filtered(lambda q: q.workflow_trigger_type == 'checkpoint')
```

---

## 💡 **Best Practices for Each Industry**

### **Construction**
- ✅ Use milestone triggers for major phases
- ✅ Create checkpoints for material deliveries
- ✅ Include inspection-based quotations
- ✅ Link quotations to regulatory approvals

### **Software Development**
- ✅ Use sprint-based milestones
- ✅ Create feature-based checkpoints
- ✅ Include testing and deployment quotations
- ✅ Link quotations to user acceptance

### **Healthcare**
- ✅ Use compliance-based milestones
- ✅ Create equipment installation checkpoints
- ✅ Include regulatory inspection quotations
- ✅ Link quotations to safety certifications

### **Automotive**
- ✅ Use service-based milestones
- ✅ Create equipment installation checkpoints
- ✅ Include quality control quotations
- ✅ Link quotations to safety testing

### **Financial Services**
- ✅ Use regulatory milestone triggers
- ✅ Create compliance checkpoints
- ✅ Include audit-based quotations
- ✅ Link quotations to regulatory approvals

---

## 📈 **Expected Outcomes**

### **For Project Managers:**
- **Better Cash Flow**: Progressive billing throughout the project
- **Reduced Administrative Work**: Automatic quotation creation
- **Improved Tracking**: Clear link between work and billing
- **Enhanced Client Communication**: Transparent billing process

### **For Clients:**
- **Transparency**: See exactly what triggers each quotation
- **Predictability**: Know when to expect billing
- **Quality Assurance**: Billing tied to completed work
- **Better Planning**: Understand project progress through billing

### **For Teams:**
- **Motivation**: Clear milestones with financial recognition
- **Quality Focus**: Billing tied to quality checkpoints
- **Efficiency**: Automated processes reduce manual work
- **Accountability**: Clear responsibility for milestone completion

---

This dynamic quotation system transforms how you manage project billing, making it more transparent, efficient, and aligned with actual project progress.
