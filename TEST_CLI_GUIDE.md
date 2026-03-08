# 🧪 BigDataOps 命令行测试程序

## 📋 简介

这是一个独立的命令行测试工具，使用 **Mock 数据**模拟大数据组件的指标查询和分析功能。无需真实的大数据集群即可测试和演示插件功能。

## 🚀 快速开始

### 运行环境要求

- Python 3.10+
- 无需任何外部依赖（使用 Python 标准库）

### 基本用法

```bash
# 查看帮助
python test_cli.py help

# 分析 Spark 组件
python test_cli.py analyze spark

# 查看 Hadoop 健康状态
python test_cli.py status hadoop

# 查看所有组件汇总
python test_cli.py summary
```

## 💬 命令详解

### 1. analyze - 分析组件指标

**用途**: 查看指定大数据组件的详细性能指标

**语法**: 
```bash
python test_cli.py analyze <组件名>
```

**示例输出**:
```bash
$ python test_cli.py analyze spark

🔄 正在分析 SPARK 组件...

📊 Spark 组件分析报告
========================================

✅ 健康状态：HEALTHY

• 工作节点数：5
• 活跃工作节点：5
• CPU 核心数：40
• 内存总量：64.0K MB
• 运行中的应用：3
• 已完成应用：12

========================================
💡 提示：使用 test_cli.py status <组件> 查看详细健康评估
```

### 2. status - 查看健康状态

**用途**: 获取组件的健康评估、问题诊断和改进建议

**语法**:
```bash
python test_cli.py status <组件名>
```

**示例输出**:
```bash
$ python test_cli.py status hadoop

🔄 正在检查 HADOOP 组件健康状态...

🏥 Hadoop 健康检查报告
========================================

⚠️ 状态：WARNING
📈 健康分数：70/100

⚠️ 发现的问题:
  1. 有 2 个节点离线
  2. 内存使用率过高 (78.1%)

💡 改进建议:
  1. 检查离线节点的网络和进程状态
  2. 考虑增加集群资源或优化作业配置

========================================
```

### 3. summary - 查看汇总信息

**用途**: 一键查看所有支持组件的整体状态

**语法**:
```bash
python test_cli.py summary
```

**示例输出**:
```bash
$ python test_cli.py summary

🔄 正在获取所有组件汇总信息...

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
✅ FLINK: 95 分 (healthy)
❌ KAFKA: 35 分 (critical)
✅ HDFS: 95 分 (healthy)
✅ YARN: 95 分 (healthy)

========================================
💡 提示：使用 test_cli.py analyze <组件名> 查看单个组件详情
```

### 4. help - 显示帮助信息

**用途**: 查看可用的命令和支持的组件列表

**语法**:
```bash
python test_cli.py help
```

## 🔧 支持的组件

| 组件 | 命令 | 类型 | Mock 健康状态 |
|------|------|------|--------------|
| Apache Spark | `analyze spark` | 分布式计算引擎 | ✅ Healthy |
| Apache Hadoop | `analyze hadoop` | 分布式存储和计算 | ⚠️ Warning |
| Apache Flink | `analyze flink` | 流式计算引擎 | ✅ Healthy |
| Apache Kafka | `analyze kafka` | 消息队列 | ❌ Critical |
| Hadoop HDFS | `analyze hdfs` | 分布式文件系统 | ✅ Healthy |
| Hadoop YARN | `analyze yarn` | 资源调度器 | ✅ Healthy |

## 🎯 使用场景

### 1. 开发测试
在开发 AstrBot 插件时，无需连接真实集群即可测试代码逻辑。

### 2. 功能演示
向他人展示 BigDataOps 插件的功能，即使没有大数据环境。

### 3. 学习工具
理解大数据分析插件的工作原理和数据流程。

### 4. 原型验证
快速验证新的分析算法和健康评估逻辑。

## 📊 Mock 数据说明

### Spark (Healthy)
- 5 个 Worker 节点，全部在线
- 40 个 CPU 核心
- 64GB 内存
- 3 个运行中的应用

### Hadoop (Warning)
- 10 个节点中 8 个活跃
- 内存使用率 78%
- 15 个运行中的容器
- **模拟问题**: 节点离线、内存压力

### Flink (Healthy)
- 1 个 JobManager
- 16 个 Slot，8 个可用
- 5 个运行中的作业
- 仅 2 个失败作业

### Kafka (Critical)
- 3 个 Broker
- 15 个主题，60 个分区
- 5 个复制不足的分区
- **模拟问题**: 分区复制异常

### HDFS (Healthy)
- 125,000 个文件
- 380,000 个区块
- 1TB 总容量，使用 716GB

### YARN (Healthy)
- 10 个节点中 9 个活跃
- 内存使用率 75%
- 12 个运行中的容器

## 🔍 代码结构

```
test_cli.py
├── MockBigDataService    # Mock 数据服务
│   ├── get_component_metrics()
│   ├── get_health_status()
│   └── get_all_components_summary()
├── MockRenderer          # Mock 渲染器
│   ├── render_analyze_report()
│   ├── render_health_report()
│   └── render_summary_report()
└── main()               # 命令行入口
```

## 🛠️ 扩展指南

### 添加新的 Mock 组件

1. 在 `MockBigDataService._init_mock_data()` 中添加新组件的数据
2. 在 `MockRenderer.render_analyze_report()` 的 `key_names` 字典中添加中文映射
3. 更新帮助文档

**示例**: 添加 Apache Hive
```python
"hive": {
    "component": "Hive",
    "databases": 5,
    "tables": 120,
    "queries_running": 3,
    "health": "healthy",
}
```

### 自定义健康评估逻辑

修改 `MockBigDataService.get_health_status()` 方法：

```python
if component_name == "custom":
    if metrics.get("some_metric", 0) > 100:
        health = "warning"
        score = 60
```

## 📝 与真实插件的对比

| 特性 | 测试程序 | 真实插件 |
|------|----------|----------|
| 数据来源 | Mock 数据 | 真实 API |
| 网络请求 | 模拟延迟 | 真实 HTTP |
| 数据库 | 无 | SQLite |
| 配置系统 | 无 | 完整的 ConfigManager |
| 错误处理 | 简化版 | 完善的重试机制 |
| 适用场景 | 开发/演示 | 生产环境 |

## 🎓 学习路径

1. **入门**: 运行 `python test_cli.py help` 了解基本命令
2. **熟悉**: 尝试各个命令，观察不同的输出
3. **理解**: 阅读源代码，了解 Mock 数据的生成逻辑
4. **扩展**: 添加自己的 Mock 组件和评估规则
5. **实战**: 将 Mock 服务替换为真实的 API 调用

## 💡 最佳实践

### 1. 测试驱动开发
```bash
# 先写测试用例
python test_cli.py analyze spark

# 验证输出符合预期
# 然后实现真实功能
```

### 2. 渐进式替换
```python
# 1. 保持 Mock 数据结构
mock_data = {...}

# 2. 添加真实 API 调用
async def get_real_metrics(component):
    # 调用真实 API
    pass

# 3. 通过配置切换数据源
if USE_MOCK:
    return mock_data
else:
    return await get_real_metrics(component)
```

### 3. 对比测试
```bash
# 同时运行 Mock 和真实版本，对比结果
python test_cli.py analyze spark      # Mock 版本
python main.py analyze spark          # 真实版本（需配置）
```

## 🐛 常见问题

### Q1: 为什么显示的数据和我实际的不一样？
**A**: 这是 Mock 数据，用于演示和测试。要使用真实数据，需要配置真实的大数据集群 API。

### Q2: 可以修改 Mock 数据吗？
**A**: 当然可以！编辑 `test_cli.py` 中的 `_init_mock_data()` 方法即可。

### Q3: 如何连接到真实集群？
**A**: 参考 [USAGE.md](USAGE.md) 配置 `api_endpoint` 等参数。

### Q4: 能添加自定义指标吗？
**A**: 可以，在 Mock 数据字典中添加新字段，并在渲染器的 `key_names` 中定义中文名称。

## 📚 相关文档

- [QUICKSTART.md](QUICKSTART.md) - 快速启动指南
- [USAGE.md](USAGE.md) - 详细使用文档
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 项目结构说明

---

**祝你测试愉快！** 🎉

如有任何问题，欢迎随时提问。
