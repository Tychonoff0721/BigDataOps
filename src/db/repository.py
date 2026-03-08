"""数据库模型模块"""

import sqlite3
from pathlib import Path
from typing import Any


class BigDataRepository:
    """大数据仓库类，用于持久化组件指标数据和历史记录。"""

    def __init__(self, db_path: str) -> None:
        """
        初始化仓库。

        Args:
            db_path: SQLite 数据库文件路径
        """
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self) -> None:
        """初始化数据库表结构。"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建组件指标历史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS component_metrics_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    component TEXT NOT NULL,
                    metrics_json TEXT NOT NULL,
                    health_status TEXT NOT NULL,
                    score INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建用户查询历史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    component TEXT NOT NULL,
                    query_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_component 
                ON component_metrics_history(component)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at 
                ON component_metrics_history(created_at)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_id 
                ON query_history(user_id)
            """)
            
            conn.commit()

    def save_metrics(
        self,
        component: str,
        metrics: dict[str, Any],
        health_status: str,
        score: int | None = None,
    ) -> None:
        """
        保存组件指标数据。

        Args:
            component: 组件名称
            metrics: 指标数据字典
            health_status: 健康状态
            score: 健康分数
        """
        import json
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO component_metrics_history 
                (component, metrics_json, health_status, score)
                VALUES (?, ?, ?, ?)
                """,
                (component, json.dumps(metrics), health_status, score),
            )
            conn.commit()

    def get_metrics_history(
        self, component: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        获取组件的历史指标数据。

        Args:
            component: 组件名称
            limit: 返回的记录数量限制

        Returns:
            历史指标数据列表
        """
        import json
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT metrics_json, health_status, score, created_at
                FROM component_metrics_history
                WHERE component = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (component, limit),
            )
            
            rows = cursor.fetchall()
            return [
                {
                    "metrics": json.loads(row[0]),
                    "health_status": row[1],
                    "score": row[2],
                    "created_at": row[3],
                }
                for row in rows
            ]

    def save_query(
        self,
        user_id: str,
        component: str,
        query_type: str,
    ) -> None:
        """
        保存用户查询记录。

        Args:
            user_id: 用户 ID
            component: 查询的组件名称
            query_type: 查询类型 (metrics, health, summary)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO query_history 
                (user_id, component, query_type)
                VALUES (?, ?, ?)
                """,
                (user_id, component, query_type),
            )
            conn.commit()

    def get_popular_components(self, limit: int = 5) -> list[str]:
        """
        获取最常查询的组件。

        Args:
            limit: 返回的组件数量限制

        Returns:
            热门组件列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT component, COUNT(*) as count
                FROM query_history
                GROUP BY component
                ORDER BY count DESC
                LIMIT ?
                """,
                (limit,),
            )
            
            rows = cursor.fetchall()
            return [row[0] for row in rows]

    def clear_old_records(self, days: int = 30) -> None:
        """
        清理指定天数之前的旧记录。

        Args:
            days: 保留的天数
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 删除旧的指标记录
            cursor.execute(
                """
                DELETE FROM component_metrics_history
                WHERE created_at < datetime('now', '-' || ? || ' days')
                """,
                (days,),
            )
            
            # 删除旧的查询记录
            cursor.execute(
                """
                DELETE FROM query_history
                WHERE created_at < datetime('now', '-' || ? || ' days')
                """,
                (days,),
            )
            
            conn.commit()
