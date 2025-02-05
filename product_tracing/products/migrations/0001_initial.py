# Generated by Django 4.2.14 on 2025-02-03 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch_number', models.CharField(db_index=True, max_length=50, unique=True, verbose_name='批次号')),
                ('production_date', models.DateField(verbose_name='生产日期')),
                ('expiry_date', models.DateField(verbose_name='过期日期')),
                ('quantity', models.IntegerField(verbose_name='数量')),
                ('cost_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='成本价')),
                ('status', models.CharField(choices=[('produced', '已生产'), ('in_storage', '入库'), ('out_storage', '出库'), ('sold', '已售出')], default='produced', max_length=20, verbose_name='状态')),
                ('qr_code', models.ImageField(blank=True, null=True, upload_to='qrcodes/', verbose_name='追溯码')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '商品批次',
                'verbose_name_plural': '商品批次',
                'db_table': 'product_batch',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='名称')),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='编码')),
                ('level', models.IntegerField(default=1, verbose_name='层级')),
                ('sort_order', models.IntegerField(default=0, verbose_name='排序')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '商品分类',
                'verbose_name_plural': '商品分类',
                'ordering': ['sort_order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(verbose_name='数量')),
                ('location', models.CharField(choices=[('warehouse', '仓库'), ('store', '门店'), ('transit', '在途')], default='warehouse', max_length=20, verbose_name='库存位置')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '库存',
                'verbose_name_plural': '库存',
            },
        ),
        migrations.CreateModel(
            name='InventoryRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('in', '入库'), ('out', '出库')], max_length=10, verbose_name='类型')),
                ('quantity', models.IntegerField(verbose_name='数量')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '库存记录',
                'verbose_name_plural': '库存记录',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='名称')),
                ('code', models.CharField(max_length=50, unique=True, verbose_name='编码')),
                ('specifications', models.JSONField(default=dict, verbose_name='规格')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='价格')),
                ('unit', models.CharField(max_length=20, verbose_name='单位')),
                ('description', models.TextField(blank=True, null=True, verbose_name='描述')),
                ('image', models.ImageField(blank=True, null=True, upload_to='products/', verbose_name='图片')),
                ('status', models.CharField(choices=[('active', '在售'), ('inactive', '下架')], default='active', max_length=20, verbose_name='状态')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '商品',
                'verbose_name_plural': '商品',
            },
        ),
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='仓库名称')),
                ('address', models.CharField(max_length=200, verbose_name='地址')),
                ('phone', models.CharField(max_length=20, verbose_name='联系电话')),
                ('area', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='面积(平方米)')),
                ('status', models.BooleanField(default=True, verbose_name='是否启用')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '仓库',
                'verbose_name_plural': '仓库',
                'db_table': 'warehouse',
            },
        ),
    ]
