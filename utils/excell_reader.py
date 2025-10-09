# excel_reader.py
import openpyxl
from dataclasses import dataclass
from typing import List

#TesestData 类名以 Test 开头，且有（@dataclass 隐式生成的）__init__ 方法，pytest 就会 “误把它当成测试类来收集”，从而触发 PytestCollectionWarning（但它其实是 “数据类”，不是测试类）。
@dataclass
class AETestData:
    test_case_id: str
    description:str          #流程描述
    step_id: str          #步骤序号
    determin_type: str    #定位类型
    determin_method: str  #定位方式
    determin_value: str   #定位值
    input_value: str
    expected_result: str  #预期结果
    outputed_result: str  #实际结果
    status: str


class Excellreader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        #self.file_path = "D:/AE_PythonProject/testUI/testcases/test_data.xlsx" #代码失去灵活性，变成 “专用工具”
        self.workbook = openpyxl.load_workbook(self.file_path)

    def get_test_data(self, sheet_name: str)-> List[AETestData]:
        """从Excel读取测试数据"""
        # 打印所有可用的工作表名称
        print("实际读取到的工作表：", self.workbook.sheetnames)
        if sheet_name not in self.workbook.sheetnames:
            raise ValueError(f"工作表 '{sheet_name}' 不存在，可用工作表：{self.workbook.sheetnames}")
        sheet = self.workbook[sheet_name]
        test_data_list = []

        # 跳过标题行，从第二行开始读取
        for row in range(2, sheet.max_row + 1):
            # 检查是否要运行该用例
            # run_flag = sheet.cell(row=row, column=7).value
            # if run_flag and run_flag.upper() == 'Y':
            test_data = AETestData(
                test_case_id=sheet.cell(row=row, column=1).value,
                description=sheet.cell(row=row, column=2).value,
                step_id=sheet.cell(row=row, column=3).value,
                determin_type=sheet.cell(row=row, column=4).value,
                determin_method=sheet.cell(row=row, column=5).value,
                determin_value=sheet.cell(row=row, column=6).value,
                input_value=sheet.cell(row=row, column=7).value,
                expected_result=sheet.cell(row=row, column=8).value,
                outputed_result=sheet.cell(row=row, column=9).value,
                status=sheet.cell(row=row, column=10).value,
            )
            # test_data = [test_data]
            test_data_list.append(test_data)

        return test_data_list

    # def write_result(self, test_case_id: str, actual_result: str, status: str):
    #     """将测试结果写回Excel"""
    #     sheet = self.workbook.active
    #     for row in range(2, sheet.max_row + 1):
    #         if sheet.cell(row=row, column=1).value == test_case_id:
    #             sheet.cell(row=row, column=6).value = actual_result  # 实际结果
    #             sheet.cell(row=row, column=7).value = status  # 测试状态
    #             break
    #     self.workbook.save(self.file_path)