from django.shortcuts import render
from rest_framework import permissions, generics, status, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permissions import IsApiAllowed
from .serializers import EmployeeSerializer
from .models import Employee


class EmployeeListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated & (IsAdminUser | IsApiAllowed)]
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()


class EmployeeLevelListView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & (IsAdminUser | IsApiAllowed)]
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()

    def get_queryset(self):
        return Employee.objects.filter(level=self.kwargs["level"])
