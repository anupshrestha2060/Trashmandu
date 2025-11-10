from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import PickupRequest, PlasticItem, PlasticType
from .models import UserProfile
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
import uuid
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import PickupRequest
from django.utils import timezone

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Generate a temporary password
            temp_password = str(uuid.uuid4())[:8]  # First 8 characters of UUID
            user.set_password(temp_password)
            user.save()
            
            # Send new password by email
            subject = 'Your New Trashmandu Password'
            message = f'''Hi {user.get_full_name() or user.username},

Your temporary password is: {temp_password}

Please login with this password and change it immediately.

Thanks,
Trashmandu Team'''
            
            from_email = settings.DEFAULT_FROM_EMAIL
            send_mail(subject, message, from_email, [user.email], fail_silently=False)
            messages.success(request, "If the email exists in our system, you will receive your new password by email.")
            return redirect('user-login')
            
        except User.DoesNotExist:
            # Don't reveal if email exists or not
            messages.success(request, "If the email exists in our system, you will receive your new password by email.")
            return redirect('user-login')
            
    return render(request, 'userapp/password/forgot_password.html')

def reset_password(request, token):
    try:
        profile = UserProfile.objects.get(reset_token=token)
        if profile.reset_token_expiry and profile.reset_token_expiry < timezone.now():
            messages.error(request, "Password reset link has expired. Please request a new one.")
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
            
            # Clear the reset token
            profile.reset_token = ''
            profile.reset_token_expiry = None
            profile.save()
            
            messages.success(request, "Password reset successfully. Please login with your new password.")
            return redirect('user-login')
            
        return render(request, 'userapp/password/reset_password.html')
        
    except UserProfile.DoesNotExist:
        messages.error(request, "Invalid password reset link.")
        return redirect('user-login')
from datetime import datetime
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('user-dashboard')
        else:
            messages.error(request, 'Invalid credentials. Please try again or register.')
            return redirect('user-login')
    return render(request, 'userapp/login.html')

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

        user = User.objects.create_user(username=username, email=email, password=password, first_name=name)
        user.save()
        # Create user profile
        try:
            profile = user.userprofile
        except Exception:
            profile = UserProfile.objects.create(user=user)
        messages.success(request, "Account created successfully. Please log in.")
        return redirect('user-login')

    return render(request, 'userapp/register.html')

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

            # Create PickupRequest (no weight/total_amount fields on model)
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

            # Ensure a PlasticType exists; fall back to a default if not
            plastic_type = PlasticType.objects.first()
            if not plastic_type:
                plastic_type = PlasticType.objects.create(name='Mixed', price_per_kg=RATE_PER_KG)

            # Create a PlasticItem for this pickup
            PlasticItem.objects.create(
                pickup_request=pickup,
                plastic_type=plastic_type,
                weight=weight_val,
                price_at_time=plastic_type.price_per_kg
            )

            messages.success(request, "Pickup request scheduled successfully!")
            return redirect('user-dashboard')

        except ValueError as e:
            messages.error(request, f"Invalid input: {str(e)}")
            return redirect('user-dashboard')

    # Annotate pickup requests with totals from related PlasticItem rows
    from django.db.models import Sum, F, ExpressionWrapper, FloatField
    pickup_requests = PickupRequest.objects.filter(user=request.user).annotate(
        total_weight=Sum('plasticitem__weight'),
        total_amount=Sum(ExpressionWrapper(F('plasticitem__weight') * F('plasticitem__price_at_time'), output_field=FloatField()))
    ).order_by('-scheduled_date', '-scheduled_time')

    return render(request, 'userapp/dashboard.html', {'pickup_requests': pickup_requests})

@login_required(login_url='user-login')
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')
@login_required(login_url='user-login')
def pickup_request(request):
    if request.method == 'POST':
        weight = request.POST.get('weight')
        phone= request.POST.get('phone')
        
        location = request.POST.get('location')
        date = request.POST.get('date')
        time = request.POST.get('time')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        if weight and location and date and time:
            try:
                # create PickupRequest and associated PlasticItem
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
                messages.error(request, "Invalid date or time format.")
        else:
            messages.error(request, "Please fill all fields.")

    return render(request, 'userapp/pickup_request.html')


# Removing unused email verification view since verification is not implemented
# def user_verify_email(request):
#     pass


# Removing unused password set view since it's handled in registration
# @login_required(login_url='user-login')
# def user_set_password(request):
#     pass