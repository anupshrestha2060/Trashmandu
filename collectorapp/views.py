from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django import forms
from datetime import datetime
from django.db import transaction, IntegrityError
from django.views.decorators.http import require_POST
import random
from django.contrib.auth import update_session_auth_hash

from .models import CollectorProfile
from userapp.models import PickupRequest
from django.db.models import Sum

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
    # Detect whether the PickupRequest model has an 'assigned_collector' field.
    field_names = [f.name for f in PickupRequest._meta.get_fields()]
    per_collector_available = 'assigned_collector' in field_names

    # Calculate total kilograms collected by this collector (accepted requests)
    if per_collector_available:
        total_kg = PickupRequest.objects.filter(assigned_collector=request.user, status='Accepted').aggregate(total=Sum('weight'))['total'] or 0.0
    else:
        # assigned_collector not present; per-collector totals not available
        total_kg = 0.0

    rate_per_kg = 9.0  # Rs 9 per kg
    net_amount = round(total_kg * rate_per_kg, 2)

    context = {
        'pickup_requests': pickup_requests,
        'profile': profile,
        'user': request.user,
        'total_kg_collected': total_kg,
        'rate_per_kg': rate_per_kg,
        'net_amount': net_amount,
        'per_collector_available': per_collector_available,
    }
    return render(request, 'collectorapp/dashboard.html', context)

# Accept pickup request
@login_required
def accept_request(request, request_id):
    pickup_request = get_object_or_404(PickupRequest, id=request_id)
    # If model supports assigned_collector, set it; otherwise just mark accepted.
    field_names = [f.name for f in PickupRequest._meta.get_fields()]
    if pickup_request.status == 'Pending':
        pickup_request.status = 'Accepted'
        if 'assigned_collector' in field_names:
            try:
                setattr(pickup_request, 'assigned_collector', request.user)
            except Exception:
                # If assignment fails for any reason, ignore and proceed with status change
                pass
        pickup_request.save()
        messages.success(request, "Request accepted successfully.")
    else:
        messages.error(request, "This request cannot be accepted.")
    return redirect('collector-dashboard')

# Reject pickup request
@login_required
def reject_request(request, request_id):
    pickup_request = get_object_or_404(PickupRequest, id=request_id)
    field_names = [f.name for f in PickupRequest._meta.get_fields()]
    # allow reject if pending, or accepted & assigned to this user (if field exists)
    allowed = False
    if pickup_request.status == 'Pending':
        allowed = True
    elif pickup_request.status == 'Accepted' and 'assigned_collector' in field_names:
        try:
            if getattr(pickup_request, 'assigned_collector') == request.user:
                allowed = True
        except Exception:
            allowed = False

    if allowed:
        pickup_request.status = 'Rejected'
        if 'assigned_collector' in field_names:
            try:
                setattr(pickup_request, 'assigned_collector', None)
            except Exception:
                pass
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

        # A post_save signal may already create a CollectorProfile for this user.
        # Use an atomic block and handle IntegrityError to avoid UNIQUE constraint
        # failures in the rare race where the signal and this view both try to
        # create the profile at the same time.
        try:
            with transaction.atomic():
                profile, created = CollectorProfile.objects.get_or_create(user=user)
        except IntegrityError:
            # Another process created the profile concurrently — fetch it.
            profile = CollectorProfile.objects.get(user=user)

        if not profile.email_verified:
            profile.email_verified = True
            profile.save()

        messages.success(request, 'Collector account created successfully. Please log in.')
        return redirect('collector-login')

    return render(request, 'collectorapp/register.html')

# Collector profile update
@login_required
def collector_profile(request):
    profile = request.user.collectorprofile
    if request.method == 'POST':
        action = request.POST.get('action')

        # Update basic profile fields
        if action == 'update_profile':
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

            if citizenship and len(citizenship) < 8:
                messages.error(request, "Citizenship ID seems invalid.")
                return redirect('collector-profile')

            profile.phone_number = phone or profile.phone_number
            profile.citizenship_id = citizenship or profile.citizenship_id
            profile.date_of_birth = dob_date
            profile.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('collector-profile')

        # Change password
        if action == 'change_password':
            current = request.POST.get('current_password')
            new = request.POST.get('new_password')
            confirm = request.POST.get('confirm_password')
            user = request.user
            if not user.check_password(current):
                messages.error(request, "Current password is incorrect.")
                return redirect('collector-profile')
            if not new or new != confirm:
                messages.error(request, "New passwords do not match.")
                return redirect('collector-profile')
            user.set_password(new)
            user.save()
            # Keep the user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect('collector-profile')

        # Change email
        if action == 'change_email':
            new_email = request.POST.get('new_email')
            if not new_email or '@' not in new_email:
                messages.error(request, "Please provide a valid email address.")
                return redirect('collector-profile')
            user = request.user
            user.email = new_email
            user.save()
            # mark not verified and generate a new code
            profile.email_verified = False
            profile.verification_code = str(random.randint(100000, 999999))
            profile.save()
            messages.success(request, "Email updated. A new verification code was generated.")
            return redirect('collector-profile')

        # Request new verification code (without changing email)
        if action == 'request_verification':
            profile.verification_code = str(random.randint(100000, 999999))
            profile.email_verified = False
            profile.save()
            messages.success(request, "A new verification code has been generated.")
            return redirect('collector-profile')

    return render(request, 'collectorapp/profile.html', {'profile': profile, 'user': request.user})


@require_POST
@login_required
def verify_email(request):
    """Verify collector email using a code posted from the profile form."""
    profile = getattr(request.user, 'collectorprofile', None)
    if not profile:
        messages.error(request, "No collector profile found.")
        return redirect('collector-profile')

    code = request.POST.get('code')
    if code and str(getattr(profile, 'verification_code', '')) == str(code):
        profile.email_verified = True
        profile.save()
        messages.success(request, "Email verified successfully.")
    else:
        messages.error(request, "Invalid verification code.")

    return redirect('collector-profile')
