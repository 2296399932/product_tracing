from django.shortcuts import render
from rest_framework import status, generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from .models import User
from .serializers import UserSerializer, UserRegisterSerializer, UserLoginSerializer, UserProfileSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
import traceback
from django.core.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.authentication import JWTAuthentication

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        print("Login request data:", request.data)
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            # 使用 JWT token
            refresh = RefreshToken.for_user(user)
            
            response_data = {
                'token': str(refresh.access_token),  # 使用 JWT token
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'phone': user.phone,
                    'is_active': user.is_active,
                    'last_login': user.last_login
                }
            }
            print("Login response data:", response_data)
            
            return Response(response_data)
        else:
            return Response({
                'error': '用户名或密码错误'
            }, status=400)

class UserLogoutView(APIView):
    """用户登出视图"""
    permission_classes = [AllowAny]
    
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
            a
            return Response({
                'message': '注册失败',
                'errors': errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'message': '注册失败',
                'errors': [str(e)]
            }, status=status.HTTP_400_BAD_REQUEST)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = []
    permission_classes = []
    pagination_class = StandardResultsSetPagination
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("\n=== ViewSet 初始化 ===")
        print("ViewSet 类:", self.__class__.__name__)
        print("=== ViewSet 初始化结束 ===\n")
    
    def initial(self, request, *args, **kwargs):
        """
        在任何方法执行之前调用
        """
        print("\n=== 请求初始化开始 ===")
        print(f"请求方法: {request.method}")
        print(f"请求路径: {request.path}")
        print(f"请求头: {request.headers}")
        print(f"请求数据: {request.data}")
        print(f"用户认证状态: {request.user.is_authenticated}")
        if request.user.is_authenticated:
            print(f"用户角色: {request.user.role}")
        try:
            super().initial(request, *args, **kwargs)
            print("请求初始化成功")
        except Exception as e:
            print(f"请求初始化失败: {str(e)}")
            raise
        finally:
            print("=== 请求初始化结束 ===\n")

    def get_queryset(self):
        """
        根据查询参数过滤用户列表
        """
        queryset = User.objects.all()
        username = self.request.query_params.get('username')
        role = self.request.query_params.get('role')
        
        if username:
            queryset = queryset.filter(username__icontains=username)
        if role:
            queryset = queryset.filter(role=role)
            
        return queryset.order_by('-created_at')

    def perform_update(self, serializer):
        """
        处理更新操作
        """
        print("\n=== 执行更新开始 ===")
        data = self.request.data.copy()
        print(f"原始更新数据: {data}")
        
        try:
            if 'is_active' in data:
                is_active = data.pop('is_active')
                print("更新用户状态")
                serializer.save(is_active=is_active)
            else:
                print("更新用户信息（不包含状态）")
                serializer.save()
            print("更新成功")
        except Exception as e:
            print(f"更新失败，错误: {str(e)}")
            print("错误堆栈:")
            print(traceback.format_exc())
            raise e
        finally:
            print("=== 执行更新结束 ===\n")

    def create(self, request, *args, **kwargs):
        """
        创建新用户
        """
        try:
            # 移除只读字段
            data = request.data.copy()
            for field in ['created_at', 'updated_at', 'last_login']:
                data.pop(field, None)
            
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            return Response({
                'message': '创建成功',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({
                'message': '创建失败',
                'errors': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        更新用户信息
        """
        try:
            instance = self.get_object()
            data = request.data.copy()
            
            # 移除只读字段
            for field in ['created_at', 'updated_at', 'last_login']:
                data.pop(field, None)
            
            # 处理状态字段
            if 'status' in data:
                data['is_active'] = data.pop('status')
            
            serializer = self.get_serializer(instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            return Response({
                'message': '更新成功',
                'data': serializer.data
            })
        except ValidationError as e:
            return Response({
                'message': '更新失败',
                'errors': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        删除用户
        """
        try:
            instance = self.get_object()
            if instance.role == 'admin':
                return Response({
                    'message': '不能删除管理员用户'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            self.perform_destroy(instance)
            return Response({
                'message': '删除成功'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message': '删除失败',
                'errors': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        print("List users with params:", request.query_params)
        response = super().list(request, *args, **kwargs)
        print("List response count:", response.data.get('count'))
        return Response({
            'data': response.data,
            'message': '获取成功'
        })

    def retrieve(self, request, *args, **kwargs):
        print("Retrieving user with ID:", kwargs.get('pk'))
        response = super().retrieve(request, *args, **kwargs)
        print("Retrieve response:", response.data)
        return Response({
            'data': response.data,
            'message': '获取成功'
        })

    def get_serializer(self, *args, **kwargs):
        print("\n=== 序列化开始 ===")
        print(f"序列化参数: {kwargs}")
        serializer = super().get_serializer(*args, **kwargs)
        print(f"使用的序列化器: {serializer.__class__.__name__}")
        print("=== 序列化结束 ===\n")
        return serializer

    def get_object(self):
        print("\n=== 获取对象开始 ===")
        obj = super().get_object()
        print(f"获取到的对象: ID={obj.id}, 用户名={obj.username}")
        print("=== 获取对象结束 ===\n")
        return obj

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """用户详情视图"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = []
    permission_classes = []
    
    def get_object(self):
        obj = super().get_object()
        return obj

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        print('=== Profile Request ===')
        print('Headers:', request.headers)
        print('User:', request.user)
        print('Auth:', request.auth)
        
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class ChangePasswordView(APIView):
    """修改密码视图"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        # 确保用户已认证
        if not request.user.is_authenticated:
            return Response({'error': '用户未认证'}, status=status.HTTP_401_UNAUTHORIZED)
            
        # 验证旧密码
        if not request.user.check_password(old_password):
            return Response({'error': '原密码不正确'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 设置新密码
        request.user.set_password(new_password)
        request.user.save()
        
        return Response({'message': '密码修改成功'})
