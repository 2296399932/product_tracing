from django.db import models
from users.models import User

class Category(models.Model):
    """商品分类"""
    name = models.CharField('名称', max_length=50)
    code = models.CharField('编码', max_length=20, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, 
                             null=True, blank=True, related_name='children',
                             verbose_name='父分类')
    level = models.IntegerField('层级', default=1)
    sort_order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '商品分类'
        verbose_name_plural = verbose_name
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name

class Product(models.Model):
    """商品"""
    STATUS_CHOICES = (
        ('active', '在售'),
        ('inactive', '下架'),
    )
    
    name = models.CharField('名称', max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, 
                               related_name='products', verbose_name='分类')
    code = models.CharField('编码', max_length=50, unique=True)
    specifications = models.JSONField('规格', default=dict)
    price = models.DecimalField('价格', max_digits=10, decimal_places=2)
    unit = models.CharField('单位', max_length=20)
    description = models.TextField('描述', blank=True, null=True)
    image = models.ImageField('图片', upload_to='products/', blank=True, null=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    manufacturer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='制造商',
        related_name='products'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Batch(models.Model):
    """批次模型"""
    STATUS_CHOICES = (
        ('active', '正常'),
        ('sold_out', '售罄'),
        ('expired', '过期'),
        ('disabled', '停用')
    )
    
    batch_number = models.CharField('批次号', max_length=50, unique=True)
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='batches',
        verbose_name='商品'
    )
    production_date = models.DateField('生产日期')
    expiry_date = models.DateField('过期日期')
    quantity = models.IntegerField('数量')
    cost_price = models.DecimalField('成本价', max_digits=10, decimal_places=2)
    status = models.CharField(
        '状态',
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True, 
                               verbose_name='追溯码')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '批次'
        verbose_name_plural = verbose_name
        db_table = 'batch'
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gte=0),
                name='batch_quantity_non_negative'
            )
        ]

    def __str__(self):
        return self.batch_number

class Inventory(models.Model):
    """库存模型"""
    LOCATION_CHOICES = (
        ('warehouse', '仓库'),
        ('store', '门店'),
        ('transit', '在途'),
    )
    
    batch = models.OneToOneField(Batch, on_delete=models.CASCADE, 
                                related_name='inventory_info', verbose_name='批次')
    quantity = models.IntegerField('数量')
    location = models.CharField('库存位置', max_length=20, 
                              choices=LOCATION_CHOICES, default='warehouse')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '库存'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.batch.batch_number}-{self.get_location_display()}"

class Warehouse(models.Model):
    """仓库"""
    name = models.CharField(max_length=100, unique=True, verbose_name='仓库名称')
    address = models.CharField(max_length=200, verbose_name='地址')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, 
                              null=True, verbose_name='仓库管理员')
    phone = models.CharField(max_length=20, verbose_name='联系电话')
    area = models.DecimalField(max_digits=10, decimal_places=2, 
                             verbose_name='面积(平方米)')
    status = models.BooleanField(default=True, verbose_name='是否启用')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '仓库'
        verbose_name_plural = verbose_name
        db_table = 'warehouse'

    def __str__(self):
        return self.name

# 添加库存记录模型，用于记录出入库历史
class InventoryRecord(models.Model):
    """库存记录"""
    TYPE_CHOICES = (
        ('in', '入库'),
        ('out', '出库'),
    )
    
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, 
                                related_name='records', verbose_name='库存')
    type = models.CharField('类型', max_length=10, choices=TYPE_CHOICES)
    quantity = models.IntegerField('数量')
    operator = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='操作员')
    remark = models.TextField('备注', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '库存记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.inventory.batch.batch_number}-{self.get_type_display()}-{self.quantity}"

    def save(self, *args, **kwargs):
        # 更新库存数量
        if self.type == 'in':
            self.inventory.quantity += self.quantity
        else:
            self.inventory.quantity -= self.quantity
        self.inventory.save()
        super().save(*args, **kwargs)
