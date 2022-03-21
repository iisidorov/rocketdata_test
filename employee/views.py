from django.shortcuts import render
from rest_framework import permissions, generics, status, viewsets
from .serializers import EmployeeSerializer
from .models import Employee


class EmployeeListView(generics.ListCreateAPIView):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()


class EmployeeLevelListView(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()

    def get_queryset(self):
        return Employee.objects.filter(level=self.kwargs["level"])
