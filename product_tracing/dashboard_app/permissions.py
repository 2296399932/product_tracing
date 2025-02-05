from rest_framework import permissions

class IsDashboardUser(permissions.BasePermission):
    """
    仪表盘访问权限
    - 管理员可以访问所有功能
    - 企业用户可以访问本企业相关数据
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        if request.user.is_staff:
            return True
            
        if hasattr(request.user, 'company'):
            return True
            
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
            
        if hasattr(obj, 'company') and obj.company == request.user.company:
            return True
            
        return False 