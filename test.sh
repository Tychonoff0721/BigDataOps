#!/bin/bash
# BigDataOps 命令行测试程序 - Linux/Mac 启动器

echo "========================================"
echo "BigDataOps 命令行测试工具"
echo "========================================"
echo

if [ $# -eq 0 ]; then
    echo "用法：./test.sh <命令> [参数]"
    echo
    echo "可用命令:"
    echo "  analyze <组件名>  - 分析指定组件的各项指标"
    echo "  status <组件名>   - 查看组件健康状态评估"
    echo "  summary           - 查看所有组件汇总信息"
    echo "  help              - 显示帮助信息"
    echo
    echo "示例:"
    echo "  ./test.sh analyze spark"
    echo "  ./test.sh status hadoop"
    echo "  ./test.sh summary"
    echo
    exit 0
fi

python3 test_cli.py "$@"
