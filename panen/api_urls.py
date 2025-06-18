from django.urls import path
from . import views

app_name = 'panen_api'

urlpatterns = [
    path('sensor-data/<int:location_id>/', views.get_sensor_data, name='sensor_data'),
    path('recommendations/', views.generate_recommendations, name='recommendations'),
]
