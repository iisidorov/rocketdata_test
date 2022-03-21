from . import views
from django.urls import path

urlpatterns = [
    path('employees/', views.EmployeeListView.as_view()),
    path('employees/level/<int:level>/', views.EmployeeLevelListView.as_view({'get': 'list'})),
]
