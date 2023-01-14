# -*- coding: gbk -*-

"""
基于规则的数据库调参
"""
import os
import shutil
import time
import psycopg2
from ip_24 import *
from multiprocessing import Process


# 开启一个线程获取相关信息,并监控相关信息
def process_information(starting_time, run_time, conn, cursor):

    # 将内容写入文件
    with open(status_path, 'a') as f:

        # 进行死循环，等待主线程杀死该进程
        while True:
            print("收集LSN状态数据")
            # 如果超过运行时间，则关闭数据库，结束进程
            if time.time()-starting_time > run_time + 9:
                f.flush()
                cursor.close()
                conn.close()
                break

            # 记录各种运行前的status值
            cursor.execute("select pg_wal_lsn_diff(pg_current_wal_insert_lsn(), pg_current_wal_flush_lsn())")

            # 用共享变量记录各种状态
            for i_content in cursor.fetchall():
                f.write(str(i_content))
            f.write("++")

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
def run_PG_for_oltp():


    # 建立数据库连接
    conn = psycopg2.connect(host=ip, user=user, password=password, database=database_wiki, port=i_port)
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
    print("休眠30秒")
    time.sleep(30)

    # 判断是否读取标记
    flag_throughput = False
    flag_average = False

    cnt = 0
    # 判断文件是否写入成功
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
    # 获取结果
    if cnt <= 20:
        return get_result()
    else:
        return (-1, -1)

# 使数据库回到原来状态
def data_recovery():

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
    print("关闭数据库")

    # 导入备份数据库
    os.system("psql -h 127.0.0.1 -p 5432 -U postgres wikipedia < /root/PG/wikipedia")

    # 清空各个记录日志
    print("清空各个日志记录")
    os.system(clean_status)
    os.system(clean_sar_u_com)
    os.system(clean_sar_d_com)
    os.system(del_result_file)
    print("各个日志记录清空完成")

    print("休眠60秒")
    time.sleep(60)


# 运行数据库进行测试
if __name__ == '__main__':

    for i in range(10):

        # 启动数据库
        start_PG()

        # 查看启动状态
        status_PG()

        # 复原数据库数据
        data_recovery()

        # 清空缓存
        free_cache()

        # 运行oltp
        print(run_PG_for_oltp())

        # 使数据库复原
        stop_PG()
