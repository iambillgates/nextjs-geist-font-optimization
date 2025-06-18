from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class Location(models.Model):
    name = models.CharField(max_length=100)
    area_size = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.name

class HarvestRecord(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    date = models.DateField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    quality_score = models.IntegerField(validators=[MinValueValidator(0)])
    weather_condition = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Harvest at {self.location} on {self.date}"

class SensorData(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    humidity = models.DecimalField(max_digits=5, decimal_places=2)
    soil_moisture = models.DecimalField(max_digits=5, decimal_places=2)
    light_intensity = models.DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Sensor data from {self.location} at {self.timestamp}"

class SupplyChain(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
    ]

    harvest_record = models.ForeignKey(HarvestRecord, on_delete=models.CASCADE)
    destination = models.CharField(max_length=200)
    departure_date = models.DateTimeField()
    estimated_arrival = models.DateTimeField()
    actual_arrival = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    vehicle_info = models.CharField(max_length=100)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Shipment from {self.harvest_record.location} to {self.destination}"

class Recommendation(models.Model):
    CATEGORY_CHOICES = [
        ('harvest_timing', 'Harvest Timing'),
        ('resource_management', 'Resource Management'),
        ('quality_improvement', 'Quality Improvement'),
        ('weather_alert', 'Weather Alert'),
    ]

    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    recommendation = models.TextField()
    priority = models.IntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField()
    is_implemented = models.BooleanField(default=False)

    class Meta:
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"{self.category} recommendation for {self.location}"

class PredictionModel(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    prediction_date = models.DateField()
    predicted_yield = models.DecimalField(max_digits=10, decimal_places=2)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2)
    factors_considered = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-prediction_date']

    def __str__(self):
        return f"Prediction for {self.location} on {self.prediction_date}"
