import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trashmandu.settings')
django.setup()

# Import models
from django.contrib.auth.models import User
from userapp.models import UserProfile, PickupRequest
from collectorapp.models import CollectorProfile
from django.contrib.sessions.models import Session
from django.contrib.auth.models import Group, Permission

def clear_all_login_data():
    print("Starting to clear all login-related data...")
    
    # Clear all sessions first
    print("Clearing sessions...")
    Session.objects.all().delete()
    print("✓ Sessions cleared")
    
    # Clear pickup requests
    print("Clearing pickup requests...")
    PickupRequest.objects.all().delete()
    print("✓ Pickup requests cleared")
    
    # Clear collector profiles
    print("Clearing collector profiles...")
    CollectorProfile.objects.all().delete()
    print("✓ Collector profiles cleared")
    
    # Clear user profiles
    print("Clearing user profiles...")
    UserProfile.objects.all().delete()
    print("✓ User profiles cleared")
    
    # Clear all users except superuser
    print("Clearing users (except superuser)...")
    User.objects.exclude(is_superuser=True).delete()
    print("✓ Users cleared")
    
    print("\nAll login data has been cleared successfully!")

if __name__ == "__main__":
    # Ask for confirmation
    response = input("⚠️ WARNING: This will delete all users and related data (except superuser). Are you sure? (yes/no): ")
    if response.lower() == 'yes':
        clear_all_login_data()
    else:
        print("Operation cancelled.")