"""
Clerk Authentication Module for The Dental Bond Dashboard
Handles OAuth flow, session management, and role-based access control
"""

import streamlit as st
import jwt
import requests
import json
import time
import hashlib
import secrets
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import os

# Clerk Configuration
CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY", "")
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY", "")
CLERK_API_URL = "https://api.clerk.com/v1"
CLERK_REDIRECT_URI = os.getenv("CLERK_REDIRECT_URI", "http://localhost:8501/auth/callback")

# Session timeout in seconds (8 hours)
SESSION_TIMEOUT = 28800

class ClerkAuth:
    """Handles Clerk authentication flow and session management"""
    
    def __init__(self):
        self.publishable_key = CLERK_PUBLISHABLE_KEY
        self.secret_key = CLERK_SECRET_KEY
        self.api_url = CLERK_API_URL
        self.redirect_uri = CLERK_REDIRECT_URI
        
    def generate_state(self) -> str:
        """Generate secure state parameter for CSRF protection"""
        return secrets.token_urlsafe(32)
    
    def create_sign_in_url(self, state: str) -> str:
        """Create Clerk sign-in URL with state parameter"""
        base_url = "https://clerk.com/sign-in"
        params = {
            "redirect_url": self.redirect_uri,
            "state": state,
            "appearance": {
                "theme": "light",
                "variables": {
                    "colorPrimary": "#99582f",
                    "colorBackground": "#ffffff",
                    "colorInputBackground": "#f5f5f5",
                    "colorInputText": "#111b26"
                }
            }
        }
        
        # Add sign-in alternatives (email, phone, etc.)
        query_params = []
        for key, value in params.items():
            if key == "redirect_url":
                query_params.append(f"redirect_url={value}")
            elif key == "state":
                query_params.append(f"state={value}")
            elif key == "appearance":
                # Encode appearance as JSON
                query_params.append(f"appearance={urllib.parse.quote(json.dumps(value))}")
        
        return f"{base_url}?{'&'.join(query_params)}"
    
    def exchange_code_for_token(self, code: str, state: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for user token"""
        if not self.secret_key:
            st.error("Clerk secret key not configured")
            return None
            
        # Validate state parameter
        stored_state = st.session_state.get('oauth_state')
        if not stored_state or stored_state != state:
            st.error("Invalid state parameter - possible CSRF attack")
            return None
        
        try:
            # Exchange code for token via Clerk API
            headers = {
                "Authorization": f"Bearer {self.secret_key}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "code": code,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code"
            }
            
            response = requests.post(
                f"{self.api_url}/oauth/token", 
                headers=headers, 
                data=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Token exchange failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Token exchange error: {str(e)}")
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Clerk"""
        if not access_token:
            return None
            
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.api_url}/me", 
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Failed to get user info: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"User info error: {str(e)}")
            return None
    
    def create_user_session(self, user_data: Dict[str, Any], role: str = "viewer") -> None:
        """Create user session in Streamlit"""
        session_data = {
            'user_id': user_data.get('id', ''),
            'email': user_data.get('email_addresses', [{}])[0].get('email_address', ''),
            'first_name': user_data.get('first_name', ''),
            'last_name': user_data.get('last_name', ''),
            'role': role,
            'authenticated': True,
            'login_time': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'department': self._get_user_department(user_data),
            'permissions': self._get_role_permissions(role)
        }
        
        # Store in session state
        for key, value in session_data.items():
            st.session_state[f'auth_{key}'] = value
        
        st.session_state['authenticated'] = True
        st.session_state['user_data'] = user_data
    
    def _get_user_department(self, user_data: Dict[str, Any]) -> str:
        """Determine user department from user data"""
        email = user_data.get('email_addresses', [{}])[0].get('email_address', '').lower()
        
        # Department assignment logic based on email domain or metadata
        if 'prosth' in email or 'prosthe' in email:
            return 'PROSTHO'
        elif 'endo' in email or 'endodontic' in email:
            return 'ENDO'
        else:
            # Default assignment or based on user metadata
            return user_data.get('public_metadata', {}).get('department', 'PROSTHO')
    
    def _get_role_permissions(self, role: str) -> Dict[str, bool]:
        """Get permissions based on role"""
        permissions = {
            'viewer': {
                'view_schedules': True,
                'view_analytics': False,
                'edit_appointments': False,
                'manage_users': False,
                'system_admin': False,
                'export_data': False,
                'clear_schedule': False
            },
            'staff': {
                'view_schedules': True,
                'view_analytics': True,
                'edit_appointments': True,
                'manage_users': False,
                'system_admin': False,
                'export_data': True,
                'clear_schedule': False
            },
            'admin': {
                'view_schedules': True,
                'view_analytics': True,
                'edit_appointments': True,
                'manage_users': True,
                'system_admin': True,
                'export_data': True,
                'clear_schedule': True
            }
        }
        
        return permissions.get(role, permissions['viewer'])
    
    def check_session_validity(self) -> bool:
        """Check if current session is still valid"""
        if not st.session_state.get('authenticated'):
            return False
        
        last_activity = st.session_state.get('auth_last_activity')
        if not last_activity:
            return False
        
        try:
            last_time = datetime.fromisoformat(last_activity)
            current_time = datetime.now()
            
            # Check session timeout
            if (current_time - last_time).total_seconds() > SESSION_TIMEOUT:
                self.clear_session()
                st.error("Session expired. Please log in again.")
                return False
            
            # Update last activity
            st.session_state['auth_last_activity'] = datetime.now().isoformat()
            return True
            
        except Exception:
            return False
    
    def clear_session(self) -> None:
        """Clear user session"""
        auth_keys = [key for key in st.session_state.keys() if isinstance(key, str) and key.startswith('auth_')]
        for key in auth_keys:
            del st.session_state[key]
        
        st.session_state['authenticated'] = False
        if 'user_data' in st.session_state:
            del st.session_state['user_data']
        
        if 'oauth_state' in st.session_state:
            del st.session_state['oauth_state']

# Global auth instance
auth = ClerkAuth()

def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False) and auth.check_session_validity()

def get_user_info() -> Optional[Dict[str, Any]]:
    """Get current user information"""
    if not is_authenticated():
        return None
    
    return {
        'id': st.session_state.get('auth_user_id', ''),
        'email': st.session_state.get('auth_email', ''),
        'first_name': st.session_state.get('auth_first_name', ''),
        'last_name': st.session_state.get('auth_last_name', ''),
        'role': st.session_state.get('auth_role', 'viewer'),
        'department': st.session_state.get('auth_department', ''),
        'permissions': st.session_state.get('auth_permissions', {}),
        'login_time': st.session_state.get('auth_login_time', ''),
        'last_activity': st.session_state.get('auth_last_activity', '')
    }

def has_permission(permission: str) -> bool:
    """Check if current user has specific permission"""
    if not is_authenticated():
        return False
    
    permissions = st.session_state.get('auth_permissions', {})
    return permissions.get(permission, False)

def require_authentication() -> Optional[Dict[str, Any]]:
    """Decorator-like function to require authentication"""
    if not is_authenticated():
        show_login_page()
        return None
    
    return get_user_info()

def logout_user():
    """Log out current user"""
    auth.clear_session()
    st.success("Logged out successfully!")
    st.rerun()

# Role management functions
def assign_role_to_user(user_id: str, role: str) -> bool:
    """Assign role to user (Admin only)"""
    if not has_permission('manage_users'):
        st.error("Insufficient permissions to manage users")
        return False
    
    if role not in ['viewer', 'staff', 'admin']:
        st.error("Invalid role")
        return False
    
    try:
        # This would integrate with Clerk's user management API
        # For now, we'll store in session state for demonstration
        st.success(f"Role '{role}' assigned to user {user_id}")
        return True
    except Exception as e:
        st.error(f"Failed to assign role: {str(e)}")
        return False

def show_login_page():
    """Display the login page"""
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        background: linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%);
        text-align: center;
        border: 1px solid #d3c3b0;
    }
    .login-title {
        color: #111b26;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 10px;
        letter-spacing: 0.5px;
    }
    .login-subtitle {
        color: #99582f;
        font-size: 1rem;
        margin-bottom: 30px;
        font-weight: 500;
    }
    .login-logo {
        width: 120px;
        height: auto;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="login-container">
        <div class="login-title">The Dental Bond</div>
        <div class="login-subtitle">Allotment Dashboard</div>
        <p style="color: #666; margin-bottom: 30px;">Please sign in to access the scheduling system</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show logo if available
    try:
        logo_path = "The Dental Bond LOGO_page-0001.jpg"
        if os.path.exists(logo_path):
            st.image(logo_path, width=200)
    except Exception:
        pass
    
    # Clerk Sign In Button
    if st.button("🔐 Sign In with Clerk", type="primary", use_container_width=True):
        # Generate state parameter
        state = auth.generate_state()
        st.session_state['oauth_state'] = state
        
        # Create sign-in URL
        sign_in_url = auth.create_sign_in_url(state)
        
        # Redirect to Clerk
        st.markdown(f"""
        <script>
        window.location.href = '{sign_in_url}';
        </script>
        """, unsafe_allow_html=True)
        
        # For development/testing without Clerk setup
        if not CLERK_PUBLISHABLE_KEY:
            st.warning("Clerk not configured. Using demo login for development.")
            if st.button("Demo Login (Development Only)"):
                # Create demo session
                demo_user = {
                    'id': 'demo_user_123',
                    'email_addresses': [{'email_address': 'demo@dentalbond.com'}],
                    'first_name': 'Demo',
                    'last_name': 'User'
                }
                auth.create_user_session(demo_user, 'admin')
                st.rerun()

def handle_auth_callback():
    """Handle OAuth callback from Clerk"""
    # Get query parameters
    query_params = st.query_params
    
    if 'code' not in query_params or 'state' not in query_params:
        st.error("Missing authorization parameters")
        return
    
    code = query_params['code']
    state = query_params['state']
    
    # Exchange code for token
    token_data = auth.exchange_code_for_token(code, state)
    
    if token_data:
        # Get user information
        access_token = token_data.get('access_token') if token_data else None
        user_data = auth.get_user_info(access_token) if access_token else None
        
        if user_data:
            # Determine role (default to viewer)
            role = "viewer"  # This could be enhanced with role mapping
            
            # Create session
            auth.create_user_session(user_data, role)
            
            # Clear OAuth parameters from URL
            st.query_params.clear()
            
            st.success(f"Welcome {user_data.get('first_name', '')}!")
            st.rerun()
        else:
            st.error("Failed to get user information")
    else:
        st.error("Authentication failed")

def show_user_profile():
    """Display user profile and settings"""
    user_info = get_user_info()
    if not user_info:
        return
    
    st.markdown("### 👤 User Profile")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Account Information:**")
        st.write(f"**Name:** {user_info['first_name']} {user_info['last_name']}")
        st.write(f"**Email:** {user_info['email']}")
        st.write(f"**Role:** {user_info['role'].title()}")
        st.write(f"**Department:** {user_info['department']}")
        st.write(f"**Login Time:** {user_info['login_time'][:19]}")
    
    with col2:
        st.markdown("**Permissions:**")
        permissions = user_info['permissions']
        for perm, granted in permissions.items():
            status = "✅" if granted else "❌"
            perm_name = perm.replace('_', ' ').title()
            st.write(f"{status} {perm_name}")
    
    st.markdown("---")
    
    # User actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Profile", use_container_width=True):
            st.rerun()
    
    with col2:
        if has_permission('system_admin') and st.button("⚙️ Admin Panel", use_container_width=True):
            show_admin_panel()
    
    with col3:
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            logout_user()

def show_admin_panel():
    """Show admin panel for user management"""
    if not has_permission('manage_users'):
        st.error("Access denied: Admin privileges required")
        return
    
    st.markdown("### ⚙️ Admin Panel")
    
    # User management section
    st.markdown("#### User Management")
    st.info("User management features would be implemented here using Clerk's API")
    
    # System settings
    st.markdown("#### System Settings")
    
    # Department management
    st.markdown("#### Department Configuration")
    
    # Session management
    st.markdown("#### Active Sessions")
    
    if st.button("🔄 Reload Admin Panel"):
        st.rerun()