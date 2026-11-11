from django.urls import path

from . import views

urlpatterns = [
    path("start/", views.journey_start, name="journey-start"),
    path("<str:journey_id>/location/", views.journey_location, name="journey-location"),
    path("<str:journey_id>/", views.journey_state, name="journey-state"),
    path("<str:journey_id>/pause/", views.journey_pause, name="journey-pause"),
    path("<str:journey_id>/resume/", views.journey_resume, name="journey-resume"),
    path("<str:journey_id>/complete/", views.journey_complete, name="journey-complete"),
    path("<str:journey_id>/reroute/", views.journey_reroute, name="journey-reroute"),
]