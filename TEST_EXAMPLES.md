# 🎯 BigDataOps 测试程序示例输出

本文档展示了命令行测试程序的各种输出示例。

## 📋 示例 1: 查看帮助

### 命令
```bash
python test_cli.py help
```

### 输出
```
📊 BigDataOps 命令行测试工具

用法：python test_cli.py <命令> [参数]

可用命令:
  analyze <组件名>     - 分析指定组件的各项指标
  status <组件名>      - 查看组件健康状态评估
  summary              - 查看所有组件汇总信息
  help                 - 显示此帮助信息

支持的组件:
  • spark       - Apache Spark (分布式计算引擎)
  • hadoop      - Apache Hadoop (分布式存储和计算)
  • flink       - Apache Flink (流式计算引擎)
  • kafka       - Apache Kafka (消息队列)
  • hdfs        - Hadoop HDFS (分布式文件系统)
  • yarn        - Hadoop YARN (资源调度器)

示例:
  python test_cli.py analyze spark
  python test_cli.py status hadoop
  python test_cli.py summary
  python test_cli.py help

注意：本测试程序使用 Mock 数据，无需真实的大数据集群即可运行。
```

---

## 📊 示例 2: 分析 Spark 组件（健康状态）

### 命令
```bash
python test_cli.py analyze spark
```

### 输出
```
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

**解读**: 
- ✅ 所有 Worker 节点都在线
- 💪 资源配置充足（40 核 64GB）
- 🚀 当前有 3 个应用在运行

---

## ⚠️ 示例 3: 查看 Hadoop 健康状态（警告）

### 命令
```bash
python test_cli.py status hadoop
```

### 输出
```
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

**解读**:
- ⚠️ 集群有问题需要关注
- 🔴 10% 的节点离线（10 个中 2 个）
- 💾 内存压力较大（接近 80%）
- 🎯 需要运维介入检查

---

## ❌ 示例 4: 查看 Kafka 健康状态（严重）

### 命令
```bash
python test_cli.py status kafka
```

### 输出
```
🔄 正在检查 KAFKA 组件健康状态...

🏥 Kafka 健康检查报告
========================================

❌ 状态：CRITICAL
📈 健康分数：35/100

⚠️ 发现的问题:
  1. 有 5 个分区复制不足
  2. 有 0 个分区离线

💡 改进建议:
  1. 立即检查 Broker 节点状态和网络连接
  2. 紧急处理离线分区，检查 Controller 状态

========================================
```

**解读**:
- 🚨 情况危急，需要立即处理
- ⚠️ 数据复制异常，可能影响高可用
- 🔧 需要马上检查 Broker 和网络

---

## 📈 示例 5: 查看所有组件汇总

### 命令
```bash
python test_cli.py summary
```

### 输出
```
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

**解读**:
- 📊 整体状况：67% 的组件健康
- ⚠️ 需要关注：Hadoop（警告）
- 🚨 紧急处理：Kafka（严重）
- ✅ 运行良好：Spark、Flink、HDFS、YARN

---

## 🔍 示例 6: 分析 Flink 组件

### 命令
```bash
python test_cli.py analyze flink
```

### 输出
```
🔄 正在分析 FLINK 组件...

📊 Flink 组件分析报告
========================================

✅ 健康状态：HEALTHY

• JobManager 数量：1
• 可用 Slot 数：8
• 总 Slot 数：16
• 运行中的作业：5
• 已完成的作业：23
• 失败的作业：2

========================================
💡 提示：使用 test_cli.py status <组件> 查看详细健康评估
```

**解读**:
- 🎯 Slot 利用率 50%（8/16 可用）
- ✅ 作业成功率很高（23 成功 vs 2 失败）
- 💪 系统运行稳定

---

## 💾 示例 7: 分析 HDFS 存储系统

### 命令
```bash
python test_cli.py analyze hdfs
```

### 输出
```
🔄 正在分析 HDFS 组件...

📊 HDFS 组件分析报告
========================================

✅ 健康状态：HEALTHY

• 文件总数：125.0K
• 区块总数：380.0K
• 总容量：1.0T B
• 已使用：716.0G B
• 剩余：308.0G B

========================================
💡 提示：使用 test_cli.py status <组件> 查看详细健康评估
```

**解读**:
- 💾 存储使用率约 70%（716GB/1TB）
- 📁 平均每个文件约 3 个区块
- ⚠️ 需要考虑扩容（剩余空间不多）

---

## 🎯 示例 8: 分析 YARN 资源调度器

### 命令
```bash
python test_cli.py analyze yarn
```

### 输出
```
🔄 正在分析 YARN 组件...

📊 YARN 组件分析报告
========================================

✅ 健康状态：HEALTHY

• 节点总数：10
• 活跃节点数：9
• 已用内存：48.0K MB
• 总内存：64.0K MB
• 已用虚拟核心：28
• 总虚拟核心：40
• 运行中的容器：12

========================================
💡 提示：使用 test_cli.py status <组件> 查看详细健康评估
```

**解读**:
- 🖥️ 90% 节点在线（9/10）
- 💾 内存使用率 75%
- 🔧 CPU 使用率 70%
- 📊 资源利用合理

---

## 🎨 输出格式说明

### Emoji 含义

| Emoji | 含义 | 使用场景 |
|-------|------|----------|
| ✅ | 健康/正常 | Healthy 状态 |
| ⚠️ | 警告/注意 | Warning 状态 |
| ❌ | 严重/错误 | Critical 状态 |
| 🟢 | 绿色/健康 | 健康组件计数 |
| 🟡 | 黄色/警告 | 警告组件计数 |
| 🔴 | 红色/严重 | 严重组件计数 |
| 📊 | 图表/统计 | 汇总报告标题 |
| 🏥 | 医院/健康 | 健康检查报告 |
| 🔄 | 刷新/加载 | 正在处理提示 |
| 💡 | 灯泡/提示 | 提示信息 |
| 💾 | 磁盘/存储 | 内存、容量相关 |
| 📁 | 文件 | 文件数量 |
| 🚀 | 火箭/性能 | 应用、作业 |
| 🎯 | 靶心/目标 | 精准提示 |

### 分隔线规范

- `=` (40 个): 主报告标题分隔
- `-` (40 个): 列表项分隔
- 空行：段落间距

---

## 🧪 测试建议

### 1. 完整测试流程
```bash
# 1. 查看所有组件汇总
python test_cli.py summary

# 2. 逐个分析健康组件
python test_cli.py analyze spark
python test_cli.py analyze flink

# 3. 重点检查问题组件
python test_cli.py status hadoop   # 查看警告
python test_cli.py status kafka    # 查看严重问题
```

### 2. 对比测试
```bash
# 对比不同组件的状态
python test_cli.py analyze spark
python test_cli.py analyze hadoop
python test_cli.py analyze flink
```

### 3. 场景模拟
```bash
# 模拟日常巡检
python test_cli.py summary

# 模拟故障排查
python test_cli.py status kafka

# 模拟性能分析
python test_cli.py analyze yarn
```

---

## 📝 自定义 Mock 数据

如果你想修改测试数据，编辑 `test_cli.py` 中的 `_init_mock_data()` 方法：

```python
def _init_mock_data(self) -> dict[str, dict[str, Any]]:
    return {
        "spark": {
            "component": "Spark",
            "workers": 10,  # 修改为 10 个节点
            "active_workers": 10,
            "cores": 80,    # 修改为 80 核
            "memory": 131072,  # 修改为 128GB
            "running_apps": 8,  # 修改为 8 个应用
            "completed_apps": 50,
            "health": "healthy",
        },
        # ... 其他组件
    }
```

然后重新运行：
```bash
python test_cli.py analyze spark
```

---

**以上就是完整的测试示例！** 🎉

你可以根据需要修改 Mock 数据，或者添加新的测试场景。
