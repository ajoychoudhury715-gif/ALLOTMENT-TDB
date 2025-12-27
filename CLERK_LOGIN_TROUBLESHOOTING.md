npx create-next-app@latest nextjs-app --use-npm# 🔧 Clerk Login Troubleshooting Guide

## Common Issues and Solutions for Clerk Authentication

### 🚨 **Quick Diagnosis**

#### **Symptoms:**
- Login button doesn't work
- Redirects to Clerk but stays there
- "Clerk not configured" message
- 404 errors on callback
- CORS errors

#### **Most Common Causes:**
1. **Missing Environment Variables**
2. **Incorrect Redirect URI**
3. **Clerk Application Not Set Up**
4. **Network/Firewall Issues**

---

## 🔧 **Step-by-Step Troubleshooting**

### **Step 1: Verify Environment Variables**

#### **Check if Clerk keys are set:**

**For Local Development:**
```bash
# Check if environment variables are set
echo $CLERK_PUBLISHABLE_KEY
echo $CLERK_SECRET_KEY
echo $CLERK_REDIRECT_URI

# If empty, set them:
export CLERK_PUBLISHABLE_KEY="pk_test_your_key_here"
export CLERK_SECRET_KEY="sk_test_your_secret_here"
export CLERK_REDIRECT_URI="http://localhost:8501/auth/clerk/callback"
```

**For Streamlit Cloud:**
- Go to your app settings
- Add secrets in TOML format:
```toml
[clerk]
publishable_key = "pk_test_your_key_here"
secret_key = "sk_test_your_secret_here"
redirect_uri = "https://your-app-name.streamlit.app/auth/clerk/callback"
```

### **Step 2: Verify Clerk Application Setup**

#### **Check Clerk Dashboard:**
1. Go to https://dashboard.clerk.com/
2. Select your application
3. Navigate to **"Configure"** → **"JWT Templates"**
4. Ensure you have a JWT template

#### **Check API Keys:**
1. Go to **"Configure"** → **"API Keys"**
2. Copy your **Publishable key** and **Secret key**
3. Verify they match your environment variables

#### **Check Redirect URLs:**
1. Go to **"Configure"** → **"Redirect URLs"**
2. Add your redirect URL:
   - **Local**: `http://localhost:8501/auth/clerk/callback`
   - **Production**: `https://your-app.streamlit.app/auth/clerk/callback`

### **Step 3: Test Basic Connectivity**

#### **Test Clerk API Connection:**
```python
# Add this to your app for testing
import requests

def test_clerk_connection():
    headers = {
        "Authorization": f"Bearer {os.getenv('CLERK_SECRET_KEY')}"
    }
    response = requests.get(
        "https://api.clerk.com/v1/users", 
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    if response.status_code == 200:
        print("✅ Clerk API connection successful")
    else:
        print("❌ Clerk API connection failed")
        print(f"Error: {response.text}")
```

### **Step 4: Debug Authentication Flow**

#### **Add Debug Information to Your App:**

```python
# Add to the top of app.py for debugging
if st.checkbox("🔍 Debug Authentication"):
    st.write("### Authentication Debug Info")
    
    # Check environment variables
    st.write("**Environment Variables:**")
    st.write(f"- CLERK_PUBLISHABLE_KEY: {'✅ Set' if os.getenv('CLERK_PUBLISHABLE_KEY') else '❌ Missing'}")
    st.write(f"- CLERK_SECRET_KEY: {'✅ Set' if os.getenv('CLERK_SECRET_KEY') else '❌ Missing'}")
    st.write(f"- CLERK_REDIRECT_URI: {os.getenv('CLERK_REDIRECT_URI', 'Not set')}")
    
    # Check session state
    st.write("**Session State:**")
    st.write(f"- Current User: {st.session_state.get('current_user', 'None')}")
    st.write(f"- Is Authenticated: {is_authenticated()}")
    
    # Test Clerk connection
    try:
        test_clerk_connection()
    except Exception as e:
        st.error(f"Connection test failed: {e}")
```

---

## 🛠️ **Common Fixes**

### **Fix 1: Environment Variables Not Loading**

**Problem**: Keys are set but not recognized by the app.

**Solution:**
```python
# In auth_clerk.py, add explicit loading
CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY") or st.secrets.get("clerk", {}).get("publishable_key", "")
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY") or st.secrets.get("clerk", {}).get("secret_key", "")
CLERK_REDIRECT_URI = os.getenv("CLERK_REDIRECT_URI") or st.secrets.get("clerk", {}).get("redirect_uri", "")
```

### **Fix 2: Redirect URI Mismatch**

**Problem**: Clerk expects different redirect URI than configured.

**Solution:**
1. **Exact match required**: `https://your-app.streamlit.app/auth/clerk/callback`
2. **No trailing slashes**
3. **Correct protocol** (https for production)

### **Fix 3: CORS Issues**

**Problem**: Browser blocks requests due to CORS.

**Solution:**
1. **Verify redirect URLs** in Clerk dashboard
2. **Check network connectivity**
3. **Try different browser**
4. **Clear browser cache**

### **Fix 4: Clerk Application Not Active**

**Problem**: Clerk application is paused or has issues.

**Solution:**
1. **Check Clerk dashboard** for application status
2. **Ensure application is active**
3. **Verify billing status** (if applicable)

---

## 🚀 **Quick Test Setup**

### **Minimal Working Configuration:**

1. **Create Clerk Application:**
   - Go to https://clerk.com
   - Create new application
   - Choose any sign-in method (Google, Email, etc.)

2. **Get Keys:**
   - Copy Publishable Key: `pk_test_...`
   - Copy Secret Key: `sk_test_...`

3. **Set Environment Variables:**
   ```bash
   export CLERK_PUBLISHABLE_KEY="pk_test_your_key"
   export CLERK_SECRET_KEY="sk_test_your_secret"
   export CLERK_REDIRECT_URI="http://localhost:8501/auth/clerk/callback"
   ```

4. **Configure Redirect URL in Clerk:**
   - Go to Configure → Redirect URLs
   - Add: `http://localhost:8501/auth/clerk/callback`

5. **Test:**
   - Start the app: `streamlit run app.py`
   - Try logging in

---

## 🔍 **Advanced Debugging**

### **Browser Developer Tools**

1. **Open Developer Tools** (F12)
2. **Go to Network tab**
3. **Try logging in**
4. **Check for failed requests**
5. **Look for CORS errors**
6. **Check request headers**

### **Application Logs**

```python
# Add to auth_clerk.py for detailed logging
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def log_debug(message):
    logger.debug(f"CLERK DEBUG: {message}")

# Use throughout the authentication flow
log_debug(f"Starting login with redirect URI: {CLERK_REDIRECT_URI}")
```

### **Network Analysis**

#### **Expected Request Flow:**
1. **User clicks login** → Redirect to Clerk
2. **User authenticates** → Clerk redirects back
3. **App receives code** → Exchange for token
4. **Token validated** → User session created

#### **Common Failure Points:**
- **Step 1**: Environment variables missing
- **Step 2**: Redirect URI mismatch
- **Step 3**: Invalid client credentials
- **Step 4**: Token validation failure

---

## 📞 **Getting Help**

### **Clerk Documentation:**
- **Main Docs**: https://clerk.com/docs
- **Authentication**: https://clerk.com/docs/authentication/overview
- **API Reference**: https://clerk.com/docs/reference/core-api

### **Common Error Messages:**

#### **"Clerk not configured"**
- **Cause**: Environment variables missing
- **Fix**: Set CLERK_PUBLISHABLE_KEY and CLERK_SECRET_KEY

#### **"Invalid redirect URI"**
- **Cause**: URI doesn't match Clerk configuration
- **Fix**: Update redirect URLs in Clerk dashboard

#### **"Invalid client"**
- **Cause**: Wrong publishable key
- **Fix**: Use correct pk_test_... key from Clerk

#### **"Unauthorized"**
- **Cause**: Wrong secret key
- **Fix**: Use correct sk_test_... key from Clerk

#### **CORS Error**
- **Cause**: Redirect URL not whitelisted
- **Fix**: Add URL to Clerk redirect URLs

---

## ✅ **Verification Checklist**

Before deploying, verify:

- [ ] Clerk application is active
- [ ] Environment variables are set correctly
- [ ] Redirect URLs match exactly
- [ ] API keys are valid and unexpired
- [ ] Network connectivity works
- [ ] Browser allows popups/redirects
- [ ] CORS is configured properly

---

**With this troubleshooting guide, you should be able to resolve most Clerk login issues!** 🛠️

If problems persist, check the browser console and application logs for specific error messages.