# -*- coding: gbk -*-
"""
分析sar -d 获得的数据库
"""
from ip_24 import *


# 对sar -d 命令进行数据分析
def analysis_sar_d(path_sar_d):

    # 获取文件信息
    with open(path_sar_d, 'r') as f:
        sar_d_list_list = f.readlines()

    # # 获取整个信息
    # for i_sar_list in sar_d_list_list:
    #     print(i_sar_list)

    # 使用字典记录相关信息
    sar_d_dict = {}
    sar_d_dict["avgqu-sz"] = []
    sar_d_dict["await"] = []
    sar_d_dict["svctm"] = []
    sar_d_dict["%util"] = []

    # 进行信息过滤
    for i_sar_list in sar_d_list_list:
        if "dev253-0" in i_sar_list:
            if "Average" not in i_sar_list:
                i_sar_list = i_sar_list.replace("\n", '')
                i_sar_list = i_sar_list.split(" ")
                i_sar_list_clean = []
                for i in i_sar_list:
                    if len(i) > 0:
                        i_sar_list_clean.append(i)

                # 获取各个指标的信息
                sar_d_dict["avgqu-sz"].append(i_sar_list_clean[7])
                sar_d_dict["await"].append(i_sar_list_clean[8])
                sar_d_dict["svctm"].append(i_sar_list_clean[9])
                sar_d_dict["%util"].append(i_sar_list_clean[10])

    # 返回获得的结果
    return sar_d_dict


if __name__ == "__main__":

    # 进行sar -d 数据分析
    result = analysis_sar_d(path_sar_d)

    # 打印结果
    print(result)