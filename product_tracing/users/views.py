from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer, UserRegisterSerializer, UserLoginSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers

class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            return Response({
                'token': response.data['access'],
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'role': request.user.role if hasattr(request.user, 'role') else 'user'
                }
            })
        return response

class UserLogoutView(APIView):
    """用户登出视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # JWT token 不需要在服务端处理登出
        return Response({'message': '登出成功'})

class UserRegisterView(APIView):
    """用户注册视图"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': '注册成功',
                    'data': {
                        'token': str(refresh.access_token),
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'role': getattr(user, 'role', 'user')
                        }
                    }
                }, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            # 处理验证错误
            errors = []
            error_dict = e.detail
            for field, field_errors in error_dict.items():
                if isinstance(field_errors, list):
                    for error in field_errors:
                        errors.append(f"{field}: {error}")
                else:
                    errors.append(f"{field}: {field_errors}")
            
            return Response({
                'message': '注册失败',
                'errors': errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'message': '注册失败',
                'errors': [str(e)]
            }, status=status.HTTP_400_BAD_REQUEST)

class UserListView(generics.ListCreateAPIView):
    """用户列表视图"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = User.objects.all()
        role = self.request.query_params.get('role', None)
        company = self.request.query_params.get('company_name', None)
        
        if role:
            queryset = queryset.filter(role=role)
        if company:
            queryset = queryset.filter(company_name__icontains=company)
        
        return queryset

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """用户详情视图"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_object(self):
        obj = super().get_object()
        if not self.request.user.is_staff and obj != self.request.user:
            self.permission_denied(self.request)
        return obj

class UserProfileView(generics.RetrieveUpdateAPIView):
    """当前用户信息视图"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class ChangePasswordView(APIView):
    """修改密码视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        # 验证旧密码
        if not request.user.check_password(old_password):
            return Response({
                'error': '原密码不正确'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 设置新密码
        request.user.set_password(new_password)
        request.user.save()
        
        return Response({
            'message': '密码修改成功'
        })
