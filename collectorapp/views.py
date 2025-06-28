from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django import forms
from datetime import datetime

from .models import CollectorProfile
from userapp.models import PickupRequest

# Age validation function
def validate_age(value):
    today = datetime.today().date()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise forms.ValidationError("You must be at least 18 years old to register as a collector.")

# Form for profile creation
class CollectorProfileForm(forms.ModelForm):
    class Meta:
        model = CollectorProfile
        fields = ['phone_number', 'citizenship_id', 'date_of_birth']

    def clean_date_of_birth(self):
        dob = self.cleaned_data['date_of_birth']
        validate_age(dob)
        return dob

# Collector login logic
class CollectorLoginView(LoginView):
    template_name = 'collectorapp/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'collectorprofile'):
            return reverse_lazy('collector-dashboard')
        else:
            logout(self.request)
            messages.error(self.request, "You are not registered as a collector.")
            return reverse_lazy('collector-login')

# Collector dashboard view
@login_required
def collector_dashboard(request):
    pickup_requests = PickupRequest.objects.filter(
        status='Pending'
    ).order_by('-scheduled_date', '-scheduled_time')

    profile = getattr(request.user, 'collectorprofile', None)

    context = {
        'pickup_requests': pickup_requests,
        'profile': profile,
        'user': request.user,
    }
    return render(request, 'collectorapp/dashboard.html', context)

# Accept pickup request
@login_required
def accept_request(request, request_id):
    pickup_request = get_object_or_404(PickupRequest, id=request_id)
    if pickup_request.status == 'Pending':
        pickup_request.status = 'Accepted'
        pickup_request.assigned_collector = request.user
        pickup_request.save()
        messages.success(request, "Request accepted successfully.")
    else:
        messages.error(request, "This request cannot be accepted.")
    return redirect('collector-dashboard')

# Reject pickup request
@login_required
def reject_request(request, request_id):
    pickup_request = get_object_or_404(PickupRequest, id=request_id)
    if pickup_request.status == 'Pending' or (pickup_request.status == 'Accepted' and pickup_request.assigned_collector == request.user):
        pickup_request.status = 'Rejected'
        pickup_request.assigned_collector = None
        pickup_request.save()
        messages.success(request, "Request rejected successfully.")
    else:
        messages.error(request, "This request cannot be rejected.")
    return redirect('collector-dashboard')

# Logout collector
@login_required
def collector_logout(request):
    logout(request)
    return redirect('home')

# Collector registration without email verification
def collector_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('collector-register')

        user = User.objects.create_user(username=username, email=email, password=password)

        # Create collector profile with email already verified
        CollectorProfile.objects.create(user=user, email_verified=True)

        messages.success(request, 'Collector account created successfully. Please log in.')
        return redirect('collector-login')

    return render(request, 'collectorapp/register.html')

# Collector profile update
@login_required
def collector_profile(request):
    profile = request.user.collectorprofile

    if request.method == 'POST':
        phone = request.POST.get('phone')
        citizenship = request.POST.get('citizenship')
        dob = request.POST.get('dob')

        try:
            dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
            today = datetime.today().date()
            age = (today - dob_date).days // 365
            if age < 18:
                messages.error(request, "You must be at least 18 years old.")
                return redirect('collector-profile')
        except ValueError:
            messages.error(request, "Invalid date of birth format.")
            return redirect('collector-profile')

        if len(citizenship) < 8:
            messages.error(request, "Citizenship ID seems invalid.")
            return redirect('collector-profile')

        profile.phone_number = phone
        profile.citizenship_id = citizenship
        profile.date_of_birth = dob_date
        profile.save()

        messages.success(request, "Profile updated successfully.")
        return redirect('collector-profile')

    return render(request, 'collectorapp/profile.html', {'profile': profile})
