项目概述
产品追溯系统是一个基于Django+Vue.js的全栈应用，用于追踪和管理产品的生命周期。系统分为前端和后端两部分：
前端：基于Vue.js 2.6和Element UI构建的单页应用
后端：基于Django 4.2和Django REST Framework构建的API服务
系统架构
前端架构
前端项目位于vue/目录下，主要结构如下：
src/views/: 页面组件
src/components/: 可复用组件
src/router/: 路由配置
src/assets/: 静态资源
src/layout/: 布局组件
后端架构
后端项目位于product_tracing/目录下，主要结构如下：
users/: 用户管理模块
products/: 产品管理模块
tracing/: 追溯管理模块
data_analysis/: 数据分析模块
dashboard_app/: 仪表盘模块
product_tracing/: 项目配置
主要功能模块
1. 用户管理模块
前端文件
vue/src/views/Login.vue: 登录页面
vue/src/views/Register.vue: 注册页面
vue/src/views/Profile.vue: 个人信息页面
vue/src/views/system/Users.vue: 用户管理页面
后端文件
product_tracing/users/models.py: 用户模型
product_tracing/users/views.py: 用户视图
product_tracing/users/serializers.py: 用户序列化器
product_tracing/users/urls.py: 用户路由
功能说明
用户注册与登录
JWT认证
用户信息管理
角色权限控制（管理员、企业用户、普通用户）
2. 产品管理模块
前端文件
vue/src/views/products/Products.vue: 产品列表页面
vue/src/views/products/Categories.vue: 分类管理页面
vue/src/views/products/Batches.vue: 批次管理页面
后端文件
product_tracing/products/models.py: 产品相关模型
product_tracing/products/views.py: 产品相关视图
product_tracing/products/serializers.py: 产品序列化器
product_tracing/products/urls.py: 产品路由
product_tracing/products/permissions.py: 产品权限控制
功能说明
商品分类管理
商品信息管理
批次管理
二维码生成
3. 追溯管理模块
前端文件
vue/src/views/tracing/Trace.vue: 追溯查询页面
vue/src/views/tracing/Production.vue: 生产记录管理
vue/src/views/tracing/Logistics.vue: 物流记录管理
vue/src/views/tracing/Sales.vue: 销售记录管理
vue/src/views/TraceDetail.vue: 追溯详情页面
后端文件
product_tracing/tracing/models.py: 追溯相关模型
product_tracing/tracing/views.py: 追溯相关视图
product_tracing/tracing/serializers.py: 追溯序列化器
product_tracing/tracing/urls.py: 追溯路由
product_tracing/tracing/permissions.py: 追溯权限控制
功能说明
生产记录管理
物流记录管理
销售记录管理
追溯查询
二维码扫描
4. 数据分析模块
前端文件
vue/src/views/analysis/Analysis.vue: 数据分析总览
vue/src/views/analysis/Sales.vue: 销售分析
vue/src/views/analysis/Tracing.vue: 追溯分析
vue/src/views/analysis/Quality.vue: 质量分析
后端文件
product_tracing/data_analysis/models.py: 分析相关模型
product_tracing/data_analysis/views.py: 分析相关视图
product_tracing/data_analysis/serializers.py: 分析序列化器
product_tracing/data_analysis/urls.py: 分析路由
功能说明
销售分析
追溯分析
质量分析
数据导出
5. 仪表盘模块
前端文件
vue/src/views/Dashboard.vue: 仪表盘页面
后端文件
product_tracing/dashboard_app/views.py: 仪表盘视图
product_tracing/dashboard_app/serializers.py: 仪表盘序列化器
product_tracing/dashboard_app/urls.py: 仪表盘路由
product_tracing/dashboard_app/permissions.py: 仪表盘权限控制
功能说明
数据概览
销售趋势
最新订单
预警信息
页面与API对应关系
1. 登录页面
前端：vue/src/views/Login.vue
API：/api/users/auth/login/
后端处理：product_tracing/users/views.py 中的 LoginView
2. 注册页面
前端：vue/src/views/Register.vue
API：/api/users/auth/register/
后端处理：product_tracing/users/views.py 中的 UserRegisterView
3. 仪表盘页面
前端：vue/src/views/Dashboard.vue
API：
/api/dashboard/overview/
/api/dashboard/sales-trend/
/api/dashboard/category-stats/
/api/dashboard/latest-orders/
/api/dashboard/warnings/
后端处理：product_tracing/dashboard_app/views.py
4. 产品管理页面
前端：vue/src/views/products/Products.vue
API：
/api/products/list/
/api/products/<id>/
后端处理：product_tracing/products/views.py 中的 ProductListCreateView 和 ProductDetailView
5. 分类管理页面
前端：vue/src/views/products/Categories.vue
API：
/api/products/categories/
/api/products/categories/<id>/
后端处理：product_tracing/products/views.py 中的 CategoryListCreateView 和 CategoryDetailView
6. 批次管理页面
前端：vue/src/views/products/Batches.vue
API：
/api/products/batches/
/api/products/batches/<id>/
/api/products/qrcode/<batch_number>/
后端处理：product_tracing/products/views.py 中的 BatchListCreateView、BatchDetailView 和 generate_qrcode
7. 追溯查询页面
前端：vue/src/views/tracing/Trace.vue
API：
/api/tracing/trace/<batch_number>/
/api/tracing/search-batches/
/api/tracing/recent-batches/
后端处理：product_tracing/tracing/views.py 中的 trace_batch、search_batches 和 recent_batches
8. 生产记录管理页面
前端：vue/src/views/tracing/Production.vue
API：
/api/tracing/production/
/api/tracing/production/<id>/
后端处理：product_tracing/tracing/views.py 中的 ProductionRecordListCreateView 和 ProductionRecordDetailView
9. 物流记录管理页面
前端：vue/src/views/tracing/Logistics.vue
API：
/api/tracing/logistics/
/api/tracing/logistics/<id>/
后端处理：product_tracing/tracing/views.py 中的 LogisticsRecordListCreateView 和 LogisticsRecordDetailView
10. 销售记录管理页面
前端：vue/src/views/tracing/Sales.vue
API：
/api/tracing/sales/
/api/tracing/sales/<id>/
后端处理：product_tracing/tracing/views.py 中的 SalesRecordListCreateView 和 SalesRecordDetailView
11. 数据分析页面
前端：vue/src/views/analysis/ 下的各个分析页面
API：
/api/analysis/sales/
/api/analysis/tracing/
/api/analysis/quality/
/api/analysis/export/
后端处理：product_tracing/data_analysis/views.py 中的各个分析视图
12. 用户管理页面
前端：vue/src/views/system/Users.vue
API：
/api/users/users/
/api/users/users/<id>/
后端处理：product_tracing/users/views.py 中的 UserViewSet
数据流向
用户在前端页面进行操作
前端通过Axios发送HTTP请求到后端API
后端路由将请求转发到对应的视图函数
视图函数处理请求，可能涉及数据库操作
视图函数返回JSON响应
前端接收响应并更新页面
权限控制
系统实现了多级权限控制：
IsAuthenticated: 基本的认证权限，要求用户已登录
IsManufacturerOrAdmin: 只允许产品制造商或管理员访问
IsEnterpriseUser: 企业用户权限，允许企业用户访问本企业相关数据
IsSalesUser: 销售人员权限，允许销售人员访问销售相关数据
IsDashboardUser: 仪表盘访问权限，允许管理员和企业用户访问
前端路由
前端路由配置在 vue/src/router/main.js 中，主要包括：
/login: 登录页面
/register: 注册页面
/dashboard: 仪表盘
/products: 产品管理
/categories: 分类管理
/batches: 批次管理
/tracing: 追溯管理
/analysis: 数据分析
/system: 系统管理
/profile: 个人信息
/trace/:batchNumber: 追溯详情页面