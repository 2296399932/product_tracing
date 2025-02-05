from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
# users/urls.py

app_name = 'users'

urlpatterns = [
    # 认证相关
    path('auth/login/', views.LoginView.as_view(), name='login'),           # POST: 用户登录
    path('auth/logout/', views.UserLogoutView.as_view(), name='logout'),    # POST: 用户登出
    path('auth/register/', views.UserRegisterView.as_view(), name='register'), # POST: 用户注册
    path('auth/token/', TokenObtainPairView.as_view()),
    path('auth/token/refresh/', TokenRefreshView.as_view()),
    
    # 用户管理
    path('users/', views.UserListView.as_view(), name='user_list'),         # GET: 获取用户列表, POST: 创建用户
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'), # GET: 获取用户详情, PUT: 更新用户, DELETE: 删除用户
    path('profile/', views.UserProfileView.as_view(), name='user_profile'), # GET: 获取当前用户信息, PUT: 更新当前用户信息
]