# -*- coding: gbk -*-

"""
���ڹ�������ݿ����
"""
import os
import shutil
import time
import psycopg2
from ip_24 import *
from multiprocessing import Process


# ����һ���̻߳�ȡ�����Ϣ,����������Ϣ
def process_information(starting_time, run_time, conn, cursor):

    # ������д���ļ�
    with open(status_path, 'a') as f:

        # ������ѭ�����ȴ����߳�ɱ���ý���
        while True:
            print("�ռ�LSN״̬����")
            # �����������ʱ�䣬��ر����ݿ⣬��������
            if time.time()-starting_time > run_time + 9:
                f.flush()
                cursor.close()
                conn.close()
                break

            # ��¼��������ǰ��statusֵ
            cursor.execute("select pg_wal_lsn_diff(pg_current_wal_insert_lsn(), pg_current_wal_flush_lsn())")

            # �ù��������¼����״̬
            for i_content in cursor.fetchall():
                f.write(str(i_content))
            f.write("++")

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
def run_PG_for_oltp():


    # �������ݿ�����
    conn = psycopg2.connect(host=ip, user=user, password=password, database=database_wiki, port=i_port)
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
    print("����30��")
    time.sleep(30)

    # �ж��Ƿ��ȡ���
    flag_throughput = False
    flag_average = False

    cnt = 0
    # �ж��ļ��Ƿ�д��ɹ�
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
    # ��ȡ���
    if cnt <= 20:
        return get_result()
    else:
        return (-1, -1)

# ʹ���ݿ�ص�ԭ��״̬
def data_recovery():

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
    print("�ر����ݿ�")

    # ���뱸�����ݿ�
    os.system("psql -h 127.0.0.1 -p 5432 -U postgres wikipedia < /root/PG/wikipedia")

    # ��ո�����¼��־
    print("��ո�����־��¼")
    os.system(clean_status)
    os.system(clean_sar_u_com)
    os.system(clean_sar_d_com)
    os.system(del_result_file)
    print("������־��¼������")

    print("����60��")
    time.sleep(60)


# �������ݿ���в���
if __name__ == '__main__':

    for i in range(10):

        # �������ݿ�
        start_PG()

        # �鿴����״̬
        status_PG()

        # ��ԭ���ݿ�����
        data_recovery()

        # ��ջ���
        free_cache()

        # ����oltp
        print(run_PG_for_oltp())

        # ʹ���ݿ⸴ԭ
        stop_PG()
