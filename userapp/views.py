from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import uuid

from .models import PickupRequest, PlasticItem, PlasticType, UserProfile


# -----------------------------------------------------------
# FORGOT PASSWORD (SENDS TEMPORARY PASSWORD)
# -----------------------------------------------------------
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        user = User.objects.filter(email=email).first()  # safe lookup

        if user:
            # Generate temporary password
            temp_password = str(uuid.uuid4())[:8]
            user.set_password(temp_password)
            user.save()

            subject = "Your New Trashmandu Password"
            message = f"""
Hi {user.username},

Your temporary password is: {temp_password}

Please log in and change it immediately.

Trashmandu Team
"""
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                      [user.email], fail_silently=False)

        messages.success(request, "If the email exists, a temporary password was sent.")
        return redirect('user-login')

    return render(request, 'userapp/password/forgot_password.html')


# -----------------------------------------------------------
# (OPTIONAL TOKEN SYSTEM — CURRENTLY UNUSED)
# KEEPING IT FOR FUTURE EXPANSION
# -----------------------------------------------------------
def reset_password(request, token):
    profile = UserProfile.objects.filter(reset_token=token).first()

    if not profile:
        messages.error(request, "Invalid or expired reset link.")
        return redirect('user-login')

    if profile.reset_token_expiry < timezone.now():
        messages.error(request, "Password reset link expired.")
        return redirect('forgot-password')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('reset-password', token=token)

        user = profile.user
        user.set_password(new_password)
        user.save()

        profile.reset_token = None
        profile.reset_token_expiry = None
        profile.save()

        messages.success(request, "Password reset successful! Login now.")
        return redirect('user-login')

    return render(request, 'userapp/password/reset_password.html')


# -----------------------------------------------------------
# USER LOGIN
# -----------------------------------------------------------
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('user-dashboard')
        else:
            messages.error(request, "Invalid credentials. Try again.")
            return redirect('user-login')

    return render(request, 'userapp/login.html')


# -----------------------------------------------------------
# USER REGISTRATION
# -----------------------------------------------------------
def user_register(request):
    if request.method == 'POST':
        name = request.POST['name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm = request.POST['confirm']

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('user-register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('user-register')

        user = User.objects.create_user(username=username, email=email,
                                        password=password, first_name=name)

        UserProfile.objects.get_or_create(user=user)

        messages.success(request, "Account created! Please log in.")
        return redirect('user-login')

    return render(request, 'userapp/register.html')


# -----------------------------------------------------------
# USER DASHBOARD
# -----------------------------------------------------------
@login_required(login_url='user-login')
def user_dashboard(request):
    RATE_PER_KG = 9

    if request.method == "POST":
        weight = request.POST.get('weight')
        phone = request.POST.get('phone')
        date = request.POST.get('date')
        time = request.POST.get('time')
        location = request.POST.get('location')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        if not all([phone, weight, date, time, location]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('user-dashboard')

        try:
            weight_val = float(weight)
            if weight_val <= 0:
                raise ValueError("Weight must be positive")

            scheduled_date = datetime.strptime(date, '%Y-%m-%d').date()
            scheduled_time = datetime.strptime(time, '%H:%M').time()

            pickup = PickupRequest.objects.create(
                user=request.user,
                phone=phone,
                location=location,
                scheduled_date=scheduled_date,
                scheduled_time=scheduled_time,
                latitude=latitude or None,
                longitude=longitude or None,
                status='Pending'
            )

            plastic_type = PlasticType.objects.first()
            if not plastic_type:
                plastic_type = PlasticType.objects.create(name='Mixed', price_per_kg=RATE_PER_KG)

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

    # Calculate totals using annotation
    from django.db.models import Sum, F, ExpressionWrapper, FloatField
    pickup_requests = PickupRequest.objects.filter(user=request.user).annotate(
        total_weight=Sum('plasticitem__weight'),
        total_amount=Sum(
            ExpressionWrapper(
                F('plasticitem__weight') * F('plasticitem__price_at_time'),
                output_field=FloatField()
            )
        )
    ).order_by('-scheduled_date', '-scheduled_time')

    return render(request, 'userapp/dashboard.html', {'pickup_requests': pickup_requests})


# -----------------------------------------------------------
# LOGOUT
# -----------------------------------------------------------
@login_required(login_url='user-login')
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')


# -----------------------------------------------------------
# PICKUP REQUEST FORM
# -----------------------------------------------------------
@login_required(login_url='user-login')
def pickup_request(request):
    if request.method == 'POST':
        weight = request.POST.get('weight')
        phone = request.POST.get('phone')
        location = request.POST.get('location')
        date = request.POST.get('date')
        time = request.POST.get('time')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        if weight and location and date and time:
            try:
                pickup = PickupRequest.objects.create(
                    user=request.user,
                    phone=phone,
                    location=location,
                    scheduled_date=datetime.strptime(date, '%Y-%m-%d').date(),
                    scheduled_time=datetime.strptime(time, '%H:%M').time(),
                    latitude=latitude or None,
                    longitude=longitude or None,
                    status='Pending'
                )

                plastic_type = PlasticType.objects.first()
                if not plastic_type:
                    plastic_type = PlasticType.objects.create(name='Mixed', price_per_kg=9)

                PlasticItem.objects.create(
                    pickup_request=pickup,
                    plastic_type=plastic_type,
                    weight=float(weight),
                    price_at_time=plastic_type.price_per_kg
                )

                messages.success(request, "Pickup request submitted successfully!")
                return redirect('user-dashboard')

            except ValueError:
                messages.error(request, "Invalid date or time.")

        else:
            messages.error(request, "Please fill all fields.")

    return render(request, 'userapp/pickup_request.html')
