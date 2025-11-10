def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            profile = UserProfile.objects.get(user=user)
            
            # Generate unique token and set expiry
            token = str(uuid.uuid4())
            profile.reset_token = token
            profile.reset_token_expiry = timezone.now() + timedelta(hours=24)
            profile.save()
            
            # Send reset email
            reset_link = request.build_absolute_uri(f'/user/reset-password/{token}/')
            subject = 'Reset Your Trashmandu Password'
            message = f'''Hi {user.get_full_name() or user.username},

You requested to reset your password. Click the link below to reset your password:

{reset_link}

This link will expire in 24 hours.

If you didn't request this, you can safely ignore this email.

Thanks,
Trashmandu Team'''
            
            from_email = settings.DEFAULT_FROM_EMAIL
            send_mail(subject, message, from_email, [user.email], fail_silently=False)
            messages.success(request, "If the email exists in our system, you will receive password reset instructions.")
            return redirect('user-login')
            
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            # Don't reveal if email exists or not
            messages.success(request, "If the email exists in our system, you will receive password reset instructions.")
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