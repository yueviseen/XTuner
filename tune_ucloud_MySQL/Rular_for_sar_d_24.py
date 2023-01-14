# -*- coding: gbk -*-
"""
����sar -d ��õ����ݿ�
"""
from ip_24 import *


# ��sar -d ����������ݷ���
def analysis_sar_d(path_sar_d):

    # ��ȡ�ļ���Ϣ
    with open(path_sar_d, 'r') as f:
        sar_d_list_list = f.readlines()

    # # ��ȡ������Ϣ
    # for i_sar_list in sar_d_list_list:
    #     print(i_sar_list)

    # ʹ���ֵ��¼�����Ϣ
    sar_d_dict = {}
    sar_d_dict["avgqu-sz"] = []
    sar_d_dict["await"] = []
    sar_d_dict["svctm"] = []
    sar_d_dict["%util"] = []

    # ������Ϣ����
    for i_sar_list in sar_d_list_list:
        if "dev253-0" in i_sar_list:
            if "Average" not in i_sar_list:
                i_sar_list = i_sar_list.replace("\n", '')
                i_sar_list = i_sar_list.split(" ")
                i_sar_list_clean = []
                for i in i_sar_list:
                    if len(i) > 0:
                        i_sar_list_clean.append(i)

                # ��ȡ����ָ�����Ϣ
                sar_d_dict["avgqu-sz"].append(i_sar_list_clean[7])
                sar_d_dict["await"].append(i_sar_list_clean[8])
                sar_d_dict["svctm"].append(i_sar_list_clean[9])
                sar_d_dict["%util"].append(i_sar_list_clean[10])

    # ���ػ�õĽ��
    return sar_d_dict


if __name__ == "__main__":

    # ����sar -d ���ݷ���
    result = analysis_sar_d(path_sar_d)

    # ��ӡ���
    print(result)