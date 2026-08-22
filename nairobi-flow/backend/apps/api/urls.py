from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("roads", views.RoadSegmentViewSet, basename="road")
router.register("corridors", views.CorridorViewSet, basename="corridor")
router.register("incidents", views.IncidentViewSet, basename="incident")
router.register("models", views.ModelVersionViewSet, basename="model")

urlpatterns = [
    path("health/", views.health, name="health"),
    path("network/segments.geojson", views.network_geojson, name="network-geojson"),
    path("traffic/current/", views.current_traffic, name="traffic-current"),
    path("traffic/history/", views.traffic_history, name="traffic-history"),
    path("traffic/predictions/", views.traffic_predictions, name="traffic-predictions"),
    path("routes/recommend/", views.recommend_route, name="routes-recommend"),
    path("routes/", views.list_routes, name="routes-list"),
    path("simulation/", views.list_simulations, name="simulation-list"),
    path("simulation/run/", views.run_simulation, name="simulation-run"),
    path("metrics/", views.metrics, name="metrics"),
    *router.urls,
]
