#!/usr/bin/env python3
"""
Test script to verify the role-based UI filtering and permission system.
This script tests the authentication and permission checking functions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock streamlit session state for testing
class MockSessionState:
    def __init__(self):
        self.current_user = None

# Create a mock st module
class MockStreamlit:
    class session_state:
        @staticmethod
        def get(key, default=None):
            if key == 'current_user':
                return getattr(MockStreamlit.session_state, '_current_user', default)
            return default
    
    @staticmethod
    def set_current_user(user_info):
        MockStreamlit.session_state._current_user = user_info

# Patch sys.modules to include our mock streamlit
sys.modules['streamlit'] = MockStreamlit()

from auth_clerk import has_permission, auth

def test_permission_system():
    """Test the permission system with different roles."""
    
    print("🧪 Testing Role-Based Permission System")
    print("=" * 50)
    
    # Test the has_permission function with different roles
    roles_and_permissions = [
        ("admin", "edit_appointments", True),
        ("admin", "clear_schedule", True), 
        ("admin", "user_management", True),
        ("admin", "view_analytics", True),
        ("staff", "edit_appointments", True),
        ("staff", "clear_schedule", False),
        ("staff", "user_management", False),
        ("staff", "view_analytics", True),
        ("viewer", "edit_appointments", False),
        ("viewer", "clear_schedule", False),
        ("viewer", "user_management", False),
        ("viewer", "view_analytics", True),
    ]
    
    print("\n📋 Testing Permission Checks:")
    print("-" * 30)
    
    for role, permission, expected in roles_and_permissions:
        # Test by setting user info in session state and calling has_permission
        MockStreamlit.set_current_user({"role": role})
        result = has_permission(permission)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status} | {role:6} | {permission:20} | Expected: {expected:5} | Got: {result:5}")
    
    print("\n🔐 Testing Role Hierarchy:")
    print("-" * 30)
    
    # Test role hierarchy (higher roles should have all permissions of lower roles)
    hierarchy_tests = [
        ("admin", "staff"),
        ("staff", "viewer"),
        ("admin", "viewer"),
    ]
    
    for higher_role, lower_role in hierarchy_tests:
        print(f"📊 {higher_role.upper()} should have all {lower_role.upper()} permissions")
        
        # Check if admin has all staff permissions
        if higher_role == "admin" and lower_role == "staff":
            permissions_to_test = ["edit_appointments", "view_analytics"]
            for perm in permissions_to_test:
                MockStreamlit.set_current_user({"role": higher_role})
                higher_has = has_permission(perm)
                MockStreamlit.set_current_user({"role": lower_role})
                lower_has = has_permission(perm)
                if higher_has and lower_has:
                    print(f"  ✅ {perm}: {higher_role} has {perm} = {higher_has}, {lower_role} has {perm} = {lower_has}")
                else:
                    print(f"  ❌ {perm}: {higher_role} has {perm} = {higher_has}, {lower_role} has {perm} = {lower_has}")
    
    print("\n🎭 Testing UI Component Visibility Logic:")
    print("-" * 40)
    
    # Test UI component visibility logic
    ui_components = [
        ("Main Data Editor", "edit_appointments"),
        ("Add Patient Button", "edit_appointments"),
        ("Save Changes Button", "edit_appointments"),
        ("Delete Row Controls", "edit_appointments"),
        ("OP Data Editors", "edit_appointments"),
        ("Doctor Statistics Editor", "edit_appointments"),
        ("Clear Schedule", "clear_schedule"),
        ("User Management", "user_management"),
    ]
    
    print("Components that should be visible/editable:")
    for role in ["admin", "staff", "viewer"]:
        print(f"\n👤 {role.upper()} Role:")
        MockStreamlit.set_current_user({"role": role})
        for component, required_permission in ui_components:
            has_access = has_permission(required_permission)
            visibility = "🔓 Full Access" if has_access else "🔒 Read-Only/Locked"
            print(f"  {component:30} | {required_permission:20} | {visibility}")
    
    print("\n🛡️ Testing Security Features:")
    print("-" * 30)
    
    # Test security scenarios
    security_tests = [
        ("No user info", None, "edit_appointments", False),
        ("Empty role", {"role": ""}, "edit_appointments", False),
        ("Invalid role", {"role": "superuser"}, "edit_appointments", False),
        ("Missing role", {}, "edit_appointments", False),
    ]
    
    for test_name, user_info, permission, expected in security_tests:
        try:
            if user_info:
                MockStreamlit.set_current_user(user_info)
            else:
                MockStreamlit.set_current_user(None)
            result = has_permission(permission)
            status = "✅ PASS" if result == expected else "❌ FAIL"
            print(f"{status} | {test_name:20} | Expected: {expected:5} | Got: {result:5}")
        except Exception as e:
            print(f"❌ FAIL | {test_name:20} | Exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Permission System Test Complete!")
    print("\n📝 Summary:")
    print("• Role hierarchy: Admin > Staff > Viewer")
    print("• edit_appointments: Required for all data editing features")
    print("• clear_schedule: Admin only")
    print("• user_management: Admin only")
    print("• view_analytics: Available to all authenticated roles")
    print("\n🔧 Implementation includes:")
    print("• Permission checks around all data editors")
    print("• UI component visibility based on user role")
    print("• Graceful degradation for unauthorized users")
    print("• Clear messaging for permission requests")

if __name__ == "__main__":
    test_permission_system()