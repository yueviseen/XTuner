# -*- coding: gbk -*-
"""
����show global status ��õ�����
"""
import math

from Rular_for_oltp_24 import *


# ����show global status������
def analysis_show_global_status(path_show_global_status):

    # ��ȡ�ļ�
    with open(path_show_global_status, 'r') as f:
        str_status_list_list = f.read()

    max_value = 0

    # ��ȡ�����׶ε�״̬
    for i_status_list in str_status_list_list.split("++"):
        # ��ȡ��ʼʱ��
        if len(i_status_list) > 0:
            # ���и�ʽ���
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
    # ���ؽ��
    return max_value


if __name__ == "__main__":

    # ����show global status ����
    result = analysis_show_global_status(status_path)
    print(math.floor(result/1024/1024))