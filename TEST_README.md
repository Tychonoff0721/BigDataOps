# 🧪 BigDataOps 测试程序快速指南

## ⚡ 30 秒开始

### Windows 用户
```cmd
test.bat help
test.bat analyze spark
test.bat summary
```

### Linux/Mac 用户
```bash
chmod +x test.sh
./test.sh help
./test.sh analyze spark
./test.sh summary
```

### 或直接使用 Python
```bash
python test_cli.py help
python test_cli.py analyze spark
python test_cli.py summary
```

---

## 📋 可用命令

| 命令 | 用途 | 示例 |
|------|------|------|
| `analyze <组件>` | 分析组件指标 | `python test_cli.py analyze spark` |
| `status <组件>` | 查看健康状态 | `python test_cli.py status hadoop` |
| `summary` | 查看所有组件汇总 | `python test_cli.py summary` |
| `help` | 显示帮助信息 | `python test_cli.py help` |

---

## 🎯 支持的组件

- **spark** - Apache Spark（分布式计算引擎）✅
- **hadoop** - Apache Hadoop（分布式存储和计算）⚠️
- **flink** - Apache Flink（流式计算引擎）✅
- **kafka** - Apache Kafka（消息队列）❌
- **hdfs** - Hadoop HDFS（分布式文件系统）✅
- **yarn** - Hadoop YARN（资源调度器）✅

---

## 💬 示例输出

### 1. 分析 Spark 组件
```bash
$ python test_cli.py analyze spark

📊 Spark 组件分析报告
========================================

✅ 健康状态：HEALTHY

• 工作节点数：5
• CPU 核心数：40
• 内存总量：64.0K MB
• 运行中的应用：3
```

### 2. 查看 Hadoop 健康状态
```bash
$ python test_cli.py status hadoop

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
```

### 3. 查看所有组件汇总
```bash
$ python test_cli.py summary

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
```

---

## 🔍 详细说明

### analyze 命令
**用途**: 查看指定组件的详细性能指标

**输出内容**:
- 健康状态
- 各项关键指标（节点数、CPU、内存等）
- 运行中的应用/作业数量

### status 命令
**用途**: 获取组件的健康评估和问题诊断

**输出内容**:
- 健康状态（Healthy/Warning/Critical）
- 健康分数（0-100）
- 发现的问题列表
- 改进建议列表

### summary 命令
**用途**: 一键查看所有支持组件的整体状态

**输出内容**:
- 组件总数
- 健康/警告/严重的数量统计
- 各组件的评分和状态

---

## 🎨 特点

✅ **无需真实环境** - 使用 Mock 数据，开箱即用  
✅ **快速测试** - 毫秒级响应，无需等待网络请求  
✅ **易于扩展** - 可自定义 Mock 数据和评估规则  
✅ **美观输出** - Emoji 格式化，清晰易读  
✅ **跨平台** - Windows/Linux/Mac 全支持  

---

## 🛠️ 自定义 Mock 数据

编辑 `test_cli.py` 文件中的 `_init_mock_data()` 方法：

```python
def _init_mock_data(self):
    return {
        "spark": {
            "component": "Spark",
            "workers": 10,      # 修改这里
            "cores": 80,        # 修改这里
            "health": "healthy",
        },
        # ... 其他组件
    }
```

---

## 📚 更多文档

- [TEST_CLI_GUIDE.md](TEST_CLI_GUIDE.md) - 完整使用指南
- [TEST_EXAMPLES.md](TEST_EXAMPLES.md) - 详细示例输出
- [USAGE.md](USAGE.md) - 真实插件使用文档
- [QUICKSTART.md](QUICKSTART.md) - 插件快速启动

---

## ❓ 常见问题

### Q: 为什么数据是假的？
A: 这是 Mock 数据，用于测试和演示。要使用真实数据，请配置真实的大数据集群 API。

### Q: 能修改健康评估规则吗？
A: 可以！编辑 `get_health_status()` 方法中的逻辑即可。

### Q: 如何添加新组件？
A: 
1. 在 `_init_mock_data()` 中添加新组件数据
2. 在渲染器的 `key_names` 字典中添加中文映射
3. 更新帮助文档

---

## 🎉 开始测试吧！

```bash
python test_cli.py summary
```

**祝你使用愉快！** 🚀
