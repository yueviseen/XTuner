# -*- coding: gbk -*-

"""
���ڹ�������ݿ����
"""
import os
import shutil

import pymysql
import time
from ip_24 import *
from multiprocessing import Process


# ����һ���̻߳�ȡ�����Ϣ,����������Ϣ
def process_information(starting_time, run_time, conn, cursor):

    # ������д���ļ�
    with open(status_path, 'a') as f:

        # д�뿪ʼʱ��
        f.write(str(starting_time))
        f.write("++")
        # ������ѭ�����ȴ����߳�ɱ���ý���
        while True:
            print("�ռ�״̬����")
            # �����������ʱ�䣬��ر����ݿ⣬��������
            if time.time()-starting_time > run_time + 9:
                f.flush()
                cursor.close()
                conn.close()
                break

            # ��¼��������ǰ��statusֵ
            cursor.execute("show global status like '%innodb%'")

            # �ù��������¼����״̬
            f.write(str(time.time()))
            for i_content in cursor.fetchall():
                f.write("++")
                f.write(str(i_content))
            f.write("+++")

            # ÿ10��ɼ�һ������
            time.sleep(10)


# ������и��صĽ��
def get_result():

    # �������
    mid_throught = 0
    mid_latency = 0

    # ��ȡ�ļ���������
    with open(result_file_path) as f:
        for ii in f.readlines():
            if "Throughput (requests/second)" in ii:
                mid_throught = float(ii.split(": ")[1].replace(",", ''))
            if "Average Latency" in ii:
                mid_latency = float(ii.split(": ")[1].replace(",", ''))

    # ɾ���ļ�
    os.system(del_result_file)
    return (mid_throught, mid_latency)


# ����oltp������¼�����Ϣ
def run_mysql_for_oltp():

    # �ж����ݿ��Ƿ����ɹ�
    status_mysql()

    # �������ݿ�����
    conn = pymysql.connect(host=ip, user=user, password=password, database=database_wiki, charset='utf8', port=i_port)
    cursor = conn.cursor()

    print("��̨�������ݿ�")
    # ����oltp
    os.system(oltp_cmd_wiki_background)

    # ��ʼʱ��
    starting_time = time.time()

    # ���cpu��io
    print("����cpu��io�ļ��")
    os.system(sar_u_com)
    os.system(sar_d_com)

    global run_time
    # ���̣߳���¼�����Ϣ
    p = Process(target=process_information, args=(starting_time, run_time, conn, cursor))
    p.start()
    p.join()

    # ���н���������40�룬����������ļ������ݵ�д��
    print("����140��")
    time.sleep(run_time + 60)

    # �ж��Ƿ��ȡ���
    flag_throughput = False
    flag_average = False



    # �ж��ļ��Ƿ�д��ɹ�
    while True:

        # ÿ������10��
        time.sleep(10)
        print("�ж�result�ļ��Ƿ�д��ɹ�")

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
    # ��ȡ���
    return get_result()


# ʹ���ݿ�ص�ԭ��״̬
def data_recovery():

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

    # ��ո�����¼��־
    print("��ո�����־��¼")
    os.system(clean_log_err)
    os.system(clean_status)
    os.system(clean_sar_u_com)
    os.system(clean_sar_d_com)
    print("������־��¼������")




# �������ݿ���в���
if __name__ == '__main__':

    for i in range(10):

        # ��ԭ���ݿ�����
        data_recovery()

        # ��ջ���
        free_cache()

        # �������ݿ�
        start_mysql()

        # ����oltp
        print(run_mysql_for_oltp())

        # ʹ���ݿ⸴ԭ
        stop_mysql()
