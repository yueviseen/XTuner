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

    # �ж��ļ��Ƿ�д��ɹ�
    flag_average = False
    flag_throughput = False
    cnt = 0
    while True:

        # ÿ������10��
        time.sleep(10)
        print("�ж�result�ļ��Ƿ�д��ɹ�")
        cnt = cnt + 1
        if cnt > 20:
            break
        # ����ҵ��ļ����򣬽���ѭ��
        if os.path.exists(result_file_path) is True:
            with open(result_file_path, 'r') as f:
                for i in f.readlines():
                    if "Throughput (requests/second)" in i:
                        flag_throughput = True
                    if "Average Latency" in i:
                        flag_average = True
                    if flag_average is True and flag_throughput is True:
                        break
        if flag_average is True and flag_throughput is True:
            break
    print("result�ļ�д��ɹ�")

    if cnt > 20:
        return (-1, -1)

    else:
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
def run_PG_for_oltp():
    # �ж����ݿ��Ƿ����ɹ�
    # status_PG()

    # ����oltp
    print("����oltp��������")
    print(oltp_cmd_wiki)
    t = os.system(oltp_cmd_wiki)
    if t == 0:
        print("���гɹ�")
    # ˯��20��
    print("˯��60s")
    time.sleep(60)

    return get_result()

# �Ժ��޸�
def run_mysql_for_oltp_ycsb():
    # �ж����ݿ��Ƿ����ɹ�
    status_PG()

    # ����oltp
    print("����oltp��������")
    os.system(oltp_cmd_ycsb)

    # ˯��20��
    print("˯��20s")
    time.sleep(20)

    return get_result()

# �Ժ��޸�
def run_mysql_for_oltp_wiki():
    # �ж����ݿ��Ƿ����ɹ�
    # status_PG()

    # ����oltp
    print("����oltp��������")
    os.system(oltp_cmd_wiki)

    # ˯��20��
    print("˯��20s")
    time.sleep(20)

    # return get_result()

# ʹ���ݿ�ص�ԭ��״̬
def data_recovery():

    # Ϊ�˰�ȫ����10��
    # time.sleep(10)

    # �жϲ��������ݿ�ı��ݣ���������ݿⱸ��
    if os.path.exists("/root/PG/wikipedia") is False:
        os.system("pg_dump -U postgres -d wikipedia > /root/PG/wikipedia")
    else:
        print("exist backup")
    # ɾ�����ݿ�
    os.system("dropdb -h 127.0.0.1 -p 5432 -U postgres wikipedia")
    print("ɾ�����ݿ�")

    # �������ݿ�
    os.system("createdb -h 127.0.0.1 -p 5432 -U postgres wikipedia")
    print("�������ݿ�")

    # ���뱸�����ݿ�
    os.system("psql -h 127.0.0.1 -p 5432 -U postgres wikipedia < /root/PG/wikipedia")

    print("����60��")
    time.sleep(60)





# �������ݻ�ȡ
if __name__ == '__main__':

    ss = []
    for i in range(3):
        # �������ݿ�
        start_PG()

        status_PG()

        # ���ݿ⸴ԭ
        data_recovery()

        # ��ջ���
        free_cache()

        # ����oltp
        ss.append(run_PG_for_oltp())

        # �ر����ݿ�
        stop_PG()

        time.sleep(60)
    print(ss)


