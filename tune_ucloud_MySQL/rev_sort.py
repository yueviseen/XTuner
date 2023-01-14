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

# 初始化参数
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
    # 返回参数字典
    return return_dict


# 进行数据的运行和把参数写入文件
def run_and_write_file(param_dict, param_unit_dict, i, param_dict_list, ii):
    # 写参数值到配置文件
    write_my_cnf(param_dict, param_unit_dict)

    # 获取吞吐量
    mid_throught = get_throught()
    param_dict["throught"] = mid_throught
    print("显示本次迭代次数及其迭代的参数值")
    print("-----------------------------")
    global cnt
    print("cnt is %d" % cnt)
    cnt = cnt + 1
    print("-----------------------------")
    for ii in param_dict:
        print(ii, param_dict[ii])
    print("-----------------------------")
    param_dict_list.append(param_dict)
    # 返回所有迭代的参数列表
    return param_dict_list


# 获取当先工作负载的吞吐量
def get_throught():

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



# 获得运行负载的结果
def get_result():
    throught = 0
    latency = 0
    # 获取文件的吞吐量
    with open(result_file_path, 'r') as f:
        for ii in f.readlines():
            if "Throughput (requests/second)" in ii:
                throught = float(ii.split(": ")[1].replace(",", ''))
            if "Average Latency" in ii:
                latency = float(ii.split(": ")[1].replace(",", ''))

    # 删除文件
    os.system(del_result_file)
    return (throught, latency)


# 运行oltp，并记录相关信息
def run_mysql_for_oltp():
    # 判断数据库是否开启成功
    status_mysql()

    # 运行oltp
    print("运行oltp工作负载")
    os.system(oltp_cmd)

    # 睡眠20秒
    print("睡眠20s")
    time.sleep(20)

    return get_result()


if __name__ == "__main__":
    """
    主要进行数据库innodb整个调优过程的迭代
    """

    # 设定最大的迭代次数
    iterations_num = 150

    # 记录当前最好的参数列表和吞吐量
    param_dict = {}

    param_dict_list = []

    # 记录需要输入M单位的参数
    param_unit_dict = {}
    param_unit_dict["innodb_buffer_pool_size"] = "M"
    param_unit_dict["innodb_buffer_pool_chunk_size"] = "M"
    param_unit_dict["innodb_log_file_size"] = "M"
    param_unit_dict["innodb_log_buffer_size"] = "M"


    mid_throught = 0

    # 记录迭代次数
    i = 0
    loop_flag = True
    cnt_tune = 0

    LRU_list = [18000, 1024]
    read_ahead_list = [14, 56]
    first = True

    # 进行参数的迭代修改
    while loop_flag is True:

        # 第一次迭代，主要进行初始化
        if i == 0:
            LRU_list = [18000, 1024]
            read_ahead_list = [14, 56]
            # 进行参数初始化
            param_dict = initialization_parameters()

            # 写配置参数到my.cnf,并运行workload
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

                        # 写配置参数到my.cnf,并运行workload
                        param_dict_list = run_and_write_file(copy.copy(param_dict_latest), param_unit_dict, None, param_dict_list, None)

                        if param_dict_latest["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                            param_dict_latest["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                            read_ahead_list.pop(0)

                        else:
                            param_dict_latest["innodb_read_ahead_threshold"] = int(mid_value)
                            print("当前最好是")
                            print(param_dict_latest)
                            break

                    while True:
                        print(LRU_list)

                        if len(LRU_list) == 0:
                            break

                        mid_value = float(param_dict_latest["innodb_lru_scan_depth"])
                        param_dict_latest["innodb_lru_scan_depth"] = int(LRU_list[0])

                        # 写配置参数到my.cnf,并运行workload
                        param_dict_list = run_and_write_file(copy.copy(param_dict_latest), param_unit_dict, None, param_dict_list, None)

                        if param_dict_latest["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                            param_dict_latest["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                            LRU_list.pop(0)

                        else:
                            param_dict_latest["innodb_lru_scan_depth"] = int(mid_value)
                            print("当前最好是")
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

                        # 写配置参数到my.cnf,并运行workload
                        param_dict_list = run_and_write_file(copy.copy(param_dict_latest), param_unit_dict, None, param_dict_list, None)

                        if param_dict_latest["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                            param_dict_latest["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                            LRU_list.pop(0)

                        else:
                            param_dict_latest["innodb_lru_scan_depth"] = int(mid_value)
                            print("当前最好是")
                            print(param_dict_latest)
                            break

                    while True:
                        print(read_ahead_list)
                        if len(read_ahead_list) == 0:
                            break

                        mid_value = float(param_dict_latest["innodb_read_ahead_threshold"])
                        param_dict_latest["innodb_read_ahead_threshold"] = int(read_ahead_list[0])

                        # 写配置参数到my.cnf,并运行workload
                        param_dict_list = run_and_write_file(copy.copy(param_dict_latest), param_unit_dict, None, param_dict_list, None)

                        if param_dict_latest["throught"] < param_dict_list[len(param_dict_list) - 1]["throught"]:
                            param_dict_latest["throught"] = param_dict_list[len(param_dict_list) - 1]["throught"]
                            read_ahead_list.pop(0)

                        else:
                            param_dict_latest["innodb_read_ahead_threshold"] = int(mid_value)
                            print("当前最好是")
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

