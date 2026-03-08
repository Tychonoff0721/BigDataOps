# BigDataOps 使用指南

## 📋 快速开始

### 1. 安装插件

将 BigDataOps 插件克隆到 AstrBot 的 `plugins` 目录：

```bash
cd /path/to/AstrBot/plugins
git clone <your-repo-url> astrbot_plugin_bigdataops
```

### 2. 安装依赖

```bash
cd astrbot_plugin_bigdataops
pip install -r requirements.txt
```

### 3. 配置插件

在 AstrBot 管理界面中找到 BigDataOps 插件，配置以下参数：

#### 必需配置
- **api_endpoint**: 大数据组件的 REST API 地址
  - Hadoop YARN: `http://<host>:8088`
  - Spark Master: `http://<host>:8080`
  - Flink JobManager: `http://<host>:8081`

#### 可选配置
- **api_username/password**: API 认证凭据（如果启用了认证）
- **timeout_seconds**: 请求超时时间（默认 30 秒）
- **max_retries**: 失败重试次数（默认 3 次）
- **cache_enabled**: 是否启用缓存（默认开启）
- **render_server_url**: 远程渲染服务地址（用于生成图片报告）

### 4. 启用插件

在 AstrBot 管理界面启用 `astrbot_plugin_bigdataops` 插件。

## 💬 使用示例

### 查看组件指标

```
/bigdata spark
```

输出示例：
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

### 查看健康状态

```
/bigdata-status hadoop
```

输出示例：
```
🏥 Hadoop 健康检查报告
========================================

✅ 状态：WARNING
📈 健康分数：70/100

⚠️ 发现的问题:
  1. 有 2 个 NodeManager 离线
  2. 内存使用率超过 80%

💡 改进建议:
  1. 检查 NodeManager 进程状态
  2. 考虑增加集群资源或优化作业配置

========================================
```

### 查看所有组件汇总

```
/bigdata-summary
```

输出示例：
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

### 获取帮助

```
/bigdata-help
```

## 🔧 支持的组件

### 计算引擎
| 组件 | 命令 | 默认端口 |
|------|------|----------|
| Apache Spark | `/bigdata spark` | 8080 |
| Apache Flink | `/bigdata flink` | 8081 |
| Apache Storm | `/bigdata storm` | 8080 |

### 存储系统
| 组件 | 命令 | 默认端口 |
|------|------|----------|
| Hadoop HDFS | `/bigdata hdfs` | 9870 |
| HBase | `/bigdata hbase` | 16010 |
| Cassandra | `/bigdata cassandra` | 9042 |

### 消息队列
| 组件 | 命令 | 默认端口 |
|------|------|----------|
| Apache Kafka | `/bigdata kafka` | 9092 |
| RabbitMQ | `/bigdata rabbitmq` | 15672 |

### 资源调度
| 组件 | 命令 | 默认端口 |
|------|------|----------|
| Hadoop YARN | `/bigdata yarn` | 8088 |
| Kubernetes | `/bigdata kubernetes` | 6443 |

### 数据仓库
| 组件 | 命令 | 默认端口 |
|------|------|----------|
| Apache Hive | `/bigdata hive` | 10000 |
| Presto | `/bigdata presto` | 8080 |
| ClickHouse | `/bigdata clickhouse` | 8123 |

## 🎯 高级功能

### 1. 历史记录查询

插件会自动保存查询历史到本地数据库，方便后续分析趋势。

数据库位置：`plugins/astrbot_plugin_bigdataops/data/data.db`

### 2. 缓存机制

启用缓存后，相同的查询会直接返回缓存结果，提升响应速度。

缓存配置：
- `cache_enabled`: true/false
- `cache_ttl_seconds`: 缓存存活时间（秒）

### 3. 自定义告警

可以通过修改源代码添加自定义告警规则：

```python
# 在 src/services/__init__.py 中添加告警逻辑
if metrics.get("memory_used", 0) > metrics.get("memory_total", 0) * 0.9:
    # 发送告警通知
    logger.warning("内存使用率超过 90%！")
```

## 🐛 故障排查

### 问题 1: 提示"服务未初始化"

**原因**: API 端点未配置或配置错误

**解决方法**:
1. 检查插件配置中的 `api_endpoint` 是否正确
2. 确认大数据组件是否正常运行
3. 检查网络连接是否正常

### 问题 2: 请求超时

**原因**: 网络延迟或组件响应慢

**解决方法**:
1. 增加 `timeout_seconds` 配置值
2. 检查大数据组件负载情况
3. 验证防火墙规则

### 问题 3: 认证失败

**原因**: 用户名或密码错误

**解决方法**:
1. 确认 `api_username` 和 `api_password` 配置正确
2. 检查大数据组件的认证配置
3. 尝试使用 API Token 代替密码

## 📝 开发指南

### 添加新组件支持

1. 在 `src/services/base.py` 中添加新的指标获取方法：

```python
async def _get_newcomponent_metrics(self, endpoint: str) -> dict[str, Any]:
    """获取新组件指标。"""
    url = f"{endpoint}/api/metrics"
    data = await self._request("GET", url)
    
    return {
        "component": "NewComponent",
        "key_metric_1": data.get("metric1", 0),
        "key_metric_2": data.get("metric2", 0),
        "health": "healthy" if data.get("status") else "unhealthy",
    }
```

2. 在 `get_component_metrics` 方法中注册处理器：

```python
component_handlers["newcomponent"] = self._get_newcomponent_metrics
```

3. 更新 `ComponentType` 枚举（`src/services/types.py`）

4. 添加中文键名映射（`src/render/component_renderer.py`）

### 自定义报告样式

修改 `templates/component_report.html` 中的 CSS 样式。

## 📞 技术支持

- GitHub Issues: [提交问题](https://github.com/yourusername/astrbot_plugin_bigdataops/issues)
- 邮件：your.email@example.com
- 文档：[在线文档](https://github.com/yourusername/astrbot_plugin_bigdataops/wiki)

## 📄 许可证

Apache License 2.0

---

**祝你使用愉快！** 🎉
