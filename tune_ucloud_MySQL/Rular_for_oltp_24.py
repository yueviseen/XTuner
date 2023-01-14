# -*- coding: gbk -*-

"""
基于规则的数据库调参
"""
import os
import shutil

import pymysql
import time
from ip_24 import *
from multiprocessing import Process


# 开启一个线程获取相关信息,并监控相关信息
def process_information(starting_time, run_time, conn, cursor):

    # 将内容写入文件
    with open(status_path, 'a') as f:

        # 写入开始时间
        f.write(str(starting_time))
        f.write("++")
        # 进行死循环，等待主线程杀死该进程
        while True:
            print("收集状态数据")
            # 如果超过运行时间，则关闭数据库，结束进程
            if time.time()-starting_time > run_time + 9:
                f.flush()
                cursor.close()
                conn.close()
                break

            # 记录各种运行前的status值
            cursor.execute("show global status like '%innodb%'")

            # 用共享变量记录各种状态
            f.write(str(time.time()))
            for i_content in cursor.fetchall():
                f.write("++")
                f.write(str(i_content))
            f.write("+++")

            # 每10秒采集一次数据
            time.sleep(10)


# 获得运行负载的结果
def get_result():

    # 定义变量
    mid_throught = 0
    mid_latency = 0

    # 获取文件的吞吐量
    with open(result_file_path) as f:
        for ii in f.readlines():
            if "Throughput (requests/second)" in ii:
                mid_throught = float(ii.split(": ")[1].replace(",", ''))
            if "Average Latency" in ii:
                mid_latency = float(ii.split(": ")[1].replace(",", ''))

    # 删除文件
    os.system(del_result_file)
    return (mid_throught, mid_latency)


# 运行oltp，并记录相关信息
def run_mysql_for_oltp():

    # 判断数据库是否开启成功
    status_mysql()

    # 建立数据库连接
    conn = pymysql.connect(host=ip, user=user, password=password, database=database_wiki, charset='utf8', port=i_port)
    cursor = conn.cursor()

    print("后台运行数据库")
    # 运行oltp
    os.system(oltp_cmd_wiki_background)

    # 开始时间
    starting_time = time.time()

    # 监控cpu和io
    print("进行cpu与io的监控")
    os.system(sar_u_com)
    os.system(sar_d_com)

    global run_time
    # 另开线程，记录相关信息
    p = Process(target=process_information, args=(starting_time, run_time, conn, cursor))
    p.start()
    p.join()

    # 运行结束后，休眠40秒，方便后续的文件等内容的写入
    print("休眠140秒")
    time.sleep(run_time + 60)

    # 判断是否读取标记
    flag_throughput = False
    flag_average = False



    # 判断文件是否写入成功
    while True:

        # 每次休眠10秒
        time.sleep(10)
        print("判断result文件是否写入成功")

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
    # 获取结果
    return get_result()


# 使数据库回到原来状态
def data_recovery():

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

    # 清空各个记录日志
    print("清空各个日志记录")
    os.system(clean_log_err)
    os.system(clean_status)
    os.system(clean_sar_u_com)
    os.system(clean_sar_d_com)
    print("各个日志记录清空完成")




# 运行数据库进行测试
if __name__ == '__main__':

    for i in range(10):

        # 复原数据库数据
        data_recovery()

        # 清空缓存
        free_cache()

        # 启动数据库
        start_mysql()

        # 运行oltp
        print(run_mysql_for_oltp())

        # 使数据库复原
        stop_mysql()
