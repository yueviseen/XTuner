# -*- coding: gbk -*-
"""
����show global status ��õ�����
"""
from Rular_for_oltp_24 import *


# ����show global status������
def analysis_show_global_status(path_show_global_status):

    # ��ȡ�ļ�
    with open(path_show_global_status, 'r') as f:
        str_status_list_list = f.read()

    # ��¼����״ֵ̬�ı仯
    dict_status = {}

    first_split = False

    # ��ȡ�����׶ε�״̬
    for i_status_list in str_status_list_list.split("+++"):
        for ii_status in i_status_list.split("++"):

            # ��ȡ��ʼʱ��
            if first_split is False:
                global start_time
                start_time = float(ii_status)
                first_split = True

            if 'Innodb' in ii_status:
                # ���и�ʽ���
                ii_status = ii_status.replace('(', '')
                ii_status = ii_status.replace(')', '')
                ii_status = ii_status.replace(' ', '')
                ii_status = ii_status.replace("'", '')
                ii_status = ii_status.split(',')

                # ת�������Ͳ������ֵ�
                try:
                    mid_value = int(ii_status[1])
                    if ii_status[0] not in dict_status.keys():
                        dict_status[ii_status[0]] = []
                    dict_status[ii_status[0]].append(mid_value)
                except Exception:
                    pass

    # ���ؽ��
    return dict_status


if __name__ == "__main__":

    # ����show global status ����
    result = analysis_show_global_status(status_path)

    # ��ӡ���
    for i in result:
        print(i, result[i])

    print(start_time)

