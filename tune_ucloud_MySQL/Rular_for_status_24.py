# -*- coding: gbk -*-
"""
分析show global status 获得的数据
"""
from Rular_for_oltp_24 import *


# 分析show global status的数据
def analysis_show_global_status(path_show_global_status):

    # 读取文件
    with open(path_show_global_status, 'r') as f:
        str_status_list_list = f.read()

    # 记录各个状态值的变化
    dict_status = {}

    first_split = False

    # 获取各个阶段的状态
    for i_status_list in str_status_list_list.split("+++"):
        for ii_status in i_status_list.split("++"):

            # 获取开始时间
            if first_split is False:
                global start_time
                start_time = float(ii_status)
                first_split = True

            if 'Innodb' in ii_status:
                # 进行格式清楚
                ii_status = ii_status.replace('(', '')
                ii_status = ii_status.replace(')', '')
                ii_status = ii_status.replace(' ', '')
                ii_status = ii_status.replace("'", '')
                ii_status = ii_status.split(',')

                # 转换成整型并记入字典
                try:
                    mid_value = int(ii_status[1])
                    if ii_status[0] not in dict_status.keys():
                        dict_status[ii_status[0]] = []
                    dict_status[ii_status[0]].append(mid_value)
                except Exception:
                    pass

    # 返回结果
    return dict_status


if __name__ == "__main__":

    # 分析show global status 数据
    result = analysis_show_global_status(status_path)

    # 打印结果
    for i in result:
        print(i, result[i])

    print(start_time)

