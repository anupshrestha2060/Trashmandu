from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import datetime
import re

from .models import UserProfile, PickupRequest, PlasticItem, PlasticType

# ---------------------------
# HELPER FUNCTION: Validate Name
# ---------------------------
def is_valid_name(name):
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

        if not name or not is_valid_name(name):
            messages.error(request, "Name should contain only letters and spaces.")
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

        user = User.objects.create_user(username=username, email=email, password=password, first_name=name)
        user.is_active = False
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        verification_link = request.build_absolute_uri(f"/user/verify/{profile.verification_token}/")

        try:
            send_mail(
                "Verify your Trashmandu account",
                f"Hi {name},\n\nClick here to verify your account:\n{verification_link}\n\nTrashmandu Team",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )
            messages.success(request, "Account created! Check your email to verify your account.")
            return redirect('user-login')
        except Exception as e:
            user.delete()
            messages.error(request, f"Failed to send verification email: {str(e)}")
            return redirect('user-register')

    return render(request, 'userapp/register.html')

# ---------------------------
# EMAIL VERIFICATION
# ---------------------------
def verify_user(request, token):
    profile = get_object_or_404(UserProfile, verification_token=token)
    if profile.is_verified:
        messages.info(request, "Account already verified.")
    else:
        profile.is_verified = True
        profile.user.is_active = True
        profile.user.save()
        profile.save()
        messages.success(request, "Verified! You can now log in.")
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

# ---------------------------
# FORGOT PASSWORD
# ---------------------------
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            profile = UserProfile.objects.get(user=user)
            profile.password_reset_token = get_random_string(50)
            profile.save()

            reset_link = request.build_absolute_uri(f"/user/reset-password/{profile.password_reset_token}/")
            send_mail(
                "Trashmandu - Reset your password",
                f"Hi {user.first_name}, click here to reset your password:\n{reset_link}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )
            messages.success(request, "Password reset link sent to your email.")
            return redirect('user-login')
        except User.DoesNotExist:
            messages.error(request, "Email not found.")
            return redirect('forgot-password')
        except Exception as e:
            messages.error(request, f"Failed to send reset email: {str(e)}")
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
        messages.success(request, "Password reset successful. You can now log in.")
        return redirect('user-login')

    return render(request, 'userapp/reset_password.html', {'token': token})

# ---------------------------
# USER DASHBOARD
# ---------------------------
# ---------------------------
# USER DASHBOARD
# ---------------------------
@login_required(login_url='user-login')
def user_dashboard(request):
    RATE_PER_KG = 9  # Set rate per kg here

    if request.method == "POST":
        phone = request.POST.get('phone')
        weight = request.POST.get('weight')
        date = request.POST.get('date')
        time_input = request.POST.get('time')
        location = request.POST.get('location')
        latitude = request.POST.get('latitude') or None
        longitude = request.POST.get('longitude') or None

        # Validate form inputs
        if not all([phone, weight, date, time_input, location]):
            messages.error(request, "Please fill all required fields.")
            return redirect('user-dashboard')

        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, "Phone number must be exactly 10 digits.")
            return redirect('user-dashboard')

        try:
            weight_val = float(weight)
            if weight_val <= 0:
                raise ValueError("Weight must be positive.")

            # Convert date/time safely
            scheduled_date = datetime.strptime(date, "%Y-%m-%d").date()
            scheduled_time = datetime.strptime(time_input, "%H:%M").time()
            now = timezone.localtime(timezone.now())
            scheduled_datetime = timezone.make_aware(datetime.combine(scheduled_date, scheduled_time))

            if scheduled_datetime < now:
                messages.error(request, "Cannot schedule pickup in the past.")
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

            # Handle PlasticType
            plastic_type, created = PlasticType.objects.get_or_create(name="Mixed")
            # Always update rate for new pickups
            plastic_type.price_per_kg = RATE_PER_KG
            plastic_type.save()

            # Create PlasticItem for this pickup
            PlasticItem.objects.create(
                pickup_request=pickup,
                plastic_type=plastic_type,
                weight=weight_val,
                price_at_time=RATE_PER_KG
            )

            # Optionally, store total_amount in PickupRequest if you have field
            pickup.total_amount = weight_val * RATE_PER_KG
            pickup.save()

            messages.success(request, "Pickup request scheduled successfully!")
            return redirect('user-dashboard')

        except ValueError as e:
            messages.error(request, f"Invalid input: {str(e)}")
            return redirect('user-dashboard')

    # Fetch all pickup requests for this user
    pickup_requests = PickupRequest.objects.filter(user=request.user).order_by('-scheduled_date', '-scheduled_time')
    return render(request, 'userapp/dashboard.html', {'pickup_requests': pickup_requests})

# ---------------------------
# USER LOGOUT
# ---------------------------
@login_required(login_url='user-login')
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')
