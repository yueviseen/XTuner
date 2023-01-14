# -*- coding: gbk -*-

"""
基于规则的数据库调参
"""
import os
import shutil
from ip_24 import *
import pymysql
import time
from multiprocessing import Process


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

def run_mysql_for_oltp_ycsb():
    # 判断数据库是否开启成功
    status_mysql()

    # 运行oltp
    print("运行oltp工作负载")
    os.system(oltp_cmd_ycsb)

    # 睡眠20秒
    print("睡眠20s")
    time.sleep(20)

    return get_result()

def run_mysql_for_oltp_wiki():
    # 判断数据库是否开启成功
    status_mysql()

    # 运行oltp
    print("运行oltp工作负载")
    os.system(oltp_cmd_wiki)

    # 睡眠20秒
    print("睡眠20s")
    time.sleep(20)

    return get_result()

# 使数据库回到原来状态
def data_recovery():

    # 为了安全休眠10秒
    time.sleep(10)

    # 删除文件
    print(os.listdir(mysql_path))
    shutil.rmtree(data_path)
    print(os.listdir(mysql_path))

    # 复制文件
    shutil.copytree(data_cp_path, data_path)
    print(os.listdir(data_path))
    print(os.listdir(mysql_path))

    os.system("chown -R mysql:mysql /var/lib/mysql")
    print("清空内容")
    os.system(clean_log_err)
    print("数据恢复完成")


# 进行数据获取
if __name__ == '__main__':

    for i in range(1):

        # 数据库复原
        data_recovery()

        # # 清空缓存
        # free_cache()
        #
        # # 启动数据库
        # start_mysql()
        #
        # # 运行oltp
        # print(run_mysql_for_oltp_ycsb())
        #
        # # 关闭数据库
        # stop_mysql()

