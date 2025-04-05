from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Supplier(models.Model):
    """供应商模型"""
    name = models.CharField('名称', max_length=100)
    contact_person = models.CharField('联系人', max_length=50, blank=True, null=True)
    phone = models.CharField('联系电话', max_length=20, blank=True, null=True)
    email = models.EmailField('邮箱', blank=True, null=True)
    address = models.CharField('地址', max_length=200, blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '供应商'
        verbose_name_plural = '供应商'
        db_table = 'supplier'
    
    def __str__(self):
        return self.name

class Material(models.Model):
    """原材料模型"""
    code = models.CharField('编码', max_length=50, unique=True)
    name = models.CharField('名称', max_length=100)
    category = models.CharField('分类', max_length=50)
    specification = models.CharField('规格', max_length=100, blank=True, null=True)
    origin = models.CharField('产地', max_length=100, blank=True, null=True)
    description = models.TextField('描述', blank=True, null=True)
    status = models.CharField('状态', max_length=20, default='active',
                             choices=[('active', '活跃'), ('inactive', '停用')])
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '原材料'
        verbose_name_plural = '原材料'
        db_table = 'material'
    
    def __str__(self):
        return self.name

class MaterialSupplier(models.Model):
    """原材料与供应商关联"""
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='material_suppliers', verbose_name='原材料')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='material_suppliers', verbose_name='供应商')
    is_preferred = models.BooleanField('是否首选供应商', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '原材料供应商关联'
        verbose_name_plural = '原材料供应商关联'
        db_table = 'material_supplier'
        unique_together = ('material', 'supplier')
    
    def __str__(self):
        return f"{self.material.name} - {self.supplier.name}"

class MaterialBatch(models.Model):
    """原材料批次"""
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='batches', verbose_name='原材料')
    batch_number = models.CharField('批次号', max_length=50)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name='material_batches', verbose_name='供应商')
    quantity = models.DecimalField('数量', max_digits=10, decimal_places=2)
    unit = models.CharField('单位', max_length=20)
    production_date = models.DateField('生产日期', blank=True, null=True)
    expiry_date = models.DateField('有效期至', blank=True, null=True)
    status = models.CharField('状态', max_length=20, default='in_storage',
                            choices=[('in_storage', '在库'), ('used', '已使用'), ('expired', '已过期'), ('returned', '已退货')])
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_batches', verbose_name='创建人')
    price = models.DecimalField('采购价格', max_digits=10, decimal_places=2, blank=True, null=True)

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '原材料批次'
        verbose_name_plural = '原材料批次'
        db_table = 'material_batch'
        unique_together = ('material', 'batch_number')
    
    def __str__(self):
        return f"{self.material.name} - {self.batch_number}" 