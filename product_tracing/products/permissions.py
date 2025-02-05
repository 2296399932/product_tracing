from rest_framework import permissions

class IsManufacturerOrAdmin(permissions.BasePermission):
    """
    只允许产品制造商或管理员访问
    """
    def has_object_permission(self, request, view, obj):
        # 管理员可以访问所有对象
        if request.user.role == 'admin':
            return True
        # 制造商只能访问自己的产品
        return obj.manufacturer == request.user