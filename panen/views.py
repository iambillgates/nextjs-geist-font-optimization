from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg
from rest_framework.decorators import api_view
from rest_framework.response import Response
import numpy as np
from sklearn.cluster import KMeans
from .models import (
    Location, 
    HarvestRecord, 
    SensorData, 
    SupplyChain, 
    Recommendation,
    PredictionModel
)

def dashboard(request):
    """
    Main dashboard view showing overview of palm oil harvest management
    """
    context = {
        'locations': Location.objects.all(),
        'recent_harvests': HarvestRecord.objects.all().order_by('-date')[:5],
        'active_shipments': SupplyChain.objects.filter(status='in_transit'),
        'recent_recommendations': Recommendation.objects.filter(
            valid_until__gte=timezone.now()
        )[:5]
    }
    return render(request, 'panen/dashboard.html', context)

def monitoring(request):
    """
    Real-time monitoring view for sensor data
    """
    locations = Location.objects.all()
    sensor_data = {}
    
    for location in locations:
        latest_data = SensorData.objects.filter(location=location).first()
        if latest_data:
            sensor_data[location.id] = latest_data
    
    context = {
        'locations': locations,
        'sensor_data': sensor_data,
    }
    return render(request, 'panen/monitoring.html', context)

def predict_harvest(request):
    """
    View for harvest prediction using K-means clustering
    """
    if request.method == 'POST':
        location_id = request.POST.get('location')
        try:
            location = Location.objects.get(id=location_id)
            
            # Get historical data for clustering
            historical_data = HarvestRecord.objects.filter(
                location=location
            ).values_list('quantity', flat=True)
            
            # Convert to numpy array and reshape for K-means
            X = np.array(historical_data).reshape(-1, 1)
            
            # Apply K-means clustering
            # Comment: Using 3 clusters to categorize yields into low, medium, and high
            kmeans = KMeans(n_clusters=3, random_state=42)
            kmeans.fit(X)
            
            # Get the cluster centers (average yields for each cluster)
            cluster_centers = kmeans.cluster_centers_
            
            # Predict the cluster for the most recent data point
            latest_data = X[-1].reshape(1, -1)
            cluster_prediction = kmeans.predict(latest_data)[0]
            
            # Calculate predicted yield based on cluster center
            predicted_yield = float(cluster_centers[cluster_prediction][0])
            
            # Store prediction
            PredictionModel.objects.create(
                location=location,
                prediction_date=timezone.now().date(),
                predicted_yield=predicted_yield,
                confidence_score=0.8,  # Simplified confidence score
                factors_considered={
                    'historical_data_points': len(historical_data),
                    'cluster_centers': cluster_centers.tolist(),
                    'assigned_cluster': int(cluster_prediction)
                }
            )
            
            messages.success(request, 'Prediction generated successfully!')
            
        except Location.DoesNotExist:
            messages.error(request, 'Invalid location selected.')
        except Exception as e:
            messages.error(request, f'Error generating prediction: {str(e)}')
            
    locations = Location.objects.all()
    recent_predictions = PredictionModel.objects.all().order_by('-created_at')[:5]
    
    context = {
        'locations': locations,
        'recent_predictions': recent_predictions,
    }
    return render(request, 'panen/predict.html', context)

def supply_chain(request):
    """
    View for managing supply chain operations
    """
    context = {
        'pending_shipments': SupplyChain.objects.filter(status='pending'),
        'active_shipments': SupplyChain.objects.filter(status='in_transit'),
        'completed_shipments': SupplyChain.objects.filter(status='delivered')[:5],
    }
    return render(request, 'panen/supply_chain.html', context)

@api_view(['GET'])
def get_sensor_data(request, location_id):
    """
    API endpoint for getting real-time sensor data
    """
    try:
        sensor_data = SensorData.objects.filter(
            location_id=location_id
        ).order_by('-timestamp')[:10]
        
        data = [{
            'timestamp': reading.timestamp,
            'temperature': reading.temperature,
            'humidity': reading.humidity,
            'soil_moisture': reading.soil_moisture,
            'light_intensity': reading.light_intensity,
        } for reading in sensor_data]
        
        return Response({
            'status': 'success',
            'data': data
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=400)

@api_view(['POST'])
def generate_recommendations(request):
    """
    API endpoint for generating automated recommendations
    """
    try:
        location_id = request.data.get('location_id')
        location = Location.objects.get(id=location_id)
        
        # Get recent sensor data
        recent_data = SensorData.objects.filter(
            location=location
        ).order_by('-timestamp')[:24]  # Last 24 readings
        
        # Calculate averages
        avg_temp = recent_data.aggregate(Avg('temperature'))['temperature__avg']
        avg_humidity = recent_data.aggregate(Avg('humidity'))['humidity__avg']
        avg_moisture = recent_data.aggregate(Avg('soil_moisture'))['soil_moisture__avg']
        
        # Generate recommendations based on conditions
        recommendations = []
        
        if avg_moisture < 30:
            recommendations.append({
                'category': 'resource_management',
                'recommendation': 'Increase irrigation frequency due to low soil moisture',
                'priority': 1
            })
        
        if avg_humidity > 85:
            recommendations.append({
                'category': 'weather_alert',
                'recommendation': 'High humidity detected. Monitor for potential fungal growth',
                'priority': 2
            })
        
        # Store recommendations
        for rec in recommendations:
            Recommendation.objects.create(
                location=location,
                category=rec['category'],
                recommendation=rec['recommendation'],
                priority=rec['priority'],
                valid_until=timezone.now() + timezone.timedelta(days=1)
            )
        
        return Response({
            'status': 'success',
            'recommendations': recommendations
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=400)
