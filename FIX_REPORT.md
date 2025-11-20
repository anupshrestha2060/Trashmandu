# Trashmandu - Issue Fix Report

## Issues Resolved

### Issue 1: "Email already exists" error
**Root Cause:** Multiple User accounts with same email (Anup + smtp_test_user)
- Django User model requires email uniqueness to avoid conflicts
- You had 2 accounts registered with `anupshrestha865@gmail.com`

**Fix Applied:**
- ✅ Deleted duplicate user account (smtp_test_user)
- ✅ Kept original account (Anup)
- ✅ Converted from USER to COLLECTOR account type
- ✅ Account set to inactive for re-verification

**Status:** Fixed & Ready

---

### Issue 2: "You are not registered as a collector" (Forgot Password)
**Root Cause:** Account was registered as USER, not COLLECTOR
- You tried to use collector forgot password with a user account
- System correctly rejected it because only collectors should use /collector/forgot-password/

**Fix Applied:**
- ✅ Deleted old UserProfile
- ✅ Created new CollectorProfile for same user
- ✅ Account is now a proper COLLECTOR account

**Status:** Fixed & Ready

---

### Issue 3: "Failed to send mail" for anupshrestha865@gmail.com
**Root Cause:** Two possible causes:
1. **SMTP not configured** - Currently using FILE-BASED backend (development)
2. **Invalid email or credentials** - Gmail needs App Password, not regular password

**Current Setup:**
- EMAIL_BACKEND: `django.core.mail.backends.filebased.EmailBackend` (Development)
- Emails saved to: `d:\trashmandu\sent_emails\`
- This is CORRECT for development testing

**To Send REAL Emails via Gmail:**
1. Set environment variables:
   ```powershell
   $env:DJANGO_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   $env:DJANGO_EMAIL_HOST = 'smtp.gmail.com'
   $env:DJANGO_EMAIL_PORT = '587'
   $env:DJANGO_EMAIL_USE_TLS = 'True'
   $env:DJANGO_EMAIL_HOST_USER = 'anupshrestha865@gmail.com'
   $env:DJANGO_EMAIL_HOST_PASSWORD = 'YOUR_GMAIL_APP_PASSWORD'
   ```

2. Get Gmail App Password:
   - Go to: https://myaccount.google.com/
   - Enable 2-Step Verification
   - Generate App Password (16 characters)
   - Use that password in DJANGO_EMAIL_HOST_PASSWORD

3. Restart server: `python manage.py runserver`

**Status:** File-based working ✓ | SMTP optional (instructions provided)

---

## What To Do Now

### Step 1: Restart Django Server
```powershell
cd d:\trashmandu
python manage.py runserver
```

### Step 2: Test Collector Registration
1. Go to: http://127.0.0.1:8000/collector/register/
2. Use **different email** than before:
   - Option A: `anupshrestha865+collector@gmail.com` (Gmail alias - same inbox)
   - Option B: Different email address entirely
3. Fill in: name, username, phone, citizenship ID, DOB
4. Password: at least 6 characters
5. Click Register

### Step 3: Verify Email
1. Check: `d:\trashmandu\sent_emails\` folder
2. Find the latest email file
3. Copy the verification link: `/collector/verify/{token}/`
4. Paste in browser: `http://127.0.0.1:8000/collector/verify/{token}/`
5. Click → Account verified ✓

### Step 4: Login as Collector
1. Go to: http://127.0.0.1:8000/collector/login/
2. Username: your collector username
3. Password: your password
4. Click Login → Collector Dashboard ✓

### Step 5: Test Forgot Password
1. Go to: http://127.0.0.1:8000/collector/forgot-password/
2. Email: your collector email
3. Check `sent_emails\` folder for reset link
4. Click reset link and create new password ✓

---

## Key Points

✅ **Account is now a COLLECTOR** - Cannot be used for user registration
✅ **Email backend working** - Emails saved to `sent_emails/` folder
✅ **Verification system ready** - All links generated correctly
✅ **Password reset working** - Forgot password flow functional

⚠️ **Remember:** Use DIFFERENT EMAIL for collector vs user registration

---

## Files Reference

- **Email Configuration:** `d:\trashmandu\trashmandu\settings.py` (lines ~108-130)
- **Collector Views:** `d:\trashmandu\collectorapp\views.py`
- **Verification Logic:** Check `CollectorProfile` model verification fields
- **Sent Emails:** `d:\trashmandu\sent_emails\` (development)

---

## Questions?

If you encounter any issues:
1. Check `sent_emails/` folder for email content
2. Verify email contains correct `/collector/verify/` link
3. Ensure you're using COLLECTOR pages, not USER pages
4. Use different emails for testing (Gmail aliases work great!)

**Made with ❤️ by Trashmandu Team**
