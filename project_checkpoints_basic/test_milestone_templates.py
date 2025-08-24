#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to check if milestone templates are being created properly.
Run this script in Odoo shell to diagnose milestone template issues.
"""

def test_milestone_templates():
    """Test if milestone templates are being created properly"""
    
    # Check if the model exists
    try:
        milestone_template_model = env['project.milestone.template']
        print("✓ Milestone template model exists")
    except Exception as e:
        print(f"✗ Milestone template model error: {e}")
        return False
    
    # Check if there are any milestone templates
    try:
        templates = milestone_template_model.search([])
        print(f"✓ Found {len(templates)} milestone templates")
        
        if templates:
            for template in templates:
                print(f"  - {template.name} (ID: {template.id})")
                print(f"    Milestone Name: {template.milestone_name}")
                print(f"    Checkpoint Count: {template.checkpoint_count}")
                print(f"    Active: {template.active}")
        else:
            print("  No milestone templates found")
            
    except Exception as e:
        print(f"✗ Error searching milestone templates: {e}")
        return False
    
    # Check if the action exists
    try:
        action = env.ref('project_checkpoints_basic.action_project_milestone_template')
        print("✓ Milestone template action exists")
    except Exception as e:
        print(f"✗ Milestone template action error: {e}")
        return False
    
    # Check if the menu exists
    try:
        menu = env.ref('project_checkpoints_basic.menu_project_milestone_template')
        print("✓ Milestone template menu exists")
    except Exception as e:
        print(f"✗ Milestone template menu error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing Milestone Templates...")
    test_milestone_templates()
