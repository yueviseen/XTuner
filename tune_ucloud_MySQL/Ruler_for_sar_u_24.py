# -*- coding: gbk -*-
"""
����sar -u ��õ����ݿ�
"""
from ip_24 import *

# ��sar -u ����������ݷ���
def analysis_sar_u(path_sar_u):

    # ��ȡ�ļ���Ϣ
    with open(path_sar_u, 'r') as f:
        sar_u_list_list = f.readlines()

    # ��¼���������ֵ�
    sar_u_dict = {}
    sar_u_dict["%user"] = []
    sar_u_dict["%system"] = []
    sar_u_dict["%iowait"] = []
    sar_u_dict["%idle"] = []

    # for i in sar_u_list_list:
    #     print(i)

    # ���ļ�ֵд���ֵ���
    cnt = 0
    for i_sar_u_list in sar_u_list_list:
        if "all" in i_sar_u_list:
            if "Average" not in i_sar_u_list:
                i_sar_u_list = i_sar_u_list.replace("\n", "")
                i_sar_u_list = i_sar_u_list.split(" ")
                i_sar_u_list_clean = []
                for i in i_sar_u_list:
                    if len(i) > 0:
                        i_sar_u_list_clean.append(i)
                sar_u_dict["%user"].append(i_sar_u_list_clean[3])
                sar_u_dict["%system"].append(i_sar_u_list_clean[5])
                sar_u_dict["%iowait"].append(i_sar_u_list_clean[6])
                sar_u_dict["%idle"].append(i_sar_u_list_clean[8])

    # ������Ϣ���
    return sar_u_dict


if __name__ == "__main__":

    # �����ļ�����
    result = analysis_sar_u(path_sar_u)

    # ��ӡ���
    for i in result:
        print(i, result[i])