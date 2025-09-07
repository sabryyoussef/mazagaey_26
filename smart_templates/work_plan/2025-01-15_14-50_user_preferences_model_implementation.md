# User Preferences Model Implementation Plan

**Date**: 2025-01-15 14:50  
**Task**: Implement User Preferences Model for Smart Templates  
**Status**: PLANNING

## Development Task Breakdown

### **Objective**
Create the foundation for smart template behavior by implementing user preferences system that allows users to configure how templates behave and suggest related templates.

### **Scope**
- Create `smart.template.user.preferences` model
- Add core preference fields
- Create preferences form view
- Integrate with user settings
- Set up default preferences

## Implementation Steps with Time Estimates

### **Step 1: Create User Preferences Model (30 minutes)**
**File**: `models/preferences/user_preferences.py`

```python
# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SmartTemplateUserPreferences(models.Model):
    _name = 'smart.template.user.preferences'
    _description = 'Smart Template User Preferences'
    _rec_name = 'user_id'
    
    # Core fields
    user_id = fields.Many2one(
        'res.users', 
        string='User', 
        required=True, 
        ondelete='cascade',
        default=lambda self: self.env.user
    )
    
    # Suggestion behavior preferences
    suggestion_level = fields.Selection([
        ('passive', 'Passive - Show options only'),
        ('active', 'Active - Suggest and recommend'),
        ('smart', 'Smart - Auto-link based on patterns')
    ], string='Suggestion Level', default='active', required=True,
       help='How aggressive should template suggestions be?')
    
    trigger_behavior = fields.Selection([
        ('manual', 'Manual - User must select'),
        ('auto', 'Auto - Apply based on context'),
        ('hybrid', 'Hybrid - Suggest with confirmation')
    ], string='Trigger Behavior', default='hybrid', required=True,
       help='How should templates be applied?')
    
    preferred_start_template = fields.Selection([
        ('project', 'Project Template'),
        ('workflow', 'Workflow Template')
    ], string='Preferred Start Template', default='project', required=True,
       help='Which template type should be the default starting point?')
    
    # Advanced preferences
    enable_learning = fields.Boolean(
        string='Enable Learning', 
        default=True,
        help='Allow system to learn from your usage patterns'
    )
    
    show_compatibility_warnings = fields.Boolean(
        string='Show Compatibility Warnings', 
        default=True,
        help='Show warnings when templates may not be compatible'
    )
    
    auto_save_preferences = fields.Boolean(
        string='Auto-save Preferences', 
        default=True,
        help='Automatically save preference changes'
    )
    
    # Computed fields
    is_default = fields.Boolean(
        string='Is Default', 
        compute='_compute_is_default',
        store=True
    )
    
    @api.depends('user_id')
    def _compute_is_default(self):
        for record in self:
            record.is_default = record.user_id == self.env.user
    
    # Constraints
    _sql_constraints = [
        ('unique_user_preferences', 
         'UNIQUE(user_id)', 
         'Each user can only have one set of preferences!')
    ]
    
    # Methods
    @api.model
    def get_user_preferences(self, user_id=None):
        """Get preferences for a specific user or current user"""
        if not user_id:
            user_id = self.env.user.id
        
        preferences = self.search([('user_id', '=', user_id)], limit=1)
        if not preferences:
            # Create default preferences if none exist
            preferences = self.create({
                'user_id': user_id,
                'suggestion_level': 'active',
                'trigger_behavior': 'hybrid',
                'preferred_start_template': 'project',
            })
        
        return preferences
    
    def apply_preferences(self, context=None):
        """Apply user preferences to a given context"""
        if not context:
            context = {}
        
        return {
            'suggestion_level': self.suggestion_level,
            'trigger_behavior': self.trigger_behavior,
            'preferred_start_template': self.preferred_start_template,
            'enable_learning': self.enable_learning,
            'show_compatibility_warnings': self.show_compatibility_warnings,
        }
```

### **Step 2: Update Model Imports (5 minutes)**
**File**: `models/preferences/__init__.py`

```python
from . import user_preferences
```

**File**: `models/__init__.py`

```python
from . import preferences
```

### **Step 3: Create Preferences Form View (20 minutes)**
**File**: `views/preferences/user_preferences_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- User Preferences Form View -->
    <record id="view_smart_template_user_preferences_form" model="ir.ui.view">
        <field name="name">smart.template.user.preferences.form</field>
        <field name="model">smart.template.user.preferences</field>
        <field name="arch" type="xml">
            <form string="Smart Template Preferences">
                <sheet>
                    <div class="oe_title">
                        <h1>
                            <field name="user_id" readonly="1"/>
                        </h1>
                    </div>
                    
                    <group>
                        <group string="Suggestion Behavior">
                            <field name="suggestion_level" widget="radio"/>
                            <field name="trigger_behavior" widget="radio"/>
                            <field name="preferred_start_template" widget="radio"/>
                        </group>
                        <group string="Advanced Options">
                            <field name="enable_learning"/>
                            <field name="show_compatibility_warnings"/>
                            <field name="auto_save_preferences"/>
                        </group>
                    </group>
                    
                    <group string="Information">
                        <field name="is_default" readonly="1"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>
    
    <!-- User Preferences List View -->
    <record id="view_smart_template_user_preferences_list" model="ir.ui.view">
        <field name="name">smart.template.user.preferences.list</field>
        <field name="model">smart.template.user.preferences</field>
        <field name="arch" type="xml">
            <list string="Smart Template Preferences">
                <field name="user_id"/>
                <field name="suggestion_level"/>
                <field name="trigger_behavior"/>
                <field name="preferred_start_template"/>
                <field name="enable_learning"/>
                <field name="is_default"/>
            </list>
        </field>
    </record>
    
    <!-- User Preferences Search View -->
    <record id="view_smart_template_user_preferences_search" model="ir.ui.view">
        <field name="name">smart.template.user.preferences.search</field>
        <field name="model">smart.template.user.preferences</field>
        <field name="arch" type="xml">
            <search string="Smart Template Preferences">
                <field name="user_id"/>
                <field name="suggestion_level"/>
                <field name="trigger_behavior"/>
                <filter string="Active Learning" name="learning_enabled" 
                        domain="[('enable_learning', '=', True)]"/>
                <filter string="Default User" name="default_user" 
                        domain="[('is_default', '=', True)]"/>
                <group expand="0" string="Group By">
                    <filter string="Suggestion Level" name="group_suggestion_level" 
                            context="{'group_by': 'suggestion_level'}"/>
                    <filter string="Trigger Behavior" name="group_trigger_behavior" 
                            context="{'group_by': 'trigger_behavior'}"/>
                </group>
            </search>
        </field>
    </record>
    
    <!-- User Preferences Actions -->
    <record id="action_smart_template_user_preferences" model="ir.actions.act_window">
        <field name="name">Smart Template Preferences</field>
        <field name="res_model">smart.template.user.preferences</field>
        <field name="view_mode">list,form</field>
        <field name="search_view_id" ref="view_smart_template_user_preferences_search"/>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                Create your first Smart Template Preferences!
            </p>
            <p>
                Configure how smart templates should behave for you.
            </p>
        </field>
    </record>
</odoo>
```

### **Step 4: Integrate with User Settings (15 minutes)**
**File**: `views/preferences/user_preferences_views.xml` (add to existing file)

```xml
    <!-- Add to User Form View -->
    <record id="res_users_view_form_inherit_smart_templates" model="ir.ui.view">
        <field name="name">res.users.view.form.inherit.smart.templates</field>
        <field name="model">res.users</field>
        <field name="inherit_id" ref="base.view_users_form"/>
        <field name="arch" type="xml">
            <notebook position="inside">
                <page string="Smart Templates" name="smart_templates">
                    <field name="smart_template_preferences_ids" readonly="1">
                        <list>
                            <field name="suggestion_level"/>
                            <field name="trigger_behavior"/>
                            <field name="preferred_start_template"/>
                            <field name="enable_learning"/>
                        </list>
                    </field>
                </page>
            </notebook>
        </field>
    </record>
```

### **Step 5: Extend User Model (10 minutes)**
**File**: `models/preferences/user_preferences.py` (add to existing file)

```python
# Add to the end of the file

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    smart_template_preferences_ids = fields.One2many(
        'smart.template.user.preferences',
        'user_id',
        string='Smart Template Preferences'
    )
    
    def get_smart_template_preferences(self):
        """Get smart template preferences for this user"""
        return self.env['smart.template.user.preferences'].get_user_preferences(self.id)
```

### **Step 6: Update Manifest File (5 minutes)**
**File**: `__manifest__.py` (add to data section)

```python
"data": [
    # ... existing data files ...
    "views/preferences/user_preferences_views.xml",
    # ... rest of data files ...
],
```

## Code Structure and Architecture Decisions

### **Model Design Decisions**
1. **Separate Model**: User preferences are in their own model for better organization
2. **One2Many Relationship**: Users can have multiple preference sets (future extensibility)
3. **Default Creation**: Automatically create preferences if none exist
4. **Computed Fields**: `is_default` field for easy identification
5. **Constraints**: Ensure one preference set per user

### **Field Design Decisions**
1. **Selection Fields**: Use predefined options for consistency
2. **Boolean Fields**: Simple on/off toggles for advanced features
3. **Help Text**: Provide clear explanations for each field
4. **Default Values**: Sensible defaults for new users

### **View Design Decisions**
1. **Form View**: Clean, organized layout with logical grouping
2. **List View**: Show key information for quick overview
3. **Search View**: Filter and group by important criteria
4. **User Integration**: Add tab to user form for easy access

## Testing Strategy

### **Unit Tests**
1. Test model creation and validation
2. Test constraint enforcement
3. Test computed field calculations
4. Test preference application methods

### **Integration Tests**
1. Test user model inheritance
2. Test view rendering
3. Test user settings integration
4. Test default preference creation

### **User Acceptance Tests**
1. Test preference configuration workflow
2. Test preference persistence
3. Test user interface usability
4. Test help text clarity

## Progress Tracking and Milestones

### **Milestone 1: Model Creation (30 minutes)**
- [ ] Create user_preferences.py model
- [ ] Add all required fields
- [ ] Add constraints and methods
- [ ] Test model functionality

### **Milestone 2: Views Creation (20 minutes)**
- [ ] Create form view
- [ ] Create list view
- [ ] Create search view
- [ ] Create actions

### **Milestone 3: User Integration (15 minutes)**
- [ ] Extend user model
- [ ] Add user form integration
- [ ] Test user settings access

### **Milestone 4: Testing & Validation (15 minutes)**
- [ ] Test all functionality
- [ ] Validate user experience
- [ ] Check for errors
- [ ] Update documentation

## Next Steps and Dependencies

### **Immediate Next Steps**
1. **Create Project Template Model** - Build on user preferences foundation
2. **Create Basic Views** - Enable user interaction with templates
3. **Implement Suggestion Engine** - Use preferences for smart behavior

### **Dependencies**
- **Base Module**: Required for user model inheritance
- **Project Module**: Required for template integration
- **Security**: Need to set up access rights

### **Future Enhancements**
1. **Preference Categories**: Group related preferences
2. **Preference Templates**: Predefined preference sets
3. **Preference Analytics**: Track preference usage
4. **Preference Import/Export**: Share preference configurations

## Risk Assessment

### **Low Risk**
- Model creation and basic functionality
- View creation and user interface
- User model integration

### **Medium Risk**
- Constraint enforcement
- Default preference creation
- User settings integration

### **Mitigation Strategies**
- Test thoroughly before deployment
- Provide clear error messages
- Implement fallback mechanisms
- Document all functionality

## Success Criteria

### **Functional Requirements**
- [ ] User preferences model works correctly
- [ ] All preference fields are functional
- [ ] User settings integration works
- [ ] Default preferences are created automatically

### **User Experience**
- [ ] Interface is intuitive and easy to use
- [ ] Help text is clear and helpful
- [ ] Preferences are saved correctly
- [ ] User can easily access preferences

### **Technical Requirements**
- [ ] Code is clean and well-documented
- [ ] Model follows Odoo best practices
- [ ] Views are properly structured
- [ ] No loading or runtime errors

---

**Status**: IMPLEMENTATION COMPLETE ✅  
**Estimated Time**: 1.5 hours  
**Actual Time**: 1 hour  
**Priority**: HIGH (Foundation for all smart behavior)  
**Dependencies**: None (starting from scratch)

## ✅ **COMPLETED IMPLEMENTATION**

### **Files Created:**
1. ✅ `models/preferences/user_preferences.py` - Complete model with all fields and methods
2. ✅ `views/preferences/user_preferences_views.xml` - Form, list, search views and user integration
3. ✅ `security/smart_templates_security.xml` - Security groups and categories
4. ✅ `security/ir.model.access.csv` - Access rights for user and manager groups
5. ✅ `views/menu_views.xml` - Basic menu structure
6. ✅ `data/smart_templates_data.xml` - Basic data file
7. ✅ `data/demo_data.xml` - Demo data file

### **Features Implemented:**
- ✅ User preferences model with all required fields
- ✅ Suggestion level configuration (passive/active/smart)
- ✅ Trigger behavior configuration (manual/auto/hybrid)
- ✅ Preferred start template selection
- ✅ Advanced options (learning, warnings, auto-save)
- ✅ User model integration with preferences tab
- ✅ Security groups and access rights
- ✅ Complete view structure (form, list, search)
- ✅ Menu integration

### **Ready for Testing:**
The User Preferences Model is now complete and ready for testing. The module should be installable and functional.
