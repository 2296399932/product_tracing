from rest_framework import permissions



class IsEnterpriseUser(permissions.BasePermission):
    """
    企业用户权限
    - 管理员可以访问所有功能
    - 企业用户可以访问本企业相关数据
    """
    
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
            
        return request.user.is_authenticated and request.user.role == 'enterprise'
        
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
            
        if hasattr(obj, 'company') and obj.company == request.user.company:
            return True
            
        return False

class IsSalesUser(permissions.BasePermission):
    """
    销售人员权限
    - 管理员可以访问所有功能
    - 销售人员可以访问销售相关数据
    """
    
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
            
        return request.user.is_authenticated and request.user.role == 'sales'
        
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
            
        # 销售人员只能访问自己创建的销售记录
        if hasattr(obj, 'seller') and obj.seller == request.user:
            return True
            
        return False 