# -*- coding: gbk -*-
"""
分析show global status 获得的数据
"""
import math

from Rular_for_oltp_24 import *


# 分析show global status的数据
def analysis_show_global_status(path_show_global_status):

    # 读取文件
    with open(path_show_global_status, 'r') as f:
        str_status_list_list = f.read()

    max_value = 0

    # 获取各个阶段的状态
    for i_status_list in str_status_list_list.split("++"):
        # 获取开始时间
        if len(i_status_list) > 0:
            # 进行格式清楚
            # print(i_status_list)
            ii_status = i_status_list.replace('(', '')
            ii_status = ii_status.replace(')', '')
            ii_status = ii_status.replace(' ', '')
            ii_status = ii_status.replace("'", '')
            ii_status = ii_status.replace(",", '')
            ii_status = ii_status.replace("Decimal", '')

            if max_value < int(ii_status):
                 max_value = int(ii_status)
            # print(ii_status)
    # 返回结果
    return max_value


if __name__ == "__main__":

    # 分析show global status 数据
    result = analysis_show_global_status(status_path)
    print(math.floor(result/1024/1024))