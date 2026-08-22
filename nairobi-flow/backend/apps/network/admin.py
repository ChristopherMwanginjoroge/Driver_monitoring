from django.contrib.gis import admin

from .models import Corridor, CorridorSegment, Intersection, RoadSegment

admin.site.register(RoadSegment, admin.GISModelAdmin)
admin.site.register(Intersection, admin.GISModelAdmin)
admin.site.register(Corridor)
admin.site.register(CorridorSegment)
