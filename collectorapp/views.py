from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from .models import CollectorProfile
from userapp.models import PickupRequest
import re

# -----------------------------
# HELPER FUNCTION
# -----------------------------
def is_valid_name(name):
    return bool(re.match(r"^[a-zA-Z\s]+$", name.strip()))

# -----------------------------
# COLLECTOR REGISTRATION
# -----------------------------
def collector_register(request):
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        citizenship_id = request.POST.get('citizenship_id', '').strip()
        date_of_birth = request.POST.get('date_of_birth', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not is_valid_name(name):
            messages.error(request, "Name must contain only letters and spaces.")
            return redirect('collector-register')
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('collector-register')
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return redirect('collector-register')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('collector-register')

        # Check email
        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            try:
                profile = CollectorProfile.objects.get(user=existing_user)
                if profile.is_verified:
                    messages.error(request, "Email already registered.")
                    return redirect('collector-register')
                else:
                    existing_user.delete()
            except CollectorProfile.DoesNotExist:
                messages.error(request, "Email already used by another account.")
                return redirect('collector-register')

        user = User.objects.create_user(username=username, email=email, password=password, first_name=name)
        user.is_active = False
        user.save()

        profile = CollectorProfile.objects.create(
            user=user,
            phone_number=phone_number,
            citizenship_id=citizenship_id,
            date_of_birth=date_of_birth if date_of_birth else '2000-01-01'
        )

        verification_link = request.build_absolute_uri(f"/collector/verify/{profile.verification_token}/")
        try:
            send_mail(
                "Trashmandu - Verify your Collector account",
                f"Hi {name},\n\nClick this link to verify your account:\n{verification_link}\n\nTrashmandu Team",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )
            messages.success(request, "Account created! Check your email to verify your account.")
            return redirect('collector-login')
        except Exception as e:
            user.delete()
            messages.error(request, f"Failed to send verification email. Error: {str(e)}")
            return redirect('collector-register')

    return render(request, 'collectorapp/register.html')


# -----------------------------
# COLLECTOR LOGIN
# -----------------------------
def collector_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            try:
                profile = CollectorProfile.objects.get(user=user)
            except CollectorProfile.DoesNotExist:
                messages.error(request, "Not a registered collector account.")
                return redirect('collector-login')

            if not profile.is_verified:
                messages.error(request, "Please verify your email before logging in.")
                return redirect('collector-login')

            login(request, user)
            messages.success(request, "Welcome back!")
            return redirect('collector-dashboard')
        else:
            messages.error(request, "Invalid credentials!")
            return redirect('collector-login')
    return render(request, 'collectorapp/login.html')


# -----------------------------
# COLLECTOR LOGOUT
# -----------------------------
@login_required
def collector_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('collector-login')


# -----------------------------
# DASHBOARD
# -----------------------------
@login_required
def collector_dashboard(request):
    collector_profile = get_object_or_404(CollectorProfile, user=request.user)
    
    # Pending pickup requests (all)
    pending_requests = PickupRequest.objects.filter(status='pending').order_by('-scheduled_date', '-scheduled_time')
    
    # Accepted pickup requests by this collector
    accepted_requests = PickupRequest.objects.filter(
        assigned_collector=request.user,
        status='accepted'
    ).order_by('-scheduled_date', '-scheduled_time')
    
    all_requests = list(pending_requests) + list(accepted_requests)

    # Total collected weight (sum over related PlasticItems)
    accepted_and_completed = PickupRequest.objects.filter(
        assigned_collector=request.user,
        status__in=['accepted', 'completed']
    )
    total_collected = sum(req.get_total_weight() for req in accepted_and_completed)

    rate_per_kg = 9
    net_amount = total_collected * rate_per_kg

    context = {
        "pickup_requests": all_requests,
        "profile": collector_profile,
        "total_kg_collected": total_collected,
        "rate_per_kg": rate_per_kg,
        "net_amount": net_amount,
    }
    return render(request, 'collectorapp/dashboard.html', context)

# -----------------------------
# ACCEPT REQUEST
# -----------------------------
@login_required
def accept_request(request, request_id):
    pickup = get_object_or_404(PickupRequest, id=request_id, status='pending')
    pickup.assigned_collector = request.user
    pickup.status = 'accepted'
    pickup.save()
    messages.success(request, "Request accepted successfully!")
    return redirect('collector-dashboard')


# -----------------------------
# REJECT REQUEST
# -----------------------------
@login_required
def reject_request(request, request_id):
    pickup = get_object_or_404(PickupRequest, id=request_id, assigned_collector=request.user)
    
    if pickup.status == 'accepted':
        pickup.assigned_collector = None
        pickup.status = 'pending'
        pickup.save()
        messages.success(request, "Request has been rejected and is now pending.")
    else:
        messages.error(request, "You cannot reject this request.")
    
    return redirect('collector-dashboard')


# -----------------------------
# PROFILE VIEW
# -----------------------------
@login_required
def collector_profile(request):
    return render(request, 'collectorapp/profile.html')


# -----------------------------
# VERIFY EMAIL
# -----------------------------
def verify_collector(request, token):
    try:
        profile = CollectorProfile.objects.get(verification_token=token)
    except CollectorProfile.DoesNotExist:
        messages.error(request, "Invalid or expired verification link.")
        return redirect('collector-login')

    if profile.is_verified:
        messages.info(request, "Already verified.")
    else:
        profile.is_verified = True
        profile.user.is_active = True
        profile.user.save()
        profile.save()
        messages.success(request, "Your account has been verified! You can now log in.")
    return redirect('collector-login')


# -----------------------------
# FORGOT PASSWORD
# -----------------------------
def collector_forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            profile = CollectorProfile.objects.get(user=user)

            if not profile.is_verified:
                messages.error(request, "This collector account is not verified yet.")
                return redirect('collector-forgot-password')

            profile.password_reset_token = get_random_string(50)
            profile.save()

            reset_link = request.build_absolute_uri(f"/collector/reset-password/{profile.password_reset_token}/")
            send_mail(
                "Trashmandu - Reset your password",
                f"Hi {user.first_name},\n\nClick here to reset your password:\n{reset_link}\n\nTrashmandu Team",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )
            messages.success(request, "Password reset link sent! Check your email.")
            return redirect('collector-login')
        except User.DoesNotExist:
            messages.error(request, "Email not found.")
            return redirect('collector-forgot-password')
        except CollectorProfile.DoesNotExist:
            messages.error(request, "This email is not registered as a collector account.")
            return redirect('collector-forgot-password')

    return render(request, 'collectorapp/forgot_password.html')


# -----------------------------
# RESET PASSWORD
# -----------------------------
def collector_reset_password(request, token):
    try:
        profile = CollectorProfile.objects.get(password_reset_token=token)
    except CollectorProfile.DoesNotExist:
        messages.error(request, "Invalid or expired reset link.")
        return redirect('collector-login')

    if request.method == "POST":
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('collector-reset-password', token=token)

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return redirect('collector-reset-password', token=token)

        profile.user.set_password(password)
        profile.user.save()
        profile.password_reset_token = None
        profile.save()
        messages.success(request, "Password reset successfully! You can now login.")
        return redirect('collector-login')

    return render(request, 'collectorapp/reset_password.html', {'token': token})
