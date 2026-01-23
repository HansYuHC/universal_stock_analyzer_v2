#!/usr/bin/env python3
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(__file__))

if __name__ == "__main__":
    print("股票分析系统 v2.0")
    print("=" * 50)
    print("1. python main.py                     # 命令行分析")
    print("2. streamlit run ui/streamlit_app.py  # Web界面分析")
    print("=" * 50)

    mode = input("\n选择模式 (1或2): ").strip()

    if mode == "1":
        from main import main

        main()
    elif mode == "2":
        import subprocess

        subprocess.run(["streamlit", "run", "ui/streamlit_app.py"])
    else:
        print("无效选择")