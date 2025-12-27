# 🚀 Deployment Guide - The Dental Bond Dashboard

## ✅ Pre-Deployment Checklist
- [x] Code compiles without syntax errors
- [x] Role-based authentication system implemented
- [x] Permission checks added to all data editors
- [x] UI filtering implemented for 3-tier role system
- [x] Streamlit app starts successfully
- [x] Clerk OAuth integration complete
- [x] Changes ready for GitHub

## 🔐 Authentication Setup (NEW)

### **Clerk Authentication Configuration**

The dashboard now includes secure Clerk authentication with role-based access control.

#### **Required Clerk Setup:**

1. **Create Clerk Application**
   - Go to https://clerk.com
   - Create new application
   - Note your Publishable Key and Secret Key

2. **Configure OAuth Providers**
   - Enable Google OAuth (recommended)
   - Configure redirect URLs:
     - `https://your-app.streamlit.app/auth/clerk/callback`
     - `http://localhost:8501/auth/clerk/callback` (for local testing)

3. **Set User Roles**
   - Add custom metadata to users:
   ```json
   {
     "role": "admin",    // or "staff" or "viewer"
     "department": "PROSTHO"  // or "ENDO"
   }
   ```

4. **Configure Environment Variables**
   ```toml
   [clerk]
   publishable_key = "pk_test_your_key_here"
   secret_key = "sk_test_your_secret_here"
   ```

## 📦 Deployment Options

### **Option 1: Streamlit Cloud (Recommended - FREE)**

Streamlit Cloud is the easiest way to deploy your app with the new authentication system.

#### Steps:

1. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io/
   - Click "New app"

2. **Connect Your Repository**
   - Repository: `ajoychoudhury715-gif/ALLOTMENT-TDB`
   - Branch: `main`
   - Main file path: `app.py`

3. **Configure Secrets (CRITICAL for Authentication)**

   **Add Clerk Authentication:**
   ```toml
   [clerk]
   publishable_key = "pk_test_..."
   secret_key = "sk_test_..."
   redirect_uri = "https://your-app-name.streamlit.app/auth/clerk/callback"
   ```

   **For Supabase (Recommended for Data Storage):**
   ```toml
   [supabase]
   url = "https://your-project.supabase.co"
   key = "your-anon-key"
   service_role_key = "your-service-role-key"  # Recommended for server-side apps
   table = "tdb_allotment_state"
   row_id = "main"
   ```

   **Or for Google Sheets:**
   ```toml
   [spreadsheet_url] = "https://docs.google.com/spreadsheets/d/your-sheet-id"
   
   [gcp_service_account_json]
   {
     "type": "service_account",
     "project_id": "your-project-id",
     "private_key_id": "your-key-id",
     "private_key": "-----BEGIN PRIVATE KEY-----\\nYour-Key\\n-----END PRIVATE KEY-----\\n",
     "client_email": "your-service-account@project.iam.gserviceaccount.com",
     "client_id": "your-client-id",
     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     "token_uri": "https://oauth2.googleapis.com/token",
     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
     "client_x509_cert_url": "your-cert-url"
   }
   ```

4. **Deploy!**
   - Click "Deploy"
   - Wait 3-4 minutes for initial deployment
   - Your app will be live at: `https://your-app-name.streamlit.app`

5. **Test Authentication**
   - Access your app URL
   - Should redirect to Clerk login
   - Test different user roles
   - Verify permission-based UI behavior

---

### **Option 2: Local Development**

Run locally with authentication for testing:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (create .env file)
export CLERK_PUBLISHABLE_KEY="pk_test_..."
export CLERK_SECRET_KEY="sk_test_..."
export CLERK_REDIRECT_URI="http://localhost:8501/auth/clerk/callback"

# Run the app
streamlit run app.py
```

Access at: http://localhost:8501

---

## 🔒 Role-Based Access Control

### **User Roles & Permissions**

**Admin Role (`admin`):**
- ✅ Full system access and editing
- ✅ User management functions
- ✅ Schedule clearing permissions
- ✅ All data editor functionalities
- ✅ Complete operational control

**Staff Role (`staff`):**
- ✅ Schedule editing and patient management
- ✅ Status updates and operational changes
- ✅ Department analytics access
- ❌ User management functions
- ❌ Schedule clearing permissions
- 🔒 Read-only access to admin functions

**Viewer Role (`viewer`):**
- ✅ Read-only monitoring and viewing
- ✅ Analytics and status overview
- ✅ Assistant availability dashboard
- ❌ No editing capabilities
- ❌ No administrative functions
- 🔒 Locked controls with clear messaging

### **UI Components Protection**

All major dashboard components are now protected:
- Main schedule data editor
- Add Patient button
- Save Changes functionality
- Delete row controls
- OP-specific data editors
- Doctor statistics editor
- Schedule clearing functions

---

## 🗄️ Data Storage Setup

### **Supabase (Recommended for Production)**

1. **Create Supabase Project**: https://supabase.com
2. **Run SQL Setup**:
```sql
CREATE TABLE IF NOT EXISTS tdb_allotment_state (
  id TEXT PRIMARY KEY,
  payload JSONB NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enable RLS (Row Level Security)
ALTER TABLE tdb_allotment_state ENABLE ROW LEVEL SECURITY;

-- Create policies for the main state row
CREATE POLICY "read main" ON tdb_allotment_state
  FOR SELECT USING (id = 'main');

CREATE POLICY "insert main" ON tdb_allotment_state
  FOR INSERT WITH CHECK (id = 'main');

CREATE POLICY "update main" ON tdb_allotment_state
  FOR UPDATE USING (id = 'main') WITH CHECK (id = 'main');
```

3. **Get Credentials**:
   - Project URL: Settings → API → Project URL
   - Service Role Key: Settings → API → Project API keys → service_role

### **Google Sheets (Alternative)**

1. Create Google Sheet with "Sheet1"
2. Enable Google Sheets API
3. Create Service Account
4. Share sheet with service account email
5. Add credentials to Streamlit secrets

---

## 🔧 Environment Configuration

### **Required Environment Variables**

```bash
# Clerk Authentication (Required)
CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
CLERK_REDIRECT_URI=https://your-app.streamlit.app/auth/clerk/callback

# Data Storage (Choose one)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# OR

SPREADSHEET_URL=https://docs.google.com/spreadsheets/d/your-id
GCP_SERVICE_ACCOUNT_JSON={"type": "service_account", ...}
```

---

## 📊 Monitoring & Maintenance

### **Streamlit Cloud Dashboard**
- View logs: Streamlit Cloud → Your app → Logs
- Monitor usage: Analytics tab
- Reboot app: Menu → Reboot

### **Authentication Monitoring**
- Check Clerk dashboard for user activity
- Monitor authentication success/failure rates
- Review user role assignments

### **Auto-Updates**
- Push to GitHub `main` branch
- Streamlit Cloud auto-deploys within 1-2 minutes
- Authentication configuration preserved

---

## 🆘 Troubleshooting

### **Authentication Issues**
- Verify Clerk keys are correct
- Check redirect URI matches exactly
- Ensure user roles are set in Clerk metadata
- Check app logs for authentication errors

### **App Won't Start**
- Check logs in Streamlit Cloud
- Verify secrets are correctly formatted (TOML syntax)
- Ensure all dependencies in requirements.txt
- Confirm Clerk configuration is complete

### **Data Not Saving**
- Verify Supabase/Google Sheets credentials
- Check table exists and has correct structure
- Test with service role key for Supabase
- Check app logs for error messages

### **Permission Issues**
- Verify user roles in Clerk dashboard
- Check that role metadata is properly set
- Test with different user accounts
- Review permission logic in app logs

---

## 🎯 Post-Deployment Checklist

1. **Deploy to Streamlit Cloud** (takes 5 minutes)
2. **Configure Clerk authentication** with proper user roles
3. **Set up Supabase** for persistent data storage
4. **Test authentication flow** with different user roles
5. **Verify permission-based UI** behavior
6. **Share app URL** with your team
7. **Monitor usage** and authentication logs
8. **Configure user roles** in Clerk dashboard

---

## 📞 Support

- **Clerk Docs**: https://clerk.com/docs
- **Streamlit Docs**: https://docs.streamlit.io/
- **Supabase Docs**: https://supabase.com/docs
- **GitHub Issues**: Create an issue in your repo

---

## 🎉 Success!

**Your secure, role-based dashboard is now production-ready!**

The application includes:
- ✅ Secure Clerk authentication
- ✅ Role-based access control (Admin/Staff/Viewer)
- ✅ Protected UI components
- ✅ Persistent data storage
- ✅ Real-time assistant availability tracking
- ✅ Professional dental clinic management features

Simply deploy to Streamlit Cloud with your Clerk authentication configuration and you're live! 🚀