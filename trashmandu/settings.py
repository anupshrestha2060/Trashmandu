from pathlib import Path
from django.contrib.messages import constants as messages

# -------------------------
# BASE CONFIG
# -------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-#2xif5$##u2@y29&2=0wcsv%t)eho^&d3@vv#+1=tyw71oc7pu'
DEBUG = True
ALLOWED_HOSTS = []

# -------------------------
# INSTALLED APPS
# -------------------------
INSTALLED_APPS = [
    # Django default
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # required for allauth

    # Custom apps
    'collection',
    'userapp',
    'collectorapp',
    'adminapp',

    # Allauth for registration/email verification
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
]

# -------------------------
# SITE & AUTH
# -------------------------
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # default
    'allauth.account.auth_backends.AuthenticationBackend',  # allauth
]

# Allauth configuration
ACCOUNT_SIGNUP_FIELDS = ['username*', 'email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_ON_EMAIL = True
LOGIN_REDIRECT_URL = '/user/dashboard/'
LOGOUT_REDIRECT_URL = '/user/login/'
ACCOUNT_EMAIL_SUBJECT_PREFIX = "Trashmandu "

# -------------------------
# MIDDLEWARE
# -------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Add Allauth middleware here (must be **after** AuthenticationMiddleware)
    'allauth.account.middleware.AccountMiddleware',
]

# -------------------------
# URL & TEMPLATES
# -------------------------
ROOT_URLCONF = 'trashmandu.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # required by allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'trashmandu.wsgi.application'

# -------------------------
# DATABASE (MySQL)
# -------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'trashmandu_db',      # Make sure this DB exists
        'USER': 'root',               # Your MySQL username
        'PASSWORD': 'anup',           # Your MySQL password
        'HOST': '127.0.0.1',          # localhost
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# -------------------------
# PASSWORD VALIDATORS
# -------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------
# LOCALIZATION
# -------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kathmandu'
USE_I18N = True
USE_TZ = True

# -------------------------
# STATIC FILES
# -------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# -------------------------
# DEFAULT PRIMARY KEY
# -------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------------
# MESSAGE TAGS
# -------------------------
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
    messages.SUCCESS: 'success',
}

# -------------------------
# EMAIL CONFIGURATION (GMAIL SMTP)
# -------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'anupshrestha865@gmail.com'
EMAIL_HOST_PASSWORD = 'pjcvhjrhcughgcji'  # 16-char Gmail app password
DEFAULT_FROM_EMAIL = 'Trashmandu <no-reply@trashmandu.com>'
