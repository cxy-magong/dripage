#!/usr/bin/env python
"""
模型配置管理器
从 YAML 配置文件加载模型参数
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ModelConfig:
    """模型配置类"""

    def __init__(self, config_path: Path = None):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径，默认为 config/models_config.yaml
        """
        if config_path is None:
            # 默认配置文件路径
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "models_config.yaml"

        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def get_model_config(self, model_key: str) -> Dict[str, Any]:
        """
        获取指定模型的配置

        Args:
            model_key: 模型的 key（如 'glm_4_6v'）

        Returns:
            模型配置字典

        Raises:
            KeyError: 模型不存在
        """
        if model_key not in self.config['models']:
            available_models = list(self.config['models'].keys())
            raise KeyError(
                f"Model '{model_key}' not found. Available models: {available_models}"
            )

        return self.config['models'][model_key]

    def get_model_name(self, model_key: str) -> str:
        """
        获取模型的显示名称

        Args:
            model_key: 模型的 key

        Returns:
            模型名称（如 'GLM-4.6V'）
        """
        return self.get_model_config(model_key)['name']

    def get_default_model_key(self) -> str:
        """
        获取默认模型的 key

        Returns:
            默认模型 key
        """
        return self.config['default']['model']

    def get_gui_agent_model_key(self) -> str:
        """
        获取 GUI Agent 使用的模型 key

        Returns:
            GUI Agent 模型 key
        """
        return self.config['gui_agent']['model']

    def get_gui_agent_config(self) -> Dict[str, Any]:
        """
        获取 GUI Agent 的完整配置

        Returns:
            GUI Agent 配置字典
        """
        model_key = self.get_gui_agent_model_key()
        model_config = self.get_model_config(model_key)

        config = {
            "model": model_config['name'],
            "temperature": self.config['gui_agent'].get('temperature', model_config['temperature']),
            "max_tokens": self.config['gui_agent'].get('max_tokens', model_config['max_tokens']),
            "context_length": model_config['context_length'],
            "description": model_config.get('description', '')
        }

        # 添加 thinking 配置
        if model_config.get('thinking_supported', False):
            config['thinking_enabled'] = self.config['gui_agent'].get(
                'thinking_enabled',
                model_config.get('thinking_enabled', False)
            )
            config['thinking_supported'] = True
        else:
            config['thinking_enabled'] = False
            config['thinking_supported'] = False

        return config

    def list_models(self) -> Dict[str, Dict[str, Any]]:
        """
        列出所有可用模型

        Returns:
            所有模型的配置字典
        """
        return self.config['models']

    def is_thinking_supported(self, model_key: str) -> bool:
        """
        检查模型是否支持 thinking 功能

        Args:
            model_key: 模型的 key

        Returns:
            是否支持 thinking
        """
        model_config = self.get_model_config(model_key)
        return model_config.get('thinking_supported', False)

    def is_thinking_enabled(self, model_key: str, context: str = 'default') -> bool:
        """
        检查模型是否启用了 thinking 功能

        Args:
            model_key: 模型的 key
            context: 上下文，'default' 或 'gui_agent'

        Returns:
            是否启用了 thinking
        """
        model_config = self.get_model_config(model_key)

        if context == 'gui_agent':
            return self.config['gui_agent'].get(
                'thinking_enabled',
                model_config.get('thinking_enabled', False)
            )
        else:
            return self.config['default'].get(
                'thinking_enabled',
                model_config.get('thinking_enabled', False)
            )

    def get_thinking_config(self, model_key: str, context: str = 'default') -> Optional[Dict[str, str]]:
        """
        获取 thinking 配置字典，用于 API 调用

        Args:
            model_key: 模型的 key
            context: 上下文，'default' 或 'gui_agent'

        Returns:
            thinking 配置字典，如果不支持或未启用则返回 None

        Example:
            >>> thinking_config = config.get_thinking_config('glm_4_6v')
            >>> if thinking_config:
            ...     client.chat.completions.create(..., thinking=thinking_config)
        """
        if not self.is_thinking_supported(model_key):
            return None

        if not self.is_thinking_enabled(model_key, context):
            return None

        return {"type": "enabled"}

    def print_models(self):
        """打印所有可用模型"""
        print("\n" + "=" * 80)
        print("Available Models")
        print("=" * 80)

        for key, config in self.config['models'].items():
            recommended = " [RECOMMENDED]" if config.get('recommended', False) else ""
            print(f"\n{key}{recommended}")
            print(f"  Name: {config['name']}")
            print(f"  Description: {config['description']}")
            print(f"  Context Length: {config['context_length']:,} tokens")
            print(f"  Temperature: {config['temperature']}")
            print(f"  Max Tokens: {config['max_tokens']}")

            # Thinking 信息
            thinking_supported = config.get('thinking_supported', False)
            thinking_enabled = config.get('thinking_enabled', False)

            if thinking_supported:
                status = "✓ Enabled" if thinking_enabled else "✗ Disabled"
                print(f"  Thinking: {status}")
            else:
                print(f"  Thinking: Not supported")

        print("\n" + "=" * 80)
        print(f"Default Model: {self.get_default_model_key()}")
        print(f"GUI Agent Model: {self.get_gui_agent_model_key()}")
        print("=" * 80)


# 全局配置实例
_config_instance: Optional[ModelConfig] = None


def get_config() -> ModelConfig:
    """
    获取全局配置实例（单例模式）

    Returns:
        ModelConfig 实例
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ModelConfig()
    return _config_instance


if __name__ == "__main__":
    # 测试代码
    config = get_config()

    # 打印所有模型
    config.print_models()

    # 获取 GUI Agent 配置
    print("\n" + "=" * 80)
    print("GUI Agent Configuration")
    print("=" * 80)
    gui_config = config.get_gui_agent_config()
    for key, value in gui_config.items():
        print(f"{key}: {value}")
    print("=" * 80)
