from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_image, name='upload_image'),
    path('essay/<int:pk>/', views.essay_detail, name='essay_detail'),
]
