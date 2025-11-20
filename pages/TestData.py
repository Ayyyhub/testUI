from dataclasses import dataclass


### 数据类

@dataclass
class AETestData:
    test_case_id: str
    description:str       #流程描述
    step_id: str          #步骤序号
    determin_type: str    #操作类型
    determin_method: str  #定位方式
    determin_value: str   #定位值
    input_value: str      #输入的值
    cv_points: bool       #可视化检测点
    assert_type: str  # 断言类型
    assert_method: str    #断言方式
    expected_result: str  #预期结果
    outputed_result: str  #实际结果
    status: str           #测试状态