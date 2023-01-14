# -*- coding: gbk -*-
import os
import time

ip = "106.75.245.152"
user = "root"
password = "Yzw123456"
database = "tpcc"
database_ycsb = "ycsb"
database_wiki = "wikipedia"
i_port = 3306

# ���ݿ�Ŀ����ر�ָ��
start_mysql_cmd = "systemctl start mysqld"
stop_mysql_cmd = "systemctl stop mysqld"
status_mysql_cmd = "systemctl status mysqld"

# ������ݿ��Ƿ���
port_open = "netstat -tulpn"
port = ":3306"
mysql_safe_open = "/usr/sbin/mysqld"
pid_open = "ps -ef | grep mysqld"

# ��ջ���
free_cache_cmd = "echo 3 > /proc/sys/vm/drop_caches"

# ��������ָ��
oltp_cmd = "cd /root/oltpbench; ./oltpbenchmark -b tpcc -c config/sample_tpcc_config.xml --execute=true -s 10 -o outputfile"
oltp_cmd_background = "cd /root/oltpbench; ./oltpbenchmark -b tpcc -c config/sample_tpcc_config.xml --execute=true -s 10 -o outputfile &"
oltp_cmd_ycsb = "cd /root/oltpbench; ./oltpbenchmark -b ycsb -c config/sample_ycsb_config.xml --execute=true -s 10 -o outputfile"
oltp_cmd_ycsb_background = "cd /root/oltpbench; ./oltpbenchmark -b ycsb -c config/sample_ycsb_config.xml --execute=true -s 10 -o outputfile &"
oltp_cmd_wiki = "cd /root/oltpbench; ./oltpbenchmark -b wikipedia -c config/sample_wikipedia_config.xml --execute=true -s 10 -o outputfile"
oltp_cmd_wiki_background = "cd /root/oltpbench; ./oltpbenchmark -b wikipedia -c config/sample_wikipedia_config.xml --execute=true -s 10 -o outputfile &"
throught_char = "requests/sec"
del_result_file = "rm /root/oltpbench/results/output*"
del_inner_file = "rm /root/status/inner_metrics"
chown_result = "chown -R mysql:mysql /root/oltpbench/results"

# �ָ����ݿ�ָ��
mysql_path = "/var/lib/"
data_path = "/var/lib/mysql"
data_cp_path = "/var/lib/cp_mysql_init"
del_data_cmd = "rm -rf /var/lib/mysql"
cp_data_cmd = "cp -rf /var/lib/cp_mysql_init /var/lib/mysql"
clean_log_err = "echo '' >  /var/log/mysqld.log"
clean_inner_metrics = "echo '' > /root/status/inner_metrics"

# �ļ�·��
path_my_cnf = "/etc/my.cnf"
result_file_path = "/root/oltpbench/results/outputfile.summary"
status_path = "/root/status/status"
clean_status = "echo '' >  /root/status/status"
log_err_path = "/var/log/mysqld.log"
tunning_process_path = "/root/status/tuning_process"
clean_tuning_process = "echo '' > /root/status/tuning_process"
inner_metrics_path = "/root/status/inner_metrics"
memory_path = "/root/status/memory_replay"
model_path = "/root/status/model"


# �ռ���Ϣʱ��
run_time = 180
start_time = None

# sarָ����Ϣ
sar_num = int(run_time/10)
sar_u_com = "sar -u 10 " + str(sar_num) + "  > /root/status/sar_u &"
sar_d_com = "sar -d 10 " + str(sar_num) + " > /root/status/sar_d &"
clean_sar_u_com = "echo '' > /root/status/sar_u"
clean_sar_d_com = "echo '' > /root/status/sar_d"
path_sar_d = "/root/status/sar_d"
path_sar_u = "/root/status/sar_u"


# �������ݿ�
def start_mysql():
    if os.system(start_mysql_cmd) == 0:
        print("���ݿ⿪���ɹ�")


# �ر����ݿ�
def stop_mysql():
    if os.system(stop_mysql_cmd) == 0:
        print("���ݿ�ɹ��ر�")


# �ж����ݿ��״̬, ע�⣺Ϊ�˱�֤��ȫ������������30��
def status_mysql():
    # ���д���ͳ��
    cnt = 0
    # �ж����ݿ��Ƿ���������
    flag_start = False
    while True:
        cnt = cnt + 1

        # ��������������ѭ��
        if flag_start is True:
            break

        # ÿ�ε���˯��5��
        time.sleep(5)

        # �������ݿ���ٴ���������
        if cnt % 40 == 0:
            start_mysql()

        # �ж϶˿��Ƿ��
        tps = os.popen(port_open)
        for i_port in tps.readlines():
            if port in i_port and "mysqld" in i_port:
                flag_start = True
                break
    print("�˿ڿ��������ɹ�")

    flag_start = False
    cnt = 0
    while True:
        cnt = cnt + 1
        if flag_start is True:
            break
        time.sleep(5)

        # �������ݿ���ٴ�����
        if cnt % 40 == 0:
            start_mysql()

        # �ж�pid�Ƿ��
        tps = os.popen(pid_open)
        list_pid = tps.readlines()
        for i_pid in list_pid:
            if mysql_safe_open in i_pid:
                flag_start = True

    print("pid �����ɹ�")

    # �ж����ݿ��״̬
    cnt = 0
    flag_start = False
    while True:
        cnt = cnt + 1

        if flag_start is True:
            break

        time.sleep(5)

        if cnt % 40 == 0:
            start_mysql()

        status = os.popen(status_mysql_cmd)
        list_status = status.readlines()
        for i_status in list_status:
            if "active (running)" in i_status:
                flag_start = True
                break
    print("���ݿ�״̬����״̬")

    # Ϊ�˱�֤��ȫ���ٴεȴ�70����
    print("���ݿ�����60��")
    time.sleep(70)
    print("���ݿ����߽���")


# ��ջ���
def free_cache():
    print("��ʼ��ջ���")
    if os.system(free_cache_cmd) == 0:
        print("������ճɹ�")


if __name__ == "__main__":
    # ��ջ���
    free_cache()
    # # �������ݿ�
    start_mysql()
    # # �鿴���ݿ�״̬
    status_mysql()
    # # �ر����ݿ�
    stop_mysql()
    # print(sar_u_com)
    # os.system(sar_u_com)
    # time.sleep(100)
    # print("sssssss")
    # os.system(clean_sar_u_com)