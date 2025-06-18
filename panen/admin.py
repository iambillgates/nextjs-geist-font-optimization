from django.contrib import admin
from .models import (
    Location,
    HarvestRecord,
    SensorData,
    SupplyChain,
    Recommendation,
    PredictionModel
)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'area_size', 'latitude', 'longitude')
    search_fields = ('name',)

@admin.register(HarvestRecord)
class HarvestRecordAdmin(admin.ModelAdmin):
    list_display = ('location', 'date', 'quantity', 'quality_score', 'weather_condition')
    list_filter = ('location', 'date', 'quality_score')
    search_fields = ('location__name', 'notes')
    date_hierarchy = 'date'

@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('location', 'timestamp', 'temperature', 'humidity', 'soil_moisture', 'light_intensity')
    list_filter = ('location', 'timestamp')
    date_hierarchy = 'timestamp'

@admin.register(SupplyChain)
class SupplyChainAdmin(admin.ModelAdmin):
    list_display = ('harvest_record', 'destination', 'status', 'departure_date', 'estimated_arrival', 'actual_arrival')
    list_filter = ('status', 'departure_date')
    search_fields = ('destination', 'vehicle_info', 'notes')
    date_hierarchy = 'departure_date'

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('location', 'category', 'priority', 'created_at', 'valid_until', 'is_implemented')
    list_filter = ('category', 'priority', 'is_implemented')
    search_fields = ('location__name', 'recommendation')
    date_hierarchy = 'created_at'

@admin.register(PredictionModel)
class PredictionModelAdmin(admin.ModelAdmin):
    list_display = ('location', 'prediction_date', 'predicted_yield', 'confidence_score', 'created_at')
    list_filter = ('location', 'prediction_date')
    search_fields = ('location__name',)
    date_hierarchy = 'prediction_date'
