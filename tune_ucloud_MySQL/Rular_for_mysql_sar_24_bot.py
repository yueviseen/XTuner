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

# 定义全局参数
cpu_num_all = int(os.popen("cat /proc/cpuinfo| grep 'processor'| wc -l").readlines()[0].replace("\n", ''))
cnt = 0
tune_param = {}
num_table = 9


# 将累计量列表转变成增量列表
def tranfer_status(result_list):
    result_list_1 = []
    length = len(result_list)
    for i in range(1, length):
        result_list_1.append(result_list[i] - result_list[i - 1])
    return result_list_1


# 获取锁等待的次数
def param_lock_row_num(dict_show_global_status, engine_status_dict):
    lock_num_status = dict_show_global_status["Innodb_row_lock_current_waits"]
    max_lock_num = 0
    for i in lock_num_status:
        max_lock_num = max(i, max_lock_num)
    lock_num_dict = engine_status_dict["transactions"]
    for i in lock_num_dict:
        max_lock_num = max(max_lock_num, i["lock_wait_num"])

    return max_lock_num


# 获取锁定平均值和最大值
def param_lock_row_time(dict_show_global_status):
    avg_time = dict_show_global_status["Innodb_row_lock_time_avg"]
    max_time = dict_show_global_status["Innodb_row_lock_time_max"]

    avg_time = avg_time[len(avg_time) - 1]
    max_time = max_time[len(max_time) - 1]

    return avg_time, max_time


# 判断log_buffer 是否是瓶颈
def status_estimate(dict_show_global_status):
    # 判断log buffer的内存是否偏小,
    innodb_log_waits_list = tranfer_status(dict_show_global_status["Innodb_log_waits"])
    sum_innodb_log_wait = 0
    for ii in innodb_log_waits_list:
        sum_innodb_log_wait = sum_innodb_log_wait + int(ii)
    print("日志等待次数")
    print(dict_show_global_status["Innodb_log_waits"])

    # 记录线性预读的页数
    sum_innodb_buffer_pool_read_ahead = 0
    innodb_buffer_pool_read_ahead_list = tranfer_status(dict_show_global_status["Innodb_buffer_pool_read_ahead"])
    for ii in innodb_buffer_pool_read_ahead_list:
        sum_innodb_buffer_pool_read_ahead = sum_innodb_buffer_pool_read_ahead + int(ii)
    print("线性预读次数")
    print(dict_show_global_status["Innodb_buffer_pool_read_ahead"])

    # 记录随机预读的页数
    sum_innodb_buffer_pool_read_ahead_rnd = 0
    innodb_buffer_pool_read_ahead_rnd_list = tranfer_status(dict_show_global_status["Innodb_buffer_pool_read_ahead_rnd"])
    for ii in innodb_buffer_pool_read_ahead_rnd_list:
        sum_innodb_buffer_pool_read_ahead_rnd = sum_innodb_buffer_pool_read_ahead_rnd + int(ii)
    print("随机预读次数")
    print(dict_show_global_status["Innodb_buffer_pool_read_ahead_rnd"])

    # 记录没有预读就消失的页数
    sum_innodb_buffer_pool_read_ahead_evicted = 0
    innodb_buffer_pool_read_ahead_evicted_list = tranfer_status(dict_show_global_status["Innodb_buffer_pool_read_ahead_evicted"])
    for ii in innodb_buffer_pool_read_ahead_evicted_list:
        sum_innodb_buffer_pool_read_ahead_evicted = sum_innodb_buffer_pool_read_ahead_evicted + int(ii)
    print("没有预读就消失的次数")
    print(dict_show_global_status["Innodb_buffer_pool_read_ahead_evicted"])

    # 记录内存命中率
    # (1)逻辑读取的次数
    sum_innodb_buffer_pool_read_requests = 0
    innodb_buffer_pool_read_requests_list = tranfer_status(dict_show_global_status["Innodb_buffer_pool_read_requests"])
    for ii in innodb_buffer_pool_read_requests_list:
        sum_innodb_buffer_pool_read_requests = sum_innodb_buffer_pool_read_requests + int(ii)
    print("逻辑读次数")
    print(dict_show_global_status["Innodb_buffer_pool_read_requests"])
    # (2)物理读取的次数
    sum_innodb_buffer_pool_reads = 0
    innodb_buffer_pool_reads_list = tranfer_status(dict_show_global_status["Innodb_buffer_pool_reads"])
    for ii in innodb_buffer_pool_reads_list:
        sum_innodb_buffer_pool_reads = sum_innodb_buffer_pool_reads + int(ii)
    print("物理读次数")
    print(dict_show_global_status["Innodb_buffer_pool_reads"])

    # 返回相关结果
    return sum_innodb_log_wait, sum_innodb_buffer_pool_read_ahead_rnd, sum_innodb_buffer_pool_read_ahead_evicted, \
           sum_innodb_buffer_pool_reads / sum_innodb_buffer_pool_read_requests


# 读取上一次的参数值
def read_tunning_process(i):
    # 记录返回结果
    param_dict = {}

    # 判断是否进行读取
    flag = False

    # 设置匹配的字符
    start_i = "start_" + str(i - 1)

    # 进行数据的读取
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

                # 进行格式的分割
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
 # 对运行的数据库进行分析， 以获得更好的效果
 内存与磁盘差距是645
 # 主要根据指标进行调参，调参的优先级大致顺序是io, 内存， 锁， 线程
# 参数的优先级定义如下：
# 0, innodb_flush_neighbors
# 1，innodb_read_ahead_threshold
# 2，innodb_random_read_ahead
# 3，innodb_adaptive_hash_index
# 4，innodb_log_buffer_size
# 5，innodb_adaptive_hash_index
# 6，innodb_adaptive_hash_index_parts
# 7，innodb_buffer_pool_instances
# 8，innodb_read_io_threads
# 9，innodb_write_io_threads
# 10, innodb_log_writer_threads
"""


# 进行engine的规则调优
def engine_estimate(engine_status_dict):
    # 记录返回列表
    return_dict = {}

    # file io获取相关的信息列表
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

    # semaphores获取相关的信息列表
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

    # 对buffer pool 进行相关信息分析
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

    # 对INSERT BUFFER AND ADAPTIVE HASH INDEX进行信息提取
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

    # 对transaction进行分析
    transaction_lock_wait_sum_list = []
    for ii in engine_status_dict["transactions"]:
        if ii.get("lock_wait_sum", None) is not None:
            transaction_lock_wait_sum_list.append(ii["lock_wait_sum"])
        else:
            transaction_lock_wait_sum_list.append(0)

    # 用来监控读写线程
    print("读线程的等待次数")
    mid = 0
    print(file_io_pending_normal_aio_reads_list)
    for ii in file_io_pending_normal_aio_reads_list:
        for iii in ii:
            mid = mid + int(iii)
    print(mid)
    return_dict["innodb_read_io_threads"] = mid
    print("写线程等待次数")
    mid = 0
    print(file_io_pending_normal_aio_writes_list)
    for ii in file_io_pending_normal_aio_writes_list:
        for iii in ii:
            mid = mid + int(iii)
    print(mid)
    return_dict["innodb_write_io_threads"] = mid
    # 判定buffer的分区特性
    print("判定缓冲池的分区")
    mid = 0
    for ii in semaphores_buf0buf_list:
        mid = mid + int(ii)
    print(mid)
    return_dict["innodb_buffer_pool_instances"] = mid

    # 判定分区AHI
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

    print("AHI索引")
    mid1 = 0.0
    for ii in insert_AHI_hash_search_list:
        mid1 = mid1 + float(ii)
    print(mid1)
    print("非AHI索引")
    mid2 = 0.0
    for ii in insert_AHI_hash_search_list:
        mid2 = mid1 + float(ii)
    print(mid2)
    return_dict["innodb_adaptive_hash_2"] = [mid1, mid2]

    # 判定预读的特性
    print("判定线性预读")
    mid1 = 0
    for ii in buffer_pool_page_ahead:
        mid1 = mid1 + int(ii)
    print(mid1)
    print("判定随机预读")
    mid2 = 0
    for ii in buffer_pool_random_read_ahead:
        mid = mid2 + int(ii)
    print(mid2)
    print("判定未预读的页数")
    mid3 = 0
    for ii in buffer_pool_page_evicted_without_access:
        mid3 = mid3 + int(ii)
    print(mid3)
    return_dict["innodb_read_ahead"] = [mid1, mid2, mid3]

    return return_dict


# 定义实例个数
def param_innodb_buffer_pool_instance():
    # 记录锁定总数
    sum = 0
    for i in engine_status_dict["semaphores"]:
        sum = sum + i["buf0buf"]
    return sum


# 定义log_buffer的大小
def param_innodb_log_buffer_size():
    length = len(dict_show_global_status["Innodb_log_waits"]) - 1
    sum = dict_show_global_status["Innodb_log_waits"][length] - dict_show_global_status["Innodb_log_waits"][0]
    return sum


def log_buffer():
    max_value = 0
    for i_log in engine_status_dict["LOG"]:
        max_value = max(max_value, (i_log["Log sequence number"] - i_log["Log flushed up to"]) / 1024 / 1024)

    return max_value


# 修改change_buffer的大小
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


# 对调参判断的指标,最好计算出随机读与顺序读的iops是33倍（通过fio的随机读和顺序读得出比例是33）,同时根据吞吐量进行判断
def param_innodb_read_ahead_threshold(mid_dict_show_global_status):
    # 定义num的数值
    num = 0
    read_ahead = mid_dict_show_global_status["Innodb_buffer_pool_read_ahead"]
    read_ahead_evicted = mid_dict_show_global_status["Innodb_buffer_pool_read_ahead_evicted"]
    read_ahead = tranfer_status(read_ahead)
    read_ahead_evicted = tranfer_status(read_ahead_evicted)

    # 获取总值
    sum_read_ahead = 0
    sum_read_ahead_evicted = 0

    # 进行是否线性预读判断
    for i in read_ahead[num:]:
        sum_read_ahead = sum_read_ahead + i
    for i in read_ahead_evicted[num:]:
        sum_read_ahead_evicted = sum_read_ahead_evicted + i

    sum_read_ahead_used = sum_read_ahead - sum_read_ahead_evicted

    return sum_read_ahead


# 对调参判断的指标,最好计算出随机读与顺序读的iops是33倍（通过fio的随机读和顺序读得出比例是33）,其结果不稳定，一般不调整
def param_innodb_random_read_ahead():
    # 定义num的数值
    num = 7
    read_ahead_rnd = dict_show_global_status["Innodb_buffer_pool_read_ahead_rnd"]
    read_ahead_evicted = dict_show_global_status["Innodb_buffer_pool_read_ahead_evicted"]
    read_ahead_rnd = tranfer_status(read_ahead_rnd)
    read_ahead_evicted = tranfer_status(read_ahead_evicted)

    print(read_ahead_rnd)
    print(read_ahead_evicted)

    # 获取总值
    sum_read_ahead_rnd = 0
    sum_read_ahead_evicted = 0

    # 进行是否随机预读判断
    for i in read_ahead_rnd[num:]:
        sum_read_ahead_rnd = sum_read_ahead_rnd + i
    for i in read_ahead_evicted[num:]:
        sum_read_ahead_evicted = sum_read_ahead_evicted + i

    print(sum_read_ahead_rnd, sum_read_ahead_evicted)
    if sum_read_ahead_rnd == 0 or sum_read_ahead_rnd == sum_read_ahead_evicted:
        print("不进行线性预读")
        return False
    elif sum_read_ahead_evicted / (sum_read_ahead_rnd - sum_read_ahead_evicted) < 33:
        print("进行线性预读")
        return True
    else:
        print("不进行线性预读")
        return False


# 对参数hash_index进行调试
def param_hash_index():
    # 锁的总数
    sum_btr0sea = 0
    for i in engine_status_dict["semaphores"]:
        sum_btr0sea = sum_btr0sea + i["btr0sea"]

    # hash_index的相关统计
    sum_hash = 0
    sum_no_hash = 0
    for i in engine_status_dict["insert_AHI"]:
        sum_hash = sum_hash + i["hash_searches/s"]
        sum_no_hash = sum_no_hash + i["non-hash_searches/s"]
    return sum_btr0sea, sum_hash, sum_no_hash


# 进行读写io线程的配置,目标是保持io总和等于逻辑cpu数量，主要参考两个指标，为以后判断
def param_read_and_write_io_thread():
    # 记录engine的读写比例
    engine_length = len(engine_status_dict["buffer_pool"]) - 1
    engine_read = engine_status_dict["buffer_pool"][engine_length]["Pages_read"] - engine_status_dict["buffer_pool"][0]["Pages_read"]
    engine_write = engine_status_dict["buffer_pool"][engine_length]["written"] - engine_status_dict["buffer_pool"][0]["written"]

    # 记录status的读写比例
    status_length = len(dict_show_global_status["Innodb_dblwr_writes"]) - 1
    status_write = dict_show_global_status["Innodb_buffer_pool_pages_flushed"][status_length] - dict_show_global_status["Innodb_buffer_pool_pages_flushed"][0]
    status_write = status_write + dict_show_global_status["Innodb_dblwr_writes"][status_length] - dict_show_global_status["Innodb_dblwr_writes"][0]
    status_read = dict_show_global_status["Innodb_buffer_pool_reads"][status_length] - dict_show_global_status["Innodb_buffer_pool_reads"][0]

    return [(status_read, status_write), (engine_read, engine_write)]


# 定义需要调整的参数
def def_tune_param():
    # 需要调整的参数设置为1，不需要调整的参数设置为0
    global tune_param
    # 初始化参数 14个
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

    # 指标相关参数
    tune_param["innodb_log_buffer_size"] = 1
    # cpu相关参数 4个 + (还有4个初始化参数)
    tune_param["innodb_sync_spin_loops"] = 1
    tune_param["innodb_concurrency_tickets"] = 1
    tune_param["innodb_log_wait_for_flush_spin_hwm"] = 1
    tune_param["innodb_log_writer_threads"] = 1
    # io相关参数 6个 + (1个初始化， 1个重叠)
    tune_param["innodb_extend_and_initialize"] = 1
    tune_param["innodb_adaptive_hash_index"] = 1
    tune_param["innodb_adaptive_hash_index_parts"] = 1
    tune_param["innodb_change_buffer_max_size"] = 1
    tune_param["innodb_lru_scan_depth"] = 1
    tune_param["innodb_read_ahead_threshold"] = 1
    tune_param["innodb_use_fdatasync"] = 1

    # 与锁相关 3个 + (1个重叠)
    tune_param["innodb_sync_array_size"] = 1
    tune_param["innodb_deadlock_detect"] = 1
    tune_param["innodb_lock_wait_timeout"] = 1


# 初始化参数
def initialization_parameters():
    """
    1， 进行参数初始化，初始化的参数如下
    (1)innodb_thread_concurrency = cpu逻辑核数*2
    (2)innodb_log_file_size = 能用的最大磁盘空间
    (3）innodb_log_files_in_group 默认为2
    (4)innodb_buffer_pool_size = 最大可用的内存
    (5)innodb_buffer_pool_instances = math.ceil(innodb_buffer_pool_size/1024)
    (6)innodb_read_io_threads = 默认cpu逻辑核数，以后工作负载读比例*cpu逻辑核数/2
    (7)innodb_write_io_threads = 默认cpu逻辑核数，以后工作负载写比例*cpu逻辑核数/2
    (8)innodb_io_capacity = 磁盘最大iops的50%
    (9)innodb_io_capacity_max = 磁盘最大iops
    (10)innodb_flush_neighbors = 0 (随机iops与顺序iops差不多) 否则选择其他参数探索
    (11)innodb_flush_method = 一般选择fsync， 除非随机iops与顺序iops差不多,则选择O_DSYNC
    (12)innodb_page_cleaners = min(等于分区数, 4)
    (13)innodb_purge_threads = min（表的数量，4）
	(14）innodb_random_read_ahead 默认关闭
	(innodb_log_buffer_size = 默认值)
    2， 设定下列参数为系统默认值：
    2.1 cpu相关
    (1)innodb_sync_spin_loops
    (2)innodb_concurrency_tickets（跟事务大小有关）
    (3)innodb_log_wait_for_flush_spin_hwm（用户线程日志平均刷新的spin最大上限）
    (4)innodb_log_writer_threads（io）
    (5)innodb_read_io_threads = 默认cpu逻辑核数，以后工作负载读比例*cpu逻辑核数/2
    (6)innodb_write_io_threads = 默认cpu逻辑核数，以后工作负载写比例*cpu逻辑核数/2
    (7)innodb_page_cleaners
    (8)innodb_purge_threads
    2.2 io相关
    (1)innodb_adaptive_hash_index（占用内存）
    (2)innodb_adaptive_hash_index_parts（减少线程的锁竞争）
    (3)innodb_change_buffer_max_size（优化磁盘io，是否有二级索引）可以计算的
    (4)innodb_read_ahead_threshold
    innodb_flushing_avg_loops(计算刷新速率)该参数待定
    (5)innodb_lru_scan_depth（io）
    (6)innodb_log_writer_threads（io）
    (7)innodb_io_capacity = 磁盘最大iops的50%
    (8)innodb_io_capacity_max = 磁盘最大iops
    (9)innodb_flush_neighbors(磁盘io)
    (10)innodb_extend_and_initialize = 0 申请空间不写null值
    2.3与锁相关
    (1)innodb_sync_array_size(建议cpu核数，768等待，探索)
    (2)innodb_deadlock_detect （是否进行死锁检测）
    (3)innodb_lock_wait_timeout（行锁的超时时间）
    (4)innodb_buffer_pool_instances(减少线程的锁竞争)有指标
    (5)innodb_adaptive_hash_index_parts
    """
    # innodb_thread_concurrency, innodb_buffer_pool_size, innodb_buffer_pool_size必须一起，最好添加

    # 定义返回列表
    return_dict = {}

    global cpu_num_all
    cpu_num = cpu_num_all
    global tune_param
    # 1，初始化参数innodb_thread_concurrency
    if tune_param["innodb_thread_concurrency"] == 1:
        return_dict["innodb_thread_concurrency"] = cpu_num * 2

    # 2，初始化参数innodb_log_file_size
    if tune_param["innodb_log_file_size"] == 1:
        innodb_log_file_size = math.floor(disk_resource / 2)
        return_dict["innodb_log_file_size"] = innodb_log_file_size

    # 3，初始化参数innodb_log_files_in_group
    if tune_param["innodb_log_files_in_group"] == 1:
        return_dict["innodb_log_files_in_group"] = 2

    # 4，5初始化参数：innodb_buffer_pool_size， innodb_buffer_pool_instances
    if tune_param["innodb_buffer_pool_size"] == 1 and tune_param["innodb_buffer_pool_instances"] == 1:
        innodb_buffer_pool_size = memory_resource
        innodb_buffer_pool_instances = min(64, math.ceil(innodb_buffer_pool_size / 1024))
        per_size = math.floor(innodb_buffer_pool_size / innodb_buffer_pool_instances)
        innodb_buffer_pool_chunk_size = per_size
        innodb_buffer_pool_size = innodb_buffer_pool_chunk_size * innodb_buffer_pool_instances
        return_dict["innodb_buffer_pool_size"] = innodb_buffer_pool_size
        return_dict["innodb_buffer_pool_instances"] = innodb_buffer_pool_instances
        return_dict["innodb_buffer_pool_chunk_size"] = innodb_buffer_pool_chunk_size

    # 6初始化参数innodb_read_io_threads
    if tune_param["innodb_read_io_threads"] == 1:
        return_dict["innodb_read_io_threads"] = int(cpu_num / 2)

    # 7初始化参数innodb_write_io_threads
    if tune_param["innodb_write_io_threads"] == 1:
        return_dict["innodb_write_io_threads"] = int(cpu_num / 2)

    # 8，9初始化参数innodb_io_capacity， innodb_io_capacity_max
    if tune_param["innodb_io_capacity"] == 1 and tune_param["innodb_io_capacity_max"] == 1:
        return_dict["innodb_io_capacity"] = 2700  # 经过fio测试可得
        return_dict["innodb_io_capacity_max"] = 5400  # 经过fio测试可得

    # 10初始化参数innodb_flush_neighbors，根据随机iops与顺序iops
    if tune_param["innodb_flush_neighbors"] == 1:
        return_dict["innodb_flush_neighbors"] = 0

    # 11初始化参数innodb_flush_method, 根据随机iops与顺序iops
    if tune_param["innodb_flush_method"] == 1:
        return_dict["innodb_flush_method"] = "fsync"  # 查询磁盘参数可得

    # 12，初始化参数innodb_page_cleaners
    if tune_param["innodb_page_cleaners"] == 1:
        return_dict["innodb_page_cleaners"] = min(return_dict["innodb_buffer_pool_instances"], 4)

    # 13，初始化参数innodb_purge_threads
    if tune_param["innodb_purge_threads"] == 1:
        return_dict["innodb_purge_threads"] = min(4, num_table)

    # 14，修改参数innodb_random_read_ahead
    if tune_param["innodb_random_read_ahead"] == 1:
        return_dict["innodb_random_read_ahead"] = 0

    # 15 修改参数innodb_log_buffer_size
    if tune_param["innodb_log_buffer_size"] == 1:
        return_dict["innodb_log_buffer_size"] = 16

    # 16 修改参数innodb_use_fdatasync
    if tune_param["innodb_use_fdatasync"] == 1:
        return_dict["innodb_use_fdatasync"] = 1

    # 设定下列参数为innodb的默认值,这里显式的写出来以便于查看
    # cpu 相关参数
    """
    (1)innodb_thread_concurrency(探索)
    (2)innodb_sync_spin_loops
    (3)innodb_concurrency_tickets（跟事务大小有关）
    (4)innodb_log_wait_for_flush_spin_hwm（用户线程日志平均刷新的spin最大上限）
    (5)innodb_log_writer_threads（io）
    (6)innodb_page_cleaners（已经初始化）
    (7)innodb_purge_threads（已经初始化）
    下面两个必须一起
    (7)innodb_read_io_threads = 默认cpu逻辑核数，以后工作负载读比例*cpu逻辑核数/2（已经初始化）
    (8)innodb_write_io_threads = 默认cpu逻辑核数，以后工作负载写比例*cpu逻辑核数/2（已经初始化）

    """
    return_dict["innodb_sync_spin_loops"] = 30
    return_dict["innodb_concurrency_tickets"] = 5000
    return_dict["innodb_log_writer_threads"] = 1
    return_dict["innodb_log_wait_for_flush_spin_hwm"] = 400

    # 把调优的参数写入集合
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

    # io相关参数
    """
    # 下面两个必须一起
    (1)innodb_adaptive_hash_index（占用内存）
    (2)innodb_adaptive_hash_index_parts（减少线程的锁竞争）

    (3)innodb_change_buffer_max_size（优化磁盘io，是否有二级索引）可以计算的
    (4)innodb_read_ahead_threshold
    innodb_flushing_avg_loops(计算刷新速率)该参数待定
    (5)innodb_lru_scan_depth（io）
    (6)innodb_log_writer_threads（io）
    (7)innodb_io_capacity = 磁盘最大iops的50%
    (8)innodb_io_capacity_max = 磁盘最大iops
    (9)innodb_flush_neighbors(磁盘io) (已经初始化)
    (10)innodb_extend_and_initialize = 0 申请空间不写null值
    """
    return_dict["innodb_log_writer_threads"] = 1
    # 修改默认参数
    return_dict["innodb_read_ahead_threshold"] = 56
    return_dict["innodb_adaptive_hash_index"] = 1
    return_dict["innodb_change_buffer_max_size"] = 25
    return_dict["innodb_adaptive_hash_index_parts"] = 8
    return_dict["innodb_lru_scan_depth"] = 1024
    return_dict["innodb_extend_and_initialize"] = 1

    # 把调优的参数写入集合
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

    # 与锁相关参数
    """
    (1)innodb_sync_array_size(建议cpu核数，768等待，探索)
    # 下面两个必须一起
    (2)innodb_deadlock_detect （是否进行死锁检测）
    (3)innodb_lock_wait_timeout（行锁的超时时间）
    (4)innodb_buffer_pool_instances(减少线程的锁竞争)有指标(已经初始化)
    (5)innodb_adaptive_hash_index_parts
    """
    return_dict["innodb_sync_array_size"] = 1
    return_dict["innodb_deadlock_detect"] = 1
    return_dict["innodb_lock_wait_timeout"] = 50
    return_dict["innodb_adaptive_hash_index_parts"] = 8

    # 把调优的参数写入集合
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

    # 返回参数字典
    return return_dict


# 获取当先工作负载的吞吐量
def get_throught():
    # 设置变量
    mid_throught = 0
    mid_latency = 0

    # 数据库复原
    data_recovery()

    # 清空缓存
    free_cache()

    # 启动数据库
    start_mysql()

    # 运行数据库
    (mid_throught, mid_latency) = run_mysql_for_oltp()

    # 关闭数据库
    stop_mysql()

    # 进行数据库休眠
    time.sleep(10)

    return mid_throught


# 初始化 my.cnf的格式
def initialization_my_cnf():
    # 进行配置参数的初始化
    my_cnf_list = []
    with open(path_my_cnf, 'r') as f:
        for ii in f.readlines():
            if "tuning param" in ii:
                my_cnf_list.append(ii)
                break
            else:
                my_cnf_list.append(ii)

    # 把配置文件写入my.cnf
    with open(path_my_cnf, 'w') as f:
        for ii in my_cnf_list:
            f.write(ii)
        f.flush()


# 写配置文件,注意每次写my.cnf都要初始化
def write_my_cnf(param_dict, param_unit_dict):
    # 进行文件my.cnf的初始化
    initialization_my_cnf()

    # 写入param_dict
    with open(path_my_cnf, 'a') as f:
        for ii in param_dict:
            if "throught" in ii or "start" in ii or "param" in ii or "test" in ii:
                continue
            if param_unit_dict.get(ii, None) is None:
                f.write(str(ii) + "=" + str(param_dict[ii]) + "\n")
            else:
                f.write(str(ii) + "=" + str(param_dict[ii]) + str(param_unit_dict[ii]) + "\n")
        f.flush()


# 读取配置文件my.cnf
def read_my_cnf():
    # 记录当前配置
    return_list = []
    # 读取当前配置
    with open(path_my_cnf, 'r') as f:
        flag_mysqlld = False
        for ii in f.readlines():
            if "tuning param" in ii:
                flag_mysqlld = True
            elif flag_mysqlld is True:
                return_list.append(ii)
    return return_list


# 进行数据的运行和把参数写入文件
def run_and_write_file(param_dict, param_unit_dict, i, param_dict_list, ii):
    # 写参数值到配置文件
    write_my_cnf(param_dict, param_unit_dict)

    # 获取吞吐量
    mid_throught = get_throught()
    param_dict["throught"] = mid_throught

    # 把当前的参数值记录，以便下次使用
    param_dict_list.append(param_dict)
    print("显示本次迭代次数及其迭代的参数值")
    print("-----------------------------")
    global cnt
    print("cnt is %d" % cnt)
    cnt = cnt + 1
    print("-----------------------------")
    for ii in param_dict:
        print(ii, param_dict[ii])
    print("-----------------------------")

    # 返回所有迭代的参数列表
    return param_dict_list


# 记录根据中间值探索的参数
def param_mid_value_tuning_2(value, param_dict, param, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck, diff_value, min=0, max=0):
    # 记录该参数是否第一次
    param_dict[param] = value
    global mysql_sum_time
    # 各种状态赋值
    mid_dict_show_global_status = dict_show_global_status
    mid_engine_status_dict = engine_status_dict
    mid_str_bottleneck = str_bottleneck
    flag_while_1 = False
    if param_dict[param] - diff_value > min:
        flag_while_1 = True

    # value值进行减小测试
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

    # value值进行扩大测试
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


# 记录根据中间值探索的参数
def param_mid_value_tuning_max(value, param_dict, param, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck, diff_value, min=0, max=0):
    # 记录该参数是否第一次
    param_dict[param] = value
    global mysql_sum_time

    # 各种状态赋值
    mid_dict_show_global_status = copy.deepcopy(dict_show_global_status)
    mid_engine_status_dict = copy.deepcopy(engine_status_dict)
    mid_str_bottleneck = copy.deepcopy(str_bottleneck)

    flag_while_1 = False
    if param_dict[param] - diff_value > min:
        flag_while_1 = True

    # value值进行减小测试
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

    # value值进行扩大测试
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


# 记录根据中间值探索的参数, value值默认参数值
def param_mid_value_tuning(value, param_dict, param, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck, min=0, max=0):
    global mysql_sum_time

    # 记录默认值
    param_dict[param] = value

    # 各种状态赋值
    mid_dict_show_global_status = dict_show_global_status
    mid_engine_status_dict = engine_status_dict
    mid_str_bottleneck = str_bottleneck

    flag_while_1 = False
    if (param_dict[param] / 2) > min:
        flag_while_1 = True

    # value值进行减小测试
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

    # value值进行扩大测试
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


# 获取cpu和io的利用率
def analysis_bottleneck():
    """
    获取cpu和io的利用率
    """
    result_sar_u = analysis_sar_u(path_sar_u)
    result_sar_d = analysis_sar_d(path_sar_d)

    print(result_sar_d)
    print(result_sar_u)

    percent_cpu = 0
    percent_io = 0

    # 获取cpu的利用率
    length = len(result_sar_u["%idle"]) - 2
    for i in result_sar_u["%idle"][2:]:
        percent_cpu = percent_cpu + float(i)
    percent_cpu = percent_cpu / length

    # 获取io的利用率
    length = len(result_sar_d["%util"]) - 2
    for i in result_sar_d["%util"][2:]:
        percent_io = percent_io + float(i)
    percent_io = percent_io / length

    # 返回io与cpu的利用率
    print(percent_io, 100 - percent_cpu)

    return percent_io, 100 - percent_cpu


# 判断系统瓶颈
def judge_bottleneck(str_bottleneck, flag_param_IO, flag_param_CPU, flag_param_LATCH):
    """
   cpu瓶颈的判断规则是：
   注意>=50%
   告警>=70%
   严重>=90%
   io瓶颈的判断规则是：
   注意>=40%
   告警>=60%
   严重>=80%
   锁的瓶颈是：
   cpu小于<90%并且io<80%
   """

    # print("--------------")
    # print("系统瓶颈分析")
    # print(flag_param_IO, flag_param_CPU, flag_param_LATCH)
    # print(str_bottleneck)
    # print("---------------")
    # # 当出现io瓶颈时，进行瓶颈参数判断
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
    # # 当出现CPU瓶颈时， 进行瓶颈参数判断
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
    # # 当出现锁瓶颈的时候， 进行瓶颈参数判断
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
    主要进行数据库innodb整个调优过程的迭代
    """

    # 记录总共花费时间
    mysql_sum_time = 0

    start_now_time = time.time()

    # 设定可用资源的内存资源，单位M
    memory_resource = 548

    # 设定可用的磁盘资源,单位M
    disk_resource = 300

    # 设定最大的迭代次数
    iterations_num = 150

    # 记录当前最好的参数列表和吞吐量
    param_dict = {}

    # 记录整个调参过程
    param_dict_list = []

    # 记录当前调整的io相关的参数
    flag_param_IO = "start"

    # 记录当前调整的cpu相关的参数
    flag_param_CPU = "start"

    # 记录当前调整的LATCH相关的参数
    flag_param_LATCH = "start"

    # read_ahead的标志位
    mid_flag_read_ahead = False

    # hash_index的标志位
    mid_flag_hash_index = False

    # 记录随时更新的innodb_buffer_pool_chunk_size值
    mid_chunk_size = None

    # 进行循环的次数训练
    flag_loop = True

    # 记录需要输入M单位的参数
    param_unit_dict = {}
    param_unit_dict["innodb_buffer_pool_size"] = "M"
    param_unit_dict["innodb_buffer_pool_chunk_size"] = "M"
    param_unit_dict["innodb_log_file_size"] = "M"
    param_unit_dict["innodb_log_buffer_size"] = "M"

    # 记录所要调优的io集合
    IO_param_list = []

    # 记录所要调优的cpu集合
    CPU_param_list = []

    # 记录所要调优的latch集合
    LATCH_param_list = []

    # 临时保存，便于以后循环
    mid_IO_list = []
    mid_CPU_list = []
    mid_LATCH_list = []

    # 主要用于是否结束循环
    max_iter_value = 0

    # 记录迭代次数
    i = 0

    # 进行参数的迭代修改
    while i < iterations_num:

        # 主要记录当下的吞吐量,起始值是0
        throught = -1

        # 第一次迭代，主要进行初始化
        if i == 0:

            # 进行调优的过程，写在文件tuning_process(tunning_process_path)中
            os.system(clean_tuning_process)

            # 定义需要调优的参数
            def_tune_param()

            # 进行参数初始化
            param_dict = initialization_parameters()

            for i_param_dict in param_dict:
                print(i_param_dict, param_dict[i_param_dict])

            # 记录mid_chunk_size的值
            mid_chunk_size = param_dict["innodb_buffer_pool_chunk_size"]

            now_time = time.time()

            # 写配置参数到my.cnf
            param_dict_list = run_and_write_file(copy.copy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)

            mysql_sum_time = mysql_sum_time + time.time() - now_time

            # 读取上一次的参数列表
            param_dict = copy.deepcopy(param_dict_list[len(param_dict_list) - 1])

            # 获取show global status like '%innodb%'字典
            dict_show_global_status = analysis_show_global_status(status_path)

            # 获取show engine innodb status
            engine_status_dict = analysis_model()

            # 获取系统信息
            str_bottleneck = analysis_bottleneck()

            # 进行复制，便于以后循环使用
            mid_IO_list = copy.deepcopy(IO_param_list)
            mid_CPU_list = copy.deepcopy(CPU_param_list)
            mid_LATCH_list = copy.deepcopy(LATCH_param_list)

            # 尝试性修改参数log_buffer
            mid_value = math.ceil(log_buffer())
            print("进行log_buffer判断")
            print(mid_value)
            if param_dict["innodb_log_buffer_size"] == mid_value:
                continue
            else:
                param_dict["innodb_buffer_pool_size"] = param_dict["innodb_buffer_pool_size"] + (param_dict["innodb_log_buffer_size"] - mid_value)
                param_dict["innodb_log_buffer_size"] = mid_value

                # 进行相应的参数调整
                innodb_buffer_pool_size = param_dict["innodb_buffer_pool_size"]
                innodb_buffer_pool_instances = param_dict["innodb_buffer_pool_instances"]
                innodb_buffer_pool_chunk_size = param_dict["innodb_buffer_pool_chunk_size"]

                # 计算buffer_pool,chunk_size的值
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


        # 进行系统瓶颈系统判断
        else:
            """
            log_buffer保持足够内存空间，不能成为瓶颈
            """
            print(tune_param)
            print(param_innodb_log_buffer_size())
            # 如果log_buffer不是瓶颈的情况
            if tune_param["innodb_log_buffer_size"] == 0 or tune_param["innodb_log_buffer_size"] == 1 and param_innodb_log_buffer_size() == 0:

                # 进行系统瓶颈判断
                print("iiiiiii")
                is_bottleneck = judge_bottleneck(str_bottleneck, flag_param_IO, flag_param_CPU, flag_param_LATCH)

                if is_bottleneck == "IO":
                    """
                   按照下面逆序进行参数调整
                   (1)innodb_adaptive_hash_index（占用内存）
                   (2)innodb_adaptive_hash_index_parts（减少线程的锁竞争）
                   (3)innodb_change_buffer_max_size（优化磁盘io，是否有二级索引）可以计算的
                   innodb_read_ahead_threshold
                   innodb_flushing_avg_loops(计算刷新速率)该参数待定
                   (5)innodb_lru_scan_depth（io）
                   (6)innodb_log_writer_threads（io）
                   (8)innodb_io_capacity_max = 磁盘最大iops
                   (7)innodb_io_capacity = 磁盘最大iops的50%
                   (9)innodb_flush_neighbors(磁盘io)
                   (10)innodb_extend_and_initialize
                   """
                    print("判断为io瓶颈，调整io瓶颈相关参数")
                    for io_param in IO_param_list:
                        print("进行参数{}调整".format(io_param))
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
                                # 跳出当前循环
                            break

                        elif io_param == "innodb_extend_and_initialize":
                            if param_dict["innodb_extend_and_initialize"] == 1:
                                param_dict["innodb_extend_and_initialize"] = 0
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    print("为0效果好")
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()
                                else:
                                    print("为1以前效果好")
                                    param_dict["innodb_extend_and_initialize"] = 1
                                # 跳出当前循环
                                break
                            else:
                                param_dict["innodb_extend_and_initialize"] = 1
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    print("为1效果好")
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()
                                else:
                                    print("为0以前效果好")
                                    param_dict["innodb_extend_and_initialize"] = 0
                                # 跳出当前循环
                                break

                        elif io_param == "innodb_flush_neighbors":
                            # 如果参数不是机械硬盘
                            if param_dict["innodb_flush_neighbors"] == 0:
                                print("随机iops与顺序iops差不多，故不刷新相邻数据源")

                            # 如果参数是机械硬盘
                            else:
                                param_dict["innodb_flush_neighbors"] = 2
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    print("参数2的效果好")
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()
                                else:
                                    print("参数1的效果好")
                                    param_dict["innodb_flush_neighbors"] = 1
                            # 跳出当前循环
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
                                    print("不存在log_writer的瓶颈")
                                    if param_dict["throught"] > param_dict_list[len(param_dict_list) - 1]["throught"]:
                                        print("启用log_writer")
                                        param_dict["innodb_log_writer_threads"] = 1
                                    else:
                                        print("关闭log_writer")
                                        param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                        dict_show_global_status = analysis_show_global_status(status_path)
                                        engine_status_dict = analysis_model()
                                        str_bottleneck = analysis_bottleneck()
                                else:
                                    print("存在log_writer的瓶颈")
                                    innodb_buffer_pool_size_all = param_dict["innodb_buffer_pool_size"]
                                    innodb_buffer_pool_chunk_size_all = param_dict["innodb_buffer_pool_chunk_size"]
                                    innodb_log_buffer_size_all = param_dict["innodb_log_buffer_size"]
                                    while True:
                                        innodb_buffer_pool_size = param_dict["innodb_buffer_pool_size"]
                                        innodb_buffer_pool_instances = param_dict["innodb_buffer_pool_instances"]
                                        innodb_buffer_pool_chunk_size = param_dict["innodb_buffer_pool_chunk_size"]
                                        innodb_buffer_pool_size_1 = innodb_buffer_pool_size - param_dict["innodb_log_buffer_size"]
                                        param_dict["innodb_log_buffer_size"] = param_dict["innodb_log_buffer_size"] * 2

                                        # 计算buffer_pool_instance的总数
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
                                                print("上一次迭代较好")
                                                param_dict["innodb_log_buffer_size"] = innodb_log_buffer_size_all
                                                param_dict["innodb_buffer_pool_size"] = innodb_buffer_pool_size_all
                                                param_dict["innodb_buffer_pool_chunk_size"] = innodb_buffer_pool_chunk_size_all
                                                param_dict["innodb_log_writer_threads"] = 1
                                            else:
                                                print("本次迭代较好")
                                                param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                                dict_show_global_status = analysis_show_global_status(status_path)
                                                engine_status_dict = analysis_model()
                                                str_bottleneck = analysis_bottleneck()
                                            break
                            # 跳出当前循环
                            break

                        elif io_param == "innodb_lru_scan_depth":
                            param_dict, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck = \
                                param_mid_value_tuning(1024, copy.deepcopy(param_dict), "innodb_lru_scan_depth", copy.deepcopy(param_dict_list),
                                                       dict_show_global_status, engine_status_dict, str_bottleneck, 100, 1024 * 10)
                            # 跳出当前循环
                            break

                        elif io_param == "innodb_read_ahead_threshold":

                            # 判定是否存在第一个预读为0的情况
                            if param_innodb_read_ahead_threshold(dict_show_global_status) == 0:
                                print("第一个预读为0")
                                mid_flag_read_ahead = True

                            # 记录吞吐量的和
                            sum_value = param_dict["throught"]

                            # 判断是否连续
                            mid_consecutive = True

                            # 统计次数
                            sum_cnt = 1

                            # 对预读是为0进行判断
                            if mid_flag_read_ahead is True:
                                while True:
                                    param_dict["innodb_read_ahead_threshold"] = param_dict["innodb_read_ahead_threshold"] - 8
                                    now_time = time.time()
                                    param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "read_ahead")
                                    mysql_sum_time = mysql_sum_time + time.time() - now_time

                                    if param_dict["throught"] > param_dict_list[len(param_dict_list) - 1]["throught"]:
                                        print("当前吞吐量较小")
                                        param_dict["innodb_read_ahead_threshold"] = param_dict["innodb_read_ahead_threshold"] + 8
                                        break
                                    else:
                                        print("当前吞吐量较好")
                                        param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                        dict_show_global_status = analysis_show_global_status(status_path)
                                        engine_status_dict = analysis_model()
                                        str_bottleneck = analysis_bottleneck()
                                        # 达到最小值则停止read_ahead迭代
                                        if param_dict["innodb_read_ahead_threshold"] - 8 < 0:
                                            break

                            # 对预读不为0进行判断
                            else:
                                while True:
                                    param_dict["innodb_read_ahead_threshold"] = param_dict["innodb_read_ahead_threshold"] - 8
                                    now_time = time.time()
                                    param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "read_ahead")
                                    mysql_sum_time = mysql_sum_time + time.time() - now_time
                                    if param_dict["throught"] > param_dict_list[len(param_dict_list) - 1]["throught"]:
                                        print("当前吞吐量较小")
                                        param_dict["innodb_read_ahead_threshold"] = param_dict["innodb_read_ahead_threshold"] + 8
                                        break
                                    else:
                                        print("当前吞吐量较好")
                                        param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                        dict_show_global_status = analysis_show_global_status(status_path)
                                        engine_status_dict = analysis_model()
                                        str_bottleneck = analysis_bottleneck()
                                        # 达到最小值则停止read_ahead迭代
                                        if param_dict["innodb_read_ahead_threshold"] - 8 < 0:
                                            break

                                # 如果是默认值
                                flag_while = False
                                if param_dict["innodb_read_ahead_threshold"] == 56:
                                    flag_while = True
                                while flag_while:
                                    param_dict["innodb_read_ahead_threshold"] = param_dict["innodb_read_ahead_threshold"] + 8
                                    now_time = time.time()
                                    param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "read_ahead")
                                    mysql_sum_time = mysql_sum_time + time.time() - now_time

                                    if param_dict["throught"] > param_dict_list[len(param_dict_list) - 1]["throught"]:
                                        print("当前吞吐量较小")
                                        param_dict["innodb_read_ahead_threshold"] = param_dict["innodb_read_ahead_threshold"] - 8
                                        break
                                    else:
                                        print("当前吞吐量较好")
                                        param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                        dict_show_global_status = analysis_show_global_status(status_path)
                                        engine_status_dict = analysis_model()
                                        str_bottleneck = analysis_bottleneck()
                                        # 达到最小值则停止read_ahead迭代
                                        if param_dict["innodb_read_ahead_threshold"] + 8 > 64:
                                            break
                            # 跳出当前循环
                            break

                        elif io_param == "innodb_change_buffer_max_size":

                            mid_value = 25
                            mid_return = param_innodb_change_buffer()
                            print("free, sum")
                            print(mid_return)
                            if mid_return[1] / 64 / param_dict["innodb_buffer_pool_size"] < 0.25:
                                # if mid_return[1] - mid_return[0] + mid_return[1] * 0.1 < mid_return[1]:
                                #     print("change_buffer有空闲页")
                                #     if (mid_return[1] - mid_return[0]) * 1.2 < mid_return[1]:
                                #         print("空闲页很多")
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
                                    print("启用change_buffer较好")
                                    param_dict["innodb_change_buffer_max_size"] = 25
                                else:
                                    print("关闭change_buffer较好")
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()
                            else:
                                print("change_buffer没有空闲页")
                                param_dict["innodb_change_buffer_max_size"] = 50
                                print("运行最大的change_buffer")
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "change_buffer")
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    print("关闭change_buffer较好")
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()
                                else:
                                    print("启用change_buffer较好")
                                    param_dict["innodb_change_buffer_max_size"] = 25
                                # if (mid_return[1] - mid_return[0]) * 1.2 < mid_return[1]:
                                #     print("空闲页很多")
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
                                    print("关闭change_buffer较好")
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()
                                else:
                                    print("启用change_buffer较好")
                                    param_dict["innodb_change_buffer_max_size"] = mid_value

                            # 跳出当前循环
                            break

                        elif io_param == "innodb_adaptive_hash_index":  # 这里是两个参数一起调优
                            mid_return = param_hash_index()
                            print("btr0sea, hash-sum, no-hash-sum")
                            print(mid_return)
                            # 如果btr0sea的个数为0
                            if mid_return[0] == 0 and param_dict["innodb_adaptive_hash_index"] == 1:
                                print("btr0sea为0")
                                param_dict["innodb_adaptive_hash_index"] = 0
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "hash_index")
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] > param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    print("启用hash_index较好")
                                    param_dict["innodb_adaptive_hash_index"] = 1
                                else:
                                    print("不启用hash_index较好")
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()

                            # 如果btr0sea的个数不为0
                            print("btr0sea不为0")
                            while mid_return[0] > 0 and param_dict["innodb_adaptive_hash_index"] == 1:
                                param_dict["innodb_adaptive_hash_index_parts"] = param_dict["innodb_adaptive_hash_index_parts"] * 2
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "hash_index")
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                # 如果上一次吞吐量大
                                if param_dict["throught"] > param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    print("分区*2效果不好")
                                    param_dict["innodb_adaptive_hash_index_parts"] = int(param_dict["innodb_adaptive_hash_index_parts"] / 2)
                                    param_dict["innodb_adaptive_hash_index"] = 0
                                    now_time = time.time()
                                    param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "hash_index")
                                    mysql_sum_time = mysql_sum_time + time.time() - now_time
                                    # 如果上一次吞吐量大
                                    print("是否启用hash_index")
                                    if param_dict_list[len(param_dict_list) - 1]["throught"] < param_dict["throught"]:
                                        print("启用hash_index较好")
                                        param_dict["innodb_adaptive_hash_index"] = 1
                                    # 如果本次吞吐量大
                                    else:
                                        print("关闭hash_index较好")
                                        dict_show_global_status = analysis_show_global_status(status_path)
                                        engine_status_dict = analysis_model()
                                        str_bottleneck = analysis_bottleneck()
                                        param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    break
                                # 如果本次吞吐量大
                                else:
                                    print("分区数*2较高")
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()

                            # 跳出当前循环
                            break

                    print("当前最好的参数选项")
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
                    5,innodb_read_io_threads = 默认cpu逻辑核数，以后工作负载读比例*cpu逻辑核数/2
                    6,innodb_write_io_threads = 默认cpu逻辑核数，以后工作负载写比例*cpu逻辑核数/2
                    7,innodb_purge_threads
                    8,innodb_page_cleaners
                    (1)innodb_sync_spin_loops
                    (2)innodb_concurrency_tickets（跟事务大小有关）
                    (3)innodb_log_wait_for_flush_spin_hwm（用户线程日志平均刷新的spin最大上限）
                    (4)innodb_log_writer_threads（io）
                    (5)innodb_page_cleaners（已经初始化）
                    (6)innodb_purge_threads（已经初始化）
                    (7)innodb_read_io_threads = 默认cpu逻辑核数，以后工作负载读比例*cpu逻辑核数/2（已经初始化）
                    (8)innodb_write_io_threads = 默认cpu逻辑核数，以后工作负载写比例*cpu逻辑核数/2（已经初始化）
                    """
                    print("判断瓶颈是CPU, 进行相应参数修改")

                    for cpu_param in CPU_param_list:
                        print("进行参数{}调整".format(cpu_param))
                        if cpu_param == "innodb_write_io_threads":
                            # 获取各种负载地读写比例
                            return_param = param_read_and_write_io_thread()
                            read_io_thread = max(1, round(cpu_num_all * (return_param[0][0] / (return_param[0][0] + return_param[0][1]))))
                            if read_io_thread == cpu_num_all:
                                read_io_thread = read_io_thread - 1
                            # 如果和上一次配置不一样则进行如下配置
                            if param_dict["innodb_read_io_threads"] != read_io_thread:
                                print("读写比例不是1：1, 再次运行数据库")
                                param_dict["innodb_read_io_threads"] = read_io_thread
                                param_dict["innodb_write_io_threads"] = cpu_num_all - read_io_thread
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "read_write_io")
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                if param_dict["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    print("与读写比例对应的读写比例较好")
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()
                                else:
                                    print("1：1的线程结果较好")
                                    param_dict["innodb_read_io_threads"] = int(cpu_num_all / 2)
                                    param_dict["innodb_write_io_threads"] = cpu_num_all - param_dict["innodb_read_io_threads"]
                            # 如果和上次配置一样，则直接进行下一个参数配置
                            else:
                                print("读写比例1：1，不需要运行数据库")
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
                                    print("不存在log_writer的瓶颈")
                                    if param_dict["throught"] > param_dict_list[len(param_dict_list) - 1]["throught"]:
                                        print("启用log_writer")
                                        param_dict["innodb_log_writer_threads"] = 1
                                    else:
                                        print("关闭log_writer")
                                        param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                        dict_show_global_status = analysis_show_global_status(status_path)
                                        engine_status_dict = analysis_model()
                                        str_bottleneck = analysis_bottleneck()
                                else:
                                    print("存在log_writer的瓶颈")
                                    innodb_buffer_pool_size_all = param_dict["innodb_buffer_pool_size"]
                                    innodb_buffer_pool_chunk_size_all = param_dict["innodb_buffer_pool_chunk_size"]
                                    innodb_log_buffer_size_all = param_dict["innodb_log_buffer_size"]
                                    while True:
                                        innodb_buffer_pool_size = param_dict["innodb_buffer_pool_size"]
                                        innodb_buffer_pool_instances = param_dict["innodb_buffer_pool_instances"]
                                        innodb_buffer_pool_chunk_size = param_dict["innodb_buffer_pool_chunk_size"]
                                        innodb_buffer_pool_size_1 = innodb_buffer_pool_size - param_dict["innodb_log_buffer_size"]
                                        param_dict["innodb_log_buffer_size"] = param_dict["innodb_log_buffer_size"] * 2

                                        # 计算buffer_pool_instance的总数
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
                                                print("上一次迭代较好")
                                                param_dict["innodb_log_buffer_size"] = innodb_log_buffer_size_all
                                                param_dict["innodb_buffer_pool_size"] = innodb_buffer_pool_size_all
                                                param_dict["innodb_buffer_pool_chunk_size"] = innodb_buffer_pool_chunk_size_all
                                                param_dict["innodb_log_writer_threads"] = 1
                                            else:
                                                print("本次迭代较好")
                                                param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                                dict_show_global_status = analysis_show_global_status(status_path)
                                                engine_status_dict = analysis_model()
                                                str_bottleneck = analysis_bottleneck()
                                            break

                            break

                        if cpu_param == "innodb_log_wait_for_flush_spin_hwm":
                            # 进行参数判断
                            param_dict, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck = \
                                param_mid_value_tuning_2(400, copy.deepcopy(param_dict), "innodb_log_wait_for_flush_spin_hwm",
                                                         copy.deepcopy(param_dict_list), dict_show_global_status, engine_status_dict, str_bottleneck, 100, 0, 4000)
                            break

                        if cpu_param == "innodb_concurrency_tickets":
                            # 进行参数判断
                            param_dict, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck = \
                                param_mid_value_tuning_2(5000, copy.deepcopy(param_dict), "innodb_concurrency_tickets",
                                                         copy.deepcopy(param_dict_list), dict_show_global_status, engine_status_dict, str_bottleneck, 1000, 1, 50000)
                            break

                        if cpu_param == "innodb_sync_spin_loops":
                            # 进行参数判断
                            param_dict, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck = \
                                param_mid_value_tuning_2(30, copy.deepcopy(param_dict), "innodb_sync_spin_loops",
                                                         copy.deepcopy(param_dict_list), dict_show_global_status, engine_status_dict, str_bottleneck, 10, 0, 300)
                            break

                        if cpu_param == "innodb_thread_concurrency":
                            param_dict, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck = \
                                param_mid_value_tuning_2(2 * cpu_num_all, copy.deepcopy(param_dict), "innodb_thread_concurrency",
                                                         copy.deepcopy(param_dict_list), dict_show_global_status, engine_status_dict,
                                                         str_bottleneck, round(cpu_num_all * 0.2 / 2) * 2, 0, 180)

                    print("当前最好的参数选项")
                    for i_param_dict in param_dict:
                        print(i_param_dict, param_dict[i_param_dict])
                    if cpu_param == "innodb_write_io_threads":
                        CPU_param_list = CPU_param_list[1:]
                    CPU_param_list = CPU_param_list[1:]
                    if len(CPU_param_list) == 0:
                        flag_param_CPU = "end"

                # 修改与锁相关的参数
                elif is_bottleneck == "LATCH":
                    """
                    按照一下逆序调参
                    (1)innodb_sync_array_size(建议cpu核数，768等待，探索)
                    (2)innodb_deadlock_detect （是否进行死锁检测）
                    (3)innodb_lock_wait_timeout（行锁的超时时间）
                    (4)innodb_buffer_pool_instances(减少线程的锁竞争)有指标
                    (5)innodb_adaptive_hash_index_parts
                    """
                    print("判断瓶颈为LATCH,修改相应的参数")

                    for LATCH_param in LATCH_param_list:
                        print("进行参数{}调整".format(LATCH_param))
                        if LATCH_param == "innodb_adaptive_hash_index_parts":
                            mid_return = param_hash_index()
                            print("btr0sea, hash-sum, no-hash-sum")
                            print(mid_return)
                            # 如果btr0sea的个数不为0
                            print("btr0sea不为0")
                            mid_innodb_adaptive_hash_index = param_dict["innodb_adaptive_hash_index"]
                            while mid_return[0] > 0:
                                param_dict["innodb_adaptive_hash_index"] = 1
                                param_dict["innodb_adaptive_hash_index_parts"] = param_dict["innodb_adaptive_hash_index_parts"] * 2
                                now_time = time.time()
                                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "hash_index")
                                mysql_sum_time = mysql_sum_time + time.time() - now_time
                                # 如果上一次吞吐量大
                                if param_dict["throught"] > param_dict_list[len(param_dict_list) - 1]["throught"]:
                                    print("分区*2效果不好")
                                    param_dict["innodb_adaptive_hash_index_parts"] = int(param_dict["innodb_adaptive_hash_index_parts"] / 2)
                                    param_dict["innodb_adaptive_hash_index"] = mid_innodb_adaptive_hash_index
                                    break
                                # 如果本次吞吐量大
                                else:
                                    print("分区数*2较高")
                                    mid_innodb_adaptive_hash_index = 1
                                    param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                                    dict_show_global_status = analysis_show_global_status(status_path)
                                    engine_status_dict = analysis_model()
                                    str_bottleneck = analysis_bottleneck()
                                    if param_dict["innodb_adaptive_hash_index_parts"] * 2 > 512:
                                        break
                            break

                        if LATCH_param == "innodb_buffer_pool_instances":

                            # 记录该参数是否第一次
                            mid_innodb_buffer_pool_instances = param_dict["innodb_buffer_pool_instances"]

                            innodb_buffer_pool_size = param_dict["innodb_buffer_pool_size"]
                            # value值进行减小测试
                            while True:
                                innodb_buffer_pool_instances = param_dict["innodb_buffer_pool_instances"]
                                if innodb_buffer_pool_instances > 2:
                                    innodb_buffer_pool_chunk_size = param_dict["innodb_buffer_pool_chunk_size"]
                                    innodb_buffer_pool_instances_1 = innodb_buffer_pool_instances - 2
                                    innodb_buffer_pool_chunk_size_1 = math.floor(innodb_buffer_pool_size / innodb_buffer_pool_instances_1)
                                    innodb_buffer_pool_size_1 = innodb_buffer_pool_instances_1 * innodb_buffer_pool_chunk_size_1
                                    # 计算buffer_pool,chunk_size的值
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

                            # value值进行扩大测试
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
                                    # 计算buffer_pool,chunk_size的值
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
                            # 获取平均时间和最大锁时间
                            avg_time, max_time = param_lock_row_time(dict_show_global_status)
                            # 关闭死锁检测
                            mid_throught_innodb_deadlock_detect = param_dict["throught"]
                            mid_dict_show_global_status = dict_show_global_status
                            mid_engine_status_dict = engine_status_dict
                            mid_str_bottleneck = str_bottleneck

                            # 运行一次50的时间
                            param_dict["innodb_lock_wait_timeout"] = 50
                            param_dict["innodb_deadlock_detect"] = 0
                            now_time = time.time()
                            param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "lock_wait")
                            mysql_sum_time = mysql_sum_time + time.time() - now_time
                            param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                            dict_show_global_status = analysis_show_global_status(status_path)
                            engine_status_dict = analysis_model()
                            str_bottleneck = analysis_bottleneck()

                            # 进行锁时间的调整
                            param_dict, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck = \
                                param_mid_value_tuning_2(50, copy.deepcopy(param_dict), "innodb_lock_wait_timeout", copy.deepcopy(param_dict_list),
                                                         dict_show_global_status, engine_status_dict, str_bottleneck, 10, 10, 500)

                            # 进行参数的对比
                            if mid_throught_innodb_deadlock_detect > param_dict["throught"]:
                                param_dict["throught"] = mid_throught_innodb_deadlock_detect
                                param_dict["innodb_deadlock_detect"] = 1
                                param_dict["innodb_lock_wait_timeout"] = 50
                                dict_show_global_status = mid_dict_show_global_status
                                engine_status_dict = mid_engine_status_dict
                                str_bottleneck = mid_str_bottleneck
                            break

                        if LATCH_param == "innodb_sync_array_size":
                            # 进行锁时间的调整
                            param_dict, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck = \
                                param_mid_value_tuning(1, copy.deepcopy(param_dict), "innodb_sync_array_size", copy.deepcopy(param_dict_list),
                                                       dict_show_global_status, engine_status_dict, str_bottleneck, 1, 1024)
                            break

                    print("当前最好的参数选项")
                    for i_param_dict in param_dict:
                        print(i_param_dict, param_dict[i_param_dict])
                    if LATCH_param == "innodb_lock_wait_timeout":
                        LATCH_param_list = LATCH_param_list[1:]
                    print(LATCH_param_list)
                    LATCH_param_list = LATCH_param_list[1:]
                    print(LATCH_param_list)
                    if len(LATCH_param_list) == 0:
                        flag_param_LATCH = "end"

                # 进行下一次迭代
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

            # 如果log_buffer是瓶颈的情况，则调整log_buffer参数
            elif param_innodb_log_buffer_size() > 0 and tune_param["innodb_log_buffer_size"] == 1:

                # 记录以前的参数值
                print("进行参数log_buffer的修改")
                innodb_buffer_pool_size = param_dict["innodb_buffer_pool_size"]
                innodb_buffer_pool_instances = param_dict["innodb_buffer_pool_instances"]
                innodb_buffer_pool_chunk_size = param_dict["innodb_buffer_pool_chunk_size"]
                innodb_buffer_pool_size_1 = innodb_buffer_pool_size - param_dict["innodb_log_buffer_size"]
                param_dict["innodb_log_buffer_size"] = param_dict["innodb_log_buffer_size"] * 2

                # 计算buffer_pool,chunk_size的值
                innodb_buffer_pool_chunk_size_1 = math.floor(innodb_buffer_pool_size_1 / innodb_buffer_pool_instances)
                innodb_buffer_pool_size_1 = innodb_buffer_pool_chunk_size_1 * innodb_buffer_pool_instances
                param_dict["innodb_buffer_pool_size"] = innodb_buffer_pool_size_1
                param_dict["innodb_buffer_pool_chunk_size"] = innodb_buffer_pool_chunk_size_1
                now_time = time.time()
                param_dict_list = run_and_write_file(copy.deepcopy(param_dict), param_unit_dict, i, copy.deepcopy(param_dict_list), "log_buffer")
                mysql_sum_time = mysql_sum_time + time.time() - now_time
                param_dict["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]

                # 分析当前的状态
                dict_show_global_status = analysis_show_global_status(status_path)
                engine_status_dict = analysis_model()
                str_bottleneck = analysis_bottleneck()

        # 进行迭代
        i = i + 1
        print("i is {}".format(i))