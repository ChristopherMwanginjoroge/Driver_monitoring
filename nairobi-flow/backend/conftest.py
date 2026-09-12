"""pytest configuration and fixtures for testing."""

import os
import django
from django.conf import settings


def pytest_configure():
    """Configure pytest with Django settings."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nairobi_flow.settings")

    # Configure test database settings
    if not settings.configured:
        from pathlib import Path
        BASE_DIR = Path(__file__).resolve().parent
        
        settings.configure(
            DEBUG=True,
            DATABASES={
                "default": {
                    "ENGINE": "django.contrib.gis.db.backends.spatialite",
                    "NAME": ":memory:",
                }
            },
            INSTALLED_APPS=[
                "django.contrib.admin",
                "django.contrib.auth",
                "django.contrib.contenttypes",
                "django.contrib.sessions",
                "django.contrib.messages",
                "django.contrib.staticfiles",
                "django.contrib.gis",
                "rest_framework",
                "django_filters",
                "corsheaders",
                "drf_spectacular",
                "django_prometheus",
                "apps.network",
                "apps.observations",
                "apps.traffic_state",
                "apps.prediction",
                "apps.routing",
                "apps.simulation",
                "apps.api",
            ],
            MIDDLEWARE=[
                "django_prometheus.middleware.PrometheusBeforeMiddleware",
                "corsheaders.middleware.CorsMiddleware",
                "django.middleware.security.SecurityMiddleware",
                "django.contrib.sessions.middleware.SessionMiddleware",
                "django.middleware.common.CommonMiddleware",
                "django.middleware.csrf.CsrfViewMiddleware",
                "django.contrib.auth.middleware.AuthenticationMiddleware",
                "django.contrib.messages.middleware.MessageMiddleware",
                "django.middleware.clickjacking.XFrameOptionsMiddleware",
                "django_prometheus.middleware.PrometheusAfterMiddleware",
            ],
            ROOT_URLCONF="nairobi_flow.urls",
            SECRET_KEY="test-secret-key",
            ALLOWED_HOSTS=["*"],
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [],
                    "APP_DIRS": True,
                    "OPTIONS": {
                        "context_processors": [
                            "django.template.context_processors.debug",
                            "django.template.context_processors.request",
                            "django.contrib.auth.context_processors.auth",
                            "django.contrib.messages.context_processors.messages",
                        ],
                    },
                },
            ],
            REST_FRAMEWORK={
                "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
                "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
            },
            DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        )
    
    django.setup()
