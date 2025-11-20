
import os
import shutil


"""清理指定目录下的文件"""
def cleanup_directories():

    directories_to_clean = [
        "ai_comparison_results",  # AI对比结果目录
        "screenshoot_dir"  # 基准图片目录
    ]

    for dir_name in directories_to_clean:
        dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), dir_name)
        if os.path.exists(dir_path):
            try:
                # 遍历目录并删除所有文件
                for filename in os.listdir(dir_path):
                    file_path = os.path.join(dir_path, filename)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                        print(f"已删除文件: {file_path}")
                    elif os.path.isdir(file_path):
                        # 如果是子目录，递归删除
                        shutil.rmtree(file_path)
                        print(f"已删除子目录: {file_path}")
                print(f"成功清理目录: {dir_path}")
            except Exception as e:
                print(f"清理目录 {dir_path} 时出错: {str(e)}")
        else:
            # 如果目录不存在，创建它
            try:
                os.makedirs(dir_path)
                print(f"创建目录: {dir_path}")
            except Exception as e:
                print(f"创建目录 {dir_path} 时出错: {str(e)}")