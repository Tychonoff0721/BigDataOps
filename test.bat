@echo off
REM BigDataOps 命令行测试程序 - Windows 批处理启动器

echo ========================================
echo BigDataOps 命令行测试工具
echo ========================================
echo.

if "%1"=="" (
    echo 用法：test.bat ^<命令^> [参数]
    echo.
    echo 可用命令:
    echo   analyze ^<组件名^>  - 分析指定组件的各项指标
    echo   status ^<组件名^>   - 查看组件健康状态评估
    echo   summary            - 查看所有组件汇总信息
    echo   help               - 显示帮助信息
    echo.
    echo 示例:
    echo   test.bat analyze spark
    echo   test.bat status hadoop
    echo   test.bat summary
    echo.
    goto :EOF
)

python test_cli.py %*
