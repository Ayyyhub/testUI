from dataclasses import dataclass


### 数据类

#TesestData 类名以 Test 开头，且有（@dataclass 隐式生成的）__init__ 方法，pytest 就会 “误把它当成测试类来收集”，从而触发 PytestCollectionWarning（但它其实是 “数据类”，不是测试类）。
@dataclass
class AETestData:
    test_case_id: str
    description:str          #流程描述
    step_id: str          #步骤序号
    determin_type: str    #操作类型
    determin_method: str  #定位方式
    determin_value: str   #定位值
    input_value: str      #输入的值
    expected_result: str  #预期结果
    outputed_result: str  #实际结果
    status: str