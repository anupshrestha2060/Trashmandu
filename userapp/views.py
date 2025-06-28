from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import PickupRequest
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import PickupRequest
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
            total_amount = weight_val * RATE_PER_KG

            PickupRequest.objects.create(
                user=request.user,
                phone=phone,
                weight=weight_val,
                total_amount=total_amount,
                location=location,
                scheduled_date=scheduled_date,
                scheduled_time=scheduled_time,
                latitude=latitude or None,
                longitude=longitude or None,
                status='Pending'
            )

            messages.success(request, "Pickup request scheduled successfully!")
            return redirect('user-dashboard')

        except ValueError as e:
            messages.error(request, f"Invalid input: {str(e)}")
            return redirect('user-dashboard')

    pickup_requests = PickupRequest.objects.filter(user=request.user).order_by('-scheduled_date', '-scheduled_time')

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
                PickupRequest.objects.create(
                    user=request.user,
                    weight=float(weight),
                    location=location,
                    scheduled_date=datetime.strptime(date, '%Y-%m-%d').date(),
                    scheduled_time=datetime.strptime(time, '%H:%M').time(),
                    latitude=latitude or None,
                    longitude=longitude or None,
                    status='Pending'
                )
                messages.success(request, "Pickup request submitted successfully!")
                return redirect('user-dashboard')
            except ValueError:
                messages.error(request, "Invalid date or time format.")
        else:
            messages.error(request, "Please fill all fields.")

    return render(request, 'userapp/pickup_request.html')