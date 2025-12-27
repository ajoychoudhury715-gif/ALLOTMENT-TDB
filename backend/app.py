import os
from flask import Flask, redirect, request, jsonify, session
import requests
from flask_cors import CORS
from jose import jwt

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersecret")

CLERK_PUBLISHABLE_KEY = os.environ.get("CLERK_PUBLISHABLE_KEY")
CLERK_SECRET_KEY = os.environ.get("CLERK_SECRET_KEY")
CLERK_REDIRECT_URI = os.environ.get("CLERK_REDIRECT_URI")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

@app.route("/auth/clerk/login")
def clerk_login():
    # Redirect to Clerk OAuth (Google example)
    return redirect(f"https://clerk.com/oauth/google?redirect_uri={CLERK_REDIRECT_URI}")

@app.route("/auth/clerk/callback")
def clerk_callback():
    token = request.args.get("token")
    if not token:
        return "Missing token", 400
    # Verify Clerk JWT
    try:
        payload = jwt.decode(token, CLERK_SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        email = payload.get("email")
        session["user_id"] = user_id
        session["email"] = email
    except Exception as e:
        return f"JWT error: {str(e)}", 400
    # Generate Supabase token (example: just return service role key)
    return jsonify({"user_id": user_id, "email": email, "supabase_token": SUPABASE_SERVICE_ROLE_KEY})

@app.route("/auth/session")
def get_session():
    if "user_id" in session:
        return jsonify({"user_id": session["user_id"], "email": session["email"]})
    return "No session", 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
