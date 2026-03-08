# BigDataOps 项目结构

```
BigDataOps/
│
├── src/                          # 源代码目录
│   ├── __init__.py              # 包初始化文件
│   │
│   ├── config/                  # 配置管理模块
│   │   ├── __init__.py
│   │   └── config_manager.py    # 配置管理器类
│   │
│   ├── services/                # 业务逻辑服务层
│   │   ├── __init__.py          # 服务聚合和导出
│   │   ├── base.py              # 基础服务类（API 请求、指标收集）
│   │   ├── exceptions.py        # 自定义异常定义
│   │   └── types.py             # 数据类型定义
│   │
│   ├── render/                  # 渲染层（生成报告）
│   │   ├── __init__.py
│   │   ├── base_renderer.py     # 渲染器基类
│   │   └── component_renderer.py # 组件报告渲染器
│   │
│   ├── db/                      # 数据库层
│   │   ├── __init__.py
│   │   └── repository.py        # 数据持久化仓库
│   │
│   └── utils/                   # 工具函数
│       ├── __init__.py
│       ├── async_utils.py       # 异步工具函数
│       └── env_manager.py       # 环境管理器
│
├── tests/                       # 测试文件目录
│   ├── test_bigdata_service.py  # 服务层测试
│   ├── test_config.py           # 配置管理测试
│   └── test_renderer.py         # 渲染器测试
│
├── templates/                   # HTML 模板目录
│   └── component_report.html    # 组件分析报告模板
│
├── main.py                      # 插件入口文件（核心）
├── metadata.yaml                # 插件元数据
├── _conf_schema.json            # 配置 Schema 定义
├── pyproject.toml               # Python 项目配置
├── requirements.txt             # Python 依赖列表
├── README.md                    # 项目说明文档
├── USAGE.md                     # 使用指南
├── .gitignore                   # Git 忽略规则
└── LICENSE                      # 许可证文件
```

## 📁 目录说明

### src/ - 源代码
- **config/**: 配置管理，负责读取和验证用户配置
- **services/**: 核心业务逻辑，包括：
  - API 请求处理
  - 指标数据收集
  - 健康状态评估
  - 异常处理
- **render/**: 报告渲染，生成美观的文本/图片报告
- **db/**: 数据持久化，保存历史记录和查询日志
- **utils/**: 通用工具函数

### tests/ - 测试文件
- 单元测试覆盖所有核心模块
- 使用 pytest 框架
- 包含正常场景和异常场景测试

### templates/ - 模板文件
- HTML 报告模板（用于生成图片报告）
- 使用 Jinja2 模板引擎

## 🔑 核心文件说明

### main.py
**职责**: 插件入口，注册命令处理器
- `@register` 装饰器定义插件信息
- `BigDataOpsPlugin` 主类
- `initialize()`: 初始化所有服务
- `analyze_component()`: `/bigdata` 命令处理
- `get_health_status()`: `/bigdata-status` 命令处理
- `get_summary()`: `/bigdata-summary` 命令处理
- `terminate()`: 清理资源

### metadata.yaml
**内容**: 插件元数据
- 名称、版本、作者
- 描述信息
- 标签和关键词

### _conf_schema.json
**内容**: 配置表单 Schema
- 定义 Web UI 中的配置项
- 包含类型、默认值、提示信息

### src/services/base.py
**核心功能**:
- `BaseService`: HTTP 请求基类
- `ComponentMetricsService`: 各组件指标收集
- 支持 Spark、Hadoop、Flink、Kafka 等

### src/services/__init__.py
**核心功能**:
- `BigDataService`: 聚合服务类
- `analyze_component()`: 分析组件指标
- `get_health_status()`: 健康评估
- 智能计算健康分数

### src/render/component_renderer.py
**核心功能**:
- 文本报告渲染
- 健康报告渲染
- 汇总报告渲染
- Emoji 和格式化

### src/db/repository.py
**核心功能**:
- SQLite 数据库操作
- 保存指标历史
- 记录查询日志
- 自动清理旧数据

## 🔄 数据流

```
用户命令 (main.py)
    ↓
BigDataService (src/services/__init__.py)
    ↓
ComponentMetricsService (src/services/base.py)
    ↓
HTTP API 请求 → 大数据组件
    ↓
指标数据返回
    ↓
ComponentRenderer (src/render/)
    ↓
渲染报告
    ↓
发送给用户
    ↓
保存到数据库 (src/db/repository.py)
```

## 🎯 设计模式

1. **依赖注入**: ConfigManager 注入到各服务
2. **策略模式**: 不同组件使用不同的指标收集策略
3. **工厂模式**: ComponentRenderer 根据数据类型选择渲染方式
4. **仓库模式**: Repository 封装数据库操作
5. **单例模式**: aiohttp session 共享

## 📦 依赖关系

```
aiohttp → HTTP 请求
jinja2 → 模板渲染
python-dateutil → 日期处理
sqlite3 → 数据库（Python 内置）
pytest → 测试框架
```

## 🚀 扩展性

### 添加新组件支持
1. 在 `base.py` 添加 `*_get_*_metrics()` 方法
2. 在 `component_handlers` 字典中注册
3. 在 `types.py` 添加组件类型枚举
4. 在 `renderer.py` 添加中文键名映射

### 添加新功能
1. 在 `services/` 创建新服务类
2. 在 `main.py` 添加新的命令处理器
3. 在 `render/` 添加对应的渲染方法
4. 编写单元测试

## 📝 代码风格

- 遵循 PEP 8 规范
- 使用 type hints（类型提示）
- 文档字符串（docstring）完整
- 异常处理明确
- 日志记录详细

---

**这个项目完全参照 astrbot_plugin_bangumi 的架构模式构建！** ✨
