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

# ����ȫ�ֲ���
cpu_num_all = int(os.popen("cat /proc/cpuinfo| grep 'processor'| wc -l").readlines()[0].replace("\n", ''))
cnt = 0
tune_param = {}
num_table = 9


# ���ۼ����б�ת��������б�
def tranfer_status(result_list):
    result_list_1 = []
    length = len(result_list)
    for i in range(1, length):
        result_list_1.append(result_list[i] - result_list[i - 1])
    return result_list_1


# ��ȡ���ȴ��Ĵ���
def param_lock_row_num(dict_show_global_status, engine_status_dict):
    lock_num_status = dict_show_global_status["Innodb_row_lock_current_waits"]
    max_lock_num = 0
    for i in lock_num_status:
        max_lock_num = max(i, max_lock_num)
    lock_num_dict = engine_status_dict["transactions"]
    for i in lock_num_dict:
        max_lock_num = max(max_lock_num, i["lock_wait_num"])

    return max_lock_num


# ��ȡ����ƽ��ֵ�����ֵ
def param_lock_row_time(dict_show_global_status):
    avg_time = dict_show_global_status["Innodb_row_lock_time_avg"]
    max_time = dict_show_global_status["Innodb_row_lock_time_max"]

    avg_time = avg_time[len(avg_time) - 1]
    max_time = max_time[len(max_time) - 1]

    return avg_time, max_time


# �ж�log_buffer �Ƿ���ƿ��
def status_estimate(dict_show_global_status):
    # �ж�log buffer���ڴ��Ƿ�ƫС,
    innodb_log_waits_list = tranfer_status(dict_show_global_status["Innodb_log_waits"])
    sum_innodb_log_wait = 0
    for ii in innodb_log_waits_list:
        sum_innodb_log_wait = sum_innodb_log_wait + int(ii)
    print("��־�ȴ�����")
    print(dict_show_global_status["Innodb_log_waits"])

    # ��¼����Ԥ����ҳ��
    sum_innodb_buffer_pool_read_ahead = 0
    innodb_buffer_pool_read_ahead_list = tranfer_status(dict_show_global_status["Innodb_buffer_pool_read_ahead"])
    for ii in innodb_buffer_pool_read_ahead_list:
        sum_innodb_buffer_pool_read_ahead = sum_innodb_buffer_pool_read_ahead + int(ii)
    print("����Ԥ������")
    print(dict_show_global_status["Innodb_buffer_pool_read_ahead"])

    # ��¼���Ԥ����ҳ��
    sum_innodb_buffer_pool_read_ahead_rnd = 0
    innodb_buffer_pool_read_ahead_rnd_list = tranfer_status(dict_show_global_status["Innodb_buffer_pool_read_ahead_rnd"])
    for ii in innodb_buffer_pool_read_ahead_rnd_list:
        sum_innodb_buffer_pool_read_ahead_rnd = sum_innodb_buffer_pool_read_ahead_rnd + int(ii)
    print("���Ԥ������")
    print(dict_show_global_status["Innodb_buffer_pool_read_ahead_rnd"])

    # ��¼û��Ԥ������ʧ��ҳ��
    sum_innodb_buffer_pool_read_ahead_evicted = 0
    innodb_buffer_pool_read_ahead_evicted_list = tranfer_status(dict_show_global_status["Innodb_buffer_pool_read_ahead_evicted"])
    for ii in innodb_buffer_pool_read_ahead_evicted_list:
        sum_innodb_buffer_pool_read_ahead_evicted = sum_innodb_buffer_pool_read_ahead_evicted + int(ii)
    print("û��Ԥ������ʧ�Ĵ���")
    print(dict_show_global_status["Innodb_buffer_pool_read_ahead_evicted"])

    # ��¼�ڴ�������
    # (1)�߼���ȡ�Ĵ���
    sum_innodb_buffer_pool_read_requests = 0
    innodb_buffer_pool_read_requests_list = tranfer_status(dict_show_global_status["Innodb_buffer_pool_read_requests"])
    for ii in innodb_buffer_pool_read_requests_list:
        sum_innodb_buffer_pool_read_requests = sum_innodb_buffer_pool_read_requests + int(ii)
    print("�߼�������")
    print(dict_show_global_status["Innodb_buffer_pool_read_requests"])
    # (2)�����ȡ�Ĵ���
    sum_innodb_buffer_pool_reads = 0
    innodb_buffer_pool_reads_list = tranfer_status(dict_show_global_status["Innodb_buffer_pool_reads"])
    for ii in innodb_buffer_pool_reads_list:
        sum_innodb_buffer_pool_reads = sum_innodb_buffer_pool_reads + int(ii)
    print("���������")
    print(dict_show_global_status["Innodb_buffer_pool_reads"])

    # ������ؽ��
    return sum_innodb_log_wait, sum_innodb_buffer_pool_read_ahead_rnd, sum_innodb_buffer_pool_read_ahead_evicted, \
           sum_innodb_buffer_pool_reads / sum_innodb_buffer_pool_read_requests


# ��ȡ��һ�εĲ���ֵ
def read_tunning_process(i):
    # ��¼���ؽ��
    param_dict = {}

    # �ж��Ƿ���ж�ȡ
    flag = False

    # ����ƥ����ַ�
    start_i = "start_" + str(i - 1)

    # �������ݵĶ�ȡ
    with open(tunning_process_path, 'r') as f:
        for i_con in f.readlines():
            i_con = i_con.replace("\n", '')
            if start_i in i_con:
                flag = True
            if flag is True:
                if "start_" in i_con:
                    continue
                if "end_" in i_con:
                    break

                # ���и�ʽ�ķָ�
                i_con = i_con.split("=")
                if i_con[0] == "innodb_flush_method":
                    param_dict[i_con[0]] = i_con[1]
                elif i_con[0] == "throught":
                    param_dict[i_con[0]] = float(i_con[1])
                elif i_con[0] == "param":
                    param_dict[i_con[0]] = i_con[1]
                else:
                    i_con[1] = i_con[1].replace("M", '')
                    param_dict[i_con[0]] = int(i_con[1])

    return param_dict


"""
 # �����е����ݿ���з����� �Ի�ø��õ�Ч��
 �ڴ�����̲����645
 # ��Ҫ����ָ����е��Σ����ε����ȼ�����˳����io, �ڴ棬 ���� �߳�
# ���������ȼ��������£�
# 0, innodb_flush_neighbors
# 1��innodb_read_ahead_threshold
# 2��innodb_random_read_ahead
# 3��innodb_adaptive_hash_index
# 4��innodb_log_buffer_size
# 5��innodb_adaptive_hash_index
# 6��innodb_adaptive_hash_index_parts
# 7��innodb_buffer_pool_instances
# 8��innodb_read_io_threads
# 9��innodb_write_io_threads
# 10, innodb_log_writer_threads
"""


# ����engine�Ĺ������
def engine_estimate(engine_status_dict):
    # ��¼�����б�
    return_dict = {}

    # file io��ȡ��ص���Ϣ�б�
    file_io_pending_normal_aio_reads_list = []
    file_io_pending_normal_aio_writes_list = []
    pending_ibuf_aio_reads_list = []
    pending_sync_io_list = []
    pending_log_io_list = []
    pending_flushes_log_list = []
    pending_buffer_pool_list = []
    pending_preads_list = []
    pending_pwrites_list = []
    for ii in engine_status_dict["file_io"]:
        if ii.get("Pending_normal_aio_reads", None) is not None:
            file_io_pending_normal_aio_reads_list.append(ii["Pending_normal_aio_reads"])
        else:
            file_io_pending_normal_aio_reads_list.append(0)
        if ii.get("Pending_normal_aio_writes", None) is not None:
            file_io_pending_normal_aio_writes_list.append(ii["Pending_normal_aio_writes"])
        else:
            file_io_pending_normal_aio_writes_list.append(0)
        if ii.get("ibuf_aio_reads", None) is not None:
            pending_ibuf_aio_reads_list.append(ii["ibuf_aio_reads"])
        else:
            pending_ibuf_aio_reads_list.append(0)
        if ii.get("log_i/o's", None) is not None:
            pending_log_io_list.append(ii["log_i/o's"])
        else:
            pending_log_io_list.append(0)
        if ii.get("sync_i/o's", None) is not None:
            pending_sync_io_list.append(ii["sync_i/o's"])
        else:
            pending_sync_io_list.append(0)
        if ii.get("Pending_flushes_(fsync)_log", None) is not None:
            pending_flushes_log_list.append(ii["Pending_flushes_(fsync)_log"])
        else:
            pending_flushes_log_list.append(0)
        if ii.get("buffer_pool", None) is not None:
            pending_buffer_pool_list.append(ii["buffer_pool"])
        else:
            pending_buffer_pool_list.append(0)
        if ii.get("pending_preads", None) is not None:
            pending_preads_list.append(ii["pending_preads"])
        else:
            pending_preads_list.append(0)
        if ii.get("pending_pwrites", None) is not None:
            pending_pwrites_list.append(ii["pending_pwrites"])
        else:
            pending_pwrites_list.append(0)

    # semaphores��ȡ��ص���Ϣ�б�
    semaphores_buf0buf_list = []
    semaphores_btr0sea_list = []
    semaphores_dict0dict_list = []
    reservation_count = []
    signal_count = []
    for ii in engine_status_dict["semaphores"]:
        if ii.get("buf0buf", None) is not None:
            semaphores_buf0buf_list.append(ii["buf0buf"])
        else:
            semaphores_buf0buf_list.append(0)
        if ii.get("btr0sea", None) is not None:
            semaphores_btr0sea_list.append(ii["btr0sea"])
        else:
            semaphores_btr0sea_list.append(0)
        if ii.get("dict0dict", None) is not None:
            semaphores_dict0dict_list.append(ii["dict0dict"])
        else:
            semaphores_dict0dict_list.append(0)
        if ii.get("signal_count", None) is not None:
            signal_count.append(ii["signal_count"])
        else:
            signal_count.append(0)
        if ii.get("reservation_count", None) is not None:
            reservation_count.append(ii["reservation_count"])
        else:
            reservation_count.append(0)

    # ��buffer pool ���������Ϣ����
    buffer_pool_pending_read_list = []
    buffer_pool_pending_write_list_lru = []
    buffer_pool_pending_write_list_flush_list = []
    buffer_pool_pending_write_list_single_page = []
    pages_made_young_list = []
    pages_read = []
    pages_create = []
    pages_write = []
    buffer_pool_page_ahead = []
    buffer_pool_page_evicted_without_access = []
    buffer_pool_random_read_ahead = []
    for ii in engine_status_dict["buffer_pool"]:
        if ii.get("Pending reads", None) is not None:
            buffer_pool_pending_read_list.append(ii["Pending reads"])
        else:
            buffer_pool_pending_read_list.append(0)
        if ii.get("LRU", None) is not None:
            buffer_pool_pending_write_list_lru.append(ii["LRU"])
        else:
            buffer_pool_pending_write_list_lru.append(0)
        if ii.get("flush_list", None) is not None:
            buffer_pool_pending_write_list_flush_list.append(ii["flush_list"])
        else:
            buffer_pool_pending_write_list_flush_list.append(0)
        if ii.get("single_page", None) is not None:
            buffer_pool_pending_write_list_single_page.append(ii["single_page"])
        else:
            buffer_pool_pending_write_list_single_page.append(0)
        if ii.get("Pages_made_young", None) is not None:
            pages_made_young_list.append(ii["Pages_made_young"])
        else:
            pages_made_young_list.append(0)
        if ii.get("Pages_read", None) is not None:
            pages_read.append(ii["Pages_read"])
        else:
            pages_read.append(0)
        if ii.get("created", None) is not None:
            pages_create.append(ii["created"])
        else:
            pages_create.append(ii["created"])
        if ii.get("", None) is not None:
            pages_write.append(ii["written"])
        else:
            pages_write.append(0)
        if ii.get("read_ahead", None) is not None:
            buffer_pool_page_ahead.append(ii["read_ahead"])
        else:
            buffer_pool_page_ahead.append(0)
        if ii.get("evicted_without_access", None) is not None:
            buffer_pool_page_evicted_without_access.append(ii["evicted_without_access"])
        else:
            buffer_pool_page_evicted_without_access.append(0)
        if ii.get("random_read_ahead", None) is not None:
            buffer_pool_random_read_ahead.append(ii["random_read_ahead"])
        else:
            buffer_pool_random_read_ahead.append(0)

    # ��INSERT BUFFER AND ADAPTIVE HASH INDEX������Ϣ��ȡ
    insert_AHI_ibuf_size_list = []
    insert_AHI_free_list_len_list = []
    insert_AHI_seg_size_list = []
    insert_AHI_merges_list = []
    hash_table_size_list = []
    node_heap_list = []
    insert_AHI_hash_search_list = []
    insert_AHI_no_hash_search_list = []
    for ii in engine_status_dict["insert_AHI"]:
        if ii.get("Ibuf_size", None) is not None:
            insert_AHI_ibuf_size_list.append(ii["Ibuf_size"])
        else:
            insert_AHI_ibuf_size_list.append(0)
        if ii.get("free_list_len", None) is not None:
            insert_AHI_free_list_len_list.append(ii["free_list_len"])
        else:
            insert_AHI_free_list_len_list.append(0)
        if ii.get("seg_size", None) is not None:
            insert_AHI_seg_size_list.append(ii["seg_size"])
        else:
            insert_AHI_seg_size_list.append(0)
        if ii.get("hash_searches/s", None) is not None:
            insert_AHI_hash_search_list.append(ii["hash_searches/s"])
        else:
            insert_AHI_hash_search_list.append(0)
        if ii.get("non-hash_searches/s", None) is not None:
            insert_AHI_no_hash_search_list.append(ii["non-hash_searches/s"])
        else:
            insert_AHI_no_hash_search_list.append(0)
        if ii.get("merges", None) is not None:
            insert_AHI_merges_list.append(ii["merges"])
        else:
            insert_AHI_merges_list.append(0)
        if ii.get("hash_table_size", None) is not None:
            hash_table_size_list.append(ii["hash_table_size"])
        else:
            hash_table_size_list.append(0)
        if ii.get("node_heap", None) is not None:
            node_heap_list.append(ii["node_heap"])
        else:
            node_heap_list.append(0)

    # ��transaction���з���
    transaction_lock_wait_sum_list = []
    for ii in engine_status_dict["transactions"]:
        if ii.get("lock_wait_sum", None) is not None:
            transaction_lock_wait_sum_list.append(ii["lock_wait_sum"])
        else:
            transaction_lock_wait_sum_list.append(0)

    # ������ض�д�߳�
    print("���̵߳ĵȴ�����")
    mid = 0
    print(file_io_pending_normal_aio_reads_list)
    for ii in file_io_pending_normal_aio_reads_list:
        for iii in ii:
            mid = mid + int(iii)
    print(mid)
    return_dict["innodb_read_io_threads"] = mid
    print("д�̵߳ȴ�����")
    mid = 0
    print(file_io_pending_normal_aio_writes_list)
    for ii in file_io_pending_normal_aio_writes_list:
        for iii in ii:
            mid = mid + int(iii)
    print(mid)
    return_dict["innodb_write_io_threads"] = mid
    # �ж�buffer�ķ�������
    print("�ж�����صķ���")
    mid = 0
    for ii in semaphores_buf0buf_list:
        mid = mid + int(ii)
    print(mid)
    return_dict["innodb_buffer_pool_instances"] = mid

    # �ж�����AHI
    print("dict0dict")
    mid1 = 0
    for ii in semaphores_dict0dict_list:
        mid1 = mid1 + int(ii)
    print(mid1)
    print("btr0sea")
    mid2 = 0
    for ii in semaphores_btr0sea_list:
        mid2 = mid2 + int(ii)
    print(mid2)
    return_dict["innodb_adaptive_hash_2"] = [mid1, mid2]

    print("AHI����")
    mid1 = 0.0
    for ii in insert_AHI_hash_search_list:
        mid1 = mid1 + float(ii)
    print(mid1)
    print("��AHI����")
    mid2 = 0.0
    for ii in insert_AHI_hash_search_list:
        mid2 = mid1 + float(ii)
    print(mid2)
    return_dict["innodb_adaptive_hash_2"] = [mid1, mid2]

    # �ж�Ԥ��������
    print("�ж�����Ԥ��")
    mid1 = 0
    for ii in buffer_pool_page_ahead:
        mid1 = mid1 + int(ii)
    print(mid1)
    print("�ж����Ԥ��")
    mid2 = 0
    for ii in buffer_pool_random_read_ahead:
        mid = mid2 + int(ii)
    print(mid2)
    print("�ж�δԤ����ҳ��")
    mid3 = 0
    for ii in buffer_pool_page_evicted_without_access:
        mid3 = mid3 + int(ii)
    print(mid3)
    return_dict["innodb_read_ahead"] = [mid1, mid2, mid3]

    return return_dict


# ����ʵ������
def param_innodb_buffer_pool_instance():
    # ��¼��������
    sum = 0
    for i in engine_status_dict["semaphores"]:
        sum = sum + i["buf0buf"]
    return sum


# ����log_buffer�Ĵ�С
def param_innodb_log_buffer_size():
    length = len(dict_show_global_status["Innodb_log_waits"]) - 1
    sum = dict_show_global_status["Innodb_log_waits"][length] - dict_show_global_status["Innodb_log_waits"][0]
    return sum


def log_buffer():
    max_value = 0
    for i_log in engine_status_dict["LOG"]:
        max_value = max(max_value, (i_log["Log sequence number"] - i_log["Log flushed up to"]) / 1024 / 1024)

    return max_value


# �޸�change_buffer�Ĵ�С
def param_innodb_change_buffer():
    free_list = []
    size_list = []
    merge_list = []
    merge_op_list = []
    merge_dis_list = []
    seg_size = -1
    for i in engine_status_dict["insert_AHI"]:
        free_list.append(i["free_list_len"])
        size_list.append(i["seg_size"])
        merge_list.append(i["merges"])
        merge_op_list.append(i["merged_operations"])
        merge_dis_list.append(i["discarded_operations"])
    for i in size_list:
        seg_size = max(i, seg_size)

    max_size = seg_size
    for i in free_list:
        max_size = min(i, max_size)
    return max_size, seg_size, merge_list[len(merge_list) - 1] - merge_list[0], merge_op_list[len(merge_op_list) - 1] + merge_dis_list[len(merge_dis_list) - 1] - merge_op_list[0] - \
           merge_dis_list[0]


# �Ե����жϵ�ָ��,��ü�����������˳�����iops��33����ͨ��fio���������˳����ó�������33��,ͬʱ���������������ж�
def param_innodb_read_ahead_threshold(mid_dict_show_global_status):
    # ����num����ֵ
    num = 0
    read_ahead = mid_dict_show_global_status["Innodb_buffer_pool_read_ahead"]
    read_ahead_evicted = mid_dict_show_global_status["Innodb_buffer_pool_read_ahead_evicted"]
    read_ahead = tranfer_status(read_ahead)
    read_ahead_evicted = tranfer_status(read_ahead_evicted)

    # ��ȡ��ֵ
    sum_read_ahead = 0
    sum_read_ahead_evicted = 0

    # �����Ƿ�����Ԥ���ж�
    for i in read_ahead[num:]:
        sum_read_ahead = sum_read_ahead + i
    for i in read_ahead_evicted[num:]:
        sum_read_ahead_evicted = sum_read_ahead_evicted + i

    sum_read_ahead_used = sum_read_ahead - sum_read_ahead_evicted

    return sum_read_ahead


# �Ե����жϵ�ָ��,��ü�����������˳�����iops��33����ͨ��fio���������˳����ó�������33��,�������ȶ���һ�㲻����
def param_innodb_random_read_ahead():
    # ����num����ֵ
    num = 7
    read_ahead_rnd = dict_show_global_status["Innodb_buffer_pool_read_ahead_rnd"]
    read_ahead_evicted = dict_show_global_status["Innodb_buffer_pool_read_ahead_evicted"]
    read_ahead_rnd = tranfer_status(read_ahead_rnd)
    read_ahead_evicted = tranfer_status(read_ahead_evicted)

    print(read_ahead_rnd)
    print(read_ahead_evicted)

    # ��ȡ��ֵ
    sum_read_ahead_rnd = 0
    sum_read_ahead_evicted = 0

    # �����Ƿ����Ԥ���ж�
    for i in read_ahead_rnd[num:]:
        sum_read_ahead_rnd = sum_read_ahead_rnd + i
    for i in read_ahead_evicted[num:]:
        sum_read_ahead_evicted = sum_read_ahead_evicted + i

    print(sum_read_ahead_rnd, sum_read_ahead_evicted)
    if sum_read_ahead_rnd == 0 or sum_read_ahead_rnd == sum_read_ahead_evicted:
        print("����������Ԥ��")
        return False
    elif sum_read_ahead_evicted / (sum_read_ahead_rnd - sum_read_ahead_evicted) < 33:
        print("��������Ԥ��")
        return True
    else:
        print("����������Ԥ��")
        return False


# �Բ���hash_index���е���
def param_hash_index():
    # ��������
    sum_btr0sea = 0
    for i in engine_status_dict["semaphores"]:
        sum_btr0sea = sum_btr0sea + i["btr0sea"]

    # hash_index�����ͳ��
    sum_hash = 0
    sum_no_hash = 0
    for i in engine_status_dict["insert_AHI"]:
        sum_hash = sum_hash + i["hash_searches/s"]
        sum_no_hash = sum_no_hash + i["non-hash_searches/s"]
    return sum_btr0sea, sum_hash, sum_no_hash


# ���ж�дio�̵߳�����,Ŀ���Ǳ���io�ܺ͵����߼�cpu��������Ҫ�ο�����ָ�꣬Ϊ�Ժ��ж�
def param_read_and_write_io_thread():
    # ��¼engine�Ķ�д����
    engine_length = len(engine_status_dict["buffer_pool"]) - 1
    engine_read = engine_status_dict["buffer_pool"][engine_length]["Pages_read"] - engine_status_dict["buffer_pool"][0]["Pages_read"]
    engine_write = engine_status_dict["buffer_pool"][engine_length]["written"] - engine_status_dict["buffer_pool"][0]["written"]

    # ��¼status�Ķ�д����
    status_length = len(dict_show_global_status["Innodb_dblwr_writes"]) - 1
    status_write = dict_show_global_status["Innodb_buffer_pool_pages_flushed"][status_length] - dict_show_global_status["Innodb_buffer_pool_pages_flushed"][0]
    status_write = status_write + dict_show_global_status["Innodb_dblwr_writes"][status_length] - dict_show_global_status["Innodb_dblwr_writes"][0]
    status_read = dict_show_global_status["Innodb_buffer_pool_reads"][status_length] - dict_show_global_status["Innodb_buffer_pool_reads"][0]

    return [(status_read, status_write), (engine_read, engine_write)]


# ������Ҫ�����Ĳ���
def def_tune_param():
    # ��Ҫ�����Ĳ�������Ϊ1������Ҫ�����Ĳ�������Ϊ0
    global tune_param
    # ��ʼ������ 14��
    tune_param["innodb_thread_concurrency"] = 1
    tune_param["innodb_log_file_size"] = 1
    tune_param["innodb_buffer_pool_size"] = 1
    tune_param["innodb_buffer_pool_instances"] = 1
    tune_param["innodb_read_io_threads"] = 1
    tune_param["innodb_write_io_threads"] = 1
    tune_param["innodb_io_capacity"] = 1
    tune_param["innodb_io_capacity_max"] = 1
    tune_param["innodb_flush_neighbors"] = 1
    tune_param["innodb_flush_method"] = 1
    tune_param["innodb_page_cleaners"] = 1
    tune_param["innodb_purge_threads"] = 1
    tune_param["innodb_log_files_in_group"] = 1
    tune_param["innodb_random_read_ahead"] = 1

    # ָ����ز���
    tune_param["innodb_log_buffer_size"] = 1
    # cpu��ز��� 4�� + (����4����ʼ������)
    tune_param["innodb_sync_spin_loops"] = 1
    tune_param["innodb_concurrency_tickets"] = 1
    tune_param["innodb_log_wait_for_flush_spin_hwm"] = 1
    tune_param["innodb_log_writer_threads"] = 1
    # io��ز��� 6�� + (1����ʼ���� 1���ص�)
    tune_param["innodb_extend_and_initialize"] = 1
    tune_param["innodb_adaptive_hash_index"] = 1
    tune_param["innodb_adaptive_hash_index_parts"] = 1
    tune_param["innodb_change_buffer_max_size"] = 1
    tune_param["innodb_lru_scan_depth"] = 1
    tune_param["innodb_read_ahead_threshold"] = 1
    tune_param["innodb_use_fdatasync"] = 1

    # ������� 3�� + (1���ص�)
    tune_param["innodb_sync_array_size"] = 1
    tune_param["innodb_deadlock_detect"] = 1
    tune_param["innodb_lock_wait_timeout"] = 1


# ��ʼ������
def initialization_parameters():
    """
    1�� ���в�����ʼ������ʼ���Ĳ�������
    (1)innodb_thread_concurrency = cpu�߼�����*2
    (2)innodb_log_file_size = ���õ������̿ռ�
    (3��innodb_log_files_in_group Ĭ��Ϊ2
    (4)innodb_buffer_pool_size = �����õ��ڴ�
    (5)innodb_buffer_pool_instances = math.ceil(innodb_buffer_pool_size/1024)
    (6)innodb_read_io_threads = Ĭ��cpu�߼��������Ժ������ض�����*cpu�߼�����/2
    (7)innodb_write_io_threads = Ĭ��cpu�߼��������Ժ�������д����*cpu�߼�����/2
    (8)innodb_io_capacity = �������iops��50%
    (9)innodb_io_capacity_max = �������iops
    (10)innodb_flush_neighbors = 0 (���iops��˳��iops���) ����ѡ����������̽��
    (11)innodb_flush_method = һ��ѡ��fsync�� �������iops��˳��iops���,��ѡ��O_DSYNC
    (12)innodb_page_cleaners = min(���ڷ�����, 4)
    (13)innodb_purge_threads = min�����������4��
	(14��innodb_random_read_ahead Ĭ�Ϲر�
	(innodb_log_buffer_size = Ĭ��ֵ)
    2�� �趨���в���ΪϵͳĬ��ֵ��
    2.1 cpu���
    (1)innodb_sync_spin_loops
    (2)innodb_concurrency_tickets���������С�йأ�
    (3)innodb_log_wait_for_flush_spin_hwm���û��߳���־ƽ��ˢ�µ�spin������ޣ�
    (4)innodb_log_writer_threads��io��
    (5)innodb_read_io_threads = Ĭ��cpu�߼��������Ժ������ض�����*cpu�߼�����/2
    (6)innodb_write_io_threads = Ĭ��cpu�߼��������Ժ�������д����*cpu�߼�����/2
    (7)innodb_page_cleaners
    (8)innodb_purge_threads
    2.2 io���
    (1)innodb_adaptive_hash_index��ռ���ڴ棩
    (2)innodb_adaptive_hash_index_parts�������̵߳���������
    (3)innodb_change_buffer_max_size���Ż�����io���Ƿ��ж������������Լ����
    (4)innodb_read_ahead_threshold
    innodb_flushing_avg_loops(����ˢ������)�ò�������
    (5)innodb_lru_scan_depth��io��
    (6)innodb_log_writer_threads��io��
    (7)innodb_io_capacity = �������iops��50%
    (8)innodb_io_capacity_max = �������iops
    (9)innodb_flush_neighbors(����io)
    (10)innodb_extend_and_initialize = 0 ����ռ䲻дnullֵ
    2.3�������
    (1)innodb_sync_array_size(����cpu������768�ȴ���̽��)
    (2)innodb_deadlock_detect ���Ƿ����������⣩
    (3)innodb_lock_wait_timeout�������ĳ�ʱʱ�䣩
    (4)innodb_buffer_pool_instances(�����̵߳�������)��ָ��
    (5)innodb_adaptive_hash_index_parts
    """
    # innodb_thread_concurrency, innodb_buffer_pool_size, innodb_buffer_pool_size����һ��������

    # ���巵���б�
    return_dict = {}

    global cpu_num_all
    cpu_num = cpu_num_all
    global tune_param
    # 1����ʼ������innodb_thread_concurrency
    if tune_param["innodb_thread_concurrency"] == 1:
        return_dict["innodb_thread_concurrency"] = cpu_num * 2

    # 2����ʼ������innodb_log_file_size
    if tune_param["innodb_log_file_size"] == 1:
        innodb_log_file_size = math.floor(disk_resource / 2)
        return_dict["innodb_log_file_size"] = innodb_log_file_size

    # 3����ʼ������innodb_log_files_in_group
    if tune_param["innodb_log_files_in_group"] == 1:
        return_dict["innodb_log_files_in_group"] = 2

    # 4��5��ʼ��������innodb_buffer_pool_size�� innodb_buffer_pool_instances
    if tune_param["innodb_buffer_pool_size"] == 1 and tune_param["innodb_buffer_pool_instances"] == 1:
        innodb_buffer_pool_size = memory_resource
        innodb_buffer_pool_instances = min(64, math.ceil(innodb_buffer_pool_size / 1024))
        per_size = math.floor(innodb_buffer_pool_size / innodb_buffer_pool_instances)
        innodb_buffer_pool_chunk_size = per_size
        innodb_buffer_pool_size = innodb_buffer_pool_chunk_size * innodb_buffer_pool_instances
        return_dict["innodb_buffer_pool_size"] = innodb_buffer_pool_size
        return_dict["innodb_buffer_pool_instances"] = innodb_buffer_pool_instances
        return_dict["innodb_buffer_pool_chunk_size"] = innodb_buffer_pool_chunk_size

    # 6��ʼ������innodb_read_io_threads
    if tune_param["innodb_read_io_threads"] == 1:
        return_dict["innodb_read_io_threads"] = int(cpu_num / 2)

    # 7��ʼ������innodb_write_io_threads
    if tune_param["innodb_write_io_threads"] == 1:
        return_dict["innodb_write_io_threads"] = int(cpu_num / 2)

    # 8��9��ʼ������innodb_io_capacity�� innodb_io_capacity_max
    if tune_param["innodb_io_capacity"] == 1 and tune_param["innodb_io_capacity_max"] == 1:
        return_dict["innodb_io_capacity"] = 2700  # ����fio���Կɵ�
        return_dict["innodb_io_capacity_max"] = 5400  # ����fio���Կɵ�

    # 10��ʼ������innodb_flush_neighbors���������iops��˳��iops
    if tune_param["innodb_flush_neighbors"] == 1:
        return_dict["innodb_flush_neighbors"] = 0

    # 11��ʼ������innodb_flush_method, �������iops��˳��iops
    if tune_param["innodb_flush_method"] == 1:
        return_dict["innodb_flush_method"] = "fsync"  # ��ѯ���̲����ɵ�

    # 12����ʼ������innodb_page_cleaners
    if tune_param["innodb_page_cleaners"] == 1:
        return_dict["innodb_page_cleaners"] = min(return_dict["innodb_buffer_pool_instances"], 4)

    # 13����ʼ������innodb_purge_threads
    if tune_param["innodb_purge_threads"] == 1:
        return_dict["innodb_purge_threads"] = min(4, num_table)

    # 14���޸Ĳ���innodb_random_read_ahead
    if tune_param["innodb_random_read_ahead"] == 1:
        return_dict["innodb_random_read_ahead"] = 0

    # 15 �޸Ĳ���innodb_log_buffer_size
    if tune_param["innodb_log_buffer_size"] == 1:
        return_dict["innodb_log_buffer_size"] = 16

    # 16 �޸Ĳ���innodb_use_fdatasync
    if tune_param["innodb_use_fdatasync"] == 1:
        return_dict["innodb_use_fdatasync"] = 1

    # �趨���в���Ϊinnodb��Ĭ��ֵ,������ʽ��д�����Ա��ڲ鿴
    # cpu ��ز���
    """
    (1)innodb_thread_concurrency(̽��)
    (2)innodb_sync_spin_loops
    (3)innodb_concurrency_tickets���������С�йأ�
    (4)innodb_log_wait_for_flush_spin_hwm���û��߳���־ƽ��ˢ�µ�spin������ޣ�
    (5)innodb_log_writer_threads��io��
    (6)innodb_page_cleaners���Ѿ���ʼ����
    (7)innodb_purge_threads���Ѿ���ʼ����
    ������������һ��
    (7)innodb_read_io_threads = Ĭ��cpu�߼��������Ժ������ض�����*cpu�߼�����/2���Ѿ���ʼ����
    (8)innodb_write_io_threads = Ĭ��cpu�߼��������Ժ�������д����*cpu�߼�����/2���Ѿ���ʼ����

    """
    return_dict["innodb_sync_spin_loops"] = 30
    return_dict["innodb_concurrency_tickets"] = 5000
    return_dict["innodb_log_writer_threads"] = 1
    return_dict["innodb_log_wait_for_flush_spin_hwm"] = 400

    # �ѵ��ŵĲ���д�뼯��
    if tune_param["innodb_write_io_threads"] == 1:
        CPU_param_list.append("innodb_write_io_threads")
    if tune_param["innodb_read_io_threads"] == 1:
        CPU_param_list.append("innodb_read_io_threads")
    if tune_param["innodb_purge_threads"] == 1:
        CPU_param_list.append("innodb_purge_threads")
    if tune_param["innodb_page_cleaners"] == 1:
        CPU_param_list.append("innodb_page_cleaners")
    if tune_param["innodb_log_writer_threads"] == 1:
        CPU_param_list.append("innodb_log_writer_threads")
    if tune_param["innodb_log_wait_for_flush_spin_hwm"] == 1:
        CPU_param_list.append("innodb_log_wait_for_flush_spin_hwm")
    if tune_param["innodb_concurrency_tickets"] == 1:
        CPU_param_list.append("innodb_concurrency_tickets")
    if tune_param["innodb_sync_spin_loops"] == 1:
        CPU_param_list.append("innodb_sync_spin_loops")
    if tune_param["innodb_thread_concurrency"] == 1:
        CPU_param_list.append("innodb_thread_concurrency")

    # io��ز���
    """
    # ������������һ��
    (1)innodb_adaptive_hash_index��ռ���ڴ棩
    (2)innodb_adaptive_hash_index_parts�������̵߳���������

    (3)innodb_change_buffer_max_size���Ż�����io���Ƿ��ж������������Լ����
    (4)innodb_read_ahead_threshold
    innodb_flushing_avg_loops(����ˢ������)�ò�������
    (5)innodb_lru_scan_depth��io��
    (6)innodb_log_writer_threads��io��
    (7)innodb_io_capacity = �������iops��50%
    (8)innodb_io_capacity_max = �������iops
    (9)innodb_flush_neighbors(����io) (�Ѿ���ʼ��)
    (10)innodb_extend_and_initialize = 0 ����ռ䲻дnullֵ
    """
    return_dict["innodb_log_writer_threads"] = 1
    # �޸�Ĭ�ϲ���
    return_dict["innodb_read_ahead_threshold"] = 56
    return_dict["innodb_adaptive_hash_index"] = 1
    return_dict["innodb_change_buffer_max_size"] = 25
    return_dict["innodb_adaptive_hash_index_parts"] = 8
    return_dict["innodb_lru_scan_depth"] = 1024
    return_dict["innodb_extend_and_initialize"] = 1

    # �ѵ��ŵĲ���д�뼯��
    if tune_param["innodb_flush_method"] == 1:
        IO_param_list.append("innodb_flush_method")
    if tune_param["innodb_extend_and_initialize"] == 1:
        IO_param_list.append("innodb_extend_and_initialize")
    if tune_param["innodb_flush_neighbors"] == 1:
        IO_param_list.append("innodb_flush_neighbors")
    if tune_param["innodb_io_capacity_max"] == 1:
        IO_param_list.append("innodb_io_capacity_max")
    if tune_param["innodb_io_capacity"] == 1:
        IO_param_list.append("innodb_io_capacity")
    if tune_param["innodb_log_writer_threads"] == 1:
        IO_param_list.append("innodb_log_writer_threads")
    if tune_param["innodb_lru_scan_depth"] == 1:
        IO_param_list.append("innodb_lru_scan_depth")
    if tune_param["innodb_read_ahead_threshold"] == 1:
        IO_param_list.append("innodb_read_ahead_threshold")
    if tune_param["innodb_change_buffer_max_size"] == 1:
        IO_param_list.append("innodb_change_buffer_max_size")
    if tune_param["innodb_adaptive_hash_index"] == 1:
        IO_param_list.append("innodb_adaptive_hash_index")
    if tune_param["innodb_adaptive_hash_index_parts"] == 1:
        IO_param_list.append("innodb_adaptive_hash_index_parts")

    # ������ز���
    """
    (1)innodb_sync_array_size(����cpu������768�ȴ���̽��)
    # ������������һ��
    (2)innodb_deadlock_detect ���Ƿ����������⣩
    (3)innodb_lock_wait_timeout�������ĳ�ʱʱ�䣩
    (4)innodb_buffer_pool_instances(�����̵߳�������)��ָ��(�Ѿ���ʼ��)
    (5)innodb_adaptive_hash_index_parts
    """
    return_dict["innodb_sync_array_size"] = 1
    return_dict["innodb_deadlock_detect"] = 1
    return_dict["innodb_lock_wait_timeout"] = 50
    return_dict["innodb_adaptive_hash_index_parts"] = 8

    # �ѵ��ŵĲ���д�뼯��
    if tune_param["innodb_adaptive_hash_index_parts"] == 1:
        LATCH_param_list.append("innodb_adaptive_hash_index_parts")
    if tune_param["innodb_buffer_pool_instances"] == 1:
        LATCH_param_list.append("innodb_buffer_pool_instances")
    if tune_param["innodb_deadlock_detect"] == 1:
        LATCH_param_list.append("innodb_deadlock_detect")
    if tune_param["innodb_lock_wait_timeout"] == 1:
        LATCH_param_list.append("innodb_lock_wait_timeout")
    if tune_param["innodb_sync_array_size"] == 1:
        LATCH_param_list.append("innodb_sync_array_size")

    # ���ز����ֵ�
    return return_dict


# ��ȡ���ȹ������ص�������
def get_throught():
    # ���ñ���
    mid_throught = 0
    mid_latency = 0

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
    mid_throught = get_throught()
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


# ��¼�����м�ֵ̽���Ĳ���
def param_mid_value_tuning_2(value, param_dict, param, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck, diff_value, min=0, max=0):
    # ��¼�ò����Ƿ��һ��
    param_dict[param] = value
    global mysql_sum_time
    # ����״̬��ֵ
    mid_dict_show_global_status = dict_show_global_status
    mid_engine_status_dict = engine_status_dict
    mid_str_bottleneck = str_bottleneck
    flag_while_1 = False
    if param_dict[param] - diff_value > min:
        flag_while_1 = True

    # valueֵ���м�С����
    while flag_while_1:
        param_dict[param] = param_dict[param] - diff_value
        now_time = time.time()
        param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
        mysql_sum_time = mysql_sum_time + time.time() - now_time
        if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
            param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
            mid_dict_show_global_status = analysis_show_global_status(status_path)
            mid_engine_status_dict = analysis_model()
            mid_str_bottleneck = analysis_bottleneck()
            if param_dict[param] - diff_value < min:
                break
        else:
            param_dict[param] = param_dict[param] + diff_value
            break

    # valueֵ�����������
    flag_while_1 = False
    if param_dict[param] == value:
        flag_while_1 = True
    while flag_while_1:
        param_dict[param] = param_dict[param] + diff_value
        now_time = time.time()
        param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
        mysql_sum_time = mysql_sum_time + time.time() - now_time
        if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
            param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
            mid_dict_show_global_status = analysis_show_global_status(status_path)
            mid_engine_status_dict = analysis_model()
            mid_str_bottleneck = analysis_bottleneck()
            if param_dict[param] + diff_value > max:
                break

        else:
            param_dict[param] = param_dict[param] - diff_value
            break

    return param_dict, param_dict_list, mid_dict_show_global_status, mid_engine_status_dict, mid_str_bottleneck


# ��¼�����м�ֵ̽���Ĳ���
def param_mid_value_tuning_max(value, param_dict, param, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck, diff_value, min=0, max=0):
    # ��¼�ò����Ƿ��һ��
    param_dict[param] = value
    global mysql_sum_time

    # ����״̬��ֵ
    mid_dict_show_global_status = copy.deepcopy(dict_show_global_status)
    mid_engine_status_dict = copy.deepcopy(engine_status_dict)
    mid_str_bottleneck = copy.deepcopy(str_bottleneck)

    flag_while_1 = False
    if param_dict[param] - diff_value > min:
        flag_while_1 = True

    # valueֵ���м�С����
    while flag_while_1:
        param_dict[param] = param_dict[param] - diff_value
        param_dict["innodb_io_capacity"] = int(param_dict[param] / 2)
        now_time = time.time()
        param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
        mysql_sum_time = mysql_sum_time + time.time() - now_time
        if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
            param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
            mid_dict_show_global_status = analysis_show_global_status(status_path)
            mid_engine_status_dict = analysis_model()
            mid_str_bottleneck = analysis_bottleneck()
            if param_dict[param] - diff_value < min:
                break
        else:
            param_dict[param] = param_dict[param] + diff_value
            param_dict["innodb_io_capacity"] = int(param_dict[param] / 2)
            break

    # valueֵ�����������
    flag_while_1 = False
    if param_dict[param] == value:
        flag_while_1 = True
    while flag_while_1:
        param_dict[param] = param_dict[param] + diff_value
        param_dict["innodb_io_capacity"] = int(param_dict[param] / 2)
        now_time = time.time()
        param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
        mysql_sum_time = mysql_sum_time + time.time() - now_time
        if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
            param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
            mid_dict_show_global_status = analysis_show_global_status(status_path)
            mid_engine_status_dict = analysis_model()
            mid_str_bottleneck = analysis_bottleneck()
            if param_dict[param] + diff_value > max:
                break

        else:
            param_dict[param] = param_dict[param] - diff_value
            param_dict["innodb_io_capacity"] = int(param_dict[param] / 2)
            break

    return param_dict, param_dict_list, mid_dict_show_global_status, mid_engine_status_dict, mid_str_bottleneck


# ��¼�����м�ֵ̽���Ĳ���, valueֵĬ�ϲ���ֵ
def param_mid_value_tuning(value, param_dict, param, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck, min=0, max=0):
    global mysql_sum_time

    # ��¼Ĭ��ֵ
    param_dict[param] = value

    # ����״̬��ֵ
    mid_dict_show_global_status = dict_show_global_status
    mid_engine_status_dict = engine_status_dict
    mid_str_bottleneck = str_bottleneck

    flag_while_1 = False
    if (param_dict[param] / 2) > min:
        flag_while_1 = True

    # valueֵ���м�С����
    while flag_while_1:
        param_dict[param] = int(param_dict[param] / 2)
        now_time = time.time()
        param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
        mysql_sum_time = mysql_sum_time + time.time() - now_time
        if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
            param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
            mid_dict_show_global_status = analysis_show_global_status(status_path)
            mid_engine_status_dict = analysis_model()
            mid_str_bottleneck = analysis_bottleneck()
            if int(param_dict[param] / 2) < min:
                break
        else:
            param_dict[param] = param_dict[param] * 2
            break

    # valueֵ�����������
    flag_while_1 = False
    if param_dict[param] == value:
        flag_while_1 = True
    while flag_while_1:
        param_dict[param] = param_dict[param] * 2
        now_time = time.time()
        param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
        mysql_sum_time = mysql_sum_time + time.time() - now_time
        if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
            param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
            mid_dict_show_global_status = analysis_show_global_status(status_path)
            mid_engine_status_dict = analysis_model()
            mid_str_bottleneck = analysis_bottleneck()
            if param_dict[param] * 2 > max:
                break
        else:
            param_dict[param] = int(param_dict[param] / 2)
            break

    return param_dict, param_dict_list, mid_dict_show_global_status, mid_engine_status_dict, mid_str_bottleneck


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
def judge_bottleneck(str_bottleneck, flag_param_IO, flag_param_CPU, flag_param_LATCH):
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

    # print("--------------")
    # print("ϵͳƿ������")
    # print(flag_param_IO, flag_param_CPU, flag_param_LATCH)
    # print(str_bottleneck)
    # print("---------------")
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
    #         elif flag_param_LATCH != "end":
    #             return "LATCH"
    #         else:
    #             return "end"
    #     else:
    #         if flag_param_LATCH != "end":
    #             return "LATCH"
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
    #         if flag_param_LATCH != "end":
    #             return "LATCH"
    #         elif flag_param_IO != "end":
    #             return "IO"
    #         else:
    #             return "end"
    #
    # # ��������ƿ����ʱ�� ����ƿ�������ж�
    # if str_bottleneck[0] < 80 and str_bottleneck[1] < 90 and flag_param_LATCH != "end":
    #     return "LATCH"
    # if str_bottleneck[0] < 80 and str_bottleneck[1] < 90 and flag_param_LATCH == "end":
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
    while True:

        i = random.randint(1,3)
        if i == 1 and flag_param_IO != "end":
            return "IO"
        elif i == 2 and flag_param_CPU != "end":
            return "CPU"
        elif i == 3 and flag_param_LATCH != "end":
            return "OTHER"
        else:
            return "end"

if __name__ == "__main__":
    """
    ��Ҫ�������ݿ�innodb�������Ź��̵ĵ���
    """

    # ��¼�ܹ�����ʱ��
    mysql_sum_time = 0

    start_now_time = time.time()

    # �趨������Դ���ڴ���Դ����λM
    memory_resource = 548

    # �趨���õĴ�����Դ,��λM
    disk_resource = 300

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

    # ��¼��ǰ������LATCH��صĲ���
    flag_param_LATCH = "start"

    # read_ahead�ı�־λ
    mid_flag_read_ahead = False

    # hash_index�ı�־λ
    mid_flag_hash_index = False

    # ��¼��ʱ���µ�innodb_buffer_pool_chunk_sizeֵ
    mid_chunk_size = None

    # ����ѭ���Ĵ���ѵ��
    flag_loop = True

    # ��¼��Ҫ����M��λ�Ĳ���
    param_unit_dict = {}
    param_unit_dict["innodb_buffer_pool_size"] = "M"
    param_unit_dict["innodb_buffer_pool_chunk_size"] = "M"
    param_unit_dict["innodb_log_file_size"] = "M"
    param_unit_dict["innodb_log_buffer_size"] = "M"

    # ��¼��Ҫ���ŵ�io����
    IO_param_list = []

    # ��¼��Ҫ���ŵ�cpu����
    CPU_param_list = []

    # ��¼��Ҫ���ŵ�latch����
    LATCH_param_list = []

    # ��ʱ���棬�����Ժ�ѭ��
    mid_IO_list = []
    mid_CPU_list = []
    mid_LATCH_list = []

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

            # ��¼mid_chunk_size��ֵ
            mid_chunk_size = param_dict["innodb_buffer_pool_chunk_size"]

            now_time = time.time()

            # д���ò�����my.cnf
            param_dict_list = run_and_write_file(copy.copy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)

            mysql_sum_time = mysql_sum_time + time.time() - now_time

            # ��ȡ��һ�εĲ����б�
            param_dict = copy.deepcopy(param_dict_list[len(param_dict_list) - 1])

            # ��ȡshow global status like '%innodb%'�ֵ�
            dict_show_global_status = analysis_show_global_status(status_path)

            # ��ȡshow engine innodb status
            engine_status_dict = analysis_model()

            # ��ȡϵͳ��Ϣ
            str_bottleneck = analysis_bottleneck()

            # ���и��ƣ������Ժ�ѭ��ʹ��
            mid_IO_list = copy.deepcopy(IO_param_list)
            mid_CPU_list = copy.deepcopy(CPU_param_list)
            mid_LATCH_list = copy.deepcopy(LATCH_param_list)

            # �������޸Ĳ���log_buffer
            mid_value = math.ceil(log_buffer())
            print("����log_buffer�ж�")
            print(mid_value)
            if param_dict["innodb_log_buffer_size"] == mid_value:
                continue
            else:
                param_dict["innodb_buffer_pool_size"] = param_dict["innodb_buffer_pool_size"] + (param_dict["innodb_log_buffer_size"] - mid_value)
                param_dict["innodb_log_buffer_size"] = mid_value

                # ������Ӧ�Ĳ�������
                innodb_buffer_pool_size = param_dict["innodb_buffer_pool_size"]
                innodb_buffer_pool_instances = param_dict["innodb_buffer_pool_instances"]
                innodb_buffer_pool_chunk_size = param_dict["innodb_buffer_pool_chunk_size"]

                # ����buffer_pool,chunk_size��ֵ
                innodb_buffer_pool_chunk_size_1 = math.floor(innodb_buffer_pool_size / innodb_buffer_pool_instances)
                innodb_buffer_pool_size_1 = innodb_buffer_pool_chunk_size_1 * innodb_buffer_pool_instances
                param_dict["innodb_buffer_pool_size"] = innodb_buffer_pool_size_1
                param_dict["innodb_buffer_pool_chunk_size"] = innodb_buffer_pool_chunk_size_1
                now_time = time.time()
                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                mysql_sum_time = mysql_sum_time + time.time() - now_time
                param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                dict_show_global_status = analysis_show_global_status(status_path)
                engine_status_dict = analysis_model()
                str_bottleneck = analysis_bottleneck()
                i = i + 1


        # ����ϵͳƿ��ϵͳ�ж�
        else:
            """
            log_buffer�����㹻�ڴ�ռ䣬���ܳ�Ϊƿ��
            """
            print(tune_param)
            print(param_innodb_log_buffer_size())
            # ���log_buffer����ƿ�������
            if tune_param["innodb_log_buffer_size"] == 0 or tune_param["innodb_log_buffer_size"] == 1 and param_innodb_log_buffer_size() == 0:

                # ����ϵͳƿ���ж�
                print("iiiiiii")
                is_bottleneck = judge_bottleneck(str_bottleneck, flag_param_IO, flag_param_CPU, flag_param_LATCH)

                if is_bottleneck == "IO":
                    """
                   ��������������в�������
                   (1)innodb_adaptive_hash_index��ռ���ڴ棩
                   (2)innodb_adaptive_hash_index_parts�������̵߳���������
                   (3)innodb_change_buffer_max_size���Ż�����io���Ƿ��ж������������Լ����
                   innodb_read_ahead_threshold
                   innodb_flushing_avg_loops(����ˢ������)�ò�������
                   (5)innodb_lru_scan_depth��io��
                   (6)innodb_log_writer_threads��io��
                   (8)innodb_io_capacity_max = �������iops
                   (7)innodb_io_capacity = �������iops��50%
                   (9)innodb_flush_neighbors(����io)
                   (10)innodb_extend_and_initialize
                   """
                    print("�ж�Ϊioƿ��������ioƿ����ز���")
                    for io_param in IO_param_list:
                        print("���в���{}����".format(io_param))
                        if io_param == "innodb_flush_method":

                            mid_param_init = param_dict["innodb_flush_method"]
                            if mid_param_init != "fsync":
                                mid_param = param_dict["innodb_flush_method"]
                                param_dict["innodb_flush_method"] = "fsync"
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()
                                else:
                                    param_dict["innodb_flush_method"] = mid_param

                            if mid_param_init != "O_DIRECT":
                                mid_param = param_dict["innodb_flush_method"]
                                param_dict["innodb_flush_method"] = "O_DIRECT"
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()
                                else:
                                    param_dict["innodb_flush_method"] = mid_param

                            if mid_param_init != "O_DIRECT_NO_FSYNC":
                                mid_param = param_dict["innodb_flush_method"]
                                param_dict["innodb_flush_method"] = "O_DIRECT_NO_FSYNC"
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()
                                else:
                                    param_dict["innodb_flush_method"] = mid_param
                                # ������ǰѭ��
                            break

                        elif io_param == "innodb_extend_and_initialize":
                            if param_dict["innodb_extend_and_initialize"] == 1:
                                param_dict["innodb_extend_and_initialize"] = 0
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    print("Ϊ0Ч����")
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()
                                else:
                                    print("Ϊ1��ǰЧ����")
                                    param_dict["innodb_extend_and_initialize"] = 1
                                # ������ǰѭ��
                                break
                            else:
                                param_dict["innodb_extend_and_initialize"] = 1
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    print("Ϊ1Ч����")
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()
                                else:
                                    print("Ϊ0��ǰЧ����")
                                    param_dict["innodb_extend_and_initialize"] = 0
                                # ������ǰѭ��
                                break

                        elif io_param == "innodb_flush_neighbors":
                            # ����������ǻ�еӲ��
                            if param_dict["innodb_flush_neighbors"] == 0:
                                print("���iops��˳��iops��࣬�ʲ�ˢ����������Դ")

                            # ��������ǻ�еӲ��
                            else:
                                param_dict["innodb_flush_neighbors"] = 2
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    print("����2��Ч����")
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()
                                else:
                                    print("����1��Ч����")
                                    param_dict["innodb_flush_neighbors"] = 1
                            # ������ǰѭ��
                            break

                        elif io_param == "innodb_io_capacity_max":
                            param_dict, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck = \
                                param_mid_value_tuning_max(param_dict["innodb_io_capacity_max"],
                                                           copy.deepcopy(param_dict),
                                                           "innodb_io_capacity_max",
                                                           copy.deepcopy(param_dict_list),
                                                           dict_show_global_status,
                                                           engine_status_dict,
                                                           str_bottleneck, int(param_dict["innodb_io_capacity_max"] * 0.1), 100, 20000)

                            break

                        elif io_param == "innodb_log_writer_threads":
                            if param_dict["innodb_log_writer_threads"] == 1:
                                param_dict["innodb_log_writer_threads"] = 0
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_innodb_log_buffer_size() == 0:
                                    print("������log_writer��ƿ��")
                                    if param_dict["throught"] > param_dict_list[len(param_dict_list) - 1]["throught"]:
                                        print("����log_writer")
                                        param_dict["innodb_log_writer_threads"] = 1
                                    else:
                                        print("�ر�log_writer")
                                        param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                        dict_show_global_status = analysis_show_global_status(status_path)
                                        engine_status_dict = analysis_model()
                                        str_bottleneck = analysis_bottleneck()
                                else:
                                    print("����log_writer��ƿ��")
                                    innodb_buffer_pool_size_all = param_dict["innodb_buffer_pool_size"]
                                    innodb_buffer_pool_chunk_size_all = param_dict["innodb_buffer_pool_chunk_size"]
                                    innodb_log_buffer_size_all = param_dict["innodb_log_buffer_size"]
                                    while True:
                                        innodb_buffer_pool_size = param_dict["innodb_buffer_pool_size"]
                                        innodb_buffer_pool_instances = param_dict["innodb_buffer_pool_instances"]
                                        innodb_buffer_pool_chunk_size = param_dict["innodb_buffer_pool_chunk_size"]
                                        innodb_buffer_pool_size_1 = innodb_buffer_pool_size - param_dict["innodb_log_buffer_size"]
                                        param_dict["innodb_log_buffer_size"] = param_dict["innodb_log_buffer_size"] * 2

                                        # ����buffer_pool_instance������
                                        per_size = math.floor(innodb_buffer_pool_size_1 / innodb_buffer_pool_instances)
                                        innodb_buffer_pool_chunk_size_1 = per_size
                                        innodb_buffer_pool_size_1 = innodb_buffer_pool_chunk_size_1 * innodb_buffer_pool_instances
                                        param_dict["innodb_buffer_pool_size"] = innodb_buffer_pool_size_1
                                        param_dict["innodb_buffer_pool_chunk_size"] = innodb_buffer_pool_chunk_size_1
                                        now_time = time.time()
                                        param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                        mysql_sum_time = mysql_sum_time + time.time() - now_time

                                        if param_innodb_log_buffer_size() == 0:
                                            if param_dict["throught"] > param_dict_list[len(param_dict_list) - 1]["throught"]:
                                                print("��һ�ε����Ϻ�")
                                                param_dict["innodb_log_buffer_size"] = innodb_log_buffer_size_all
                                                param_dict["innodb_buffer_pool_size"] = innodb_buffer_pool_size_all
                                                param_dict["innodb_buffer_pool_chunk_size"] = innodb_buffer_pool_chunk_size_all
                                                param_dict["innodb_log_writer_threads"] = 1
                                            else:
                                                print("���ε����Ϻ�")
                                                param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                                dict_show_global_status = analysis_show_global_status(status_path)
                                                engine_status_dict = analysis_model()
                                                str_bottleneck = analysis_bottleneck()
                                            break
                            # ������ǰѭ��
                            break

                        elif io_param == "innodb_lru_scan_depth":
                            param_dict, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck = \
                                param_mid_value_tuning(1024, copy.deepcopy(param_dict), "innodb_lru_scan_depth", copy.deepcopy(param_dict_list),
                                                       dict_show_global_status, engine_status_dict, str_bottleneck, 100, 1024 * 10)
                            # ������ǰѭ��
                            break

                        elif io_param == "innodb_read_ahead_threshold":

                            # �ж��Ƿ���ڵ�һ��Ԥ��Ϊ0�����
                            if param_innodb_read_ahead_threshold(dict_show_global_status) == 0:
                                print("��һ��Ԥ��Ϊ0")
                                mid_flag_read_ahead = True

                            # ��¼�������ĺ�
                            sum_value = param_dict["throught"]

                            # �ж��Ƿ�����
                            mid_consecutive = True

                            # ͳ�ƴ���
                            sum_cnt = 1

                            # ��Ԥ����Ϊ0�����ж�
                            if mid_flag_read_ahead is True:
                                while True:
                                    param_dict["innodb_read_ahead_threshold"] = param_dict["innodb_read_ahead_threshold"] - 8
                                    now_time = time.time()
                                    param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "read_ahead")
                                    mysql_sum_time = mysql_sum_time + time.time() - now_time

                                    if param_dict["throught"] > param_dict_list[len(param_dict_list) - 1]["throught"]:
                                        print("��ǰ��������С")
                                        param_dict["innodb_read_ahead_threshold"] = param_dict["innodb_read_ahead_threshold"] + 8
                                        break
                                    else:
                                        print("��ǰ�������Ϻ�")
                                        param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                        dict_show_global_status = analysis_show_global_status(status_path)
                                        engine_status_dict = analysis_model()
                                        str_bottleneck = analysis_bottleneck()
                                        # �ﵽ��Сֵ��ֹͣread_ahead����
                                        if param_dict["innodb_read_ahead_threshold"] - 8 < 0:
                                            break

                            # ��Ԥ����Ϊ0�����ж�
                            else:
                                while True:
                                    param_dict["innodb_read_ahead_threshold"] = param_dict["innodb_read_ahead_threshold"] - 8
                                    now_time = time.time()
                                    param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "read_ahead")
                                    mysql_sum_time = mysql_sum_time + time.time() - now_time
                                    if param_dict["throught"] > param_dict_list[len(param_dict_list) - 1]["throught"]:
                                        print("��ǰ��������С")
                                        param_dict["innodb_read_ahead_threshold"] = param_dict["innodb_read_ahead_threshold"] + 8
                                        break
                                    else:
                                        print("��ǰ�������Ϻ�")
                                        param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                        dict_show_global_status = analysis_show_global_status(status_path)
                                        engine_status_dict = analysis_model()
                                        str_bottleneck = analysis_bottleneck()
                                        # �ﵽ��Сֵ��ֹͣread_ahead����
                                        if param_dict["innodb_read_ahead_threshold"] - 8 < 0:
                                            break

                                # �����Ĭ��ֵ
                                flag_while = False
                                if param_dict["innodb_read_ahead_threshold"] == 56:
                                    flag_while = True
                                while flag_while:
                                    param_dict["innodb_read_ahead_threshold"] = param_dict["innodb_read_ahead_threshold"] + 8
                                    now_time = time.time()
                                    param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "read_ahead")
                                    mysql_sum_time = mysql_sum_time + time.time() - now_time

                                    if param_dict["throught"] > param_dict_list[len(param_dict_list) - 1]["throught"]:
                                        print("��ǰ��������С")
                                        param_dict["innodb_read_ahead_threshold"] = param_dict["innodb_read_ahead_threshold"] - 8
                                        break
                                    else:
                                        print("��ǰ�������Ϻ�")
                                        param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                        dict_show_global_status = analysis_show_global_status(status_path)
                                        engine_status_dict = analysis_model()
                                        str_bottleneck = analysis_bottleneck()
                                        # �ﵽ��Сֵ��ֹͣread_ahead����
                                        if param_dict["innodb_read_ahead_threshold"] + 8 > 64:
                                            break
                            # ������ǰѭ��
                            break

                        elif io_param == "innodb_change_buffer_max_size":

                            mid_value = 25
                            mid_return = param_innodb_change_buffer()
                            print("free, sum")
                            print(mid_return)
                            if mid_return[1] / 64 / param_dict["innodb_buffer_pool_size"] < 0.25:
                                # if mid_return[1] - mid_return[0] + mid_return[1] * 0.1 < mid_return[1]:
                                #     print("change_buffer�п���ҳ")
                                #     if (mid_return[1] - mid_return[0]) * 1.2 < mid_return[1]:
                                #         print("����ҳ�ܶ�")
                                #         mid_value = math.ceil((mid_return[1] - mid_return[0]) * 1.2 * 16 / 1024 / param_dict["innodb_buffer_pool_size"] * 100)
                                #         param_dict["innodb_change_buffer_max_size"] = min(25, mid_value)
                                #         now_time = time.time()
                                #         param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "change_buffer")
                                #         mysql_sum_time = mysql_sum_time + time.time() - now_time
                                #         if param_dict_list[len(param_dict_list) - 1]["throught"] < param_dict["throught"]:
                                #             param_dict["innodb_change_buffer_max_size"] = 25
                                #         else:
                                #             param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                #             dict_show_global_status = analysis_show_global_status(status_path)
                                #             engine_status_dict = analysis_model()
                                #             str_bottleneck = analysis_bottleneck()

                                print(mid_value)
                                param_dict["innodb_change_buffer_max_size"] = 0
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "change_buffer")
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict_list[len(param_dict_list) - 1]["throught"] < param_dict["throught"]:
                                    print("����change_buffer�Ϻ�")
                                    param_dict["innodb_change_buffer_max_size"] = 25
                                else:
                                    print("�ر�change_buffer�Ϻ�")
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()
                            else:
                                print("change_bufferû�п���ҳ")
                                param_dict["innodb_change_buffer_max_size"] = 50
                                print("��������change_buffer")
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "change_buffer")
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    print("�ر�change_buffer�Ϻ�")
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()
                                else:
                                    print("����change_buffer�Ϻ�")
                                    param_dict["innodb_change_buffer_max_size"] = 25
                                # if (mid_return[1] - mid_return[0]) * 1.2 < mid_return[1]:
                                #     print("����ҳ�ܶ�")
                                #     mid_value = math.ceil((mid_return[1] - mid_return[0]) * 1.2 * 16 / 1024 / param_dict["innodb_buffer_pool_size"] * 100)
                                #     param_dict["innodb_change_buffer_max_size"] = min(50, mid_value)
                                #     mid_value = min(50, mid_value)
                                #     now_time = time.time()
                                #     param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "change_buffer")
                                #     mysql_sum_time = mysql_sum_time + time.time() - now_time
                                #     param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                #     dict_show_global_status = analysis_show_global_status(status_path)
                                #     engine_status_dict = analysis_model()
                                #     str_bottleneck = analysis_bottleneck()
                                # print(mid_value)
                                mid_value = param_dict["innodb_change_buffer_max_size"]
                                param_dict["innodb_change_buffer_max_size"] = 0
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "change_buffer")
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    print("�ر�change_buffer�Ϻ�")
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()
                                else:
                                    print("����change_buffer�Ϻ�")
                                    param_dict["innodb_change_buffer_max_size"] = mid_value

                            # ������ǰѭ��
                            break

                        elif io_param == "innodb_adaptive_hash_index":  # ��������������һ�����
                            mid_return = param_hash_index()
                            print("btr0sea, hash-sum, no-hash-sum")
                            print(mid_return)
                            # ���btr0sea�ĸ���Ϊ0
                            if mid_return[0] == 0 and param_dict["innodb_adaptive_hash_index"] == 1:
                                print("btr0seaΪ0")
                                param_dict["innodb_adaptive_hash_index"] = 0
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "hash_index")
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] > param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    print("����hash_index�Ϻ�")
                                    param_dict["innodb_adaptive_hash_index"] = 1
                                else:
                                    print("������hash_index�Ϻ�")
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()

                            # ���btr0sea�ĸ�����Ϊ0
                            print("btr0sea��Ϊ0")
                            while mid_return[0] > 0 and param_dict["innodb_adaptive_hash_index"] == 1:
                                param_dict["innodb_adaptive_hash_index_parts"] = param_dict["innodb_adaptive_hash_index_parts"] * 2
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "hash_index")
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                # �����һ����������
                                if param_dict["throught"] > param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    print("����*2Ч������")
                                    param_dict["innodb_adaptive_hash_index_parts"] = int(param_dict["innodb_adaptive_hash_index_parts"] / 2)
                                    param_dict["innodb_adaptive_hash_index"] = 0
                                    now_time = time.time()
                                    param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "hash_index")
                                    mysql_sum_time = mysql_sum_time + time.time() - now_time
                                    # �����һ����������
                                    print("�Ƿ�����hash_index")
                                    if param_dict_list[len(param_dict_list) - 1]["throught"] < param_dict["throught"]:
                                        print("����hash_index�Ϻ�")
                                        param_dict["innodb_adaptive_hash_index"] = 1
                                    # ���������������
                                    else:
                                        print("�ر�hash_index�Ϻ�")
                                        dict_show_global_status = analysis_show_global_status(status_path)
                                        engine_status_dict = analysis_model()
                                        str_bottleneck = analysis_bottleneck()
                                        param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    break
                                # ���������������
                                else:
                                    print("������*2�ϸ�")
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()

                            # ������ǰѭ��
                            break

                    print("��ǰ��õĲ���ѡ��")
                    for i_param_dict in param_dict:
                        print(i_param_dict, param_dict[i_param_dict])
                    if io_param == "innodb_adaptive_hash_index" or io_param == "innodb_io_capacity_max":
                        IO_param_list = IO_param_list[1:]
                    IO_param_list = IO_param_list[1:]
                    if len(IO_param_list) == 0:
                        flag_param_IO = "end"

                elif is_bottleneck == "CPU":
                    """
                    1,return_dict["innodb_sync_spin_loops"] = 30
                    2,return_dict["innodb_concurrency_tickets"] = 5000
                    3,return_dict["innodb_log_wait_for_flush_spin_hwm"] = 400
                    4,return_dict["innodb_log_writer_threads"] = 1
                    5,innodb_read_io_threads = Ĭ��cpu�߼��������Ժ������ض�����*cpu�߼�����/2
                    6,innodb_write_io_threads = Ĭ��cpu�߼��������Ժ�������д����*cpu�߼�����/2
                    7,innodb_purge_threads
                    8,innodb_page_cleaners
                    (1)innodb_sync_spin_loops
                    (2)innodb_concurrency_tickets���������С�йأ�
                    (3)innodb_log_wait_for_flush_spin_hwm���û��߳���־ƽ��ˢ�µ�spin������ޣ�
                    (4)innodb_log_writer_threads��io��
                    (5)innodb_page_cleaners���Ѿ���ʼ����
                    (6)innodb_purge_threads���Ѿ���ʼ����
                    (7)innodb_read_io_threads = Ĭ��cpu�߼��������Ժ������ض�����*cpu�߼�����/2���Ѿ���ʼ����
                    (8)innodb_write_io_threads = Ĭ��cpu�߼��������Ժ�������д����*cpu�߼�����/2���Ѿ���ʼ����
                    """
                    print("�ж�ƿ����CPU, ������Ӧ�����޸�")

                    for cpu_param in CPU_param_list:
                        print("���в���{}����".format(cpu_param))
                        if cpu_param == "innodb_write_io_threads":
                            # ��ȡ���ָ��صض�д����
                            return_param = param_read_and_write_io_thread()
                            read_io_thread = max(1, round(cpu_num_all * (return_param[0][0] / (return_param[0][0] + return_param[0][1]))))
                            if read_io_thread == cpu_num_all:
                                read_io_thread = read_io_thread - 1
                            # �������һ�����ò�һ���������������
                            if param_dict["innodb_read_io_threads"] != read_io_thread:
                                print("��д��������1��1, �ٴ��������ݿ�")
                                param_dict["innodb_read_io_threads"] = read_io_thread
                                param_dict["innodb_write_io_threads"] = cpu_num_all - read_io_thread
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "read_write_io")
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    print("���д������Ӧ�Ķ�д�����Ϻ�")
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()
                                else:
                                    print("1��1���߳̽���Ϻ�")
                                    param_dict["innodb_read_io_threads"] = int(cpu_num_all / 2)
                                    param_dict["innodb_write_io_threads"] = cpu_num_all - param_dict["innodb_read_io_threads"]
                            # ������ϴ�����һ������ֱ�ӽ�����һ����������
                            else:
                                print("��д����1��1������Ҫ�������ݿ�")
                            break

                        if cpu_param == "innodb_purge_threads":
                            if num_table > 4:
                                param_dict["innodb_purge_threads"] = num_table
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()
                                else:
                                    param_dict["innodb_purge_threads"] = 4
                            break

                        if cpu_param == "innodb_page_cleaners":
                            if param_dict["innodb_buffer_pool_instances"] > 4:
                                param_dict["innodb_page_cleaners"] = param_dict["innodb_buffer_pool_instances"]
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()
                                else:
                                    param_dict["innodb_page_cleaners"] = 4
                            break

                        if cpu_param == "innodb_log_writer_threads":
                            if param_dict["innodb_log_writer_threads"] == 1:
                                param_dict["innodb_log_writer_threads"] = 0
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_innodb_log_buffer_size() == 0:
                                    print("������log_writer��ƿ��")
                                    if param_dict["throught"] > param_dict_list[len(param_dict_list) - 1]["throught"]:
                                        print("����log_writer")
                                        param_dict["innodb_log_writer_threads"] = 1
                                    else:
                                        print("�ر�log_writer")
                                        param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                        dict_show_global_status = analysis_show_global_status(status_path)
                                        engine_status_dict = analysis_model()
                                        str_bottleneck = analysis_bottleneck()
                                else:
                                    print("����log_writer��ƿ��")
                                    innodb_buffer_pool_size_all = param_dict["innodb_buffer_pool_size"]
                                    innodb_buffer_pool_chunk_size_all = param_dict["innodb_buffer_pool_chunk_size"]
                                    innodb_log_buffer_size_all = param_dict["innodb_log_buffer_size"]
                                    while True:
                                        innodb_buffer_pool_size = param_dict["innodb_buffer_pool_size"]
                                        innodb_buffer_pool_instances = param_dict["innodb_buffer_pool_instances"]
                                        innodb_buffer_pool_chunk_size = param_dict["innodb_buffer_pool_chunk_size"]
                                        innodb_buffer_pool_size_1 = innodb_buffer_pool_size - param_dict["innodb_log_buffer_size"]
                                        param_dict["innodb_log_buffer_size"] = param_dict["innodb_log_buffer_size"] * 2

                                        # ����buffer_pool_instance������
                                        per_size = math.floor(innodb_buffer_pool_size_1 / innodb_buffer_pool_instances)
                                        innodb_buffer_pool_chunk_size_1 = per_size
                                        innodb_buffer_pool_size_1 = innodb_buffer_pool_chunk_size_1 * innodb_buffer_pool_instances
                                        param_dict["innodb_buffer_pool_size"] = innodb_buffer_pool_size_1
                                        param_dict["innodb_buffer_pool_chunk_size"] = innodb_buffer_pool_chunk_size_1
                                        now_time = time.time()
                                        param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                        mysql_sum_time = mysql_sum_time + time.time() - now_time
                                        if param_innodb_log_buffer_size() == 0:
                                            if param_dict["throught"] > param_dict_list[len(param_dict_list) - 1]["throught"]:
                                                print("��һ�ε����Ϻ�")
                                                param_dict["innodb_log_buffer_size"] = innodb_log_buffer_size_all
                                                param_dict["innodb_buffer_pool_size"] = innodb_buffer_pool_size_all
                                                param_dict["innodb_buffer_pool_chunk_size"] = innodb_buffer_pool_chunk_size_all
                                                param_dict["innodb_log_writer_threads"] = 1
                                            else:
                                                print("���ε����Ϻ�")
                                                param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                                dict_show_global_status = analysis_show_global_status(status_path)
                                                engine_status_dict = analysis_model()
                                                str_bottleneck = analysis_bottleneck()
                                            break

                            break

                        if cpu_param == "innodb_log_wait_for_flush_spin_hwm":
                            # ���в����ж�
                            param_dict, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck = \
                                param_mid_value_tuning_2(400, copy.deepcopy(param_dict), "innodb_log_wait_for_flush_spin_hwm",
                                                         copy.deepcopy(param_dict_list), dict_show_global_status, engine_status_dict, str_bottleneck, 100, 0, 4000)
                            break

                        if cpu_param == "innodb_concurrency_tickets":
                            # ���в����ж�
                            param_dict, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck = \
                                param_mid_value_tuning_2(5000, copy.deepcopy(param_dict), "innodb_concurrency_tickets",
                                                         copy.deepcopy(param_dict_list), dict_show_global_status, engine_status_dict, str_bottleneck, 1000, 1, 50000)
                            break

                        if cpu_param == "innodb_sync_spin_loops":
                            # ���в����ж�
                            param_dict, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck = \
                                param_mid_value_tuning_2(30, copy.deepcopy(param_dict), "innodb_sync_spin_loops",
                                                         copy.deepcopy(param_dict_list), dict_show_global_status, engine_status_dict, str_bottleneck, 10, 0, 300)
                            break

                        if cpu_param == "innodb_thread_concurrency":
                            param_dict, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck = \
                                param_mid_value_tuning_2(2 * cpu_num_all, copy.deepcopy(param_dict), "innodb_thread_concurrency",
                                                         copy.deepcopy(param_dict_list), dict_show_global_status, engine_status_dict,
                                                         str_bottleneck, round(cpu_num_all * 0.2 / 2) * 2, 0, 180)

                    print("��ǰ��õĲ���ѡ��")
                    for i_param_dict in param_dict:
                        print(i_param_dict, param_dict[i_param_dict])
                    if cpu_param == "innodb_write_io_threads":
                        CPU_param_list = CPU_param_list[1:]
                    CPU_param_list = CPU_param_list[1:]
                    if len(CPU_param_list) == 0:
                        flag_param_CPU = "end"

                # �޸�������صĲ���
                elif is_bottleneck == "LATCH":
                    """
                    ����һ���������
                    (1)innodb_sync_array_size(����cpu������768�ȴ���̽��)
                    (2)innodb_deadlock_detect ���Ƿ����������⣩
                    (3)innodb_lock_wait_timeout�������ĳ�ʱʱ�䣩
                    (4)innodb_buffer_pool_instances(�����̵߳�������)��ָ��
                    (5)innodb_adaptive_hash_index_parts
                    """
                    print("�ж�ƿ��ΪLATCH,�޸���Ӧ�Ĳ���")

                    for LATCH_param in LATCH_param_list:
                        print("���в���{}����".format(LATCH_param))
                        if LATCH_param == "innodb_adaptive_hash_index_parts":
                            mid_return = param_hash_index()
                            print("btr0sea, hash-sum, no-hash-sum")
                            print(mid_return)
                            # ���btr0sea�ĸ�����Ϊ0
                            print("btr0sea��Ϊ0")
                            mid_innodb_adaptive_hash_index = param_dict["innodb_adaptive_hash_index"]
                            while mid_return[0] > 0:
                                param_dict["innodb_adaptive_hash_index"] = 1
                                param_dict["innodb_adaptive_hash_index_parts"] = param_dict["innodb_adaptive_hash_index_parts"] * 2
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "hash_index")
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                # �����һ����������
                                if param_dict["throught"] > param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    print("����*2Ч������")
                                    param_dict["innodb_adaptive_hash_index_parts"] = int(param_dict["innodb_adaptive_hash_index_parts"] / 2)
                                    param_dict["innodb_adaptive_hash_index"] = mid_innodb_adaptive_hash_index
                                    break
                                # ���������������
                                else:
                                    print("������*2�ϸ�")
                                    mid_innodb_adaptive_hash_index = 1
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()
                                    if param_dict["innodb_adaptive_hash_index_parts"] * 2 > 512:
                                        break
                            break

                        if LATCH_param == "innodb_buffer_pool_instances":

                            # ��¼�ò����Ƿ��һ��
                            mid_innodb_buffer_pool_instances = param_dict["innodb_buffer_pool_instances"]

                            innodb_buffer_pool_size = param_dict["innodb_buffer_pool_size"]
                            # valueֵ���м�С����
                            while True:
                                innodb_buffer_pool_instances = param_dict["innodb_buffer_pool_instances"]
                                if innodb_buffer_pool_instances > 2:
                                    innodb_buffer_pool_chunk_size = param_dict["innodb_buffer_pool_chunk_size"]
                                    innodb_buffer_pool_instances_1 = innodb_buffer_pool_instances - 2
                                    innodb_buffer_pool_chunk_size_1 = math.floor(innodb_buffer_pool_size / innodb_buffer_pool_instances_1)
                                    innodb_buffer_pool_size_1 = innodb_buffer_pool_instances_1 * innodb_buffer_pool_chunk_size_1
                                    # ����buffer_pool,chunk_size��ֵ
                                    param_dict["innodb_buffer_pool_size"] = innodb_buffer_pool_size_1
                                    param_dict["innodb_buffer_pool_chunk_size"] = innodb_buffer_pool_chunk_size_1
                                    param_dict["innodb_buffer_pool_instances"] = innodb_buffer_pool_instances_1
                                    param_dict["innodb_page_cleaners"] = min(4, param_dict["innodb_buffer_pool_instances"])
                                    now_time = time.time()
                                    param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                    mysql_sum_time = mysql_sum_time + time.time() - now_time
                                    if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                        param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                        dict_show_global_status = analysis_show_global_status(status_path)
                                        engine_status_dict = analysis_model()
                                        str_bottleneck = analysis_bottleneck()
                                        if param_dict["innodb_buffer_pool_instances"] - 2 < 1:
                                            break
                                    else:
                                        param_dict["innodb_buffer_pool_size"] = innodb_buffer_pool_size
                                        param_dict["innodb_buffer_pool_chunk_size"] = innodb_buffer_pool_chunk_size
                                        param_dict["innodb_buffer_pool_instances"] = param_dict["innodb_buffer_pool_instances"] + 2
                                        param_dict["innodb_page_cleaners"] = min(4, param_dict["innodb_buffer_pool_instances"])
                                        break
                                else:
                                    break

                            # valueֵ�����������
                            flag_while = False
                            if param_dict["innodb_buffer_pool_instances"] == mid_innodb_buffer_pool_instances:
                                flag_while = True

                            innodb_buffer_pool_size = param_dict["innodb_buffer_pool_size"]
                            while flag_while:
                                innodb_buffer_pool_instances = param_dict["innodb_buffer_pool_instances"]
                                if innodb_buffer_pool_instances < 63:
                                    innodb_buffer_pool_chunk_size = param_dict["innodb_buffer_pool_chunk_size"]
                                    innodb_buffer_pool_instances_1 = innodb_buffer_pool_instances + 2
                                    innodb_buffer_pool_chunk_size_1 = math.floor(innodb_buffer_pool_size / innodb_buffer_pool_instances_1)
                                    innodb_buffer_pool_size_1 = innodb_buffer_pool_instances_1 * innodb_buffer_pool_chunk_size_1
                                    # ����buffer_pool,chunk_size��ֵ
                                    param_dict["innodb_buffer_pool_size"] = innodb_buffer_pool_size_1
                                    param_dict["innodb_buffer_pool_chunk_size"] = innodb_buffer_pool_chunk_size_1
                                    param_dict["innodb_buffer_pool_instances"] = innodb_buffer_pool_instances_1
                                    param_dict["innodb_page_cleaners"] = min(4, param_dict["innodb_buffer_pool_instances"])
                                    now_time = time.time()
                                    param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                    mysql_sum_time = mysql_sum_time + time.time() - now_time
                                    if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                        param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                        mid_dict_show_global_status = analysis_show_global_status(status_path)
                                        mid_engine_status_dict = analysis_model()
                                        mid_str_bottleneck = analysis_bottleneck()
                                        if param_dict["innodb_buffer_pool_instances"] + 2 > 64:
                                            break
                                    else:
                                        param_dict["innodb_buffer_pool_instances"] = param_dict["innodb_buffer_pool_instances"] - 2
                                        param_dict["innodb_buffer_pool_size"] = innodb_buffer_pool_size
                                        param_dict["innodb_buffer_pool_chunk_size"] = innodb_buffer_pool_chunk_size
                                        param_dict["innodb_page_cleaners"] = min(4, param_dict["innodb_buffer_pool_instances"])
                                        break
                                else:
                                    break
                            break

                        if LATCH_param == "innodb_lock_wait_timeout":
                            # ��ȡƽ��ʱ��������ʱ��
                            avg_time, max_time = param_lock_row_time(dict_show_global_status)
                            # �ر��������
                            mid_throught_innodb_deadlock_detect = param_dict["throught"]
                            mid_dict_show_global_status = dict_show_global_status
                            mid_engine_status_dict = engine_status_dict
                            mid_str_bottleneck = str_bottleneck

                            # ����һ��50��ʱ��
                            param_dict["innodb_lock_wait_timeout"] = 50
                            param_dict["innodb_deadlock_detect"] = 0
                            now_time = time.time()
                            param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "lock_wait")
                            mysql_sum_time = mysql_sum_time + time.time() - now_time
                            param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                            dict_show_global_status = analysis_show_global_status(status_path)
                            engine_status_dict = analysis_model()
                            str_bottleneck = analysis_bottleneck()

                            # ������ʱ��ĵ���
                            param_dict, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck = \
                                param_mid_value_tuning_2(50, copy.deepcopy(param_dict), "innodb_lock_wait_timeout", copy.deepcopy(param_dict_list),
                                                         dict_show_global_status, engine_status_dict, str_bottleneck, 10, 10, 500)

                            # ���в����ĶԱ�
                            if mid_throught_innodb_deadlock_detect > param_dict["throught"]:
                                param_dict["throught"] = mid_throught_innodb_deadlock_detect
                                param_dict["innodb_deadlock_detect"] = 1
                                param_dict["innodb_lock_wait_timeout"] = 50
                                dict_show_global_status = mid_dict_show_global_status
                                engine_status_dict = mid_engine_status_dict
                                str_bottleneck = mid_str_bottleneck
                            break

                        if LATCH_param == "innodb_sync_array_size":
                            # ������ʱ��ĵ���
                            param_dict, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck = \
                                param_mid_value_tuning(1, copy.deepcopy(param_dict), "innodb_sync_array_size", copy.deepcopy(param_dict_list),
                                                       dict_show_global_status, engine_status_dict, str_bottleneck, 1, 1024)
                            break

                    print("��ǰ��õĲ���ѡ��")
                    for i_param_dict in param_dict:
                        print(i_param_dict, param_dict[i_param_dict])
                    if LATCH_param == "innodb_lock_wait_timeout":
                        LATCH_param_list = LATCH_param_list[1:]
                    print(LATCH_param_list)
                    LATCH_param_list = LATCH_param_list[1:]
                    print(LATCH_param_list)
                    if len(LATCH_param_list) == 0:
                        flag_param_LATCH = "end"

                # ������һ�ε���
                elif is_bottleneck == "end":
                    if max_iter_value < param_dict["throught"]:
                        max_iter_value = param_dict["throught"]
                        flag_param_IO = "start"
                        flag_param_LATCH = "start"
                        flag_param_CPU = "start"
                        CPU_param_list = copy.deepcopy(mid_CPU_list)
                        IO_param_list = copy.deepcopy(mid_IO_list)
                        LATCH_param_list = copy.deepcopy(mid_LATCH_list)
                    else:
                        print(time.time() - start_now_time - mysql_sum_time)
                        break

            # ���log_buffer��ƿ��������������log_buffer����
            elif param_innodb_log_buffer_size() > 0 and tune_param["innodb_log_buffer_size"] == 1:

                # ��¼��ǰ�Ĳ���ֵ
                print("���в���log_buffer���޸�")
                innodb_buffer_pool_size = param_dict["innodb_buffer_pool_size"]
                innodb_buffer_pool_instances = param_dict["innodb_buffer_pool_instances"]
                innodb_buffer_pool_chunk_size = param_dict["innodb_buffer_pool_chunk_size"]
                innodb_buffer_pool_size_1 = innodb_buffer_pool_size - param_dict["innodb_log_buffer_size"]
                param_dict["innodb_log_buffer_size"] = param_dict["innodb_log_buffer_size"] * 2

                # ����buffer_pool,chunk_size��ֵ
                innodb_buffer_pool_chunk_size_1 = math.floor(innodb_buffer_pool_size_1 / innodb_buffer_pool_instances)
                innodb_buffer_pool_size_1 = innodb_buffer_pool_chunk_size_1 * innodb_buffer_pool_instances
                param_dict["innodb_buffer_pool_size"] = innodb_buffer_pool_size_1
                param_dict["innodb_buffer_pool_chunk_size"] = innodb_buffer_pool_chunk_size_1
                now_time = time.time()
                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "log_buffer")
                mysql_sum_time = mysql_sum_time + time.time() - now_time
                param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]

                # ������ǰ��״̬
                dict_show_global_status = analysis_show_global_status(status_path)
                engine_status_dict = analysis_model()
                str_bottleneck = analysis_bottleneck()

        # ���е���
        i = i + 1
        print("i is {}".format(i))