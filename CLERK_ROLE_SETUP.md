# 🔐 Clerk User Role Setup Guide

## Setting up User Roles in Clerk for The Dental Bond Dashboard

This guide explains how to configure user roles in Clerk to work with the role-based UI filtering system.

## 🎯 Role Structure

The dashboard uses a **3-tier role system**:

- **`admin`**: Full system access, user management, schedule clearing
- **`staff`**: Operational editing, patient management, analytics  
- **`viewer`**: Read-only monitoring, status overview

## 📋 Setup Methods

### **Method 1: Clerk Dashboard (Recommended)**

#### **Step 1: Access Clerk Dashboard**
1. Go to https://dashboard.clerk.com/
2. Select your application
3. Navigate to **"Users"** section

#### **Step 2: Edit User Metadata**
1. Click on a user to edit their profile
2. Go to **"Public metadata"** or **"Private metadata"**
3. Add role information:

```json
{
  "role": "admin",
  "department": "ADMIN"
}
```

#### **Step 3: Role Examples**

**Admin User:**
```json
{
  "role": "admin",
  "department": "ADMIN",
  "permissions": ["edit_appointments", "clear_schedule", "user_management", "view_analytics"]
}
```

**Staff User:**
```json
{
  "role": "staff", 
  "department": "PROSTHO",
  "permissions": ["edit_appointments", "view_analytics"]
}
```

**Viewer User:**
```json
{
  "role": "viewer",
  "department": "VIEWER", 
  "permissions": ["view_analytics"]
}
```

### **Method 2: Clerk API (Programmatic)**

#### **Update User Metadata via API**
```bash
# Using Clerk REST API
curl -X PATCH "https://api.clerk.com/v1/users/{user_id}" \
  -H "Authorization: Bearer YOUR_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "public_metadata": {
      "role": "admin",
      "department": "ADMIN"
    }
  }'
```

#### **Using Clerk SDK (Python)**
```python
import clerk

# Initialize Clerk
clerk_client = clerk.Clerk(secret_key="sk_test_...")

# Update user metadata
user = clerk_client.users.update_user_metadata(
    user_id="user_123",
    public_metadata={
        "role": "staff",
        "department": "PROSTHO"
    }
)
```

### **Method 3: Clerk Organizations (Advanced)**

#### **Create Organizations for Departments**
1. In Clerk Dashboard, go to **"Organizations"**
2. Create organizations:
   - **"PROSTHO Department"**
   - **"ENDO Department"** 
   - **"ADMIN"**
   - **"VIEWERS"**

#### **Assign Users to Organizations**
1. Select organization
2. Add members with roles:
   - **Admin**: Full permissions
   - **Staff**: Department-specific access
   - **Viewer**: Read-only access

## 🏗️ Implementation in Your App

### **Metadata Structure Expected by App**

The application expects this metadata structure:

```json
{
  "role": "admin|staff|viewer",
  "department": "PROSTHO|ENDO|ADMIN|VIEWER",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@clinic.com"
}
```

### **Role Mapping in App**

The application maps roles to permissions:

```python
ROLE_PERMISSIONS = {
    "admin": [
        "edit_appointments",
        "clear_schedule", 
        "user_management",
        "view_analytics"
    ],
    "staff": [
        "edit_appointments",
        "view_analytics"
    ],
    "viewer": [
        "view_analytics"
    ]
}
```

## 🔧 Bulk User Setup

### **Script to Set Multiple Users**

```python
# bulk_setup_users.py
import clerk
import json

clerk_client = clerk.Clerk(secret_key="sk_test_...")

# User list with roles
users_to_setup = [
    {
        "email": "admin@clinic.com",
        "role": "admin",
        "department": "ADMIN"
    },
    {
        "email": "dr.hussain@clinic.com", 
        "role": "staff",
        "department": "PROSTHO"
    },
    {
        "email": "dr.farhath@clinic.com",
        "role": "staff", 
        "department": "ENDO"
    },
    {
        "email": "assistant.anya@clinic.com",
        "role": "staff",
        "department": "ENDO"
    },
    {
        "email": "viewer@clinic.com",
        "role": "viewer",
        "department": "VIEWER"
    }
]

# Set up each user
for user_data in users_to_setup:
    try:
        # Find user by email
        users = clerk_client.users.list_users()
        user = next((u for u in users if u.email_addresses[0].email_address == user_data["email"]), None)
        
        if user:
            # Update metadata
            clerk_client.users.update_user_metadata(
                user_id=user.id,
                public_metadata={
                    "role": user_data["role"],
                    "department": user_data["department"]
                }
            )
            print(f"✅ Updated {user_data['email']} with role: {user_data['role']}")
        else:
            print(f"❌ User {user_data['email']} not found")
            
    except Exception as e:
        print(f"❌ Error setting up {user_data['email']}: {str(e)}")
```

## 🧪 Testing Role Setup

### **Verify User Metadata**

#### **Check via Clerk Dashboard:**
1. Go to Users section
2. Click on user
3. View Public/Private metadata
4. Verify role and department are set correctly

#### **Check via API:**
```bash
curl -X GET "https://api.clerk.com/v1/users/{user_id}" \
  -H "Authorization: Bearer YOUR_SECRET_KEY"
```

#### **Test in Application:**
1. Login with the user
2. Check sidebar for role display
3. Verify UI components match permissions
4. Test restricted functionality

## 🚀 Production Deployment

### **Environment Variables**

Set these in Streamlit Cloud:

```toml
[clerk]
publishable_key = "pk_live_..."  # Use live keys for production
secret_key = "sk_live_..."
redirect_uri = "https://your-app.streamlit.app/auth/clerk/callback"
```

### **User Onboarding Process**

1. **Admin creates user accounts** in Clerk
2. **Assign appropriate roles** via metadata
3. **Send invitation emails** to users
4. **Users complete registration** and login
5. **Test role-based functionality** with each user

### **Role Management Workflow**

#### **Adding New Admin:**
1. Create user in Clerk
2. Set metadata: `{"role": "admin", "department": "ADMIN"}`
3. User gets full system access

#### **Demoting User:**
1. Update metadata: `{"role": "viewer", "department": "VIEWER"}`
2. User loses editing capabilities

#### **Department Transfer:**
1. Update metadata: `{"department": "NEW_DEPT"}`
2. User sees department-specific features

## 🛠️ Troubleshooting

### **Common Issues**

#### **Role Not Applying:**
- Check metadata structure matches expected format
- Verify user logged out and back in
- Clear browser cache and session storage

#### **Permission Errors:**
- Verify role is exactly "admin", "staff", or "viewer"
- Check for typos in role names
- Ensure metadata is in "public_metadata" section

#### **Department Not Displaying:**
- Check "department" field in metadata
- Verify department value matches expected format
- Refresh application after metadata update

### **Debug Tools**

#### **Browser Console Check:**
```javascript
// Check session state
console.log(st.session_state.current_user);

// Check metadata
fetch('/api/auth/user')
  .then(response => response.json())
  .then(data => console.log(data));
```

#### **Streamlit Debug Display:**
```python
# Add to app.py for debugging
if st.checkbox("Debug User Info"):
    st.json(st.session_state.get("current_user", {}))
```

## 📞 Support

- **Clerk Documentation**: https://clerk.com/docs
- **Metadata Guide**: https://clerk.com/docs/users/metadata
- **API Reference**: https://clerk.com/docs/reference/core-api

---

**Your role-based authentication system is ready for production!** 🎉

Follow this guide to set up user roles and enjoy secure, permission-based access to your dental dashboard.