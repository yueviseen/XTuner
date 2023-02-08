# XTuner
An Interpretable Database Tuning Tool based on Knob Categorization

tune_cloud_PG 的文件说明：

(1) ip_24.py 主要是对各种文件路径的配置

(2) get_metrics.py 和 Rular_for_status_24.py 主要获取数据库内部的运行信息

(3) Ruler_for_sar_u_24.py 和 Rular_for_sar_d_24.py 主要获取系统的瓶颈信息

(4) Rular_for_mysql_sar_24_bot.py 跟据随机选择旋钮方法运行XTuner

(5) Rular_for_mysql_sar_24.py 根据系统瓶颈选择旋钮方法运行XTuner

(6) default_param_for_oltp_24.py 主要记录数据库的重启，关闭的函数

(7) Rular_for_oltp_24.py 主要记录如何使数据恢复和使用多线程记录运行信息的函数

tune_cloud_MySQL的文件说明：

(1) ip_24.py 主要是对各种文件路径的配置

(2) Rular_for_engine_24.py 和 Rular_for_status_24.py 主要获取数据库内部的运行信息

(3) Ruler_for_sar_u_24.py 和 Rular_for_sar_d_24.py 主要获取系统的瓶颈信息

(4) Rular_for_mysql_sar_24_bot.py 跟据随机选择旋钮方法运行XTuner

(5) Rular_for_mysql_sar_24.py 根据系统瓶颈选择旋钮方法运行XTuner

(6) default_param_for_oltp_24.py 主要记录数据库的重启，关闭的函数

(7) Rular_for_oltp_24.py 主要记录如何使数据恢复和使用多线程记录运行信息的函数

(8) rev_sort.py 和 rev_sort_other.py 使目前尝试的一些优化方法， 目前对XTuner的正常运行没有任何影响。


因此运行XTuner, 可以直接运行 Rular_for_mysql_sar_24.py。注意有些配置需要根据自己机器的情况进行适当调整，比如数据库启动命令，sar收集的信息记录的位置， 链接数据库的ip.这些配置大都记录在ip_24.py文件中。

