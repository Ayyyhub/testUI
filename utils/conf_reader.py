import os
import yaml

from core.browser_engine import BrowserEngine


# 读取配置文件
def load_config():
    # 获取当前脚本的目录路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录
    project_root = os.path.dirname(current_dir)
    # 配置文件路径
    config_path = os.path.join(project_root, "conf", "config.yaml")


    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except Exception as e:
        print(f"读取配置文件失败: {str(e)}")
        return None


