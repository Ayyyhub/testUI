# Excel读取工具

import pandas as pd
import openpyxl
from typing import Dict, List, Any
from pathlib import Path


class ExcelReader:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def read_test_cases(self, sheet_name: str = None) -> List[Dict[str, Any]]:
        """读取测试用例数据"""
        try:
            df = pd.read_excel(self.file_path, sheet_name=sheet_name)
            # 处理NaN值为空字符串
            df = df.fillna('')
            return df.to_dict('records')
        except Exception as e:
            raise Exception(f"读取Excel文件失败: {e}")

    def get_sheet_names(self) -> List[str]:
        """获取所有sheet名称"""
        workbook = openpyxl.load_workbook(self.file_path)
        return workbook.sheetnames

    def write_test_results(self, test_results: List[Dict], output_path: str):
        """写入测试结果到Excel"""
        df = pd.DataFrame(test_results)
        df.to_excel(output_path, index=False)