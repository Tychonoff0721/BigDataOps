# 🚀 BigDataOps 快速启动指南

## ⚡ 5 分钟快速上手

### 步骤 1: 安装依赖（1 分钟）

```bash
cd C:\Users\123\PycharmProjects\BigDataOps
pip install -r requirements.txt
```

### 步骤 2: 配置插件（2 分钟）

在 AstrBot 管理界面中配置：

**最小化配置（仅测试）：**
```yaml
api_endpoint: ""  # 留空，使用模拟数据
```

**生产环境配置：**
```yaml
api_endpoint: "http://localhost:8088"  # Hadoop YARN 地址
api_username: "admin"  # 可选
api_password: "admin123"  # 可选
timeout_seconds: 30
max_retries: 3
cache_enabled: true
```

### 步骤 3: 启用插件（1 分钟）

在 AstrBot 插件管理页面：
1. 找到 `astrbot_plugin_bigdataops`
2. 点击"启用"

### 步骤 4: 测试命令（1 分钟）

发送以下命令测试：

```
/bigdata-help           # 查看帮助
/bigdata spark          # 分析 Spark 组件
/bigdata-summary        # 查看所有组件汇总
```

## 📋 示例输出

### 示例 1: 分析 Spark 组件

**用户输入:**
```
/bigdata spark
```

**机器人回复:**
```
📊 Spark 组件分析报告
========================================

✅ 健康状态：🟢 HEALTHY

• 工作节点数：5
• 活跃工作节点：5
• CPU 核心数：40
• 内存总量：65.5K MB
• 运行中的应用：3
• 已完成应用：12

========================================
💡 提示：使用 /bigdata status <组件> 查看详细健康评估
```

### 示例 2: 查看健康状态

**用户输入:**
```
/bigdata-status hadoop
```

**机器人回复:**
```
🏥 Hadoop 健康检查报告
========================================

⚠️ 状态：WARNING
📈 健康分数：70/100

⚠️ 发现的问题:
  1. 有 2 个 NodeManager 离线
  2. 内存使用率超过 80%

💡 改进建议:
  1. 检查 NodeManager 进程状态
  2. 考虑增加集群资源或优化作业配置

========================================
```

### 示例 3: 查看所有组件

**用户输入:**
```
/bigdata-summary
```

**机器人回复:**
```
📊 大数据组件总览
========================================

📦 组件总数：6
🟢 健康：4
🟡 警告：1
🔴 严重：1

各组件状态:
----------------------------------------
✅ SPARK: 95 分 (healthy)
⚠️ HADOOP: 70 分 (warning)
✅ FLINK: 90 分 (healthy)
❌ KAFKA: 30 分 (critical)
✅ HDFS: 85 分 (healthy)
✅ YARN: 80 分 (healthy)

========================================
💡 提示：使用 /bigdata <组件名> 查看单个组件详情
```

## 🔧 常用大数据组件默认端口

| 组件 | 默认端口 | API 端点示例 |
|------|----------|-------------|
| Hadoop YARN | 8088 | http://localhost:8088 |
| Spark Master | 8080 | http://localhost:8080 |
| Flink JobManager | 8081 | http://localhost:8081 |
| HDFS NameNode | 9870 | http://localhost:9870 |
| Kafka Broker | 9092 | http://localhost:9092 |

## 🐛 常见问题

### Q1: 提示"服务未初始化"？
**A:** 检查 `api_endpoint` 是否配置正确

### Q2: 如何查看日志？
**A:** AstrBot 日志文件通常在 `logs/` 目录

### Q3: 支持哪些大数据组件？
**A:** Spark, Hadoop, Flink, Kafka, HDFS, YARN, Hive, Presto, ClickHouse 等

### Q4: 可以自定义告警吗？
**A:** 可以，修改 `src/services/__init__.py` 中的健康检查逻辑

## 📚 进阶使用

详细使用文档请查看：[USAGE.md](USAGE.md)

项目结构说明请查看：[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

---

**开始使用吧！** 🎉

如有问题，请查看 README.md 或提交 Issue。
