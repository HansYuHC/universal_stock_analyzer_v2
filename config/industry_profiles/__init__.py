"""
行业配置文件包
"""
import os
import importlib

# 自动发现所有行业配置文件
INDUSTRY_PROFILES = {}


def load_all_profiles():
    """加载所有行业配置"""
    profile_dir = os.path.dirname(__file__)
    for filename in os.listdir(profile_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            industry_name = filename[:-3]  # 去掉.py
            try:
                module = importlib.import_module(f'config.industry_profiles.{industry_name}')
                profile_key = f"{industry_name.upper()}_PROFILE"
                if hasattr(module, profile_key):
                    INDUSTRY_PROFILES[industry_name] = getattr(module, profile_key)
            except ImportError:
                continue

    return INDUSTRY_PROFILES


# 预加载所有配置文件
load_all_profiles()