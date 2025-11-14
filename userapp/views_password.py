def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Safely fetch user even if multiple exist
        user = User.objects.filter(email=email).first()
        
        if user:
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Generate token
            token = str(uuid.uuid4())
            profile.reset_token = token
            profile.reset_token_expiry = timezone.now() + timedelta(hours=24)
            profile.save()

            # Send email
            reset_link = request.build_absolute_uri(f'/user/reset-password/{token}/')
            subject = 'Reset Your Trashmandu Password'
            message = f'''Hi {user.get_full_name() or user.username},

You requested to reset your password. Click the link below to reset it:

{reset_link}

This link expires in 24 hours.

If you did not request this, simply ignore this email.

Trashmandu Team'''

            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)

        # Always show same message to avoid leaking emails
        messages.success(request, "If the email exists, you'll receive reset instructions.")
        return redirect('user-login')

    return render(request, 'userapp/password/forgot_password.html')


def reset_password(request, token):
    profile = UserProfile.objects.filter(reset_token=token).first()

    if not profile:
        messages.error(request, "Invalid or expired password reset link.")
        return redirect('user-login')

    if profile.reset_token_expiry and profile.reset_token_expiry < timezone.now():
        messages.error(request, "Your reset link has expired. Please request a new one.")
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

        # Clear token
        profile.reset_token = None
        profile.reset_token_expiry = None
        profile.save()

        messages.success(request, "Password reset successfully. Please login.")
        return redirect('user-login')

    return render(request, 'userapp/password/reset_password.html')
