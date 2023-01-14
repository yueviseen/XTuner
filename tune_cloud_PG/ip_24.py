# -*- coding: gbk -*-
import os
import time

ip = "127.0.0.1"
user = "postgres"
password = "postgres"
database = "tpcc"
database_ycsb = "ycsb"
database_wiki = "wikipedia"
i_port = 5432

# 数据库的开启关闭指令
start_PG_cmd = "systemctl restart postgresql-12"
stop_PG_cmd = "systemctl stop postgresql-12"
status_PG_cmd = "systemctl status postgresql-12"

# 检查数据库是否开启
port_open = "netstat -tulpn"
port = ":5432"
PG_open = "/usr/pgsql-12/bin/postmaster"
pid_open = "ps -ef | grep postgres"

# 清空缓存
free_cache_cmd = "echo 3 > /proc/sys/vm/drop_caches"

# 工作负载指令
oltp_cmd = "cd /root/oltpbench; ./oltpbenchmark -b tpcc -c config/pg_tpcc.xml --execute=true -s 10 -o outputfile"
oltp_cmd_background = "cd /root/oltpbench; ./oltpbenchmark -b tpcc -c config/pg_tpcc.xml --execute=true -s 10 -o outputfile &"
oltp_cmd_ycsb = "cd /root/oltpbench; ./oltpbenchmark -b ycsb -c config/pg_ycsb.xml --execute=true -s 10 -o outputfile"
oltp_cmd_ycsb_background = "cd /root/oltpbench; ./oltpbenchmark -b ycsb -c config/pg_ycsb.xml --execute=true -s 10 -o outputfile &"
oltp_cmd_wiki = "cd /root/oltpbench; ./oltpbenchmark -b wikipedia -c config/pg_wk.xml --execute=true -s 10 -o outputfile"
oltp_cmd_wiki_background = "cd /root/oltpbench; ./oltpbenchmark -b wikipedia -c config/pg_wk.xml --execute=true -s 10 -o outputfile &"
throught_char = "requests/sec"
del_result_file = "rm /root/oltpbench/results/output*"
result_file_path = "/root/oltpbench/results/outputfile.summary"
# del_inner_file = "rm /root/status/inner_metrics"
# chown_result = "chown -R mysql:mysql /root/oltpbench/results"

# 恢复数据库指令
# mysql_path = "/var/lib/"
# data_path = "/var/lib/mysql"
# data_cp_path = "/var/lib/cp_mysql_init"
# del_data_cmd = "rm -rf /var/lib/mysql"
# cp_data_cmd = "cp -rf /var/lib/cp_mysql_init /var/lib/mysql"
# clean_log_err = "echo '' >  /var/log/mysqld.log"
clean_inner_metrics = "echo '' > /root/status/inner_metrics"

# 文件路径
path_my_cnf = "/var/lib/pgsql/12/data/postgresql.conf"

status_path = "/root/status/status"
clean_status = "echo '' >  /root/status/status"
# log_err_path = "/var/log/mysqld.log"
# tunning_process_path = "/root/status/tuning_process"
clean_tuning_process = "echo '' > /root/status/tuning_process"
inner_metrics_path = "/root/status/inner_metrics"
memory_path = "/root/status/memory_replay"
# model_path = "/root/status/model"


# 收集信息时间
run_time = 180
start_time = None

# sar指令信息
sar_num = int(run_time/10)
sar_u_com = "sar -u 1 " + str(sar_num) + "  > /root/status/sar_u &"
sar_d_com = "sar -d 1 " + str(sar_num) + " > /root/status/sar_d &"
clean_sar_u_com = "echo '' > /root/status/sar_u"
clean_sar_d_com = "echo '' > /root/status/sar_d"
path_sar_d = "/root/status/sar_d"
path_sar_u = "/root/status/sar_u"


# 启动数据库
def start_PG():
    if os.system(start_PG_cmd) == 0:
        print("数据库开启成功")


# 关闭数据库
def stop_PG():
    if os.system(stop_PG_cmd) == 0:
        print("数据库成功关闭")


# 判断数据库的状态, 注意：为了保证安全，开启后休眠30秒
def status_PG():
    # 进行次数统计
    cnt = 0
    # 判断数据库是否真正启动
    flag_start = False
    while True:  # 主要判定端口是否打开
        cnt = cnt + 1

        # 满足条件则跳出循环
        if flag_start is True:
            break

        # 每次迭代睡眠5秒
        time.sleep(5)

        # 进行数据库的再次重启操作
        if cnt % 40 == 0:
            start_PG()

        # 判断端口是否打开
        tps = os.popen(port_open)
        for i_port in tps.readlines():
            if port in i_port and "postmaster" in i_port:
                print(i_port)
                flag_start = True
                break
    print("端口开启启动成功")

    flag_start = False
    cnt = 0
    while True:  # 判定PID是否开启成功
        cnt = cnt + 1
        if flag_start is True:
            break
        time.sleep(5)

        # 进行数据库的再次重启
        if cnt % 40 == 0:
            start_PG()

        # 判定pid是否打开
        tps = os.popen(pid_open)
        list_pid = tps.readlines()
        for i_pid in list_pid:
            if PG_open in i_pid:
                print(i_pid)
                flag_start = True

    print("pid 开启成功")

    # 判断数据库的状态
    cnt = 0
    flag_start = False
    while True:
        cnt = cnt + 1

        if flag_start is True:
            break

        time.sleep(5)

        if cnt % 40 == 0:
            start_PG()

        status = os.popen(status_PG_cmd)
        list_status = status.readlines()
        for i_status in list_status:
            if "active (running)" in i_status:
                flag_start = True
                print(i_status)
                break
    print("数据库状态开启状态")

    # 为了保证安全，再次等待30秒钟
    print("数据库休眠60秒")
    time.sleep(60)
    print("数据库休眠结束")


# 清空缓存
def free_cache():
    print("开始清空缓存")
    if os.system(free_cache_cmd) == 0:
        print("缓存清空成功")


if __name__ == "__main__":
    # 清空缓存
    free_cache()
    # 关闭数据库
    stop_PG()
    # 开启数据库
    start_PG()
    # 查看数据库状态
    status_PG()

    # print(sar_u_com)
    # os.system(sar_u_com)
    # print("sssssss")
    # # os.system(clean_sar_u_com)
    #
    # print(sar_d_com)
    # os.system(sar_d_com)
    # print("sssssss")
    # time.sleep(5)
    # os.system(clean_sar_d_com)