from . import views
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('employees/',
         views.EmployeeListView.as_view(),
         name='employees'),
    path('employees/level/<int:level>/',
         views.EmployeeLevelListView.as_view({'get': 'list'}),
         name='employees_level'),

    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterApi.as_view()),
    path('token/blacklist/', views.BlacklistTokenView.as_view(), name='blacklist'),

    path('profile/', views.UserProfileView.as_view({'get': 'retrieve'}), name='profile'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
