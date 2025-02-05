# Product Tracing System (产品追溯系统)

## 项目简介
Product Tracing System 是一个基于 Django 的产品追溯管理系统，用于追踪和管理产品的生命周期，包括生产、流通和销售环节。该系统帮助企业实现产品质量追溯、供应链管理和质量控制。

## 功能特点
### 用户管理系统
- 多角色用户管理（管理员、企业用户、普通用户）
- 用户认证（登录、注册、登出）
- 用户信息管理

### 产品管理
- 商品分类管理
- 商品信息管理
- 批次管理
- 库存管理

### 追溯管理
- 生产记录追踪
- 物流记录追踪
- 销售记录追踪
- 二维码追溯查询

### 数据分析
- 销售统计分析
- 追溯数据统计
- 质量分析报告
- 地区分布分析

## 技术栈
- 后端：Python/Django + Django REST framework
- 数据库：MySQL
- 认证：JWT (JSON Web Token)
- API：RESTful API
- 跨域：django-cors-headers

## 项目架构

### 后端架构
```
product_tracing/
├── users/                 # 用户管理模块
│   ├── models.py         # 用户模型
│   ├── serializers.py    # 用户序列化器
│   ├── views.py          # 用户视图
│   ├── urls.py           # 用户路由
│   └── permissions.py    # 用户权限
├── products/             # 产品管理模块
│   ├── models.py         # 产品模型
│   ├── serializers.py    # 产品序列化器
│   ├── views.py          # 产品视图
│   ├── urls.py          # 产品路由
│   └── permissions.py    # 产品权限
├── tracing/             # 追溯管理模块
│   ├── models.py        # 追溯模型
│   ├── serializers.py   # 追溯序列化器
│   ├── views.py         # 追溯视图
│   ├── urls.py         # 追溯路由
│   └── permissions.py   # 追溯权限
├── data_analysis/      # 数据分析模块
│   ├── models.py       # 分析模型
│   ├── serializers.py  # 分析序列化器
│   ├── views.py        # 分析视图
│   └── urls.py        # 分析路由
└── product_tracing/    # 项目配置
    ├── settings.py     # 项目设置
    ├── urls.py        # 主路由
    └── wsgi.py        # WSGI配置
```

### 数据库设计

#### 用户模块 (users_user)
```sql
CREATE TABLE users_user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    role VARCHAR(20) NOT NULL,  -- admin/enterprise/normal
    company_name VARCHAR(100),
    phone VARCHAR(20),
    address VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME,
    updated_at DATETIME
);
```

#### 产品模块
```sql
-- 商品分类表
CREATE TABLE product_category (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    parent_id INT,
    level INT DEFAULT 1,
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME,
    updated_at DATETIME
);

-- 商品信息表
CREATE TABLE product (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    category_id INT NOT NULL,
    specifications JSON,
    manufacturer_id INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    description TEXT,
    image VARCHAR(100),
    stock INT DEFAULT 0,
    status BOOLEAN DEFAULT TRUE,
    created_at DATETIME,
    updated_at DATETIME
);

-- 商品批次表
CREATE TABLE product_batch (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    batch_number VARCHAR(50) UNIQUE NOT NULL,
    production_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    quantity INT NOT NULL,
    cost_price DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'produced',
    qr_code VARCHAR(100),
    created_at DATETIME,
    updated_at DATETIME
);
```

#### 追溯模块
```sql
-- 生产记录表
CREATE TABLE production_record (
    id INT PRIMARY KEY AUTO_INCREMENT,
    batch_id INT NOT NULL,
    raw_materials JSON NOT NULL,
    production_date DATETIME NOT NULL,
    operator_id INT NOT NULL,
    quality_check JSON NOT NULL,
    production_line VARCHAR(50) NOT NULL,
    temperature DECIMAL(5,2),
    humidity DECIMAL(5,2),
    remark TEXT,
    created_at DATETIME
);

-- 物流记录表
CREATE TABLE logistics_record (
    id INT PRIMARY KEY AUTO_INCREMENT,
    batch_id INT NOT NULL,
    record_type VARCHAR(20) NOT NULL,
    from_location VARCHAR(200) NOT NULL,
    to_location VARCHAR(200) NOT NULL,
    operator_id INT NOT NULL,
    carrier VARCHAR(100),
    tracking_number VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending',
    estimated_arrival DATETIME,
    actual_arrival DATETIME,
    remark TEXT,
    created_at DATETIME,
    updated_at DATETIME
);

-- 销售记录表
CREATE TABLE sales_record (
    id INT PRIMARY KEY AUTO_INCREMENT,
    batch_id INT NOT NULL,
    customer_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    sale_date DATETIME NOT NULL,
    seller_id INT NOT NULL,
    remark TEXT,
    created_at DATETIME
);
```

## 开发环境配置

### 1. 安装依赖包
```bash
pip install -r requirements.txt
```

requirements.txt 内容：
```
Django==4.2.14
djangorestframework==3.14.0
djangorestframework-jwt==1.11.0
django-cors-headers==4.3.1
mysqlclient==2.2.4
redis==5.0.1
Pillow==10.2.0
```

### 2. 数据库配置
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'product_tracing',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 3. 跨域配置
```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ... 其他中间件
]

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = [
    'http://localhost:8080',
    'http://127.0.0.1:8080',
]
```

### 4. JWT认证配置
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

## 部署说明

### 1. 服务器要求
- Python 3.8+
- MySQL 5.7+
- Redis 6.0+
- Nginx 1.18+

### 2. 生产环境配置
```python
DEBUG = False
ALLOWED_HOSTS = ['your.domain.com']

# 静态文件配置
STATIC_ROOT = '/path/to/static/'
MEDIA_ROOT = '/path/to/media/'

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/path/to/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### 3. Nginx配置示例
```nginx
server {
    listen 80;
    server_name your.domain.com;

    location /static/ {
        alias /path/to/static/;
    }

    location /media/ {
        alias /path/to/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 测试说明

### 1. 单元测试
```bash
python manage.py test users
python manage.py test products
python manage.py test tracing
python manage.py test data_analysis
```

### 2. API测试
使用 Postman 或 curl 进行API测试：

```bash
# 登录测试
curl -X POST http://localhost:8000/api/users/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"username":"test","password":"test123"}'

# 获取产品列表
curl -X GET http://localhost:8000/api/products/ \
     -H "Authorization: Bearer <your_token>"
```

## API 接口说明

### 用户管理接口
- POST `/api/users/auth/login/` - 用户登录
- POST `/api/users/auth/logout/` - 用户登出
- POST `/api/users/auth/register/` - 用户注册
- GET `/api/users/users/` - 获取用户列表
- GET `/api/users/users/<id>/` - 获取用户详情

### 产品追溯接口
- GET/POST `/api/products/production/` - 生产记录管理
- GET/POST `/api/products/logistics/` - 物流记录管理
- GET/POST `/api/products/sales/` - 销售记录管理
- GET `/api/products/trace/<batch_number>/` - 批次追溯查询
- GET `/api/products/qrcode/<batch_number>/` - 获取追溯二维码

### 数据分析接口
- GET `/api/analysis/sales/statistics/` - 销售统计数据
- GET `/api/analysis/sales/trend/` - 销售趋势分析
- GET `/api/analysis/tracing/statistics/` - 追溯统计数据
- GET `/api/analysis/quality/report/` - 质量分析报告

## API 详细说明

### 用户管理模块 (users)

#### 认证相关
1. 用户登录 - `POST /api/users/auth/login/`
```json
{
    "username": "string",
    "password": "string"
}
```
响应:
```json
{
    "token": "string",
    "user": {
        "id": "integer",
        "username": "string",
        "role": "string",
        "company_name": "string"
    }
}
```

2. 用户注册 - `POST /api/users/auth/register/`
```json
{
    "username": "string",
    "password": "string",
    "role": "string",
    "company_name": "string",
    "phone": "string",
    "address": "string"
}
```

3. 用户登出 - `POST /api/users/auth/logout/`
- 需要认证头: `Authorization: Bearer <token>`

#### 用户管理
1. 获取用户列表 - `GET /api/users/users/`
- 权限要求: 管理员
- 支持过滤: `?role=admin&company_name=xxx`

2. 获取用户详情 - `GET /api/users/users/<id>/`
- 权限要求: 管理员或本人

3. 更新用户信息 - `PUT /api/users/users/<id>/`
- 权限要求: 管理员或本人

### 产品管理模块 (products)

#### 生产记录
1. 创建生产记录 - `POST /api/products/production/`
```json
{
    "batch": "integer",
    "raw_materials": "json",
    "production_date": "datetime",
    "quality_check": "json",
    "production_line": "string",
    "temperature": "decimal",
    "humidity": "decimal"
}
```

2. 获取生产记录列表 - `GET /api/products/production/`
- 支持过滤: `?batch=123&date_from=2024-01-01&date_to=2024-03-20`

#### 物流记录
1. 创建物流记录 - `POST /api/products/logistics/`
```json
{
    "batch": "integer",
    "record_type": "string",
    "from_location": "string",
    "to_location": "string",
    "carrier": "string",
    "tracking_number": "string",
    "estimated_arrival": "datetime"
}
```

2. 更新物流状态 - `PUT /api/products/logistics/<id>/`
```json
{
    "status": "string",
    "actual_arrival": "datetime"
}
```

#### 销售记录
1. 创建销售记录 - `POST /api/products/sales/`
```json
{
    "batch": "integer",
    "customer": "integer",
    "quantity": "integer",
    "unit_price": "decimal",
    "payment_method": "string"
}
```

### 数据分析模块 (data_analysis)

#### 销售统计
1. 获取销售统计 - `GET /api/analysis/sales/statistics/`
- 支持时间范围: `?start_date=2024-01-01&end_date=2024-03-20`
- 支持分组: `?group_by=product,region`

2. 获取销售趋势 - `GET /api/analysis/sales/trend/`
- 支持时间粒度: `?granularity=day,week,month`

#### 质量分析
1. 创建质量分析记录 - `POST /api/analysis/quality/`
```json
{
    "batch": "integer",
    "inspection_date": "date",
    "quality_indicators": "json",
    "analysis_result": "string"
}
```

2. 获取质量分析报告 - `GET /api/analysis/quality/report/`
- 支持批次过滤: `?batch=123`
- 支持时间范围: `?start_date=2024-01-01&end_date=2024-03-20`

## 权限说明

### 用户角色
1. 管理员 (admin)
   - 可以管理所有用户
   - 可以查看所有数据
   - 可以进行系统配置

2. 企业用户 (enterprise)
   - 可以管理本企业的产品
   - 可以创建和管理生产记录
   - 可以查看相关的统计数据

3. 普通用户 (normal)
   - 可以查看公开的产品信息
   - 可以扫码查询产品追溯信息

### 接口权限
- 公开接口: 无需认证
  - 用户登录
  - 用户注册
  - 产品追溯查询

- 需要认证的接口: 需要有效的 JWT Token
  - 用户信息管理
  - 产品管理
  - 数据分析

- 需要特定角色的接口:
  - 用户列表查询 (admin)
  - 销售统计数据 (admin, enterprise)
  - 质量分析报告 (admin, enterprise)

## 安装指南

### 1. 后端环境配置

#### 1.1 克隆项目
```bash
git clone <项目地址>
cd product_tracing
```

#### 1.2 创建虚拟环境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 1.3 安装依赖
```bash
pip install -r requirements.txt
```

requirements.txt 内容：
```
Django==4.2.14
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
mysqlclient==2.2.4
redis==5.0.1
Pillow==10.2.0
drf-yasg==1.21.5
```

#### 1.4 数据库配置
1. 创建 MySQL 数据库
```sql
CREATE DATABASE product_tracing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 修改 settings.py 中的数据库配置
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'product_tracing',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

#### 1.5 Redis 配置
1. 安装 Redis
- Windows: 下载 [Redis for Windows](https://github.com/microsoftarchive/redis/releases)
- Linux: `sudo apt install redis-server`
- Mac: `brew install redis`

2. 启动 Redis 服务
```bash
# Windows
redis-server

# Linux/Mac
sudo service redis start
# 或
redis-server
```

#### 1.6 数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 1.7 创建超级用户
```bash
python manage.py createsuperuser
```

#### 1.8 启动开发服务器
```bash
python manage.py runserver
```

### 2. 前端环境配置

#### 2.1 安装 Node.js
从 [Node.js 官网](https://nodejs.org/) 下载并安装 Node.js (推荐 LTS 版本)

#### 2.2 安装前端依赖
```bash
cd vue
npm install
```

#### 2.3 启动开发服务器
```bash
npm run serve
```

### 3. 系统要求

#### 3.1 后端要求
- Python 3.8+
- MySQL 5.7+
- Redis 6.0+

#### 3.2 前端要求
- Node.js 14+
- npm 6+ 或 yarn 1.22+

### 4. 可能遇到的问题及解决方案

#### 4.1 MySQL 相关
1. mysqlclient 安装失败
```bash
# Windows
pip install mysqlclient-1.4.6-cp38-cp38-win_amd64.whl

# Linux
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential

# Mac
brew install mysql-connector-c
```

#### 4.2 Redis 相关
1. Redis 连接失败
- 检查 Redis 服务是否启动
- 检查 Redis 端口(默认6379)是否被占用
- 检查防火墙设置

#### 4.3 跨域问题
1. 确保 settings.py 中的跨域配置正确
```python
CORS_ORIGIN_WHITELIST = [
    'http://localhost:8080',
    'http://127.0.0.1:8080',
]
```

2. 前端请求添加正确的 headers
```javascript
headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
}
```

### 5. 部署说明

#### 5.1 使用 Docker 部署
1. 构建镜像
```bash
docker build -t product_tracing .
```

2. 运行容器
```bash
docker-compose up -d
```

#### 5.2 传统部署
1. 使用 Nginx 配置
```nginx
server {
    listen 80;
    server_name your.domain.com;

    location /static/ {
        alias /path/to/static/;
    }

    location /media/ {
        alias /path/to/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

2. 使用 Gunicorn 运行 Django
```bash
gunicorn product_tracing.wsgi:application --bind 0.0.0.0:8000
```

### 6. 开发建议

#### 6.1 代码规范
- 使用 pylint 检查 Python 代码
- 使用 ESLint 检查 JavaScript 代码
- 遵循 PEP 8 规范

#### 6.2 Git 提交规范
```bash
git commit -m "type: description"
# type: feat, fix, docs, style, refactor, test, chore
```

#### 6.3 开发流程
1. 创建功能分支
2. 开发新功能
3. 编写测试
4. 提交代码
5. 创建合并请求

### 7. 常见问题解答

Q: 如何重置数据库？
A: 
```bash
python manage.py flush
python manage.py migrate
python manage.py createsuperuser
```

Q: 如何清除缓存？
A:
```python
from django.core.cache import cache
cache.clear()
```

Q: 如何更新依赖？
A:
```bash
pip freeze > requirements.txt
```

## 开发团队
- 后端开发：[姓名]
- 前端开发：[姓名]
- 产品经理：[姓名]

## 许可证
本项目采用 MIT 许可证

## 联系方式
- 项目负责人：[姓名]
- 邮箱：[邮箱地址]

## Git 使用指南

### 1. 开发流程
```bash
# 1. 克隆仓库
git clone https://github.com/your-username/product_tracing.git
cd product_tracing

# 2. 创建并切换到新的功能分支
git checkout -b feature/your-feature-name

# 3. 提交你的更改
git add .
git commit -m "feat: 添加新功能描述"

# 4. 推送到远程仓库
git push origin feature/your-feature-name
```

### 2. 分支管理
- `main`: 主分支，用于产品发布
- `develop`: 开发分支，用于功能集成
- `feature/*`: 功能分支，用于新功能开发
- `hotfix/*`: 修复分支，用于紧急bug修复

### 3. 提交规范
提交信息格式：`<type>: <description>`

类型说明：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```bash
git commit -m "feat: 添加用户认证功能"
git commit -m "fix: 修复登录验证bug"
git commit -m "docs: 更新API文档"
```

### 4. 常用 Git 命令
```bash
# 查看分支状态
git status

# 拉取最新代码
git pull origin develop

# 查看提交历史
git log

# 创建新分支
git checkout -b branch-name

# 切换分支
git checkout branch-name

# 合并分支
git merge branch-name

# 解决冲突
# 1. 手动修改冲突文件
# 2. git add .
# 3. git commit -m "resolve conflicts"
```

### 5. 版本发布流程
1. 将 develop 分支合并到 main 分支
```bash
git checkout main
git merge develop
git tag -a v1.0.0 -m "version 1.0.0"
git push origin main --tags
```

2. 创建版本发布说明
- 在 GitHub 上创建 Release
- 描述版本更新内容
- 标记版本号

### 6. Git 工作流建议
1. 每天开始工作前先更新代码
```bash
git pull origin develop
```

2. 经常性地提交代码
```bash
git add .
git commit -m "feat: 完成xxx功能"
```

3. 提交 Pull Request 前
```bash
# 确保与目标分支同步
git checkout develop
git pull origin develop
git checkout your-feature-branch
git merge develop
# 解决冲突（如果有）
```

4. 代码审查后合并
- 等待代码审查
- 解决审查意见
- 合并到目标分支
```

## API 接口文档

### 用户认证
- POST `/api/users/auth/login/` - 用户登录
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```

- POST `/api/users/auth/register/` - 用户注册
  ```json
  {
    "username": "string",
    "password": "string",
    "confirm_password": "string",
    "email": "string",
    "phone": "string"
  }
  ```

- POST `/api/users/auth/logout/` - 用户登出

### 用户管理
- GET `/api/users/profile/` - 获取当前用户信息
- PUT `/api/users/profile/` - 更新用户信息
- GET `/api/users/` - 获取用户列表（管理员）
- GET `/api/users/<id>/` - 获取用户详情
- PUT `/api/users/<id>/` - 更新用户信息
- DELETE `/api/users/<id>/` - 删除用户

### 商品管理
- GET `/api/products/categories/` - 获取商品分类列表
- POST `/api/products/categories/` - 创建商品分类
- GET `/api/products/` - 获取商品列表
- POST `/api/products/` - 创建商品
- GET `/api/products/<id>/` - 获取商品详情
- PUT `/api/products/<id>/` - 更新商品信息
- DELETE `/api/products/<id>/` - 删除商品

### 批次管理
- GET `/api/products/batches/` - 获取批次列表
- POST `/api/products/batches/` - 创建批次
- GET `/api/products/batches/<id>/` - 获取批次详情
- PUT `/api/products/batches/<id>/` - 更新批次信息
- DELETE `/api/products/batches/<id>/` - 删除批次

### 追溯管理
- GET `/api/tracing/production/` - 获取生产记录列表
- POST `/api/tracing/production/` - 创建生产记录
- GET `/api/tracing/logistics/` - 获取物流记录列表
- POST `/api/tracing/logistics/` - 创建物流记录
- GET `/api/tracing/sales/` - 获取销售记录列表
- POST `/api/tracing/sales/` - 创建销售记录

### 追溯查询
- GET `/api/trace/<batch_number>/` - 获取批次追溯信息
- GET `/api/trace/scan/<qr_code>/` - 扫码获取追溯信息

### 数据分析
- GET `/api/analysis/sales/` - 获取销售分析数据
  ```
  参数：
  - date_from: 开始日期
  - date_to: 结束日期
  - category: 商品分类ID
  - type: 分析类型(amount/count)
  ```

- GET `/api/analysis/tracing/` - 获取追溯分析数据
  ```
  参数：
  - date_from: 开始日期
  - date_to: 结束日期
  - category: 商品分类ID
  ```

- GET `/api/analysis/quality/` - 获取质量分析数据
  ```
  参数：
  - date_from: 开始日期
  - date_to: 结束日期
  - category: 商品分类ID
  - page: 页码
  - page_size: 每页数量
  ```

### 仪表盘
- GET `/api/dashboard/overview/` - 获取仪表盘概览数据
  ```json
  {
    "productCount": "商品总数",
    "productGrowth": "商品增长率",
    "batchCount": "在库批次数",
    "inventoryValue": "库存总值",
    "monthSales": "本月销售额",
    "salesGrowth": "销售额增长率",
    "warningCount": "预警总数",
    "expiringCount": "即将过期批次数"
  }
  ```

- GET `/api/dashboard/sales-trend/` - 获取销售趋势数据
- GET `/api/dashboard/category-stats/` - 获取分类统计数据
- GET `/api/dashboard/latest-orders/` - 获取最新订单
- GET `/api/dashboard/warnings/` - 获取系统预警

### 通知管理
- GET `/api/notifications/` - 获取通知列表
- PUT `/api/notifications/<id>/read/` - 标记通知为已读
- DELETE `/api/notifications/<id>/` - 删除通知

### WebSocket
- `ws://host/ws/notifications/` - 实时通知连接

## 响应格式
所有 API 响应均使用以下格式：
```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

## 错误码
- 200: 成功
- 400: 请求参数错误
- 401: 未认证
- 403: 无权限
- 404: 资源不存在
- 500: 服务器错误

## 仪表盘模块

仪表盘模块提供了系统的核心数据概览和监控功能：

### 功能特点

1. 数据概览
   - 商品总数和增长率统计
   - 在库批次数和库存总值
   - 本月销售额和增长率
   - 系统预警信息汇总

2. 销售趋势
   - 支持按日/周/月查看销售趋势
   - 展示销售额和订单量双重指标
   - 图表化展示数据变化

3. 分类统计
   - 各分类商品数量占比
   - 各分类销售额占比
   - 支持数据导出

4. 最新订单
   - 实时展示最新10条订单
   - 包含订单详细信息
   - 支持快速查看订单详情

5. 系统预警
   - 多级别预警机制
   - 支持手动添加预警
   - 预警处理状态跟踪

### API 接口

| 接口路径 | 方法 | 说明 |
|---------|------|-----|
| /api/dashboard/overview/ | GET | 获取概览数据 |
| /api/dashboard/sales-trend/ | GET | 获取销售趋势 |
| /api/dashboard/category-stats/ | GET | 获取分类统计 |
| /api/dashboard/latest-orders/ | GET | 获取最新订单 |
| /api/dashboard/warnings/ | GET/POST | 获取/创建预警 |
| /api/dashboard/warnings/<pk>/ | PUT | 更新预警状态 |

### 开发说明

1. 后端开发
   - 基于 Django REST framework
   - 使用 JWT 认证
   - 支持数据缓存
   
2. 前端开发
   - 使用 Vue.js 框架
   - Element UI 组件库
   - ECharts 图表展示

3. 部署要求
   - Python 3.8+
   - Node.js 14+
   - MySQL 5.7+
   - Redis (可选，用于缓存)