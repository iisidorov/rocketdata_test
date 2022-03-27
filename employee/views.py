from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import permissions, generics, status, viewsets, views
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from .permissions import IsApiAllowed
from .serializers import EmployeeSerializer, UserSerializer
from .models import Employee, User


class EmployeeListView(generics.ListAPIView):
    """
    Url: employees/
    Allowed requests: GET
    """
    permission_classes = [IsAuthenticated & (IsAdminUser | IsApiAllowed)]
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()


class EmployeeLevelListView(viewsets.ModelViewSet):
    """
    Url: employees/level/<int:level>/
    Allowed requests: GET
    """
    permission_classes = [IsAuthenticated & (IsAdminUser | IsApiAllowed)]
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()

    def get_queryset(self):
        return Employee.objects.filter(level=self.kwargs["level"])


class UserProfileView(viewsets.ModelViewSet):
    """
    Url: profile/
    Allowed requests: GET
    * Returns Authenticated User's credentials
    """
    permission_classes = [IsAuthenticated & (IsAdminUser | IsApiAllowed)]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.get(pk=self.request.user.id)
        self.check_object_permissions(self.request, obj)
        return obj


class RegisterApi(generics.GenericAPIView):
    """
    Url: register/
    Allowed requests: POST
    JSON-body: {
        "email": string,
        "first_name": string,
        "last_name": string,
        "father_name": string,
        "password": string
    }
    """
    serializer_class = UserSerializer

    def post(self, request, *args,  **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return JsonResponse({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "User Created Successfully. Now perform Login to get your token",
        }, status=status.HTTP_200_OK)


# Save refresh-token to Blacklist after logout
class BlacklistTokenView(views.APIView):
    """
    Url: logout/blacklist/
    Allowed requests: POST
    JSON-body: {"refresh": string}
    * Blacklisting token after user's logout
    """
    permissions_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return JsonResponse({"message": "Token Blacklisted Successfully"},
                                status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({"message": "Error while Token Blacklisting"},
                                status=status.HTTP_400_BAD_REQUEST)
