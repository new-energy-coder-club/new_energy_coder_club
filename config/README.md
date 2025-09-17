# ⚙️ 配置文件库

欢迎来到NEC新能源极客俱乐部的配置文件库！这里汇集了所有项目的配置文件、环境变量、部署配置和系统设置，实现配置的统一管理和标准化。

## 📂 目录结构

```
config/
├── environments/         # 环境配置
│   ├── development/      # 开发环境配置
│   ├── staging/          # 测试环境配置
│   ├── production/       # 生产环境配置
│   └── local/            # 本地环境配置
├── applications/         # 应用配置
│   ├── web/              # Web应用配置
│   ├── api/              # API服务配置
│   ├── database/         # 数据库配置
│   └── cache/            # 缓存配置
├── infrastructure/       # 基础设施配置
│   ├── docker/           # Docker配置
│   ├── kubernetes/       # K8s配置
│   ├── nginx/            # Nginx配置
│   └── monitoring/       # 监控配置
├── ci_cd/                # CI/CD配置
│   ├── github_actions/   # GitHub Actions
│   ├── jenkins/          # Jenkins配置
│   ├── gitlab_ci/        # GitLab CI配置
│   └── azure_devops/     # Azure DevOps配置
├── security/             # 安全配置
│   ├── ssl/              # SSL证书配置
│   ├── auth/             # 认证配置
│   ├── firewall/         # 防火墙配置
│   └── secrets/          # 密钥管理配置
├── logging/              # 日志配置
│   ├── application/      # 应用日志配置
│   ├── system/           # 系统日志配置
│   ├── audit/            # 审计日志配置
│   └── monitoring/       # 监控日志配置
├── backup/               # 备份配置
│   ├── database/         # 数据库备份配置
│   ├── files/            # 文件备份配置
│   └── system/           # 系统备份配置
└── templates/            # 配置模板
    ├── project/          # 项目配置模板
    ├── service/          # 服务配置模板
    └── deployment/       # 部署配置模板
```

## 🌍 环境配置 (Environments)

### 🔧 开发环境配置 (development/)
开发环境的配置文件和环境变量

**配置文件**:
```
development/
├── .env.development      # 开发环境变量
├── database.yml          # 数据库配置
├── redis.conf            # Redis配置
├── logging.yml           # 日志配置
└── services.yml          # 服务配置
```

**示例配置** (`.env.development`):
```bash
# 应用配置
APP_ENV=development
APP_DEBUG=true
APP_PORT=3000
APP_HOST=localhost

# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=nec_dev
DB_USER=dev_user
DB_PASSWORD=dev_password

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# 日志配置
LOG_LEVEL=debug
LOG_FILE=./logs/development.log
```

### 🧪 测试环境配置 (staging/)
测试环境的配置文件，用于集成测试和预发布验证

**特点**:
- 接近生产环境的配置
- 启用详细的日志记录
- 集成测试数据库
- 性能监控配置

### 🚀 生产环境配置 (production/)
生产环境的配置文件，注重性能、安全和稳定性

**安全要求**:
- 敏感信息使用环境变量
- 启用SSL/TLS加密
- 配置防火墙规则
- 启用审计日志

**示例配置** (`.env.production`):
```bash
# 应用配置
APP_ENV=production
APP_DEBUG=false
APP_PORT=80
APP_HOST=0.0.0.0

# 数据库配置
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}

# 安全配置
SSL_ENABLED=true
SSL_CERT_PATH=/etc/ssl/certs/app.crt
SSL_KEY_PATH=/etc/ssl/private/app.key

# 监控配置
MONITORING_ENABLED=true
METRICS_PORT=9090
```

### 🏠 本地环境配置 (local/)
开发者本地环境的个性化配置

**特点**:
- 个人开发偏好设置
- 本地服务端口配置
- 开发工具集成配置
- 调试和测试配置

## 📱 应用配置 (Applications)

### 🌐 Web应用配置 (web/)
Web前端应用的配置文件

**配置文件**:
```
web/
├── webpack.config.js     # Webpack构建配置
├── babel.config.js       # Babel转译配置
├── eslint.config.js      # ESLint代码检查配置
├── prettier.config.js    # Prettier代码格式化配置
├── tsconfig.json         # TypeScript配置
└── vite.config.ts        # Vite构建配置
```

**Webpack配置示例**:
```javascript
module.exports = {
  entry: './src/index.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js'
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        use: 'babel-loader'
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      }
    ]
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html'
    })
  ]
};
```

### 🔌 API服务配置 (api/)
后端API服务的配置文件

**配置文件**:
```
api/
├── server.yml            # 服务器配置
├── routes.yml            # 路由配置
├── middleware.yml        # 中间件配置
├── cors.yml              # CORS配置
└── rate_limit.yml        # 限流配置
```

**服务器配置示例** (`server.yml`):
```yaml
server:
  port: 8080
  host: 0.0.0.0
  timeout: 30000
  max_connections: 1000

cors:
  origin: 
    - http://localhost:3000
    - https://nec-club.com
  methods:
    - GET
    - POST
    - PUT
    - DELETE
  credentials: true

rate_limit:
  window_ms: 900000  # 15分钟
  max_requests: 100  # 最大请求数
  message: "请求过于频繁，请稍后再试"
```

### 🗄️ 数据库配置 (database/)
数据库连接和配置文件

**配置文件**:
```
database/
├── mysql.yml             # MySQL配置
├── postgresql.yml        # PostgreSQL配置
├── mongodb.yml           # MongoDB配置
├── redis.yml             # Redis配置
└── migrations/           # 数据库迁移配置
```

**MySQL配置示例** (`mysql.yml`):
```yaml
mysql:
  development:
    host: localhost
    port: 3306
    database: nec_dev
    username: dev_user
    password: dev_password
    charset: utf8mb4
    collation: utf8mb4_unicode_ci
    pool:
      min: 5
      max: 20
      idle_timeout: 30000
  
  production:
    host: ${DB_HOST}
    port: ${DB_PORT}
    database: ${DB_NAME}
    username: ${DB_USER}
    password: ${DB_PASSWORD}
    charset: utf8mb4
    collation: utf8mb4_unicode_ci
    pool:
      min: 10
      max: 50
      idle_timeout: 60000
    ssl:
      enabled: true
      ca_cert: /etc/ssl/certs/mysql-ca.pem
```

### 💾 缓存配置 (cache/)
缓存系统的配置文件

**配置文件**:
```
cache/
├── redis.yml             # Redis缓存配置
├── memcached.yml         # Memcached配置
├── application.yml       # 应用缓存配置
└── cdn.yml               # CDN配置
```

## 🏗️ 基础设施配置 (Infrastructure)

### 🐳 Docker配置 (docker/)
Docker容器化相关配置文件

**配置文件**:
```
docker/
├── Dockerfile.web        # Web应用Dockerfile
├── Dockerfile.api        # API服务Dockerfile
├── docker-compose.yml    # Docker Compose配置
├── docker-compose.prod.yml # 生产环境Compose配置
└── .dockerignore         # Docker忽略文件
```

**Docker Compose配置示例**:
```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: docker/Dockerfile.web
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
    volumes:
      - ./src:/app/src
    depends_on:
      - api
      - database

  api:
    build:
      context: .
      dockerfile: docker/Dockerfile.api
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=development
      - DB_HOST=database
    depends_on:
      - database
      - redis

  database:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=nec_dev
      - MYSQL_USER=dev_user
      - MYSQL_PASSWORD=dev_password
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  mysql_data:
  redis_data:
```

### ☸️ Kubernetes配置 (kubernetes/)
Kubernetes集群部署配置文件

**配置文件**:
```
kubernetes/
├── namespace.yaml        # 命名空间配置
├── deployment.yaml       # 部署配置
├── service.yaml          # 服务配置
├── ingress.yaml          # 入口配置
├── configmap.yaml        # 配置映射
├── secret.yaml           # 密钥配置
└── hpa.yaml              # 水平扩展配置
```

### 🌐 Nginx配置 (nginx/)
Nginx反向代理和负载均衡配置

**配置文件**:
```
nginx/
├── nginx.conf            # 主配置文件
├── sites-available/      # 可用站点配置
├── sites-enabled/        # 启用站点配置
├── ssl/                  # SSL配置
└── upstream.conf         # 上游服务器配置
```

**Nginx配置示例**:
```nginx
upstream api_servers {
    server api1:8080 weight=3;
    server api2:8080 weight=2;
    server api3:8080 weight=1;
    keepalive 32;
}

server {
    listen 80;
    server_name nec-club.com www.nec-club.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name nec-club.com www.nec-club.com;

    ssl_certificate /etc/ssl/certs/nec-club.com.crt;
    ssl_certificate_key /etc/ssl/private/nec-club.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://api_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 📊 监控配置 (monitoring/)
系统监控和指标收集配置

**配置文件**:
```
monitoring/
├── prometheus.yml        # Prometheus配置
├── grafana/              # Grafana配置
├── alertmanager.yml      # 告警管理配置
├── node_exporter.yml     # 节点监控配置
└── custom_metrics.yml    # 自定义指标配置
```

## 🔄 CI/CD配置 (CI_CD)

### 🐙 GitHub Actions (github_actions/)
GitHub Actions工作流配置

**工作流文件**:
```
github_actions/
├── ci.yml                # 持续集成工作流
├── cd.yml                # 持续部署工作流
├── test.yml              # 测试工作流
├── security.yml          # 安全扫描工作流
└── release.yml           # 发布工作流
```

**CI工作流示例** (`ci.yml`):
```yaml
name: Continuous Integration

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [16.x, 18.x, 20.x]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run tests
      run: npm run test:coverage
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage/lcov.info
    
    - name: Build application
      run: npm run build
    
    - name: Run security audit
      run: npm audit --audit-level high
```

### 🔨 Jenkins配置 (jenkins/)
Jenkins持续集成配置

**配置文件**:
```
jenkins/
├── Jenkinsfile           # 流水线配置
├── jobs/                 # 任务配置
├── plugins.txt           # 插件列表
└── scripts/              # 构建脚本
```

### 🦊 GitLab CI配置 (gitlab_ci/)
GitLab CI/CD配置

**配置文件**:
```
gitlab_ci/
├── .gitlab-ci.yml        # 主配置文件
├── stages/               # 阶段配置
├── jobs/                 # 任务配置
└── templates/            # 模板配置
```

## 🔒 安全配置 (Security)

### 🔐 SSL配置 (ssl/)
SSL/TLS证书和加密配置

**配置文件**:
```
ssl/
├── certificates/         # 证书文件
├── private_keys/         # 私钥文件
├── ca_bundles/           # CA证书包
├── ssl_config.yml        # SSL配置
└── renewal_scripts/      # 证书更新脚本
```

### 🔑 认证配置 (auth/)
身份认证和授权配置

**配置文件**:
```
auth/
├── oauth2.yml            # OAuth2配置
├── jwt.yml               # JWT配置
├── ldap.yml              # LDAP配置
├── saml.yml              # SAML配置
└── rbac.yml              # 基于角色的访问控制
```

### 🛡️ 防火墙配置 (firewall/)
网络安全和防火墙规则配置

**配置文件**:
```
firewall/
├── iptables.rules        # iptables规则
├── ufw.conf              # UFW配置
├── fail2ban.conf         # Fail2ban配置
└── security_groups.yml   # 云安全组配置
```

### 🔐 密钥管理配置 (secrets/)
密钥和敏感信息管理配置

**配置文件**:
```
secrets/
├── vault.yml             # HashiCorp Vault配置
├── kubernetes_secrets.yml # K8s密钥配置
├── env_secrets.yml       # 环境变量密钥
└── encryption.yml        # 加密配置
```

## 📝 日志配置 (Logging)

### 📱 应用日志配置 (application/)
应用程序日志配置

**配置文件**:
```
application/
├── logback.xml           # Java应用日志配置
├── winston.js            # Node.js日志配置
├── python_logging.yml    # Python日志配置
└── log_rotation.conf     # 日志轮转配置
```

**Winston日志配置示例**:
```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'nec-api' },
  transports: [
    new winston.transports.File({ 
      filename: 'logs/error.log', 
      level: 'error' 
    }),
    new winston.transports.File({ 
      filename: 'logs/combined.log' 
    })
  ]
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }));
}

module.exports = logger;
```

### 🖥️ 系统日志配置 (system/)
系统级日志配置

**配置文件**:
```
system/
├── rsyslog.conf          # Rsyslog配置
├── journald.conf         # Systemd日志配置
├── syslog-ng.conf        # Syslog-ng配置
└── logrotate.conf        # 日志轮转配置
```

### 🔍 审计日志配置 (audit/)
安全审计日志配置

**配置文件**:
```
audit/
├── auditd.conf           # Linux审计守护进程配置
├── audit.rules           # 审计规则
├── security_events.yml   # 安全事件配置
└── compliance.yml        # 合规性配置
```

## 💾 备份配置 (Backup)

### 🗄️ 数据库备份配置 (database/)
数据库备份策略和配置

**配置文件**:
```
database/
├── mysql_backup.yml      # MySQL备份配置
├── postgresql_backup.yml # PostgreSQL备份配置
├── mongodb_backup.yml    # MongoDB备份配置
└── backup_schedule.yml   # 备份计划配置
```

**MySQL备份配置示例**:
```yaml
mysql_backup:
  connection:
    host: localhost
    port: 3306
    user: backup_user
    password: ${BACKUP_PASSWORD}
  
  databases:
    - nec_production
    - nec_analytics
  
  schedule:
    full_backup: "0 2 * * 0"    # 每周日凌晨2点全量备份
    incremental: "0 2 * * 1-6"  # 每天凌晨2点增量备份
  
  retention:
    full_backup_days: 30
    incremental_days: 7
  
  storage:
    local_path: /backup/mysql
    s3_bucket: nec-backups
    encryption: true
```

### 📁 文件备份配置 (files/)
文件系统备份配置

**配置文件**:
```
files/
├── rsync_backup.yml      # Rsync备份配置
├── tar_backup.yml        # Tar归档备份配置
├── cloud_sync.yml        # 云同步配置
└── exclude_patterns.txt  # 排除模式文件
```

### 🖥️ 系统备份配置 (system/)
系统级备份配置

**配置文件**:
```
system/
├── system_backup.yml     # 系统备份配置
├── vm_snapshot.yml       # 虚拟机快照配置
├── docker_backup.yml     # Docker备份配置
└── recovery_plan.yml     # 恢复计划配置
```

## 📄 配置模板 (Templates)

### 📋 项目配置模板 (project/)
新项目的标准配置模板

**模板文件**:
```
project/
├── .env.template         # 环境变量模板
├── package.json.template # Node.js项目模板
├── requirements.txt.template # Python项目模板
├── Dockerfile.template   # Docker模板
└── README.md.template    # 项目文档模板
```

### 🔧 服务配置模板 (service/)
微服务的标准配置模板

**模板文件**:
```
service/
├── api_service.yml       # API服务模板
├── worker_service.yml    # 后台任务服务模板
├── database_service.yml  # 数据库服务模板
└── cache_service.yml     # 缓存服务模板
```

### 🚀 部署配置模板 (deployment/)
部署相关的配置模板

**模板文件**:
```
deployment/
├── docker-compose.template # Docker Compose模板
├── kubernetes.template     # Kubernetes部署模板
├── nginx.template          # Nginx配置模板
└── ci_cd.template          # CI/CD流水线模板
```

## 📊 配置统计

| 配置类型 | 文件数量 | 配置项数 | 最近更新 |
|----------|----------|----------|----------|
| 🌍 环境配置 | 0个 | 0项 | - |
| 📱 应用配置 | 0个 | 0项 | - |
| 🏗️ 基础设施配置 | 0个 | 0项 | - |
| 🔄 CI/CD配置 | 0个 | 0项 | - |
| 🔒 安全配置 | 0个 | 0项 | - |
| 📝 日志配置 | 0个 | 0项 | - |
| 💾 备份配置 | 0个 | 0项 | - |
| 📄 配置模板 | 0个 | 0项 | - |

## 🎯 使用指南

### 🚀 快速开始
1. **选择环境**: 根据部署环境选择对应配置
2. **复制模板**: 从模板目录复制相关配置文件
3. **修改配置**: 根据实际需求修改配置参数
4. **验证配置**: 使用配置验证工具检查配置正确性
5. **应用配置**: 将配置应用到目标环境

### 🔧 配置管理
1. **版本控制**: 使用Git管理配置文件版本
2. **环境隔离**: 不同环境使用独立的配置文件
3. **敏感信息**: 使用环境变量或密钥管理系统
4. **配置验证**: 定期验证配置文件的有效性
5. **文档更新**: 及时更新配置文档和说明

### 🔒 安全最佳实践
1. **密钥管理**: 不在配置文件中硬编码密钥
2. **权限控制**: 限制配置文件的访问权限
3. **加密存储**: 对敏感配置进行加密存储
4. **审计日志**: 记录配置文件的修改历史
5. **定期轮换**: 定期更新密钥和证书

## 📋 配置规范

### 📝 文件格式
- **YAML**: 推荐用于复杂配置结构
- **JSON**: 适用于API配置和数据交换
- **INI**: 适用于简单的键值对配置
- **ENV**: 环境变量配置文件
- **XML**: 特定应用的配置格式

### 🏷️ 命名规范
- **文件命名**: 使用小写字母和下划线
- **配置项**: 使用大写字母和下划线
- **环境前缀**: 使用环境名作为前缀
- **版本标识**: 在文件名中包含版本信息

### ✅ 质量标准
- **完整性**: 配置项完整，无遗漏
- **正确性**: 配置值正确，格式规范
- **一致性**: 同类配置保持一致
- **可读性**: 配置结构清晰，注释完整
- **可维护性**: 配置易于理解和修改

## 🤝 贡献指南

### 📝 配置贡献流程
1. **需求分析**: 明确配置需求和使用场景
2. **设计配置**: 设计配置结构和参数
3. **编写配置**: 按照规范编写配置文件
4. **测试验证**: 在测试环境验证配置有效性
5. **文档编写**: 编写配置说明和使用文档
6. **代码审查**: 提交配置审查
7. **部署应用**: 部署到目标环境

### 🔍 审查标准
- **功能完整**: 配置功能完整可用
- **安全合规**: 符合安全规范要求
- **性能优化**: 配置参数合理优化
- **兼容性**: 跨环境兼容性良好
- **文档完整**: 配置文档完整准确

## 🔗 相关链接

- [🏆 竞赛项目](../competitions_new/README.md)
- [🔬 技术项目](../projects_new/README.md)
- [📦 共享资源](../shared_new/README.md)
- [📚 文档库](../docs_new/README.md)
- [🛠️ 开发工具](../scripts/README.md)

---

> 💡 **理念**: 标准化配置管理，让部署和运维变得简单可靠！

**维护团队**: 配置管理小组 | **联系方式**: [GitHub Issues](https://github.com/Darrenpig/new_energy_coder_club/issues)