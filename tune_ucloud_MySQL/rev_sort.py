# -*- coding: gbk -*-
import os
import random
import sys
import math
import time

from ip_24 import *
from Rular_for_status_24 import *
from Rular_for_engine_24 import *
from Rular_for_oltp_24 import *
from Rular_for_sar_d_24 import *
from Ruler_for_sar_u_24 import *
import numpy as np
import math
import copy

cnt = 0

# ��ʼ������
def initialization_parameters():
    return_dict = {}
    return_dict["innodb_thread_concurrency"] = 32
    return_dict["innodb_log_file_size"] = 150
    return_dict["innodb_log_files_in_group"] = 2
    return_dict["innodb_buffer_pool_size"] = 561
    return_dict["innodb_buffer_pool_instances"] = 3
    return_dict["innodb_buffer_pool_chunk_size"] = 187
    return_dict["innodb_read_io_threads"] = 8
    return_dict["innodb_write_io_threads"] = 8
    return_dict["innodb_io_capacity"] = 2970
    return_dict["innodb_io_capacity_max"] = 5940
    return_dict["innodb_flush_neighbors"] = 0
    return_dict["innodb_flush_method"] = "fsync"
    return_dict["innodb_page_cleaners"] = 1
    return_dict["innodb_purge_threads"] = 4
    return_dict["innodb_random_read_ahead"] = 0
    return_dict["innodb_log_buffer_size"] = 1
    return_dict["innodb_use_fdatasync"] = 1
    return_dict["innodb_sync_spin_loops"] = 30
    return_dict["innodb_concurrency_tickets"] = 5000
    return_dict["innodb_log_writer_threads"] = 0
    return_dict["innodb_log_wait_for_flush_spin_hwm"] = 400

    return_dict["innodb_change_buffer_max_size"] = 25

    return_dict["innodb_extend_and_initialize"] = 1
    return_dict["innodb_sync_array_size"] = 1
    return_dict["innodb_deadlock_detect"] = 1
    return_dict["innodb_lock_wait_timeout"] = 50

    return_dict["innodb_lru_scan_depth"] = 40960
    return_dict["innodb_read_ahead_threshold"] = 1
    return_dict["innodb_adaptive_hash_index"] = 1
    return_dict["innodb_adaptive_hash_index_parts"] = 8
    # ���ز����ֵ�
    return return_dict


# �������ݵ����кͰѲ���д���ļ�
def run_and_write_file(param_dict, param_unit_dict, i, param_dict_list, ii):
    # д����ֵ�������ļ�
    write_my_cnf(param_dict, param_unit_dict)

    # ��ȡ������
    mid_throught = get_throught()
    param_dict["throught"] = mid_throught
    print("��ʾ���ε���������������Ĳ���ֵ")
    print("-----------------------------")
    global cnt
    print("cnt is %d" % cnt)
    cnt = cnt + 1
    print("-----------------------------")
    for ii in param_dict:
        print(ii, param_dict[ii])
    print("-----------------------------")
    param_dict_list.append(param_dict)
    # �������е����Ĳ����б�
    return param_dict_list


# ��ȡ���ȹ������ص�������
def get_throught():

    # ���ݿ⸴ԭ
    data_recovery()

    # ��ջ���
    free_cache()

    # �������ݿ�
    start_mysql()

    # �������ݿ�
    (mid_throught, mid_latency) = run_mysql_for_oltp()

    # �ر����ݿ�
    stop_mysql()

    # �������ݿ�����
    time.sleep(10)

    return mid_throught


# ��ʼ�� my.cnf�ĸ�ʽ
def initialization_my_cnf():
    # �������ò����ĳ�ʼ��
    my_cnf_list = []
    with open(path_my_cnf, 'r') as f:
        for ii in f.readlines():
            if "tuning param" in ii:
                my_cnf_list.append(ii)
                break
            else:
                my_cnf_list.append(ii)

    # �������ļ�д��my.cnf
    with open(path_my_cnf, 'w') as f:
        for ii in my_cnf_list:
            f.write(ii)
        f.flush()


# д�����ļ�,ע��ÿ��дmy.cnf��Ҫ��ʼ��
def write_my_cnf(param_dict, param_unit_dict):
    # �����ļ�my.cnf�ĳ�ʼ��
    initialization_my_cnf()

    # д��param_dict
    with open(path_my_cnf, 'a') as f:
        for ii in param_dict:
            if "throught" in ii or "start" in ii or "param" in ii or "test" in ii:
                continue
            if param_unit_dict.get(ii, None) is None:
                f.write(str(ii) + "=" + str(param_dict[ii]) + "\n")
            else:
                f.write(str(ii) + "=" + str(param_dict[ii]) + str(param_unit_dict[ii]) + "\n")
        f.flush()



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


if __name__ == "__main__":
    """
    ��Ҫ�������ݿ�innodb�������Ź��̵ĵ���
    """

    # �趨���ĵ�������
    iterations_num = 150

    # ��¼��ǰ��õĲ����б��������
    param_dict = {}

    param_dict_list = []

    # ��¼��Ҫ����M��λ�Ĳ���
    param_unit_dict = {}
    param_unit_dict["innodb_buffer_pool_size"] = "M"
    param_unit_dict["innodb_buffer_pool_chunk_size"] = "M"
    param_unit_dict["innodb_log_file_size"] = "M"
    param_unit_dict["innodb_log_buffer_size"] = "M"


    mid_throught = 0

    # ��¼��������
    i = 0
    loop_flag = True
    cnt_tune = 0

    LRU_list = [18000, 1024]
    read_ahead_list = [14, 56]
    first = True

    # ���в����ĵ����޸�
    while loop_flag is True:

        # ��һ�ε�������Ҫ���г�ʼ��
        if i == 0:
            LRU_list = [18000, 1024]
            read_ahead_list = [14, 56]
            # ���в�����ʼ��
            param_dict = initialization_parameters()

            # д���ò�����my.cnf,������workload
            param_dict_list = run_and_write_file(copy.copy(param_dict), param_unit_dict, None, param_dict_list, None)
            param_dict_latest = copy.deepcopy(param_dict_list[0])
            i = 1

        else:
            while True:
                if first is True:
                    while True:
                        print(read_ahead_list)

                        if len(read_ahead_list) == 0:
                            break

                        mid_value = float(param_dict_latest["innodb_read_ahead_threshold"])

                        param_dict_latest["innodb_read_ahead_threshold"] = int(read_ahead_list[0])

                        # д���ò�����my.cnf,������workload
                        param_dict_list = run_and_write_file(copy.copy(param_dict_latest), param_unit_dict, None, param_dict_list, None)

                        if param_dict_latest["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                            param_dict_latest["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                            read_ahead_list.pop(0)

                        else:
                            param_dict_latest["innodb_read_ahead_threshold"] = int(mid_value)
                            print("��ǰ�����")
                            print(param_dict_latest)
                            break

                    while True:
                        print(LRU_list)

                        if len(LRU_list) == 0:
                            break

                        mid_value = float(param_dict_latest["innodb_lru_scan_depth"])
                        param_dict_latest["innodb_lru_scan_depth"] = int(LRU_list[0])

                        # д���ò�����my.cnf,������workload
                        param_dict_list = run_and_write_file(copy.copy(param_dict_latest), param_unit_dict, None, param_dict_list, None)

                        if param_dict_latest["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                            param_dict_latest["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                            LRU_list.pop(0)

                        else:
                            param_dict_latest["innodb_lru_scan_depth"] = int(mid_value)
                            print("��ǰ�����")
                            print(param_dict_latest)
                            break

                else:
                    print("sssssssss")
                    while True:
                        print(LRU_list)
                        if len(LRU_list) == 0:
                            break

                        mid_value = float(param_dict_latest["innodb_lru_scan_depth"])
                        param_dict_latest["innodb_lru_scan_depth"] = int(LRU_list[0])

                        # д���ò�����my.cnf,������workload
                        param_dict_list = run_and_write_file(copy.copy(param_dict_latest), param_unit_dict, None, param_dict_list, None)

                        if param_dict_latest["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                            param_dict_latest["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                            LRU_list.pop(0)

                        else:
                            param_dict_latest["innodb_lru_scan_depth"] = int(mid_value)
                            print("��ǰ�����")
                            print(param_dict_latest)
                            break

                    while True:
                        print(read_ahead_list)
                        if len(read_ahead_list) == 0:
                            break

                        mid_value = float(param_dict_latest["innodb_read_ahead_threshold"])
                        param_dict_latest["innodb_read_ahead_threshold"] = int(read_ahead_list[0])

                        # д���ò�����my.cnf,������workload
                        param_dict_list = run_and_write_file(copy.copy(param_dict_latest), param_unit_dict, None, param_dict_list, None)

                        if param_dict_latest["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                            param_dict_latest["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                            read_ahead_list.pop(0)

                        else:
                            param_dict_latest["innodb_read_ahead_threshold"] = int(mid_value)
                            print("��ǰ�����")
                            print(param_dict_latest)
                            break

                print("is end??????")
                if mid_throught < float(param_dict_latest["throught"]):
                    mid_throught = float(param_dict_latest["throught"])
                    print("start loop")
                else:
                    print("end loop")
                    mid_throught = 0
                    cnt_tune = cnt_tune + 1
                    if cnt_tune < 2:
                        i = 0
                        if first is True:
                            first = False
                        else:
                            first = True
                    else:
                        loop_flag = False
                    break

