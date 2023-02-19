from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('download/<str:file_code>/', views.download, name='download'),
    path('library/', views.library, name='library'),
    # path('login/', views.user_login, name="user_login"),
    # path("logout/", views.user_logout, name="user_logout"),
    # path("signup/", views.user_signup, name="user_signup")
]

