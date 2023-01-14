# -*- coding: gbk -*-

"""
���ڹ�������ݿ����
"""
import os
import shutil
from ip_24 import *
import pymysql
import time
from multiprocessing import Process


# ������и��صĽ��
def get_result():
    throught = 0
    latency = 0
    # ��ȡ�ļ���������
    with open(result_file_path, 'r') as f:
        for ii in f.readlines():
            if "Throughput (requests/second)" in ii:
                throught = float(ii.split(": ")[1].replace(",", ''))
            if "Average Latency" in ii:
                latency = float(ii.split(": ")[1].replace(",", ''))

    # ɾ���ļ�
    os.system(del_result_file)
    return (throught, latency)


# ����oltp������¼�����Ϣ
def run_mysql_for_oltp():
    # �ж����ݿ��Ƿ����ɹ�
    status_mysql()

    # ����oltp
    print("����oltp��������")
    os.system(oltp_cmd)

    # ˯��20��
    print("˯��20s")
    time.sleep(20)

    return get_result()

def run_mysql_for_oltp_ycsb():
    # �ж����ݿ��Ƿ����ɹ�
    status_mysql()

    # ����oltp
    print("����oltp��������")
    os.system(oltp_cmd_ycsb)

    # ˯��20��
    print("˯��20s")
    time.sleep(20)

    return get_result()

def run_mysql_for_oltp_wiki():
    # �ж����ݿ��Ƿ����ɹ�
    status_mysql()

    # ����oltp
    print("����oltp��������")
    os.system(oltp_cmd_wiki)

    # ˯��20��
    print("˯��20s")
    time.sleep(20)

    return get_result()

# ʹ���ݿ�ص�ԭ��״̬
def data_recovery():

    # Ϊ�˰�ȫ����10��
    time.sleep(10)

    # ɾ���ļ�
    print(os.listdir(mysql_path))
    shutil.rmtree(data_path)
    print(os.listdir(mysql_path))

    # �����ļ�
    shutil.copytree(data_cp_path, data_path)
    print(os.listdir(data_path))
    print(os.listdir(mysql_path))

    os.system("chown -R mysql:mysql /var/lib/mysql")
    print("�������")
    os.system(clean_log_err)
    print("���ݻָ����")


# �������ݻ�ȡ
if __name__ == '__main__':

    for i in range(1):

        # ���ݿ⸴ԭ
        data_recovery()

        # # ��ջ���
        # free_cache()
        #
        # # �������ݿ�
        # start_mysql()
        #
        # # ����oltp
        # print(run_mysql_for_oltp_ycsb())
        #
        # # �ر����ݿ�
        # stop_mysql()

