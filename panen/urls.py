from django.urls import path
from . import views

app_name = 'panen'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('monitoring/', views.monitoring, name='monitoring'),
    path('predict/', views.predict_harvest, name='predict'),
    path('supply-chain/', views.supply_chain, name='supply_chain'),
]
