from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from datetime import datetime
import re

from .models import UserProfile, PickupRequest, PlasticItem, PlasticType
import uuid

# ---------------------------
# HELPER FUNCTION: Validate Name (no numbers)
# ---------------------------
def is_valid_name(name):
    """Check if name contains only letters and spaces"""
    return bool(re.match(r"^[a-zA-Z\s]+$", name.strip()))

# ---------------------------
# USER REGISTRATION
# ---------------------------
def user_register(request):
    if request.method == "POST":
        name = request.POST.get('name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')

        # Validate name (no numbers)
        if not name or not is_valid_name(name):
            messages.error(request, "Name should only contain letters and spaces, no numbers.")
            return redirect('user-register')

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('user-register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('user-register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('user-register')

        # Create inactive user and send verification email
        user = User.objects.create_user(username=username, email=email, password=password, first_name=name)
        user.is_active = False
        user.save()

        # The signal will automatically create UserProfile, so we just get it
        profile = UserProfile.objects.get(user=user)

        # Build verification link (prefer SITE_URL if set)
        verification_link = (f"{getattr(settings, 'SITE_URL').rstrip('/')}/user/verify/{profile.verification_token}/" if getattr(settings, 'SITE_URL', None) else request.build_absolute_uri(f"/user/verify/{profile.verification_token}/"))

        # Send email
        try:
            send_mail(
                "Trashmandu - Verify your email",
                f"Hi {name},\n\nClick this link to verify your account:\n{verification_link}\n\nThis link will expire in 24 hours.\n\nBest regards,\nTrashmandu Team",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )
            messages.success(request, "Account created! Check your email to verify your account.")
            # Notify all verified collectors about new user registration
            try:
                from collectorapp.models import CollectorProfile
                collector_emails = list(CollectorProfile.objects.filter(is_verified=True).values_list('user__email', flat=True))
                # Remove empty or duplicate emails and exclude the registering user's email
                collector_emails = [e for e in set(collector_emails) if e and e != email]
                if collector_emails:
                    notify_subject = "Trashmandu - New user registered"
                    notify_message = (
                        f"A new user has registered: {name} ({username})\n\n"
                        f"You can view users in the collector dashboard.\n\n"
                        "Best regards,\nTrashmandu Team"
                    )
                    # send as a single email with collectors as BCC
                    send_mail(
                        notify_subject,
                        notify_message,
                        settings.DEFAULT_FROM_EMAIL,
                        [],
                        bcc=collector_emails,
                        fail_silently=True,
                    )
            except Exception:
                # Do not block user registration if collector notifications fail
                pass
        except Exception as e:
            user.delete()
            messages.error(request, "Failed to send verification email. Please try again.")
            return redirect('user-register')

        return redirect('user-login')

    return render(request, 'userapp/register.html')


# ---------------------------
# EMAIL VERIFICATION
# ---------------------------
def verify_user(request, token):
    profile = get_object_or_404(UserProfile, verification_token=token)
    if profile.is_verified:
        messages.info(request, "Your account is already verified.")
        return redirect('user-login')

    profile.is_verified = True
    profile.user.is_active = True
    profile.user.save()
    profile.save()

    messages.success(request, "Your account has been verified! You can now log in.")
    return redirect('user-login')


# ---------------------------
# USER LOGIN
# ---------------------------
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            profile = get_object_or_404(UserProfile, user=user)
            if not profile.is_verified:
                messages.error(request, "Please verify your email before logging in.")
                return redirect('user-login')

            login(request, user)
            return redirect('user-dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('user-login')

    return render(request, 'userapp/login.html')

def is_valid_name(name):
    return bool(re.match(r"^[a-zA-Z\s]+$", name.strip()))

def user_register(request):
    if request.method == "POST":
        name = request.POST.get('name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')

        if not is_valid_name(name):
            messages.error(request, "Name must contain only letters.")
            return redirect('user-register')
        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('user-register')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username taken.")
            return redirect('user-register')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email registered.")
            return redirect('user-register')

        user = User.objects.create_user(username=username, email=email, password=password, first_name=name)
        user.is_active = False
        user.save()

        profile = UserProfile.objects.create(user=user)
        verification_link = request.build_absolute_uri(f"/user/verify/{profile.verification_token}/")

        try:
            send_mail(
                "Verify your Trashmandu account",
                f"Hi {name}, click here to verify: {verification_link}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )
            messages.success(request, "Check email to verify account.")
            return redirect('user-login')
        except:
            user.delete()
            messages.error(request, "Failed to send email.")
            return redirect('user-register')
    return render(request, 'userapp/register.html')

def verify_user(request, token):
    profile = get_object_or_404(UserProfile, verification_token=token)
    if profile.is_verified:
        messages.info(request, "Already verified.")
    else:
        profile.is_verified = True
        profile.user.is_active = True
        profile.user.save()
        profile.save()
        messages.success(request, "Verified! You can login.")
    return redirect('user-login')
# ---------------------------
# FORGOT PASSWORD
# ---------------------------
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
            profile = UserProfile.objects.get(user=user)
            
            # Generate a password reset token
            profile.password_reset_token = get_random_string(50)
            profile.save()

            # Build reset link (prefer SITE_URL if set)
            reset_link = (f"{getattr(settings, 'SITE_URL').rstrip('/')}/user/reset-password/{profile.password_reset_token}/" if getattr(settings, 'SITE_URL', None) else request.build_absolute_uri(f"/user/reset-password/{profile.password_reset_token}/"))

            # Send email
            send_mail(
                "Trashmandu - Reset your password",
                f"Hi {user.first_name},\n\nClick this link to reset your password:\n{reset_link}\n\nThis link will expire in 24 hours.\n\nIf you didn't request a password reset, please ignore this email.\n\nBest regards,\nTrashmandu Team",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )
            messages.success(request, "Password reset link has been sent to your email.")
            return redirect('user-login')
        
        except User.DoesNotExist:
            messages.error(request, "Email not found.")
            return redirect('forgot-password')
        except Exception as e:
            messages.error(request, "Failed to send reset email. Please try again.")
            return redirect('forgot-password')

    return render(request, 'userapp/forgot_password.html')


# ---------------------------
# RESET PASSWORD
# ---------------------------
def reset_password(request, token):
    try:
        profile = UserProfile.objects.get(password_reset_token=token)
    except UserProfile.DoesNotExist:
        messages.error(request, "Invalid or expired reset link.")
        return redirect('user-login')

    if request.method == "POST":
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('reset-password', token=token)

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return redirect('reset-password', token=token)

        profile.user.set_password(password)
        profile.user.save()
        profile.password_reset_token = None
        profile.save()

        messages.success(request, "Password has been reset. You can now log in with your new password.")
        return redirect('user-login')

    return render(request, 'userapp/reset_password.html', {'token': token})


# ---------------------------
# USER DASHBOARD
# ---------------------------
from django.utils import timezone

@login_required(login_url='user-login')
def user_dashboard(request):
    RATE_PER_KG = 12

    if request.method == "POST":
        weight = request.POST.get('weight')
        phone = request.POST.get('phone')
        date = request.POST.get('date')
        time = request.POST.get('time')
        location = request.POST.get('location')
        latitude = request.POST.get('latitude') or None
        longitude = request.POST.get('longitude') or None

        # Validate all fields
        if not all([weight, phone, date, time, location]):
            messages.error(request, "Please fill all required fields.")
            return redirect('user-dashboard')

        # Validate phone number (exactly 10 digits)
        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, "Phone number must be exactly 10 digits.")
            return redirect('user-dashboard')

        try:
            # Validate weight
            weight_val = float(weight)
            if weight_val <= 0:
                raise ValueError("Weight must be positive")

            # Parse date and time
            scheduled_date = datetime.strptime(date, "%Y-%m-%d").date()
            scheduled_time = datetime.strptime(time, "%H:%M").time()

            # Prevent scheduling for past date/time
            now = timezone.now()
            scheduled_datetime = datetime.combine(scheduled_date, scheduled_time)
            if scheduled_datetime < now:
                messages.error(request, "You cannot schedule a pickup for a past date/time.")
                return redirect('user-dashboard')

            # Create PickupRequest
            pickup = PickupRequest.objects.create(
                user=request.user,
                phone=phone,
                location=location,
                latitude=latitude,
                longitude=longitude,
                scheduled_date=scheduled_date,
                scheduled_time=scheduled_time,
                status='pending'
            )

            # Get or create default PlasticType
            plastic_type = PlasticType.objects.first()
            if not plastic_type:
                plastic_type = PlasticType.objects.create(name="Mixed", price_per_kg=RATE_PER_KG)

            # Create PlasticItem
            PlasticItem.objects.create(
                pickup_request=pickup,
                plastic_type=plastic_type,
                weight=weight_val,
                price_at_time=plastic_type.price_per_kg
            )

            messages.success(request, "Pickup request scheduled!")
            return redirect('user-dashboard')

        except ValueError as e:
            messages.error(request, f"Invalid input: {str(e)}")
            return redirect('user-dashboard')

    # Show all user's pickups
    pickups = PickupRequest.objects.filter(user=request.user).order_by('-scheduled_date', '-scheduled_time')
    return render(request, 'userapp/dashboard.html', {'pickup_requests': pickups})


# ---------------------------
# USER LOGOUT
# ---------------------------
@login_required(login_url='user-login')
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')
