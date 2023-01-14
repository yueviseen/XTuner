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

# 定义全局参数
cpu_num_all = int(os.popen("cat /proc/cpuinfo| grep 'processor'| wc -l").readlines()[0].replace("\n", ''))
cnt = 0
tune_param = {}
num_table = 9


# # 读取上一次的参数值
# def read_tunning_process(i):
#
#     # 记录返回结果
#     param_dict = {}
#
#     # 判断是否进行读取
#     flag = False
#
#     # 设置匹配的字符
#     start_i = "start_" + str(i - 1)
#
#     # 进行数据的读取
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
#                 # 进行格式的分割
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

    # 进行参数缩小测试
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
    # 进行参数缩小测试
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


# 记录根据中间值探索的参数, value值默认参数值,进行加法计算
def param_mid_value_tuning_dif(value, param_dict, param, param_dict_list, str_bottleneck, min, max, dif_value, mid_value):
    print(9999999999)
    global mysql_sum_time
    # 各种状态赋值
    mid_str_bottleneck = str_bottleneck
    mid_mid_value = mid_value
    flag_while_1 = False
    if (param_dict[param] - dif_value) >= min:
        print("11111111111")
        flag_while_1 = True

    # value值进行减小测试
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

    # value值进行扩大测试
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


# 记录根据中间值探索的参数, value值默认参数值,进行加法计算
def param_mid_value_tuning_rat(value, param_dict, param, param_dict_list, str_bottleneck, min, max, rat_value, mid_value):
    global mysql_sum_time
    # 各种状态赋值
    mid_str_bottleneck = str_bottleneck
    mid_mid_value = mid_value
    flag_while_1 = False
    if int(param_dict[param] / rat_value) >= min:
        flag_while_1 = True

    # value值进行减小测试
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

    # value值进行扩大测试
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


# 定义需要调整的参数
def def_tune_param():
    # 需要调整的参数设置为1，不需要调整的参数设置为0
    global tune_param
    # 初始化参数 10 个
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

    # 指标相关参数 1个
    tune_param["wal_buffers"] = 1

    # 基于CPU 5 个
    tune_param["force_parallel_mode"] = 1
    tune_param["autovacuum_max_workers"] = 1
    tune_param["wal_writer_delay"] = 1
    tune_param["bgwriter_delay"] = 1
    tune_param["autovacuum_naptime"] = 1

    # 基于CPU和IO的 1 个
    tune_param["wal_compression"] = 1

    # 基于io的 7 个
    tune_param["effective_io_concurrency"] = 1
    tune_param["backend_flush_after"] = 1
    tune_param["bgwriter_flush_after"] = 1
    tune_param["checkpoint_flush_after"] = 1
    tune_param["wal_writer_flush_after"] = 1
    tune_param["autovacuum_vacuum_cost_limit"] = 1
    tune_param["bgwriter_lru_maxpages"] = 1

    # 基于other的 6 个
    tune_param["default_statistics_target"] = 1
    tune_param["lock_timeout"] = 1
    tune_param["deadlock_timeout"] = 1
    tune_param["vacuum_cost_page_miss"] = 1
    tune_param["vacuum_cost_page_dirty"] = 1
    tune_param["enable_seqscan"] = 1


# 初始化参数
def initialization_parameters():
    # 定义返回列表
    return_dict = {}

    global cpu_num_all
    cpu_num = cpu_num_all
    global tune_param

    # 基于规则进行初始化,带！号的需要需修改
    # 1，初始化参数shared_buffers，取最大值,规则类参数
    if tune_param["shared_buffers"] == 1:
        return_dict["shared_buffers"] = 200
    # 3，初始化参数max_wal_size，取最大值， 规则类参数
    if tune_param["max_wal_size"] == 1:
        return_dict["max_wal_size"] = 192
    # 4， 初始化参数min_wal_size，取最大值， 规则类参数
    if tune_param["min_wal_size"] == 1:
        return_dict["min_wal_size"] = 80
    # 5 初始化参数random_page_cost，规则类参数，other类参数, +++++++++++
    if tune_param["random_page_cost"] == 1:
        return_dict["random_page_cost"] = 4
        # OTHER_param_list.append(return_dict["random_page_cost"])
    # 6 初始化参数wal_level,根据应用场景选择最小的，减少io，规则类参数
    if tune_param["wal_level"] == 1:
        return_dict["wal_level"] = 'minimal'  # 经过fio测试可得
    # 7， 8初始化参数max_worker_processes，为cpu的个数为min（4, cpu/2），规则类参数，CPU类参数!!!!!!!!!!!!!!
    if tune_param["max_worker_processes"] == 1 and tune_param["max_parallel_workers_per_gather"] == 1:
        return_dict["max_worker_processes"] = 16
        return_dict["max_parallel_workers_per_gather"] = 4
        # CPU_param_list.append(return_dict["max_worker_processes"])
        # CPU_param_list.append(return_dict["max_parallel_workers_per_gather"])
    # 9 初始化参数bgwriter_lru_multiplier,工作负载均匀所以采取1， 规则类参数， io类参数!!!!!!!!!!!!!!
    if tune_param["bgwriter_lru_multiplier"] == 1:
        return_dict["bgwriter_lru_multiplier"] = 1  # 查询磁盘参数可得
        # IO_param_list.append(return_dict["bgwriter_lru_multiplier"])

    # 基于指标
    # 11 指标相关参数 1个, 指标参数，默认为64M
    if tune_param["wal_buffers"] == 1:
        return_dict["wal_buffers"] = 96

    # 取CPU相关的默认值
    # 12 force_parallel_mode的默认值
    if tune_param["force_parallel_mode"] == 1:
        return_dict["force_parallel_mode"] = "off"
        # CPU_param_list.append(return_dict["force_parallel_mode"])
    # 14 wal_writer_delay的默认值
    if tune_param["wal_writer_delay"] == 1:
        return_dict["wal_writer_delay"] = 200
        # CPU_param_list.append(return_dict["wal_writer_delay"])
    # 15 bgwriter_delay的默认值
    if tune_param["bgwriter_delay"] == 1:
        return_dict["bgwriter_delay"] = 200
        # CPU_param_list.append(return_dict["bgwriter_delay"])
    # 16 autovacuum_naptime的默认值
    if tune_param["autovacuum_naptime"] == 1:
        return_dict["autovacuum_naptime"] = 60
        # CPU_param_list.append(return_dict["autovacuum_naptime"])

    # 取CPU和IO的默认值
    # 17 取wal_compression的默认值
    if tune_param["wal_compression"] == 1:
        return_dict["wal_compression"] = "off"
        # CPU_param_list.append(return_dict["wal_compression"])
        # IO_param_list.append(return_dict["wal_compression"])
        # 13 autovacuum_max_workers的默认值
    if tune_param["autovacuum_max_workers"] == 1:
        return_dict["autovacuum_max_workers"] = 5
        # CPU_param_list.append(return_dict["autovacuum_max_workers"])
        # IO_param_list.append(return_dict["autovacuum_max_workers"])

    # 取io的默认值
    # 19 取effective_io_concurrency的默认值
    if tune_param["effective_io_concurrency"] == 1:
        return_dict["effective_io_concurrency"] = 1
        # IO_param_list.append(return_dict["effective_io_concurrency"])
    # 20 取backend_flush_after的默认值
    if tune_param["backend_flush_after"] == 1:
        return_dict["backend_flush_after"] = 0
    # IO_param_list.append(return_dict["backend_flush_after"])
    # 21 取bgwriter_flush_after的默认值
    if tune_param["bgwriter_flush_after"] == 1:
        return_dict["bgwriter_flush_after"] = 64
        # IO_param_list.append(return_dict["bgwriter_flush_after"])
    # 22 取checkpoint_flush_after的默认值
    if tune_param["checkpoint_flush_after"] == 1:
        return_dict["checkpoint_flush_after"] = 32
        # IO_param_list.append(return_dict["checkpoint_flush_after"])
    # 23 取wal_writer_flush_after的默认值
    if tune_param["wal_writer_flush_after"] == 1:
        return_dict["wal_writer_flush_after"] = 128
        # IO_param_list.append(return_dict["wal_writer_flush_after"])
    # 24 取autovacuum_vacuum_cost_limit的默认值
    if tune_param["autovacuum_vacuum_cost_limit"] == 1:
        return_dict["autovacuum_vacuum_cost_limit"] = 200
        # IO_param_list.append(return_dict["autovacuum_vacuum_cost_limit"])
    # 25 取bgwriter_lru_maxpages的默认值
    if tune_param["bgwriter_lru_maxpages"] == 1:
        return_dict["bgwriter_lru_maxpages"] = 100
        # IO_param_list.append(return_dict["bgwriter_lru_maxpages"])
    # 10，初始化参数autovacuum_vacuum_cost_delay，不进行休眠
    if tune_param["autovacuum_vacuum_cost_delay"] == 1:
        return_dict["autovacuum_vacuum_cost_delay"] = 2
        # IO_param_list.append(return_dict["autovacuum_vacuum_cost_delay"])

    # 基于other的默认值
    # 26 取 default_statistics_target的默认值
    if tune_param["default_statistics_target"] == 1:
        return_dict["default_statistics_target"] = 100
        # OTHER_param_list.append(return_dict["default_statistics_target"])
    # 27 取lock_timeout的默认值
    if tune_param["lock_timeout"] == 1:
        return_dict["lock_timeout"] = 0
        # OTHER_param_list.append(return_dict["lock_timeout"])
    # 28 取deadlock_timeout的默认值
    if tune_param["deadlock_timeout"] == 1:
        return_dict["deadlock_timeout"] = 1000
        # OTHER_param_list.append(return_dict["deadlock_timeout"])
    # 29 vacuum_cost_page_miss 的默认值
    if tune_param["vacuum_cost_page_miss"] == 1:
        return_dict["vacuum_cost_page_miss"] = 10
        # OTHER_param_list.append(return_dict["vacuum_cost_page_miss"])
    # 30 vacuum_cost_page_dirty的默认值
    if tune_param["vacuum_cost_page_dirty"] == 1:
        return_dict["vacuum_cost_page_dirty"] = 20
        # OTHER_param_list.append(return_dict["vacuum_cost_page_dirty"])
    # 18 取autovacuum的默认值
    if tune_param["enable_seqscan"] == 1:
        return_dict["enable_seqscan"] = "on"
        # OTHER_param_list.append(return_dict["enable_seqscan"])
    # 2，初始化参数effective_cache_size， 取默认值，是探索参数
    if tune_param["effective_cache_size"] == 1:
        return_dict["effective_cache_size"] = 4096
        # OTHER_param_list.append(return_dict["effective_cache_size"])

    # 返回参数字典
    return return_dict


# 获取当先工作负载的吞吐量
def get_throught():
    # 设置变量
    mid_throught = 0
    mid_latency = 0

    # 启动数据库
    start_PG()

    status_PG()

    # 复原数据库
    data_recovery()

    # 清空缓存
    free_cache()

    # 运行数据库
    (mid_throught, mid_latency) = run_PG_for_oltp()

    # 关闭数据库
    stop_PG()

    # 进行数据库休眠
    print("休眠60秒")
    time.sleep(60)

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
    while True:
        mid_throught = get_throught()
        if mid_throught == -1:
            print("出现错误，重新计算")
        else:
            break

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


# # 记录根据中间值探索的参数
# def param_mid_value_tuning_2(value, param_dict,  param, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck, diff_value, min=0, max=0):
#
#     # 记录该参数是否第一次
#     param_dict[param] = value
#     global mysql_sum_time
#     # 各种状态赋值
#     mid_dict_show_global_status = dict_show_global_status
#     mid_engine_status_dict = engine_status_dict
#     mid_str_bottleneck = str_bottleneck
#     flag_while_1 = False
#     if param_dict[param] - diff_value > min:
#         flag_while_1 = True
#
#     # value值进行减小测试
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
#     # value值进行扩大测试
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
# # 记录根据中间值探索的参数
# def param_mid_value_tuning_max(value, param_dict,  param, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck, diff_value, min=0, max=0):
#
#     # 记录该参数是否第一次
#     param_dict[param] = value
#     global mysql_sum_time
#
#     # 各种状态赋值
#     mid_dict_show_global_status = copy.deepcopy(dict_show_global_status)
#     mid_engine_status_dict = copy.deepcopy(engine_status_dict)
#     mid_str_bottleneck = copy.deepcopy(str_bottleneck)
#
#     flag_while_1 = False
#     if param_dict[param] - diff_value > min:
#         flag_while_1 = True
#
#     # value值进行减小测试
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
#     # value值进行扩大测试
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
# # 记录根据中间值探索的参数, value值默认参数值
# def param_mid_value_tuning(value, param_dict,  param, param_dict_list, dict_show_global_status, engine_status_dict, str_bottleneck, min=0, max=0):
#
#     global mysql_sum_time
#
#     # 记录默认值
#     param_dict[param] = value
#
#     # 各种状态赋值
#     mid_dict_show_global_status = dict_show_global_status
#     mid_engine_status_dict = engine_status_dict
#     mid_str_bottleneck = str_bottleneck
#
#     flag_while_1 = False
#     if (param_dict[param]/2) > min:
#         flag_while_1 = True
#
#     # value值进行减小测试
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
#     # value值进行扩大测试
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
def judge_bottleneck(str_bottleneck, flag_param_IO, flag_param_CPU, flag_param_OTHER):
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

    print("--------------")
    print("系统瓶颈分析")
    print(flag_param_IO, flag_param_CPU, flag_param_OTHER)
    print(str_bottleneck)
    print("---------------")
    while True:
        print("进行随机选择")
        i = random.randint(1,3)
        if i == 1 and flag_param_IO != "end":
            return "IO"
        elif i == 2 and flag_param_CPU != "end":
            return "CPU"
        elif i == 3 and flag_param_OTHER != "end":
            return "OTHER"
        else:
            return "end"
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
    # # 当出现CPU瓶颈时， 进行瓶颈参数判断
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
    # # 当出现锁瓶颈的时候， 进行瓶颈参数判断
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
    主要进行数据库innodb整个调优过程的迭代
    """

    # 记录总共花费时间
    mysql_sum_time = 0

    start_now_time = time.time()

    # 设定可用资源的内存资源，单位M
    memory_resource = 684

    # 设定可用的磁盘资源,单位M
    disk_resource = 192

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

    # 记录当前调整的OTHER相关的参数
    flag_param_OTHER = "start"

    # 进行循环的次数训练
    flag_loop = True

    # 对参数进行调参判断
    effective_cache_size_flag = False

    # 记录需要输入M单位的参数
    param_unit_dict = {}
    param_unit_dict["shared_buffers"] = "MB"
    param_unit_dict["effective_cache_size"] = "MB"
    param_unit_dict["max_wal_size"] = "MB"
    param_unit_dict["min_wal_size"] = "MB"
    param_unit_dict["wal_buffers"] = "MB"

    # 记录所要调优的io集合
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

    # 记录所要调优的cpu集合
    CPU_param_list = ["force_parallel_mode", "bgwriter_delay", "wal_writer_delay",
                      "autovacuum_naptime", "wal_compression",
                      "max_worker_processes", "max_parallel_workers_per_gather", "autovacuum_max_workers"]

    # 记录所要调优的other集合
    OTHER_param_list = ["random_page_cost", "effective_cache_size", "deadlock_timeout", "lock_timeout",
                        "enable_seqscan", "default_statistics_target", "vacuum_cost_page_miss",
                        "vacuum_cost_page_dirty"]

    # 临时保存，便于以后循环
    mid_IO_list = []
    mid_CPU_list = []
    mid_OTHER_list = []

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

            # 记录当下时间
            now_time = time.time()

            # 写配置参数到my.cnf
            param_dict_list = run_and_write_file(copy.copy(param_dict), param_unit_dict, None, copy.deepcopy(param_dict_list), None)

            mysql_sum_time = mysql_sum_time + time.time() - now_time

            # 读取上一次的参数列表
            param_dict = copy.deepcopy(param_dict_list[len(param_dict_list) - 1])

            # 获取系统信息
            str_bottleneck = analysis_bottleneck()

            # 进行复制，便于以后循环使用
            mid_IO_list = copy.deepcopy(IO_param_list)
            mid_CPU_list = copy.deepcopy(CPU_param_list)
            mid_OTHER_list = copy.deepcopy(OTHER_param_list)

            # 尝试性修改参数
            mid_value = min(int(math.ceil(analysis_show_global_status(status_path) / 1024 / 1024) * 1.5), 96)
            print(mid_value)
            print("进行wal_buffers判断")
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
        # 进行系统瓶颈系统判断
        else:
            """
            log_buffer保持足够内存空间，不能成为瓶颈
            """
            print("进行其它参数调参")
            print(mid_value)
            # 如果log_buffer不是瓶颈的情况
            if mid_value * 1.1 < param_dict["wal_buffers"] or param_dict["wal_buffers"] == 96:

                # 进行系统瓶颈判断
                print("进行系统瓶颈判断")
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
                    print("判断为io瓶颈，调整io瓶颈相关参数")
                    for io_param in mid_IO_list:
                        print("进行参数{}调整".format(io_param))
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
                                # 各种状态赋值
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
                                # 各种状态赋值
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
                                # 各种状态赋值
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
                                # 各种状态赋值
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
                                # 各种状态赋值
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
                                # 各种状态赋值
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
                                # 各种状态赋值
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

                        # 跳出循环
                        break

                    print("当前最好的参数选项")
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
                    print("判断瓶颈是CPU, 进行相应参数修改")

                    for cpu_param in mid_CPU_list:
                        print("进行参数{}调整".format(cpu_param))
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
                            # 进行参数判断
                            param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_dif(param_dict["max_worker_processes"], param_dict,
                                                                                                                "max_worker_processes", param_dict_list, str_bottleneck,
                                                                                                                1, 48, 4, mid_value)
                        elif cpu_param == "max_parallel_workers_per_gather":
                            # 进行参数判断
                            mid_parallel = min(param_dict["max_worker_processes"], 16)
                            param_dict, param_dict_list, str_bottleneck, mid_value = param_mid_value_tuning_dif(param_dict["max_parallel_workers_per_gather"], param_dict,
                                                                                                                "max_parallel_workers_per_gather", param_dict_list, str_bottleneck,
                                                                                                                1, mid_parallel, 2, mid_value)
                        elif cpu_param == "autovacuum_max_workers":

                            flag_while_2 = False
                            if (param_dict["autovacuum_max_workers"] - 1) > 1:
                                flag_while_2 = True
                            mid_autovacuum_max_workers = param_dict["autovacuum_max_workers"]
                            # value值进行减小测试
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

                            # value值进行扩大测试
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

                        # 跳出循环
                        break

                    print("当前最好的参数选项")
                    for i_param_dict in param_dict:
                        print(i_param_dict, param_dict[i_param_dict])
                    mid_CPU_list = mid_CPU_list[1:]
                    if len(mid_CPU_list) == 0:
                        flag_param_CPU = "end"

                # 修改与锁相关的参数
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
                    print("判断瓶颈为OTHER,修改相应的参数")

                    for OTHER_param in mid_OTHER_list:
                        print("进行参数{}调整".format(OTHER_param))
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
                                # 各种状态赋值
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

                        # 跳出循环
                        break

                    print("当前最好的参数选项")
                    for i_param_dict in param_dict:
                        print(i_param_dict, param_dict[i_param_dict])
                    print(mid_OTHER_list)
                    mid_OTHER_list = mid_OTHER_list[1:]
                    print(mid_OTHER_list)
                    if len(mid_OTHER_list) == 0:
                        flag_param_OTHER = "end"

                # 进行下一次迭代
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

            # 如果log_buffer是瓶颈的情况，则调整log_buffer参数
            else:
                print("进行wal_buffer判断!!!!!!!!!!!!!!!")
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

        # 进行迭代
        i = i + 1
        print("i is {}".format(i))