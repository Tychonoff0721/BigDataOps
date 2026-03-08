# BigDataOps - AstrBot 大数据分析插件

AstrBot 大数据分析插件：为 AstrBot 打造的一站式大数据组件分析助手。支持 Hadoop、Spark、Flink、Kafka 等主流大数据组件的指标查询、性能分析和健康状态评估。

## 功能特性

- 🔍 **组件搜索**: 快速查找和识别大数据组件
- 📊 **指标分析**: 自动获取组件的关键性能指标
- 📈 **健康评估**: 智能评估组件运行状态和健康度
- ⏰ **定时监控**: 支持周期性检查和自动提醒
- 💾 **数据缓存**: 减少重复请求，提升响应速度
- 🎨 **可视化报告**: 生成美观的分析报告（支持图片和文本）

## 支持的组件

### 计算引擎
- Apache Spark
- Apache Flink
- Apache Storm

### 存储系统
- Hadoop HDFS
- HBase
- Cassandra

### 消息队列
- Apache Kafka
- RabbitMQ
- RocketMQ

### 资源调度
- Hadoop YARN
- Kubernetes

### 数据仓库
- Apache Hive
- Presto
- ClickHouse

## 安装方法

1. 确保已安装 AstrBot
2. 将本插件克隆到 AstrBot 的 `plugins` 目录
3. 安装依赖：`pip install -r requirements.txt`
4. 在 AstrBot 管理界面启用插件
5. 配置 API 端点和认证信息

## 使用示例

### 基础命令

```
/bigdata spark          # 分析 Spark 组件指标
/bigdata hadoop         # 分析 Hadoop 组件指标
/bigdata flink          # 分析 Flink 组件指标
/bigdata kafka          # 分析 Kafka 组件指标
```

### 高级功能

```
/bigdata status spark   # 查看 Spark 健康状态
/bigdata metrics all    # 查看所有组件汇总指标
/bigdata history spark  # 查看 Spark 历史趋势
```

## 配置说明

在 AstrBot 插件配置页面填写以下信息：

- **api_endpoint**: 大数据组件 REST API 地址
- **api_username/password**: API 认证凭据（可选）
- **timeout_seconds**: 请求超时时间
- **cache_enabled**: 是否启用缓存
- **render_server_url**: 远程渲染服务地址（可选）

## 开发指南

### 添加新组件支持

1. 在 `src/services/` 创建新的服务类
2. 实现 `BaseService` 接口
3. 定义指标收集逻辑
4. 在 `main.py` 中注册命令

### 项目结构

```
BigDataOps/
├── src/
│   ├── config/         # 配置管理
│   ├── services/       # 业务逻辑服务
│   ├── render/         # 报告渲染
│   ├── db/            # 数据库模型
│   └── utils/         # 工具函数
├── tests/             # 单元测试
├── templates/         # HTML 模板
└── main.py           # 插件入口
```

## 许可证

Apache License 2.0

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

- GitHub Issues
- 邮件：your.email@example.com
