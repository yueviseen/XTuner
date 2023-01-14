# -*- coding: gbk -*-
import os
import random
import sys
import math
import time

from ip_24 import *
import numpy as np
import math
import copy
from Rular_for_sar_d_24 import *
from Ruler_for_sar_u_24 import *
from Rular_for_status_24 import *
from Rular_for_oltp_24 import *

# ����ȫ�ֲ���
cpu_num_all = int(os.popen("cat /proc/cpuinfo| grep 'processor'| wc -l").readlines()[0].replace("\n", ''))
cnt = 0
tune_param = {}
num_table = 9


# # ��ȡ��һ�εĲ���ֵ
# def read_tunning_process(i):
#
#     # ��¼���ؽ��
#     param_dict = {}
#
#     # �ж��Ƿ���ж�ȡ
#     flag = False
#
#     # ����ƥ����ַ�
#     start_i = "start_" + str(i - 1)
#
#     # �������ݵĶ�ȡ
#     with open(tunning_process_path, 'r') as f:
#         for i_con in f.readlines():
#             i_con = i_con.replace("\n", '')
#             if start_i in i_con:
#                 flag = True
#             if flag is True:
#                 if "start_" in i_con:
#                     continue
#                 if "end_" in i_con:
#                     break
#
#                 # ���и�ʽ�ķָ�
#                 i_con = i_con.split("=")
#                 if i_con[0] == "innodb_flush_method":
#                     param_dict[i_con[0]] = i_con[1]
#                 elif i_con[0] == "throught":
#                     param_dict[i_con[0]] = float(i_con[1])
#                 elif i_con[0] == "param":
#                     param_dict[i_con[0]] = i_con[1]
#                 else:
#                     i_con[1] = i_con[1].replace("M", '')
#                     param_dict[i_con[0]] = int(i_con[1])
#
#     return param_dict

def param_mid_valie_tuning_dif_plus(value, param_dict, param, param_dict_list, str_bottleneck, min, max, dif_value, mid_value):
    global mysql_sum_time
    init_value = value
    cnt = 0
    while True:
        param_dict[param] = init_value
        now_time = time.time()
        param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
        mysql_sum_time = mysql_sum_time + time.time() - now_time
        if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"] or cnt == 0:
            param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
            str_bottleneck = analysis_bottleneck()
            mid_value = analysis_show_global_status(status_path) / 1024 / 1024
            cnt = cnt + 1
            if param_dict[param] + dif_value > max:
                break
        else:
            param_dict[param] = int(param_dict[param] - dif_value)
            break
        init_value = int(init_value + dif_value)

    # ���в�����С����
    if param_dict[param] == value and param_dict[param] - dif_value >= min:
        flag_while_1 = True

    while flag_while_1:
        mid_LRU = param_dict[param]
        param_dict[param] = int(param_dict[param] - dif_value)
        now_time = time.time()
        param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
        mysql_sum_time = mysql_sum_time + time.time() - now_time
        if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
            param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
            str_bottleneck = analysis_bottleneck()
            mid_value = analysis_show_global_status(status_path) / 1024 / 1024
            if int(param_dict[param]) - dif_value < min:
                break
        else:
            param_dict[param] = mid_LRU
            break

        return param_dict, param_dict_list, str_bottleneck, mid_value


def param_mid_valie_tuning_rat_plus(value, param_dict, param, param_dict_list, str_bottleneck, min, max, rat_value, mid_value):
    global mysql_sum_time
    init_value = value
    flag_while_1 = False
    print(1111111111111)
    cnt = 0
    while True:
        param_dict[param] = init_value
        now_time = time.time()
        param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
        mysql_sum_time = mysql_sum_time + time.time() - now_time
        if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"] or cnt == 0:
            param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
            str_bottleneck = analysis_bottleneck()
            mid_value = analysis_show_global_status(status_path) / 1024 / 1024
            cnt = cnt + 1
            if param_dict[param] * rat_value > max:
                break
        else:
            param_dict[param] = int(param_dict[param] / rat_value)
            break
        init_value = int(init_value * rat_value)

    print("######################")
    # ���в�����С����
    if param_dict[param] == value and param_dict[param] / rat_value >= min:
        flag_while_1 = True

    while flag_while_1:
        mid_LRU = param_dict[param]
        param_dict[param] = int(param_dict[param] / rat_value)
        now_time = time.time()
        param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
        mysql_sum_time = mysql_sum_time + time.time() - now_time
        if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
            param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
            str_bottleneck = analysis_bottleneck()
            mid_value = analysis_show_global_status(status_path) / 1024 / 1024
            if int(param_dict[param]) / rat_value < min:
                break
        else:
            param_dict[param] = mid_LRU
            break

    print(2222222222)

    return param_dict, param_dict_list, str_bottleneck, mid_value


# ��¼�����м�ֵ̽���Ĳ���, valueֵĬ�ϲ���ֵ,���мӷ�����
def param_mid_value_tuning_dif(value, param_dict, param, param_dict_list, str_bottleneck, min, max, dif_value, mid_value):
    print(9999999999)
    global mysql_sum_time
    # ����״̬��ֵ
    mid_str_bottleneck = str_bottleneck
    mid_mid_value = mid_value
    flag_while_1 = False
    if (param_dict[param] - dif_value) >= min:
        print("11111111111")
        flag_while_1 = True

    # valueֵ���м�С����
    while flag_while_1:
        param_dict[param] = param_dict[param] - dif_value
        now_time = time.time()
        param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
        mysql_sum_time = mysql_sum_time + time.time() - now_time
        if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
            param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
            mid_str_bottleneck = analysis_bottleneck()
            mid_mid_value = analysis_show_global_status(status_path) / 1024 / 1024
            if int(param_dict[param] - dif_value) < min:
                break
        else:
            param_dict[param] = param_dict[param] + dif_value
            break

    # valueֵ�����������
    flag_while_1 = False
    if param_dict[param] == value and param_dict[param] + dif_value <= max:
        flag_while_1 = True
    while flag_while_1:
        param_dict[param] = param_dict[param] + dif_value
        now_time = time.time()
        param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
        mysql_sum_time = mysql_sum_time + time.time() - now_time
        if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
            param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
            mid_str_bottleneck = analysis_bottleneck()
            mid_mid_value = analysis_show_global_status(status_path) / 1024 / 1024
            if param_dict[param] + dif_value > max:
                break
        else:
            param_dict[param] = int(param_dict[param] - dif_value)
            break

    return param_dict, param_dict_list, mid_str_bottleneck, mid_mid_value


# ��¼�����м�ֵ̽���Ĳ���, valueֵĬ�ϲ���ֵ,���мӷ�����
def param_mid_value_tuning_rat(value, param_dict, param, param_dict_list, str_bottleneck, min, max, rat_value, mid_value):
    global mysql_sum_time
    # ����״̬��ֵ
    mid_str_bottleneck = str_bottleneck
    mid_mid_value = mid_value
    flag_while_1 = False
    if int(param_dict[param] / rat_value) >= min:
        flag_while_1 = True

    # valueֵ���м�С����
    while flag_while_1:
        mid_param_value = param_dict[param]
        param_dict[param] = int(param_dict[param] / rat_value)
        now_time = time.time()
        param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
        mysql_sum_time = mysql_sum_time + time.time() - now_time
        if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
            param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
            mid_str_bottleneck = analysis_bottleneck()
            mid_mid_value = analysis_show_global_status(status_path) / 1024 / 1024
            if int(param_dict[param] / rat_value) < min:
                break
        else:
            param_dict[param] = mid_param_value
            break

    # valueֵ�����������
    flag_while_1 = False
    if param_dict[param] == value and param_dict[param] * rat_value <= max:
        flag_while_1 = True
    while flag_while_1:
        param_dict[param] = param_dict[param] * rat_value
        now_time = time.time()
        param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
        mysql_sum_time = mysql_sum_time + time.time() - now_time
        if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
            param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
            mid_str_bottleneck = analysis_bottleneck()
            mid_mid_value = analysis_show_global_status(status_path) / 1024 / 1024
            if param_dict[param] * rat_value > max:
                break
        else:
            param_dict[param] = int(param_dict[param] / rat_value)
            break

    return param_dict, param_dict_list, mid_str_bottleneck, mid_mid_value


# ������Ҫ�����Ĳ���
def def_tune_param():
    # ��Ҫ�����Ĳ�������Ϊ1������Ҫ�����Ĳ�������Ϊ0
    global tune_param
    # ��ʼ������ 10 ��
    tune_param["shared_buffers"] = 1
    tune_param["effective_cache_size"] = 1
    tune_param["max_wal_size"] = 1
    tune_param["min_wal_size"] = 1
    tune_param["random_page_cost"] = 1
    tune_param["wal_level"] = 1
    tune_param["max_worker_processes"] = 1
    tune_param["bgwriter_lru_multiplier"] = 1
    tune_param["autovacuum_vacuum_cost_delay"] = 1
    tune_param["max_parallel_workers_per_gather"] = 1

    # ָ����ز��� 1��
    tune_param["wal_buffers"] = 1

    # ����CPU 5 ��
    tune_param["force_parallel_mode"] = 1
    tune_param["autovacuum_max_workers"] = 1
    tune_param["wal_writer_delay"] = 1
    tune_param["bgwriter_delay"] = 1
    tune_param["autovacuum_naptime"] = 1

    # ����CPU��IO�� 1 ��
    tune_param["wal_compression"] = 1

    # ����io�� 7 ��
    tune_param["effective_io_concurrency"] = 1
    tune_param["backend_flush_after"] = 1
    tune_param["bgwriter_flush_after"] = 1
    tune_param["checkpoint_flush_after"] = 1
    tune_param["wal_writer_flush_after"] = 1
    tune_param["autovacuum_vacuum_cost_limit"] = 1
    tune_param["bgwriter_lru_maxpages"] = 1

    # ����other�� 6 ��
    tune_param["default_statistics_target"] = 1
    tune_param["lock_timeout"] = 1
    tune_param["deadlock_timeout"] = 1
    tune_param["vacuum_cost_page_miss"] = 1
    tune_param["vacuum_cost_page_dirty"] = 1
    tune_param["enable_seqscan"] = 1


# ��ʼ������
def initialization_parameters():
    # ���巵���б�
    return_dict = {}

    global cpu_num_all
    cpu_num = cpu_num_all
    global tune_param

    # ���ڹ�����г�ʼ��,�����ŵ���Ҫ���޸�
    # 1����ʼ������shared_buffers��ȡ���ֵ,���������
    if tune_param["shared_buffers"] == 1:
        return_dict["shared_buffers"] = 200
    # 3����ʼ������max_wal_size��ȡ���ֵ�� ���������
    if tune_param["max_wal_size"] == 1:
        return_dict["max_wal_size"] = 192
    # 4�� ��ʼ������min_wal_size��ȡ���ֵ�� ���������
    if tune_param["min_wal_size"] == 1:
        return_dict["min_wal_size"] = 80
    # 5 ��ʼ������random_page_cost�������������other�����, +++++++++++
    if tune_param["random_page_cost"] == 1:
        return_dict["random_page_cost"] = 4
        # OTHER_param_list.append(return_dict["random_page_cost"])
    # 6 ��ʼ������wal_level,����Ӧ�ó���ѡ����С�ģ�����io�����������
    if tune_param["wal_level"] == 1:
        return_dict["wal_level"] = 'minimal'  # ����fio���Կɵ�
    # 7�� 8��ʼ������max_worker_processes��Ϊcpu�ĸ���Ϊmin��4, cpu/2���������������CPU�����!!!!!!!!!!!!!!
    if tune_param["max_worker_processes"] == 1 and tune_param["max_parallel_workers_per_gather"] == 1:
        return_dict["max_worker_processes"] = 16
        return_dict["max_parallel_workers_per_gather"] = 4
        # CPU_param_list.append(return_dict["max_worker_processes"])
        # CPU_param_list.append(return_dict["max_parallel_workers_per_gather"])
    # 9 ��ʼ������bgwriter_lru_multiplier,�������ؾ������Բ�ȡ1�� ����������� io�����!!!!!!!!!!!!!!
    if tune_param["bgwriter_lru_multiplier"] == 1:
        return_dict["bgwriter_lru_multiplier"] = 1  # ��ѯ���̲����ɵ�
        # IO_param_list.append(return_dict["bgwriter_lru_multiplier"])

    # ����ָ��
    # 11 ָ����ز��� 1��, ָ�������Ĭ��Ϊ64M
    if tune_param["wal_buffers"] == 1:
        return_dict["wal_buffers"] = 96

    # ȡCPU��ص�Ĭ��ֵ
    # 12 force_parallel_mode��Ĭ��ֵ
    if tune_param["force_parallel_mode"] == 1:
        return_dict["force_parallel_mode"] = "off"
        # CPU_param_list.append(return_dict["force_parallel_mode"])
    # 14 wal_writer_delay��Ĭ��ֵ
    if tune_param["wal_writer_delay"] == 1:
        return_dict["wal_writer_delay"] = 200
        # CPU_param_list.append(return_dict["wal_writer_delay"])
    # 15 bgwriter_delay��Ĭ��ֵ
    if tune_param["bgwriter_delay"] == 1:
        return_dict["bgwriter_delay"] = 200
        # CPU_param_list.append(return_dict["bgwriter_delay"])
    # 16 autovacuum_naptime��Ĭ��ֵ
    if tune_param["autovacuum_naptime"] == 1:
        return_dict["autovacuum_naptime"] = 60
        # CPU_param_list.append(return_dict["autovacuum_naptime"])

    # ȡCPU��IO��Ĭ��ֵ
    # 17 ȡwal_compression��Ĭ��ֵ
    if tune_param["wal_compression"] == 1:
        return_dict["wal_compression"] = "off"
        # CPU_param_list.append(return_dict["wal_compression"])
        # IO_param_list.append(return_dict["wal_compression"])
        # 13 autovacuum_max_workers��Ĭ��ֵ
    if tune_param["autovacuum_max_workers"] == 1:
        return_dict["autovacuum_max_workers"] = 5
        # CPU_param_list.append(return_dict["autovacuum_max_workers"])
        # IO_param_list.append(return_dict["autovacuum_max_workers"])

    # ȡio��Ĭ��ֵ
    # 19 ȡeffective_io_concurrency��Ĭ��ֵ
    if tune_param["effective_io_concurrency"] == 1:
        return_dict["effective_io_concurrency"] = 1
        # IO_param_list.append(return_dict["effective_io_concurrency"])
    # 20 ȡbackend_flush_after��Ĭ��ֵ
    if tune_param["backend_flush_after"] == 1:
        return_dict["backend_flush_after"] = 0
    # IO_param_list.append(return_dict["backend_flush_after"])
    # 21 ȡbgwriter_flush_after��Ĭ��ֵ
    if tune_param["bgwriter_flush_after"] == 1:
        return_dict["bgwriter_flush_after"] = 64
        # IO_param_list.append(return_dict["bgwriter_flush_after"])
    # 22 ȡcheckpoint_flush_after��Ĭ��ֵ
    if tune_param["checkpoint_flush_after"] == 1:
        return_dict["checkpoint_flush_after"] = 32
        # IO_param_list.append(return_dict["checkpoint_flush_after"])
    # 23 ȡwal_writer_flush_after��Ĭ��ֵ
    if tune_param["wal_writer_flush_after"] == 1:
        return_dict["wal_writer_flush_after"] = 128
        # IO_param_list.append(return_dict["wal_writer_flush_after"])
    # 24 ȡautovacuum_vacuum_cost_limit��Ĭ��ֵ
    if tune_param["autovacuum_vacuum_cost_limit"] == 1:
        return_dict["autovacuum_vacuum_cost_limit"] = 200
        # IO_param_list.append(return_dict["autovacuum_vacuum_cost_limit"])
    # 25 ȡbgwriter_lru_maxpages��Ĭ��ֵ
    if tune_param["bgwriter_lru_maxpages"] == 1:
        return_dict["bgwriter_lru_maxpages"] = 100
        # IO_param_list.append(return_dict["bgwriter_lru_maxpages"])
    # 10����ʼ������autovacuum_vacuum_cost_delay������������
    if tune_param["autovacuum_vacuum_cost_delay"] == 1:
        return_dict["autovacuum_vacuum_cost_delay"] = 2
        # IO_param_list.append(return_dict["autovacuum_vacuum_cost_delay"])

    # ����other��Ĭ��ֵ
    # 26 ȡ default_statistics_target��Ĭ��ֵ
    if tune_param["default_statistics_target"] == 1:
        return_dict["default_statistics_target"] = 100
        # OTHER_param_list.append(return_dict["default_statistics_target"])
    # 27 ȡlock_timeout��Ĭ��ֵ
    if tune_param["lock_timeout"] == 1:
        return_dict["lock_timeout"] = 0
        # OTHER_param_list.append(return_dict["lock_timeout"])
    # 28 ȡdeadlock_timeout��Ĭ��ֵ
    if tune_param["deadlock_timeout"] == 1:
        return_dict["deadlock_timeout"] = 1000
        # OTHER_param_list.append(return_dict["deadlock_timeout"])
    # 29 vacuum_cost_page_miss ��Ĭ��ֵ
    if tune_param["vacuum_cost_page_miss"] == 1:
        return_dict["vacuum_cost_page_miss"] = 10
        # OTHER_param_list.append(return_dict["vacuum_cost_page_miss"])
    # 30 vacuum_cost_page_dirty��Ĭ��ֵ
    if tune_param["vacuum_cost_page_dirty"] == 1:
        return_dict["vacuum_cost_page_dirty"] = 20
        # OTHER_param_list.append(return_dict["vacuum_cost_page_dirty"])
    # 18 ȡautovacuum��Ĭ��ֵ
    if tune_param["enable_seqscan"] == 1:
        return_dict["enable_seqscan"] = "on"
        # OTHER_param_list.append(return_dict["enable_seqscan"])
    # 2����ʼ������effective_cache_size�� ȡĬ��ֵ����̽������
    if tune_param["effective_cache_size"] == 1:
        return_dict["effective_cache_size"] = 4096
        # OTHER_param_list.append(return_dict["effective_cache_size"])

    # ���ز����ֵ�
    return return_dict


# ��ȡ���ȹ������ص�������
def get_throught():
    # ���ñ���
    mid_throught = 0
    mid_latency = 0

    # �������ݿ�
    start_PG()

    status_PG()

    # ��ԭ���ݿ�
    data_recovery()

    # ��ջ���
    free_cache()

    # �������ݿ�
    (mid_throught, mid_latency) = run_PG_for_oltp()

    # �ر����ݿ�
    stop_PG()

    # �������ݿ�����
    print("����60��")
    time.sleep(60)

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


# ��ȡ�����ļ�my.cnf
def read_my_cnf():
    # ��¼��ǰ����
    return_list = []
    # ��ȡ��ǰ����
    with open(path_my_cnf, 'r') as f:
        flag_mysqlld = False
        for ii in f.readlines():
            if "tuning param" in ii:
                flag_mysqlld = True
            elif flag_mysqlld is True:
                return_list.append(ii)
    return return_list


# �������ݵ����кͰѲ���д���ļ�
def run_and_write_file(param_dict, param_unit_dict, i, param_dict_list, ii):
    # д����ֵ�������ļ�
    write_my_cnf(param_dict, param_unit_dict)

    # ��ȡ������
    while True:
        mid_throught = get_throught()
        if mid_throught == -1:
            print("���ִ������¼���")
        else:
            break

    param_dict["throught"] = mid_throught

    # �ѵ�ǰ�Ĳ���ֵ��¼���Ա��´�ʹ��
    param_dict_list.append(param_dict)
    print("��ʾ���ε���������������Ĳ���ֵ")
    print("-----------------------------")
    global cnt
    print("cnt is %d" % cnt)
    cnt = cnt + 1
    print("-----------------------------")
    for ii in param_dict:
        print(ii, param_dict[ii])
    print("-----------------------------")

    # �������е����Ĳ����б�
    return param_dict_list


# # ��¼�����м�ֵ̽���Ĳ���
# def param_mid_value_tuning_2(value, param_dict,  param, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck, diff_value, min=0, max=0):
#
#     # ��¼�ò����Ƿ��һ��
#     param_dict[param] = value
#     global mysql_sum_time
#     # ����״̬��ֵ
#     mid_dict_show_global_status = dict_show_global_status
#     mid_engine_status_dict = engine_status_dict
#     mid_str_bottleneck = str_bottleneck
#     flag_while_1 = False
#     if param_dict[param] - diff_value > min:
#         flag_while_1 = True
#
#     # valueֵ���м�С����
#     while flag_while_1:
#         param_dict[param] = param_dict[param] - diff_value
#         now_time = time.time()
#         param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
#         mysql_sum_time = mysql_sum_time + time.time() - now_time
#         if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
#             param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
#             mid_dict_show_global_status = analysis_show_global_status(status_path)
#             mid_engine_status_dict = analysis_model()
#             mid_str_bottleneck = analysis_bottleneck()
#             if param_dict[param] - diff_value < min:
#                 break
#         else:
#             param_dict[param] = param_dict[param] + diff_value
#             break
#
#     # valueֵ�����������
#     flag_while_1 = False
#     if param_dict[param] == value:
#         flag_while_1 = True
#     while flag_while_1:
#         param_dict[param] = param_dict[param] + diff_value
#         now_time = time.time()
#         param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
#         mysql_sum_time = mysql_sum_time + time.time() - now_time
#         if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
#             param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
#             mid_dict_show_global_status = analysis_show_global_status(status_path)
#             mid_engine_status_dict = analysis_model()
#             mid_str_bottleneck = analysis_bottleneck()
#             if param_dict[param] + diff_value > max:
#                 break
#
#         else:
#             param_dict[param] = param_dict[param] - diff_value
#             break
#
#     return param_dict, param_dict_list, mid_dict_show_global_status, mid_engine_status_dict, mid_str_bottleneck
#
#
# # ��¼�����м�ֵ̽���Ĳ���
# def param_mid_value_tuning_max(value, param_dict,  param, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck, diff_value, min=0, max=0):
#
#     # ��¼�ò����Ƿ��һ��
#     param_dict[param] = value
#     global mysql_sum_time
#
#     # ����״̬��ֵ
#     mid_dict_show_global_status = copy.deepcopy(dict_show_global_status)
#     mid_engine_status_dict = copy.deepcopy(engine_status_dict)
#     mid_str_bottleneck = copy.deepcopy(str_bottleneck)
#
#     flag_while_1 = False
#     if param_dict[param] - diff_value > min:
#         flag_while_1 = True
#
#     # valueֵ���м�С����
#     while flag_while_1:
#         param_dict[param] = param_dict[param] - diff_value
#         param_dict["innodb_io_capacity"] = int(param_dict[param] / 2)
#         now_time = time.time()
#         param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
#         mysql_sum_time = mysql_sum_time + time.time() - now_time
#         if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
#             param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
#             mid_dict_show_global_status = analysis_show_global_status(status_path)
#             mid_engine_status_dict = analysis_model()
#             mid_str_bottleneck = analysis_bottleneck()
#             if param_dict[param] - diff_value < min:
#                 break
#         else:
#             param_dict[param] = param_dict[param] + diff_value
#             param_dict["innodb_io_capacity"] = int(param_dict[param] / 2)
#             break
#
#     # valueֵ�����������
#     flag_while_1 = False
#     if param_dict[param] == value:
#         flag_while_1 = True
#     while flag_while_1:
#         param_dict[param] = param_dict[param] + diff_value
#         param_dict["innodb_io_capacity"] = int(param_dict[param] / 2)
#         now_time = time.time()
#         param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
#         mysql_sum_time = mysql_sum_time + time.time() - now_time
#         if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
#             param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
#             mid_dict_show_global_status = analysis_show_global_status(status_path)
#             mid_engine_status_dict = analysis_model()
#             mid_str_bottleneck = analysis_bottleneck()
#             if param_dict[param] + diff_value > max:
#                 break
#
#         else:
#             param_dict[param] = param_dict[param] - diff_value
#             param_dict["innodb_io_capacity"] = int(param_dict[param] / 2)
#             break
#
#     return param_dict, param_dict_list, mid_dict_show_global_status, mid_engine_status_dict, mid_str_bottleneck
#
# # ��¼�����м�ֵ̽���Ĳ���, valueֵĬ�ϲ���ֵ
# def param_mid_value_tuning(value, param_dict,  param, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck, min=0, max=0):
#
#     global mysql_sum_time
#
#     # ��¼Ĭ��ֵ
#     param_dict[param] = value
#
#     # ����״̬��ֵ
#     mid_dict_show_global_status = dict_show_global_status
#     mid_engine_status_dict = engine_status_dict
#     mid_str_bottleneck = str_bottleneck
#
#     flag_while_1 = False
#     if (param_dict[param]/2) > min:
#         flag_while_1 = True
#
#     # valueֵ���м�С����
#     while flag_while_1:
#         param_dict[param] = int(param_dict[param] / 2)
#         now_time = time.time()
#         param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
#         mysql_sum_time = mysql_sum_time + time.time() - now_time
#         if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
#             param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
#             mid_dict_show_global_status = analysis_show_global_status(status_path)
#             mid_engine_status_dict = analysis_model()
#             mid_str_bottleneck = analysis_bottleneck()
#             if int(param_dict[param] / 2) < min:
#                 break
#         else:
#             param_dict[param] = param_dict[param] * 2
#             break
#
#     # valueֵ�����������
#     flag_while_1 = False
#     if param_dict[param] == value:
#         flag_while_1 = True
#     while flag_while_1:
#         param_dict[param] = param_dict[param] * 2
#         now_time = time.time()
#         param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
#         mysql_sum_time = mysql_sum_time + time.time() - now_time
#         if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
#             param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
#             mid_dict_show_global_status = analysis_show_global_status(status_path)
#             mid_engine_status_dict = analysis_model()
#             mid_str_bottleneck = analysis_bottleneck()
#             if param_dict[param] * 2 > max:
#                 break
#         else:
#             param_dict[param] = int(param_dict[param] / 2)
#             break
#
#     return param_dict, param_dict_list, mid_dict_show_global_status, mid_engine_status_dict, mid_str_bottleneck
#

# ��ȡcpu��io��������

def analysis_bottleneck():
    """
    ��ȡcpu��io��������
    """
    result_sar_u = analysis_sar_u(path_sar_u)
    result_sar_d = analysis_sar_d(path_sar_d)

    print(result_sar_d)
    print(result_sar_u)

    percent_cpu = 0
    percent_io = 0

    # ��ȡcpu��������
    length = len(result_sar_u["%idle"]) - 2
    for i in result_sar_u["%idle"][2:]:
        percent_cpu = percent_cpu + float(i)
    percent_cpu = percent_cpu / length

    # ��ȡio��������
    length = len(result_sar_d["%util"]) - 2
    for i in result_sar_d["%util"][2:]:
        percent_io = percent_io + float(i)
    percent_io = percent_io / length

    # ����io��cpu��������
    print(percent_io, 100 - percent_cpu)

    return percent_io, 100 - percent_cpu


# �ж�ϵͳƿ��
def judge_bottleneck(str_bottleneck, flag_param_IO, flag_param_CPU, flag_param_OTHER):
    """
   cpuƿ�����жϹ����ǣ�
   ע��>=50%
   �澯>=70%
   ����>=90%
   ioƿ�����жϹ����ǣ�
   ע��>=40%
   �澯>=60%
   ����>=80%
   ����ƿ���ǣ�
   cpuС��<90%����io<80%
   """

    print("--------------")
    print("ϵͳƿ������")
    print(flag_param_IO, flag_param_CPU, flag_param_OTHER)
    print(str_bottleneck)
    print("---------------")
    while True:
        print("�������ѡ��")
        i = random.randint(1,3)
        if i == 1 and flag_param_IO != "end":
            return "IO"
        elif i == 2 and flag_param_CPU != "end":
            return "CPU"
        elif i == 3 and flag_param_OTHER != "end":
            return "OTHER"
        else:
            return "end"
    # # ������ioƿ��ʱ������ƿ�������ж�
    # if str_bottleneck[0] >= 80 and flag_param_IO != "end":
    #     if (str_bottleneck[0] - 80) / (100 - 80) > (str_bottleneck[1] - 90) / (100 - 90):
    #         return "IO"
    #     if (str_bottleneck[0] - 80) / (100 - 80) <= (str_bottleneck[1] - 90) / (100 - 90) and flag_param_CPU != "end":
    #         return "CPU"
    #     if (str_bottleneck[0] - 80) / (100 - 80) <= (str_bottleneck[1] - 90) / (100 - 90) and flag_param_CPU == "end":
    #         return "IO"
    #
    # if str_bottleneck[0] >= 80 and flag_param_IO == "end":
    #     if str_bottleneck[1] >= 90:
    #         if flag_param_CPU != "end":
    #             return "CPU"
    #         elif flag_param_OTHER != "end":
    #             return "OTHER"
    #         else:
    #             return "end"
    #     else:
    #         if flag_param_OTHER != "end":
    #             return "OTHER"
    #         elif flag_param_CPU != "end":
    #             return "CPU"
    #         else:
    #             return "end"
    #
    # # ������CPUƿ��ʱ�� ����ƿ�������ж�
    # if str_bottleneck[1] >= 90 and flag_param_CPU != "end":
    #     return "CPU"
    # if str_bottleneck[1] >= 90 and flag_param_CPU == "end":
    #     if str_bottleneck[0] < 80:
    #         if flag_param_OTHER != "end":
    #             return "OTHER"
    #         elif flag_param_IO != "end":
    #             return "IO"
    #         else:
    #             return "end"
    #
    # # ��������ƿ����ʱ�� ����ƿ�������ж�
    # if str_bottleneck[0] < 80 and str_bottleneck[1] < 90 and flag_param_OTHER != "end":
    #     return "OTHER"
    # if str_bottleneck[0] < 80 and str_bottleneck[1] < 90 and flag_param_OTHER == "end":
    #     if flag_param_CPU == "end" and flag_param_IO == "end":
    #         return "end"
    #     if flag_param_CPU == "end" and flag_param_IO != "end":
    #         return "IO"
    #     if flag_param_IO == "end" and flag_param_CPU != "end":
    #         return "CPU"
    #     if str_bottleneck[0] / 80 >= str_bottleneck[1] / 90:
    #         return "IO"
    #     if str_bottleneck[0] / 80 < str_bottleneck[1] / 90:
    #         return "CPU"


if __name__ == "__main__":
    """
    ��Ҫ�������ݿ�innodb�������Ź��̵ĵ���
    """

    # ��¼�ܹ�����ʱ��
    mysql_sum_time = 0

    start_now_time = time.time()

    # �趨������Դ���ڴ���Դ����λM
    memory_resource = 684

    # �趨���õĴ�����Դ,��λM
    disk_resource = 192

    # �趨���ĵ�������
    iterations_num = 150

    # ��¼��ǰ��õĲ����б��������
    param_dict = {}

    # ��¼�������ι���
    param_dict_list = []

    # ��¼��ǰ������io��صĲ���
    flag_param_IO = "start"

    # ��¼��ǰ������cpu��صĲ���
    flag_param_CPU = "start"

    # ��¼��ǰ������OTHER��صĲ���
    flag_param_OTHER = "start"

    # ����ѭ���Ĵ���ѵ��
    flag_loop = True

    # �Բ������е����ж�
    effective_cache_size_flag = False

    # ��¼��Ҫ����M��λ�Ĳ���
    param_unit_dict = {}
    param_unit_dict["shared_buffers"] = "MB"
    param_unit_dict["effective_cache_size"] = "MB"
    param_unit_dict["max_wal_size"] = "MB"
    param_unit_dict["min_wal_size"] = "MB"
    param_unit_dict["wal_buffers"] = "MB"

    # ��¼��Ҫ���ŵ�io����
    IO_param_list = ["autovacuum_max_workers",
                     "bgwriter_lru_multiplier",
                     "bgwriter_lru_maxpages",
                     "wal_compression",
                     "effective_io_concurrency",
                     "backend_flush_after",
                     "bgwriter_flush_after",
                     "checkpoint_flush_after",
                     "wal_writer_flush_after",
                     "autovacuum_vacuum_cost_delay", "autovacuum_vacuum_cost_limit"]

    # ��¼��Ҫ���ŵ�cpu����
    CPU_param_list = ["force_parallel_mode", "bgwriter_delay", "wal_writer_delay",
                      "autovacuum_naptime", "wal_compression",
                      "max_worker_processes", "max_parallel_workers_per_gather", "autovacuum_max_workers"]

    # ��¼��Ҫ���ŵ�other����
    OTHER_param_list = ["random_page_cost", "effective_cache_size", "deadlock_timeout", "lock_timeout",
                        "enable_seqscan", "default_statistics_target", "vacuum_cost_page_miss",
                        "vacuum_cost_page_dirty"]

    # ��ʱ���棬�����Ժ�ѭ��
    mid_IO_list = []
    mid_CPU_list = []
    mid_OTHER_list = []

    # ��Ҫ�����Ƿ����ѭ��
    max_iter_value = 0

    # ��¼��������
    i = 0

    # ���в����ĵ����޸�
    while i < iterations_num:

        # ��Ҫ��¼���µ�������,��ʼֵ��0
        throught = -1

        # ��һ�ε�������Ҫ���г�ʼ��
        if i == 0:

            # ���е��ŵĹ��̣�д���ļ�tuning_process(tunning_process_path)��
            os.system(clean_tuning_process)

            # ������Ҫ���ŵĲ���
            def_tune_param()

            # ���в�����ʼ��
            param_dict = initialization_parameters()

            for i_param_dict in param_dict:
                print(i_param_dict, param_dict[i_param_dict])

            # ��¼����ʱ��
            now_time = time.time()

            # д���ò�����my.cnf
            param_dict_list = run_and_write_file(copy.copy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)

            mysql_sum_time = mysql_sum_time + time.time() - now_time

            # ��ȡ��һ�εĲ����б�
            param_dict = copy.deepcopy(param_dict_list[len(param_dict_list) - 1])

            # ��ȡϵͳ��Ϣ
            str_bottleneck = analysis_bottleneck()

            # ���и��ƣ������Ժ�ѭ��ʹ��
            mid_IO_list = copy.deepcopy(IO_param_list)
            mid_CPU_list = copy.deepcopy(CPU_param_list)
            mid_OTHER_list = copy.deepcopy(OTHER_param_list)

            # �������޸Ĳ���
            mid_value = min(int(math.ceil(analysis_show_global_status(status_path) / 1024 / 1024) * 1.5), 96)
            print(mid_value)
            print("����wal_buffers�ж�")
            if mid_value < param_dict["wal_buffers"]:
                diff_value = param_dict["wal_buffers"] - mid_value
                param_dict["wal_buffers"] = mid_value
                param_dict["shared_buffers"] = param_dict["shared_buffers"] + diff_value
                now_time = time.time()
                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                mysql_sum_time = mysql_sum_time + time.time() - now_time
                param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                str_bottleneck = analysis_bottleneck()
                mid_value = analysis_show_global_status(status_path) / 1024 / 1024
            print("##################")
        # ����ϵͳƿ��ϵͳ�ж�
        else:
            """
            log_buffer�����㹻�ڴ�ռ䣬���ܳ�Ϊƿ��
            """
            print("����������������")
            print(mid_value)
            # ���log_buffer����ƿ�������
            if mid_value * 1.1 < param_dict["wal_buffers"] or param_dict["wal_buffers"] == 96:

                # ����ϵͳƿ���ж�
                print("����ϵͳƿ���ж�")
                is_bottleneck = judge_bottleneck(str_bottleneck, flag_param_IO, flag_param_CPU, flag_param_OTHER)

                if is_bottleneck == "IO":
                    """
                    IO_param_list.append(return_dict["bgwriter_lru_multiplier"])
                    IO_param_list.append(return_dict["wal_compression"])
                    IO_param_list.append(return_dict["effective_io_concurrency"])
                    IO_param_list.append(return_dict["backend_flush_after"])
                    IO_param_list.append(return_dict["bgwriter_flush_after"])
                    IO_param_list.append(return_dict["checkpoint_flush_after"])
                    IO_param_list.append(return_dict["wal_writer_flush_after"])
                    IO_param_list.append(return_dict["autovacuum_vacuum_cost_limit"])
                    IO_param_list.append(return_dict["bgwriter_lru_maxpages"])
                    IO_param_list.append(return_dict["autovacuum_vacuum_cost_delay"])
                    IO_param_list.append(return_dict["autovacuum_max_workers"])
                    """
                    print("�ж�Ϊioƿ��������ioƿ����ز���")
                    for io_param in mid_IO_list:
                        print("���в���{}����".format(io_param))
                        if io_param == "wal_compression":
                            if param_dict["wal_compression"] == "off":
                                param_dict["wal_compression"] = "on"
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    str_bottleneck = analysis_bottleneck()
                                    mid_value = analysis_show_global_status(status_path) / 1024 / 1024
                                else:
                                    param_dict["wal_compression"] = "off"

                        elif io_param == "autovacuum_max_workers":
                            if param_dict["autovacuum_max_workers"] > 2:
                                while True:
                                    param_dict["autovacuum_max_workers"] = param_dict["autovacuum_max_workers"] - 2
                                    rate_value = param_dict["effective_cache_size"] / param_dict["shared_buffers"]
                                    param_dict["shared_buffers"] = param_dict["shared_buffers"] + 128
                                    if effective_cache_size_flag is True:
                                        param_dict["effective_cache_size"] = min(int(math.ceil(rate_value * param_dict["shared_buffers"])), 6000)
                                    now_time = time.time()
                                    param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                    mysql_sum_time = mysql_sum_time + time.time() - now_time
                                    if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                        param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                        mid_str_bottleneck = analysis_bottleneck()
                                        mid_value = analysis_show_global_status(status_path) / 1024 / 1024
                                        if param_dict["autovacuum_max_workers"] - 2 < 1:
                                            break
                                    else:
                                        param_dict["autovacuum_max_workers"] = int(param_dict["autovacuum_max_workers"] + 2)
                                        param_dict["shared_buffers"] = param_dict["shared_buffers"] - 128
                                        if effective_cache_size_flag is True:
                                            param_dict["effective_cache_size"] = min(int(math.ceil(rate_value * param_dict["shared_buffers"])), 6000)
                                        break
                        elif io_param == "bgwriter_lru_multiplier":
                            param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_dif(param_dict["bgwriter_lru_multiplier"], param_dict,
                                                                                                                "bgwriter_lru_multiplier", param_dict_list, str_bottleneck,
                                                                                                                1, 10, 1, mid_value)
                        elif io_param == "bgwriter_lru_maxpages":
                            if param_dict["bgwriter_lru_maxpages"] != 0:
                                param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_rat(param_dict["bgwriter_lru_maxpages"], param_dict,
                                                                                                                    "bgwriter_lru_maxpages", param_dict_list, str_bottleneck,
                                                                                                                    1, 2000, 2, mid_value)
                                print(param_dict)
                                mid_bgwriter_lru_maxpages = param_dict["bgwriter_lru_maxpages"]
                                mid_throughtput = param_dict["throught"]
                                param_dict["bgwriter_lru_maxpages"] = 0
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                if param_dict["throught"] < mid_throughtput:
                                    param_dict["throught"] = mid_throughtput
                                    param_dict["bgwriter_lru_maxpages"] = mid_bgwriter_lru_maxpages
                                else:
                                    str_bottleneck = analysis_bottleneck()
                                    mid_value = analysis_show_global_status(status_path) / 1024 / 1024
                            else:
                                # ����״̬��ֵ
                                other_str_bottleneck = copy.deepcopy(str_bottleneck)
                                other_mid_value = copy.deepcopy(mid_value)
                                other_param_dict = copy.deepcopy(param_dict)
                                param_dict["bgwriter_lru_maxpages"] = 100
                                param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_valie_tuning_rat_plus(param_dict["bgwriter_lru_maxpages"], param_dict,
                                                                                                                         "bgwriter_lru_maxpages", param_dict_list, str_bottleneck,
                                                                                                                         1, 2000, 2, mid_value)
                                if param_dict["throught"] < other_param_dict["throught"]:
                                    param_dict = other_param_dict
                                    mid_value = other_mid_value
                                    str_bottleneck = other_str_bottleneck

                        elif io_param == "effective_io_concurrency":
                            if param_dict["effective_io_concurrency"] != 0:
                                param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_rat(param_dict["effective_io_concurrency"], param_dict,
                                                                                                                    "effective_io_concurrency", param_dict_list, str_bottleneck,
                                                                                                                    1, 256, 2, mid_value)
                                print(param_dict)
                                mid_effective_io_concurrency = param_dict["effective_io_concurrency"]
                                param_dict["effective_io_concurrency"] = 0
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    str_bottleneck = analysis_bottleneck()
                                    mid_value = analysis_show_global_status(status_path) / 1024 / 1024
                                else:
                                    param_dict["effective_io_concurrency"] = mid_effective_io_concurrency

                            else:
                                # ����״̬��ֵ
                                other_str_bottleneck = copy.deepcopy(str_bottleneck)
                                other_mid_value = copy.deepcopy(mid_value)
                                other_param_dict = copy.deepcopy(param_dict)
                                param_dict["effective_io_concurrency"] = 4
                                param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_valie_tuning_rat_plus(param_dict["effective_io_concurrency"], param_dict,
                                                                                                                         "effective_io_concurrency", param_dict_list,
                                                                                                                         str_bottleneck,
                                                                                                                         1, 256, 2, mid_value)
                                if param_dict["throught"] < other_param_dict["throught"]:
                                    param_dict = other_param_dict
                                    mid_value = other_mid_value
                                    str_bottleneck = other_str_bottleneck
                        elif io_param == "backend_flush_after":
                            if param_dict["backend_flush_after"] != 0:
                                param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_rat(param_dict["backend_flush_after"], param_dict,
                                                                                                                    "backend_flush_after", param_dict_list, str_bottleneck,
                                                                                                                    1, 256, 2, mid_value)
                                mid_backend_flush_after = param_dict["backend_flush_after"]
                                param_dict["backend_flush_after"] = 0
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    str_bottleneck = analysis_bottleneck()
                                    mid_value = analysis_show_global_status(status_path) / 1024 / 1024
                                else:
                                    param_dict["backend_flush_after"] = mid_backend_flush_after

                            else:
                                # ����״̬��ֵ
                                mid_str_bottleneck = copy.deepcopy(str_bottleneck)
                                mid_mid_value = copy.deepcopy(mid_value)
                                mid_param_dict = copy.deepcopy(param_dict)
                                param_dict["backend_flush_after"] = 16
                                print(param_dict)
                                print(str_bottleneck)
                                print(mid_value)
                                param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_valie_tuning_rat_plus(param_dict["backend_flush_after"],
                                                                                                                         param_dict,
                                                                                                                         "backend_flush_after",
                                                                                                                         param_dict_list,
                                                                                                                         copy.deepcopy(str_bottleneck),
                                                                                                                         1, 256, 2,
                                                                                                                         mid_value)
                                print(param_dict["throught"])
                                print(mid_param_dict["throught"])
                                if param_dict["throught"] < mid_param_dict["throught"]:
                                    param_dict = mid_param_dict
                                    mid_value = mid_mid_value
                                    str_bottleneck = mid_str_bottleneck
                        elif io_param == "bgwriter_flush_after":
                            if param_dict["bgwriter_flush_after"] != 0:
                                param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_rat(param_dict["bgwriter_flush_after"], param_dict,
                                                                                                                    "bgwriter_flush_after", param_dict_list, str_bottleneck,
                                                                                                                    1, 256, 2, mid_value)
                                mid_bgwriter_flush_after = param_dict["bgwriter_flush_after"]
                                param_dict["bgwriter_flush_after"] = 0
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    str_bottleneck = analysis_bottleneck()
                                    mid_value = analysis_show_global_status(status_path) / 1024 / 1024
                                else:
                                    param_dict["bgwriter_flush_after"] = mid_bgwriter_flush_after

                            else:
                                # ����״̬��ֵ
                                mid_str_bottleneck = copy.deepcopy(str_bottleneck)
                                mid_mid_value = copy.deepcopy(mid_value)
                                mid_param_dict = copy.deepcopy(param_dict)
                                param_dict["bgwriter_flush_after"] = 64
                                param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_valie_tuning_rat_plus(param_dict["bgwriter_flush_after"], param_dict,
                                                                                                                         "bgwriter_flush_after", param_dict_list,
                                                                                                                         copy.deepcopy(str_bottleneck),
                                                                                                                         1, 256, 2, mid_value)
                                if param_dict["throught"] < mid_param_dict["throught"]:
                                    param_dict = mid_param_dict
                                    mid_value = mid_mid_value
                                    str_bottleneck = mid_str_bottleneck
                        elif io_param == "checkpoint_flush_after":
                            if param_dict["checkpoint_flush_after"] != 0:
                                param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_rat(param_dict["checkpoint_flush_after"], param_dict,
                                                                                                                    "checkpoint_flush_after", param_dict_list, str_bottleneck,
                                                                                                                    1, 256, 2, mid_value)
                                mid_checkpoint_flush_after = param_dict["checkpoint_flush_after"]
                                param_dict["checkpoint_flush_after"] = 0
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    str_bottleneck = analysis_bottleneck()
                                    mid_value = analysis_show_global_status(status_path) / 1024 / 1024
                                else:
                                    param_dict["checkpoint_flush_after"] = mid_checkpoint_flush_after

                            else:
                                # ����״̬��ֵ
                                mid_str_bottleneck = copy.deepcopy(str_bottleneck)
                                mid_mid_value = copy.deepcopy(mid_value)
                                mid_param_dict = copy.deepcopy(param_dict)
                                param_dict["checkpoint_flush_after"] = 32
                                param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_valie_tuning_rat_plus(param_dict["checkpoint_flush_after"], param_dict,
                                                                                                                         "checkpoint_flush_after", param_dict_list,
                                                                                                                         str_bottleneck,
                                                                                                                         1, 256, 2, mid_value)
                                if param_dict["throught"] < mid_param_dict["throught"]:
                                    param_dict = mid_param_dict
                                    mid_value = mid_mid_value
                                    str_bottleneck = mid_str_bottleneck
                        elif io_param == "wal_writer_flush_after":
                            if param_dict["wal_writer_flush_after"] != 0:
                                param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_rat(param_dict["wal_writer_flush_after"], param_dict,
                                                                                                                    "wal_writer_flush_after", param_dict_list, str_bottleneck,
                                                                                                                    1, 256, 2, mid_value)
                                mid_wal_writer_flush_after = param_dict["wal_writer_flush_after"]
                                param_dict["wal_writer_flush_after"] = 0
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    str_bottleneck = analysis_bottleneck()
                                    mid_value = analysis_show_global_status(status_path) / 1024 / 1024
                                else:
                                    param_dict["wal_writer_flush_after"] = mid_wal_writer_flush_after

                            else:
                                # ����״̬��ֵ
                                mid_str_bottleneck = copy.deepcopy(str_bottleneck)
                                mid_mid_value = copy.deepcopy(mid_value)
                                mid_param_dict = copy.deepcopy(param_dict)
                                param_dict["wal_writer_flush_after"] = 128
                                param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_valie_tuning_rat_plus(param_dict["wal_writer_flush_after"], param_dict,
                                                                                                                         "wal_writer_flush_after", param_dict_list,
                                                                                                                         str_bottleneck,
                                                                                                                         1, 256, 2, mid_value)
                                if param_dict["throught"] < mid_param_dict["throught"]:
                                    param_dict = mid_param_dict
                                    mid_value = mid_mid_value
                                    str_bottleneck = mid_str_bottleneck
                        elif io_param == "autovacuum_vacuum_cost_delay":
                            if param_dict["autovacuum_vacuum_cost_delay"] != 0:
                                param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_rat(param_dict["autovacuum_vacuum_cost_delay"], param_dict,
                                                                                                                    "autovacuum_vacuum_cost_delay", param_dict_list, str_bottleneck,
                                                                                                                    1, 100, 2, mid_value)
                                mid_autovacuum_vacuum_cost_delay = param_dict["autovacuum_vacuum_cost_delay"]
                                param_dict["autovacuum_vacuum_cost_delay"] = 0
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    str_bottleneck = analysis_bottleneck()
                                    mid_value = analysis_show_global_status(status_path) / 1024 / 1024
                                else:
                                    param_dict["autovacuum_vacuum_cost_delay"] = mid_autovacuum_vacuum_cost_delay

                            else:
                                # ����״̬��ֵ
                                mid_str_bottleneck = copy.deepcopy(str_bottleneck)
                                mid_mid_value = copy.deepcopy(mid_value)
                                mid_param_dict = copy.deepcopy(param_dict)
                                param_dict["autovacuum_vacuum_cost_delay"] = 2
                                param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_valie_tuning_rat_plus(param_dict["autovacuum_vacuum_cost_delay"], param_dict,
                                                                                                                         "autovacuum_vacuum_cost_delay", param_dict_list,
                                                                                                                         str_bottleneck,
                                                                                                                         1, 100, 2, mid_value)
                                if param_dict["throught"] < mid_param_dict["throught"]:
                                    param_dict = mid_param_dict
                                    mid_value = mid_mid_value
                                    str_bottleneck = mid_str_bottleneck
                        elif io_param == "autovacuum_vacuum_cost_limit":
                            if param_dict["autovacuum_vacuum_cost_delay"] > 0:
                                param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_rat(param_dict["autovacuum_vacuum_cost_limit"], param_dict,
                                                                                                                    "autovacuum_vacuum_cost_limit", param_dict_list, str_bottleneck,
                                                                                                                    100, 4000, 2, mid_value)

                        # ����ѭ��
                        break

                    print("��ǰ��õĲ���ѡ��")
                    for i_param_dict in param_dict:
                        print(i_param_dict, param_dict[i_param_dict])
                    mid_IO_list = copy.deepcopy(mid_IO_list[1:])
                    print(len(mid_IO_list))
                    print(mid_IO_list)
                    if len(mid_IO_list) == 0:
                        flag_param_IO = "end"

                elif is_bottleneck == "CPU":
                    """
                    CPU_param_list.append(return_dict["force_parallel_mode"]) 
                    CPU_param_list.append(return_dict["wal_writer_delay"])           
                    CPU_param_list.append(return_dict["bgwriter_delay"])
                    CPU_param_list.append(return_dict["autovacuum_naptime"])
                    CPU_param_list.append(return_dict["wal_compression"])
                    CPU_param_list.append(return_dict["autovacuum_max_workers"])
                    CPU_param_list.append(return_dict["max_worker_processes"])
                    CPU_param_list.append(return_dict["max_parallel_workers_per_gather"])

                    """
                    print("�ж�ƿ����CPU, ������Ӧ�����޸�")

                    for cpu_param in mid_CPU_list:
                        print("���в���{}����".format(cpu_param))
                        if cpu_param == "force_parallel_mode":
                            mid_mode = copy.deepcopy(param_dict["force_parallel_mode"])
                            list_forcr_parallel_mode = ["off", "on", "regress"]
                            print(list_forcr_parallel_mode)
                            for i_list_forcr_parallel_mode in list_forcr_parallel_mode:
                                if mid_mode == i_list_forcr_parallel_mode:
                                    continue
                                mid_force_parallel_mode = param_dict["force_parallel_mode"]
                                param_dict["force_parallel_mode"] = i_list_forcr_parallel_mode
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    str_bottleneck = analysis_bottleneck()
                                    mid_value = analysis_show_global_status(status_path) / 1024 / 1024
                                else:
                                    param_dict["force_parallel_mode"] = mid_force_parallel_mode
                        elif cpu_param == "bgwriter_delay":
                            param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_rat(param_dict["bgwriter_delay"], param_dict,
                                                                                                                "bgwriter_delay", param_dict_list, str_bottleneck,
                                                                                                                10, 4000, 2, mid_value)
                        elif cpu_param == "wal_writer_delay":
                            param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_rat(param_dict["wal_writer_delay"], param_dict,
                                                                                                                "wal_writer_delay", param_dict_list, str_bottleneck,
                                                                                                                1, 4000, 2, mid_value)
                        elif cpu_param == "autovacuum_naptime":
                            param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_dif(param_dict["autovacuum_naptime"], param_dict,
                                                                                                                "autovacuum_naptime", param_dict_list, str_bottleneck,
                                                                                                                1, 200, 20, mid_value)
                        elif cpu_param == "wal_compression":
                            if param_dict["wal_compression"] == "on":
                                param_dict["wal_compression"] = "off"
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    str_bottleneck = analysis_bottleneck()
                                    mid_value = analysis_show_global_status(status_path) / 1024 / 1024
                                else:
                                    param_dict["wal_compression"] = "on"
                        elif cpu_param == "max_worker_processes":
                            # ���в����ж�
                            param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_dif(param_dict["max_worker_processes"], param_dict,
                                                                                                                "max_worker_processes", param_dict_list, str_bottleneck,
                                                                                                                1, 48, 4, mid_value)
                        elif cpu_param == "max_parallel_workers_per_gather":
                            # ���в����ж�
                            mid_parallel = min(param_dict["max_worker_processes"], 16)
                            param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_dif(param_dict["max_parallel_workers_per_gather"], param_dict,
                                                                                                                "max_parallel_workers_per_gather", param_dict_list, str_bottleneck,
                                                                                                                1, mid_parallel, 2, mid_value)
                        elif cpu_param == "autovacuum_max_workers":

                            flag_while_2 = False
                            if (param_dict["autovacuum_max_workers"] - 1) > 1:
                                flag_while_2 = True
                            mid_autovacuum_max_workers = param_dict["autovacuum_max_workers"]
                            # valueֵ���м�С����
                            while flag_while_2:
                                param_dict["autovacuum_max_workers"] = param_dict["autovacuum_max_workers"] - 1
                                rate_value = param_dict["effective_cache_size"] / param_dict["shared_buffers"]
                                param_dict["shared_buffers"] = param_dict["shared_buffers"] + 64
                                if effective_cache_size_flag is True:
                                    param_dict["effective_cache_size"] = min(int(math.ceil(rate_value * param_dict["shared_buffers"])), 6000)
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    mid_str_bottleneck = analysis_bottleneck()
                                    mid_mid_value = analysis_show_global_status(status_path) / 1024 / 1024
                                    if int(param_dict["autovacuum_max_workers"] - 1) < 1:
                                        break
                                else:
                                    param_dict["autovacuum_max_workers"] = param_dict["autovacuum_max_workers"] + 1
                                    param_dict["shared_buffers"] = param_dict["shared_buffers"] + 64
                                    if effective_cache_size_flag is True:
                                        param_dict["effective_cache_size"] = min(int(math.ceil(rate_value * param_dict["shared_buffers"])), 6000)
                                    break

                            # valueֵ�����������
                            flag_while_2 = False
                            if param_dict["autovacuum_max_workers"] == mid_autovacuum_max_workers and param_dict["autovacuum_max_workers"] + 1 <= 5:
                                flag_while_2 = True
                            while flag_while_2:
                                param_dict["autovacuum_max_workers"] = param_dict["autovacuum_max_workers"] + 1
                                rate_value = param_dict["effective_cache_size"] / param_dict["shared_buffers"]
                                param_dict["shared_buffers"] = param_dict["shared_buffers"] - 64
                                if effective_cache_size_flag is True:
                                    param_dict["effective_cache_size"] = min(int(math.ceil(rate_value * param_dict["shared_buffers"])), 6000)
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    mid_str_bottleneck = analysis_bottleneck()
                                    mid_mid_value = analysis_show_global_status(status_path) / 1024 / 1024
                                    if param_dict["autovacuum_max_workers"] + 1 > 5:
                                        break
                                else:
                                    param_dict["autovacuum_max_workers"] = int(param_dict["autovacuum_max_workers"] - 1)
                                    param_dict["shared_buffers"] = param_dict["shared_buffers"] + 64
                                    if effective_cache_size_flag is True:
                                        param_dict["effective_cache_size"] = min(int(math.ceil(rate_value * param_dict["shared_buffers"])), 6000)

                                    break

                        # ����ѭ��
                        break

                    print("��ǰ��õĲ���ѡ��")
                    for i_param_dict in param_dict:
                        print(i_param_dict, param_dict[i_param_dict])
                    mid_CPU_list = mid_CPU_list[1:]
                    if len(mid_CPU_list) == 0:
                        flag_param_CPU = "end"

                # �޸�������صĲ���
                elif is_bottleneck == "OTHER":
                    """
                    OTHER_param_list.append(return_dict["default_statistics_target"])
                    OTHER_param_list.append(return_dict["lock_timeout"])
                    OTHER_param_list.append(return_dict["deadlock_timeout"])
                    OTHER_param_list.append(return_dict["vacuum_cost_page_miss"])
                    OTHER_param_list.append(return_dict["vacuum_cost_page_dirty"])
                    OTHER_param_list.append(return_dict["enable_seqscan"])
                    OTHER_param_list.append(return_dict["effective_cache_size"])
                    OTHER_param_list.append(return_dict["random_page_cost"])

                    """
                    print("�ж�ƿ��ΪOTHER,�޸���Ӧ�Ĳ���")

                    for OTHER_param in mid_OTHER_list:
                        print("���в���{}����".format(OTHER_param))
                        if OTHER_param == "random_page_cost":
                            param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_rat(param_dict["random_page_cost"], param_dict,
                                                                                                                "random_page_cost", param_dict_list, str_bottleneck,
                                                                                                                1, 80, 2, mid_value)

                        elif OTHER_param == "effective_cache_size":
                            param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_dif(param_dict["effective_cache_size"], param_dict,
                                                                                                                "effective_cache_size", param_dict_list, str_bottleneck,
                                                                                                                500, 6000, 500, mid_value)
                            effective_cache_size_flag = True

                        elif OTHER_param == "deadlock_timeout":
                            param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_rat(param_dict["deadlock_timeout"], param_dict,
                                                                                                                "deadlock_timeout", param_dict_list, str_bottleneck,
                                                                                                                100, 10000, 2, mid_value)

                        elif OTHER_param == "lock_timeout":
                            if param_dict["lock_timeout"] != 0:
                                param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_rat(param_dict["lock_timeout"], param_dict,
                                                                                                                    "lock_timeout", param_dict_list, str_bottleneck,
                                                                                                                    1, 120000, 2, mid_value)
                                mid_lock_timeout = param_dict["lock_timeout"]
                                param_dict["lock_timeout"] = 0
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    str_bottleneck = analysis_bottleneck()
                                    mid_value = analysis_show_global_status(status_path) / 1024 / 1024
                                else:
                                    param_dict["lock_timeout"] = mid_lock_timeout

                            else:
                                # ����״̬��ֵ
                                mid_str_bottleneck = copy.deepcopy(str_bottleneck)
                                mid_mid_value = copy.deepcopy(mid_value)
                                mid_param_dict = copy.deepcopy(param_dict)
                                param_dict["lock_timeout"] = 20000
                                param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_valie_tuning_rat_plus(param_dict["lock_timeout"], param_dict,
                                                                                                                         "lock_timeout", param_dict_list,
                                                                                                                         str_bottleneck,
                                                                                                                         1, 120000, 2, mid_value)
                                if param_dict["throught"] < mid_param_dict["throught"]:
                                    param_dict = mid_param_dict
                                    mid_value = mid_mid_value
                                    str_bottleneck = mid_str_bottleneck
                        elif OTHER_param == "enable_seqscan":
                            if param_dict["enable_seqscan"] == "on":
                                param_dict["enable_seqscan"] = "off"
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    str_bottleneck = analysis_bottleneck()
                                    mid_value = analysis_show_global_status(status_path) / 1024 / 1024
                                else:
                                    param_dict["enable_seqscan"] = "on"
                            elif param_dict["enable_seqscan"] == "off":
                                param_dict["enable_seqscan"] = "on"
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    str_bottleneck = analysis_bottleneck()
                                    mid_value = analysis_show_global_status(status_path) / 1024 / 1024
                                else:
                                    param_dict["enable_seqscan"] = "off"
                        elif OTHER_param == "default_statistics_target":
                            param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_rat(param_dict["default_statistics_target"], param_dict,
                                                                                                                "default_statistics_target", param_dict_list, str_bottleneck,
                                                                                                                10, 1000, 2, mid_value)
                        elif OTHER_param == "vacuum_cost_page_miss":
                            param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_rat(param_dict["vacuum_cost_page_miss"], param_dict,
                                                                                                                "vacuum_cost_page_miss", param_dict_list, str_bottleneck,
                                                                                                                1, 200, 2, mid_value)
                        elif OTHER_param == "vacuum_cost_page_dirty":
                            param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_rat(param_dict["vacuum_cost_page_dirty"], param_dict,
                                                                                                                "vacuum_cost_page_dirty", param_dict_list, str_bottleneck,
                                                                                                                1, 400, 2, mid_value)

                        # ����ѭ��
                        break

                    print("��ǰ��õĲ���ѡ��")
                    for i_param_dict in param_dict:
                        print(i_param_dict, param_dict[i_param_dict])
                    print(mid_OTHER_list)
                    mid_OTHER_list = mid_OTHER_list[1:]
                    print(mid_OTHER_list)
                    if len(mid_OTHER_list) == 0:
                        flag_param_OTHER = "end"

                # ������һ�ε���
                elif is_bottleneck == "end":
                    if max_iter_value < param_dict["throught"]:
                        max_iter_value = param_dict["throught"]
                        flag_param_IO = "start"
                        flag_param_OTHER = "start"
                        flag_param_CPU = "start"
                        mid_CPU_list = copy.deepcopy(CPU_param_list)
                        mid_IO_list = copy.deepcopy(IO_param_list)
                        mid_OTHER_list = copy.deepcopy(OTHER_param_list)
                    else:
                        print(time.time() - start_now_time - mysql_sum_time)
                        break

            # ���log_buffer��ƿ��������������log_buffer����
            else:
                print("����wal_buffer�ж�!!!!!!!!!!!!!!!")
                mid_value = min(int(math.ceil(mid_value * 1.5)), 96)
                diff_value = param_dict["wal_buffers"] - mid_value
                param_dict["wal_buffers"] = mid_value
                rate_value = param_dict["effective_cache_size"] / param_dict["shared_buffers"]
                param_dict["shared_buffers"] = param_dict["shared_buffers"] + diff_value
                if effective_cache_size_flag is True:
                    param_dict["effective_cache_size"] = min(int(rate_value * param_dict["shared_buffers"]), 6000)

                now_time = time.time()
                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                mysql_sum_time = mysql_sum_time + time.time() - now_time
                param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                mid_value = analysis_show_global_status(status_path) / 1024 / 1024
                str_bottleneck = analysis_bottleneck()

        # ���е���
        i = i + 1
        print("i is {}".format(i))