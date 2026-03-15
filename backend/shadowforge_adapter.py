#!/usr/bin/env python3
"""
ShadowForge适配器模块，用于在backend中安全地调用根目录的generate_from_config函数
"""

import os
import sys
from typing import Dict, Any, Optional, Callable
import importlib.util

# 缓存导入的函数
_generate_from_config = None


def get_generate_from_config():
    """安全地获取generate_from_config函数"""
    global _generate_from_config
    
    if _generate_from_config is None:
        try:
            # 添加根目录到sys.path
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if root_dir not in sys.path:
                sys.path.insert(0, root_dir)
            
            # 使用importlib动态导入，避免循环导入
            main_path = os.path.join(root_dir, "main.py")
            spec = importlib.util.spec_from_file_location("shadowforge_main", main_path)
            shadowforge_main = importlib.util.module_from_spec(spec)
            
            # 保存当前sys.modules中的main模块（如果有）
            original_main = sys.modules.get("main")
            
            # 使用不同的模块名导入
            sys.modules["shadowforge_main"] = shadowforge_main
            spec.loader.exec_module(shadowforge_main)
            
            # 获取函数
            _generate_from_config = getattr(shadowforge_main, "generate_from_config", None)
            
            # 恢复原来的main模块
            if original_main:
                sys.modules["main"] = original_main
            elif "main" in sys.modules:
                del sys.modules["main"]
                
            if not _generate_from_config:
                raise ImportError("generate_from_config function not found in main.py")
                
        except Exception as e:
            print(f"Warning: Could not import ShadowForge generate_from_config: {e}")
            _generate_from_config = None
    
    return _generate_from_config


def generate_from_config_safe(
    config: Dict[str, Any],
    progress_callback: Optional[Callable[[int, str], None]] = None,
    output_dir: str = "output_universe"
) -> Dict[str, Any]:
    """
    安全地调用generate_from_config函数
    
    Args:
        config: 配置字典
        progress_callback: 进度回调函数
        output_dir: 输出目录
        
    Returns:
        结果字典
    """
    func = get_generate_from_config()
    if not func:
        return {
            "success": False,
            "output_files": [],
            "errors": ["ShadowForge modules not available"],
            "metadata": {}
        }
    
    try:
        return func(config, progress_callback, output_dir)
    except Exception as e:
        return {
            "success": False,
            "output_files": [],
            "errors": [str(e)],
            "metadata": {}
        }