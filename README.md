# Product Tracing System (产品追溯系统)

## 项目简介
Product Tracing System 是一个基于 Django + Vue.js 的产品追溯管理系统，用于追踪和管理产品的生命周期，包括生产、流通和销售环节。该系统帮助企业实现产品质量追溯、供应链管理和质量控制。

## 技术栈
### 后端
- Python 3.8+
- Django 4.2
- Django REST framework
- JWT (djangorestframework-simplejwt)
- MySQL 5.7+
- Redis (缓存)

### 前端
- Vue.js 2.6
- Element UI 2.15
- ECharts 5.5
- Axios
- Vue Router

### 开发工具
- Vue CLI
- Git
- VSCode/PyCharm
- Postman

## 功能模块

### 1. 用户管理系统
- 用户注册与登录
- JWT 认证
- 用户信息管理
- 角色权限控制（管理员、企业用户、普通用户）

### 2. 产品管理
- 商品分类管理
  - 分类树形结构
  - 分类编码管理
  - 状态管理
- 商品信息管理
  - 基本信息维护
  - 规格参数配置
  - 图片管理
- 批次管理
  - 批次编号生成
  - 生产日期管理
  - 库存跟踪
  - 二维码生成

### 3. 追溯管理
- 生产记录
  - 原材料记录
  - 生产环境参数
  - 质检记录
- 物流记录
  - 运输信息记录
  - 仓储信息记录
  - 配送信息记录
- 销售记录
  - 订单管理
  - 客户信息
  - 销售数据统计

### 4. 数据分析
- 销售分析
  - 销售趋势图
  - 商品销售排行
  - 分类销售占比
- 追溯分析
  - 追溯链完整性分析
  - 追溯热点分析
  - 地域分布分析
- 质量分析
  - 质量问题统计
  - 批次合格率分析
  - 预警信息分析

### 5. 系统管理
- 系统配置
- 日志管理
- 数据备份

## 项目结构

### 后端结构
```
product_tracing/
├── users/                 # 用户管理模块
├── products/             # 产品管理模块
├── tracing/             # 追溯管理模块
├── data_analysis/       # 数据分析模块
├── dashboard_app/       # 仪表盘模块
└── product_tracing/     # 项目配置
```

### 前端结构
```
vue/
├── public/              # 静态资源
├── src/
│   ├── assets/         # 资源文件
│   ├── components/     # 公共组件
│   ├── router/         # 路由配置
│   ├── utils/          # 工具函数
│   ├── views/          # 页面组件
│   │   ├── system/     # 系统管理
│   │   ├── products/   # 产品管理
│   │   ├── tracing/    # 追溯管理
│   │   └── analysis/   # 数据分析
│   ├── App.vue         # 根组件
│   └── main.js         # 入口文件
└── package.json        # 项目配置
```

## 开发环境搭建

### 后端环境
1. 安装 Python 依赖
```bash
pip install -r requirements.txt
```

2. 配置数据库
```bash
python manage.py makemigrations
python manage.py migrate
```

3. 创建超级用户
```bash
python manage.py createsuperuser
```

4. 启动服务
```bash
python manage.py runserver
```

### 前端环境
1. 安装依赖
```bash
npm install
```

2. 启动开发服务器
```bash
npm run serve
```

3. 打包生产环境
```bash
npm run build
```

## API 文档

### 认证相关
| 接口 | 方法 | 说明 |
|-----|------|-----|
| /api/users/auth/login/ | POST | 用户登录 |
| /api/users/auth/register/ | POST | 用户注册 |
| /api/users/auth/logout/ | POST | 用户登出 |

### 用户管理
| 接口 | 方法 | 说明 |
|-----|------|-----|
| /api/users/ | GET | 获取用户列表 |
| /api/users/ | POST | 创建用户 |
| /api/users/{id}/ | GET | 获取用户详情 |
| /api/users/{id}/ | PUT | 更新用户信息 |
| /api/users/{id}/ | DELETE | 删除用户 |

### 产品管理
| 接口 | 方法 | 说明 |
|-----|------|-----|
| /api/products/categories/ | GET/POST | 分类管理 |
| /api/products/ | GET/POST | 商品管理 |
| /api/products/batches/ | GET/POST | 批次管理 |

### 追溯管理
| 接口 | 方法 | 说明 |
|-----|------|-----|
| /api/tracing/production/ | GET/POST | 生产记录 |
| /api/tracing/logistics/ | GET/POST | 物流记录 |
| /api/tracing/sales/ | GET/POST | 销售记录 |

### 数据分析
| 接口 | 方法 | 说明 |
|-----|------|-----|
| /api/analysis/sales/ | GET | 销售分析 |
| /api/analysis/tracing/ | GET | 追溯分析 |
| /api/analysis/quality/ | GET | 质量分析 |

## 部署说明

### 系统要求
- Python 3.8+
- Node.js 14+
- MySQL 5.7+
- Redis 6.0+
- Nginx 1.18+

### 部署步骤
1. 后端部署
2. 前端部署
3. Nginx 配置
4. 数据库配置
5. Redis 配置

## 开发规范

### Git 提交规范
- feat: 新功能
- fix: 修复 bug
- docs: 文档更新
- style: 代码格式
- refactor: 重构
- test: 测试
- chore: 构建过程或辅助工具的变动

### 代码规范
- Python: PEP8
- JavaScript: ESLint
- Vue: Vue Style Guide

## 贡献指南
1. Fork 项目
2. 创建功能分支
3. 提交变更
4. 发起 Pull Request

## 版本历史
- v1.0.0 基础功能实现
- v1.1.0 添加数据分析功能
- v1.2.0 优化用户体验

## 许可证
MIT License

## 联系方式
- 作者：XXX
- 邮箱：xxx@example.com