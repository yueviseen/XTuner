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

    # 判断文件是否写入成功
    flag_average = False
    flag_throughput = False
    cnt = 0
    while True:

        # 每次休眠10秒
        time.sleep(10)
        print("判断result文件是否写入成功")
        cnt = cnt + 1
        if cnt > 20:
            break
        # 如果找到文件，则，结束循环
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
    print("result文件写入成功")

    if cnt > 20:
        return (-1, -1)

    else:
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
def run_PG_for_oltp():
    # 判断数据库是否开启成功
    # status_PG()

    # 运行oltp
    print("运行oltp工作负载")
    print(oltp_cmd_wiki)
    t = os.system(oltp_cmd_wiki)
    if t == 0:
        print("运行成功")
    # 睡眠20秒
    print("睡眠60s")
    time.sleep(60)

    return get_result()

# 以后修改
def run_mysql_for_oltp_ycsb():
    # 判断数据库是否开启成功
    status_PG()

    # 运行oltp
    print("运行oltp工作负载")
    os.system(oltp_cmd_ycsb)

    # 睡眠20秒
    print("睡眠20s")
    time.sleep(20)

    return get_result()

# 以后修改
def run_mysql_for_oltp_wiki():
    # 判断数据库是否开启成功
    # status_PG()

    # 运行oltp
    print("运行oltp工作负载")
    os.system(oltp_cmd_wiki)

    # 睡眠20秒
    print("睡眠20s")
    time.sleep(20)

    # return get_result()

# 使数据库回到原来状态
def data_recovery():

    # 为了安全休眠10秒
    # time.sleep(10)

    # 判断不存在数据库的备份，则进行数据库备份
    if os.path.exists("/root/PG/wikipedia") is False:
        os.system("pg_dump -U postgres -d wikipedia > /root/PG/wikipedia")
    else:
        print("exist backup")
    # 删除数据库
    os.system("dropdb -h 127.0.0.1 -p 5432 -U postgres wikipedia")
    print("删除数据库")

    # 创建数据库
    os.system("createdb -h 127.0.0.1 -p 5432 -U postgres wikipedia")
    print("创建数据库")

    # 导入备份数据库
    os.system("psql -h 127.0.0.1 -p 5432 -U postgres wikipedia < /root/PG/wikipedia")

    print("休眠60秒")
    time.sleep(60)





# 进行数据获取
if __name__ == '__main__':

    ss = []
    for i in range(3):
        # 启动数据库
        start_PG()

        status_PG()

        # 数据库复原
        data_recovery()

        # 清空缓存
        free_cache()

        # 运行oltp
        ss.append(run_PG_for_oltp())

        # 关闭数据库
        stop_PG()

        time.sleep(60)
    print(ss)


