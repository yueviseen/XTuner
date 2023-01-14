# -*- coding: gbk -*-
"""
分析日志和show engine innodb status的数据
"""
from ip_24 import *

# 进行字典合并
def dict_merge(dict_list):
    for i in dict_list:
        mid = {}
        for ii in dict_list[i]:
            mid.update(ii)
        dict_list[i] = mid
    return dict_list


def analysis_TRANSACTIONS(str_line):

    # 记录返回的字典
    return_list = {}
    if "History list length" in str_line:
        mid = str_line.replace("\n", '').split(" ")
        return_list["History_list_length"] = int(mid[3])
    elif "Trx id counter" in str_line:
        mid = str_line.replace("\n", '').split(" ")
        # print(mid)
        return_list["Trx_id_counter"] = int(mid[3])
    elif "Purge done for trx's" in str_line:
        mid = str_line.replace("\n", '').split(" undo")
        return_list["Purge_done_for_trx's"] = int(mid[0].split("< ")[1])

    if len(return_list) == 0:
        return 0
    else:
        return return_list


# 对ROW OPERATIONS进行信息提取
def analysis_ROW_OPERATIONS(str_line):

    # 记录返回的字典
    return_list = {}
    if "queries inside InnoDB" in str_line:
        mid = str_line.replace("\n", '').split(", ")
        # print(mid)
        return_list["queries_inside_InnoDB"] = int(mid[0].split(" ")[0])
        return_list["queries_in_queue"] = int(mid[1].split(" ")[0])
    elif "read views open inside InnoDB" in str_line:
        mid = str_line.replace("\n", '').split(" ")
        # print(mid)
        return_list["read_views_open_inside_InnoDB"] = int(mid[0])
    elif "Number of rows inserted" in str_line:
        mid = str_line.replace("\n", '').split(", ")
        # print(mid)
        return_list["Number_of_rows_inserted"] = int(mid[0].split(" ")[4])
        return_list["Number_of_rows_updated"] = int(mid[1].split(" ")[1])
        return_list["Number_of_rows_deleted"] = int(mid[2].split(" ")[1])
        return_list["Number_of_rows_read"] = int(mid[3].split(" ")[1])
    elif "inserts/s" in str_line and "updates/s" in str_line and "deletes/s" in str_line:
        mid = str_line.replace("\n", '').split(", ")
        # print(mid)
        return_list["inserts/s"] = float(mid[0].split(" ")[0])
        return_list["updates/s"] = float(mid[1].split(" ")[0])
        return_list["deletes/s"] = float(mid[2].split(" ")[0])
        return_list["reads/s"] = float(mid[3].split(" ")[0])
    elif "Number of system rows inserted" in str_line:
        mid = str_line.replace("\n", '').split(", ")
        return_list["Number_of_system_rows_inserted"] = int(mid[0].split(" ")[5])
        return_list["Number_of_system_rows_updated"] = int(mid[1].split(" ")[1])
        return_list["Number_of_system_rows_deleted"] = int(mid[2].split(" ")[1])
        return_list["Number_of_system_rows_reads"] = int(mid[3].split(" ")[1])

    if len(return_list) == 0:
        return 0
    else:
        return return_list


# 对INSERT BUFFER AND ADAPTIVE HASH INDEX进行信息提取
def analysis_INSERT_BUFFER_AND_ADAPTIVE_HASH_INDEX(str_line):

    # 记录返回的字典
    return_list = {}
    if "Ibuf: size" in str_line:
        mid = str_line.replace("\n", '').split(", ")
        return_list["Ibuf_size"] = int(mid[0].split(" ")[2])
        return_list["free_list_len"] = int(mid[1].split(" ")[3])
        return_list["seg_size"] = int(mid[2].split(" ")[2])
        return_list["merges"] = int(mid[3].split(" ")[0])
    elif "hash searches/s" in str_line:
        mid = str_line.replace("\n", '').split(", ")
        return_list["hash_searches/s"] = float(mid[0].split(" ")[0])
        return_list["non-hash_searches/s"] = float(mid[1].split(" ")[0])

    if len(return_list) == 0:
        return 0
    else:
        return return_list


# 对 BUFFER POOL AND MEMORY进行信息抽取
def analysis_BUFFER_POOL_AND_MEMORY(str_line):

    # 记录返回字典
    return_list = {}
    if "Total large memory allocated" in str_line:
        mid = str_line.replace("\n", '').split(" ")
        # print(mid)
        return_list["Total_large_memory_allocated"] = int(mid[4])
    elif "Dictionary memory allocated" in str_line:
        mid = str_line.replace("\n", '').split(" ")
        # print(mid)
        return_list["Dictionary_memory_allocated"] = int(mid[3])
    elif "Buffer pool size" in str_line:
        mid = str_line.replace("\n", '').split(" ")
        # print(mid)
        return_list["Buffer_pool_size"] = int(mid[5])
    elif "Free buffers" in str_line:
        mid = str_line.replace("\n", '').split(" ")
        # print(mid)
        return_list["Free_buffers"] = int(mid[8])
    elif "Database pages" in str_line:
        mid = str_line.replace("\n", '').split(" ")
        # print(mid)
        return_list["Database_pages"] = int(mid[6])
    elif "Old database pages" in str_line:
        mid = str_line.replace("\n", '').split(" ")
        # print(mid)
        return_list["Old_database_pages"] = int(mid[3])
    elif "Modified db pages" in str_line:
        mid = str_line.replace("\n", '').split(" ")
        # print(mid)
        return_list["Modified_db_pages"] = int(mid[4])
    elif "Pending reads" in str_line:
        mid = str_line.replace("\n", '').split(" ")
        # print(mid)
        return_list["Pending_reads"] = int(mid[7])
    elif "Pending writes" in str_line:
        mid = str_line.replace("\n", '').split(": ")
        mid = mid[1].split(", ")
        # print(mid)
        return_list["LRU"] = int(mid[0].split(" ")[1])
        return_list["flush_list"] = int(mid[1].split(" ")[2])
        return_list["single_page"] = int(mid[2].split(" ")[2])
    elif "Pages made young" in str_line:
        mid = str_line.replace("\n", '').split(", ")
        # print(mid)
        return_list["Pages_made_young"] = int(mid[0].split(" ")[3])
        return_list["not_young"] = int(mid[1].split(" ")[2])
    elif "youngs/s" in str_line and "non-youngs/s" in str_line:
        mid = str_line.replace("\n", '').split(", ")
        # print(mid)
        return_list["youngs/s"] = float(mid[0].split(" ")[0])
        return_list["non-youngs/s"] = float(mid[1].split(" ")[0])
    elif "Pages read" in str_line and "created" in str_line:
        mid = str_line.replace("\n", '').split(", ")
        # print(mid)
        return_list["Pages_read"] = int(mid[0].split(" ")[2])
        return_list["created"] = int(mid[1].split(" ")[1])
        return_list["written"] = int(mid[2].split(" ")[1])
    elif "reads/s" in str_line and "creates/s" in str_line:
        mid = str_line.replace("\n", '').split(", ")
        # print(mid)
        return_list["reads/s"] = float(mid[0].split(" ")[0])
        return_list["creates/s"] = float(mid[1].split(" ")[0])
        return_list["writes/s"] = float(mid[2].split(" ")[0])
    elif "Buffer pool hit rate" in str_line:
        mid = str_line.replace("\n", '').split(", ")
        # print(mid)
        mid_mid = mid[0].split(" ")
        return_list["Buffer_pool_hit_rate"] = (int(mid_mid[4])/int(mid_mid[6]))
    elif "Pages read ahead" in str_line:
        read_ahead_array = str_line.split(", ")
        return_list["read_ahead"] = float(read_ahead_array[0].split(" ")[3].split("/")[0])
        return_list["evicted_without_access"] = float(read_ahead_array[1].split(" ")[3].split("/")[0])
        return_list["random_read_ahead"] = float(read_ahead_array[2].split(" ")[3].split("/")[0])

    if len(return_list) == 0:
        return 0
    else:
        return return_list


# 对analysis_SEMAPHORES进行信息提取
def analysis_SEMAPHORES(str_line):

    # 记录返回的列表
    return_list = {}
    if "reservation count" in str_line:
        mid = str_line.replace(" ", '').replace("\n", '').split("reservationcount")
        return_list["reservation_count"] = int(mid[1])
    elif "signal count" in str_line:
        mid = str_line.replace(" ", '').replace("\n", '').split("signalcount")
        return_list["signal_count"] = int(mid[1])
    elif "RW-shared spins" in str_line:
        mid = str_line.replace("\n", '').split(",")
        # print(mid)
        return_list["RW_shared_spins"] = int(mid[0].split(" ")[2])
        return_list["RW-shared_spins_rounds"] = int(mid[1].split(" ")[2])
        return_list["RW-shared_spins_OS_waits"] = int(mid[2].split(" ")[3])
    elif "RW-excl spins" in str_line:
        mid = str_line.replace("\n", '').split(",")
        # print(mid)
        return_list["RW_excl_spins"] = int(mid[0].split(" ")[2])
        return_list["RW-excl_spins_rounds"] = int(mid[1].split(" ")[2])
        return_list["RW_excl_spins_OS_waits"] = int(mid[2].split(" ")[3])
    elif "RW-sx spins" in str_line:
        mid = str_line.replace("\n", '').split(",")
        # print(mid)
        return_list["RW_sx_spins"] = int(mid[0].split(" ")[2])
        return_list["RW_sx_spins_rounds"] = int(mid[1].split(" ")[2])
        return_list["RW_sx_spins_OS_waits"] = int(mid[2].split(" ")[3])

    if len(return_list) == 0:
        return 0
    else:
        return return_list


# 对 FILE I/O 进行信息提取
def analysis_FILE_I_O(str_line):

    # 记录返回列表
    return_list = {}
    if "Pending normal aio reads" in str_line:
        # print(str_line)
        mid = str_line.replace(" ", '').replace("\n", '').split("]")
        # print(mid)
        mid_read = mid[0].split("[")[1].split(",")
        return_list["Pending_normal_aio_reads"] = []
        for i in mid_read:
            return_list["Pending_normal_aio_reads"].append(int(i))
        return_list["Pending_normal_aio_writes"] = []
        # print(mid)
        if (len(mid[1])>1):
            mid_write = mid[1].split("[")[1].split(",")
            for i in mid_write:
                return_list["Pending_normal_aio_writes"].append(int(i))
        else:
            return_list["Pending_normal_aio_writes"].append(None)
    elif "ibuf aio reads" in str_line:
        # print(str_line)
        mid = str_line.replace("\n", '').replace(" ", '').split(",")
        # print(mid)
        return_list["ibuf_aio_reads"] = None
        return_list["log_i/o's"] = None
        return_list["sync_i/o's"] = None
        if len(mid) > 1 and len(mid[0].split(":")[1]) > 0:
            return_list["ibuf_aio_reads"] = int(mid[0].split(":")[1])
        if len(mid) > 2 and len(mid[1].split(":")[1]) > 0:
            return_list["log_i/o's"] = int(mid[1].split(":")[1])
        if len(mid) > 3 and len(mid[2].split(":")[1]) > 0:
            return_list["sync_i/o's"] = int(mid[2].split(":")[1])
    elif "Pending flushes (fsync) log" in str_line:
        mid = str_line.replace(" ", '').replace("\n", '').split(";")
        # print(mid)
        return_list["Pending_flushes_(fsync)_log"] = int(mid[0].split(":")[1])
        return_list["buffer_pool"] = int(mid[1].split(":")[1])
    elif "OS file reads" in str_line:
        mid = str_line.replace("\n", '').split(", ")
        # print(mid)
        return_list["OS_file_reads"] = int(mid[0].split(" ")[0])
        return_list["OS_file_writes"] = int(mid[1].split(" ")[0])
        return_list["OS_fsyncs"] = int(mid[2].split(" ")[0])
    elif "pending preads" in str_line:
        mid = str_line.replace("\n", '').split(", ")
        # print(mid)
        return_list["pending_preads"] = int(mid[0].split(" ")[0])
        return_list["pending_pwrites"] = int(mid[1].split(" ")[0])
    elif "reads/s" in str_line and "bytes/read" in str_line:
        mid = str_line.replace("\n", '').split(", ")
        # print(mid)
        return_list["reads/s"] = float(mid[0].split(" ")[0])
        return_list["avg_bytes/read"] = float(mid[1].split(" ")[0])
        return_list["writes/s"] = float(mid[2].split(" ")[0])
        return_list["fsyncs/s"] = float(mid[3].split(" ")[0])

    if len(return_list) == 0:
        return 0
    else:
        return return_list


# 对BACKGROUND THREAD进行信息抽取
def analysis_BACKGROUND_THREAD(str_line):

    # 该列表记录返回值
    return_list = {}
    if "srv_master_thread log flush and writes" in str_line:
        log_flush_and_writes = str_line.split(":")[1].replace(" ", '')
        return_list["log_flush_and_writes"] = int(log_flush_and_writes)
    elif "srv_master_thread loops" in str_line:
        mid = str_line.split(":")[1].replace("\n", '').replace(" ", '').split(',')
        mid[0] = mid[0].replace("srv_active", '')
        mid[1] = mid[1].replace("srv_shutdown", '')
        mid[2] = mid[2].replace("srv_idle", '')
        return_list["srv_active"] = (int(mid[0]))
        return_list["srv_shutdown"] = (int(mid[1]))
        return_list["srv_idle"] = (int(mid[2]))
        # print(int(mid[0]), int(mid[1]), int(mid[2]))

    if len(return_list) == 0:
        return 0
    else:
        return return_list


# 对LOG进行信息抽取
def analysis_LOG(str_line):

    # 该列表记录返回值
    return_list = {}
    str1 = "Log sequence number"
    str2 = "Log buffer assigned up to"
    str3 = "Log buffer completed up to"
    str4 = "Log written up to"
    str5 = "Log flushed up to"
    str6 = "Added dirty pages up to"
    str7 = "Pages flushed up to"
    str8 = "Last checkpoint at"
    str_list = [str1, str2, str3, str4, str5, str6, str7, str8]

    for i in str_list:
        if i in str_line:
            mid = str_line.replace(i, '').replace(" ", '').replace("\n", '')
            return_list[i] = int(mid)

    if "i/o's/second" in str_line:
        mid = str_line.replace("\n", '').split(",")
        mid_done = float(mid[0].split(" log")[0])
        return_list["done"] = mid_done
        mid = mid[1].replace(" ", '').replace("logi/o's/second", '')
        return_list["i/o's/second"] = float(mid)

    if len(return_list) == 0:
        return 0
    else:
        return return_list

# 分析 err_log, 获取各个模块的编号
def analysis_errlog(path_errlog):

    # 获取文件信息
    with open(path_errlog, 'r') as f:
        status_list_list = f.readlines()

    # 记录日志的内容和innodb状态的内容
    log_list = []  # 记录mysql警告的日志内容
    engine_status_list_list_clean = []  # 记录innodb状态的内容

    # 分别提取日志和engine status信息
    for i_status_list in status_list_list:
        if "Warning" in i_status_list or "Note" in i_status_list:
            log_list.append(i_status_list)
        else:
            engine_status_list_list_clean.append(i_status_list)

    # 记录innodb状态的相关行号
    start_num_list = []
    end_num_list = []
    BACKGROUND_THREAD_list = []
    SEMAPHORES_list = []
    LATEST_DETECTED_DEADLOCK_list = []
    TRANSACTIONS_list = []
    FILE_IO_list = []
    INSERT_BUFFER_AND_ADAPTIVE_HASH_INDEX_list = []
    LOG_list = []
    BUFFER_POOL_AND_MEMORY_list = []
    ROW_OPERATIONS_list = []

    # 记录每个模块的名字
    str1 = "BACKGROUND THREAD"
    str2 = "SEMAPHORES"
    str3 = "LATEST DETECTED DEADLOCK"
    str4 = "TRANSACTIONS"
    str5 = "FILE I/O"
    str6 = "INSERT BUFFER AND ADAPTIVE HASH INDEX"
    str7 = "LOG"
    str8 = "BUFFER POOL AND MEMORY"
    str9 = "ROW OPERATIONS"

    cnt = 0
    # 记录每次采样的起始行号
    for i_status_list in engine_status_list_list_clean:
        if "END OF INNODB MONITOR OUTPUT" in i_status_list:
            end_num_list.append(cnt)
        elif "INNODB MONITOR OUTPUT" in i_status_list:
            start_num_list.append(cnt)
        cnt = cnt + 1

    # 将每次采样的起始编号汇总
    start_end_list = []
    if len(start_num_list) == len(end_num_list):
        for i in range(len(start_num_list)):
                start_end_list.append((start_num_list[i], end_num_list[i]))
    else:
        print("格式有误!!!!!!!")

    # 获取各个模块的起始行号， 如果该模块不存在则用0标记占位符
    cnt = 0
    for i in start_end_list:
        cnt = cnt + 1
        for ii in range(i[0], i[1]):
            if str1 in engine_status_list_list_clean[ii] and "---" in engine_status_list_list_clean[ii+1]:
                BACKGROUND_THREAD_list.append(ii)
            elif str2 in engine_status_list_list_clean[ii] and "---" in engine_status_list_list_clean[ii+1]:
                SEMAPHORES_list.append(ii)
            elif str3 in engine_status_list_list_clean[ii] and "---" in engine_status_list_list_clean[ii+1]:
                LATEST_DETECTED_DEADLOCK_list.append(ii)
            elif str4 in engine_status_list_list_clean[ii] and len(engine_status_list_list_clean[ii]) < 14:
                TRANSACTIONS_list.append(ii)
            elif str5 in engine_status_list_list_clean[ii] and "---" in engine_status_list_list_clean[ii+1]:
                FILE_IO_list.append(ii)
            elif str6 in engine_status_list_list_clean[ii] and "---" in engine_status_list_list_clean[ii+1]:
                INSERT_BUFFER_AND_ADAPTIVE_HASH_INDEX_list.append(ii)
            elif str7 in engine_status_list_list_clean[ii] and "---" in engine_status_list_list_clean[ii+1]:
                LOG_list.append(ii)
            elif str8 in engine_status_list_list_clean[ii] and "---" in engine_status_list_list_clean[ii+1]:
                BUFFER_POOL_AND_MEMORY_list.append(ii)
            elif str9 in engine_status_list_list_clean[ii] and "---" in engine_status_list_list_clean[ii+1]:
                ROW_OPERATIONS_list.append(ii)
        if len(BACKGROUND_THREAD_list) < cnt:
            BACKGROUND_THREAD_list.append(0)
            raise ValueError("出现错误")
        if len(SEMAPHORES_list) < cnt:
            SEMAPHORES_list.append(0)
            raise ValueError("出现错误")
        if len(LATEST_DETECTED_DEADLOCK_list) < cnt:
            LATEST_DETECTED_DEADLOCK_list.append(0)
        if len(TRANSACTIONS_list) < cnt:
            TRANSACTIONS_list.append(0)
        if len(FILE_IO_list) < cnt:
            FILE_IO_list.append(0)
            raise ValueError("出现错误")
        if len(INSERT_BUFFER_AND_ADAPTIVE_HASH_INDEX_list) < cnt:
            INSERT_BUFFER_AND_ADAPTIVE_HASH_INDEX_list.append(0)
            raise ValueError("出现错误")
        if len(LOG_list) < cnt:
            LOG_list.append(0)
            raise ValueError("出现错误")
        if len(BUFFER_POOL_AND_MEMORY_list) < cnt:
            BUFFER_POOL_AND_MEMORY_list.append(0)
            raise ValueError("出现错误")
        if len(ROW_OPERATIONS_list) < cnt:
            ROW_OPERATIONS_list.append(0)
            raise ValueError("出现错误")

    # 打印行号
    # print(start_end_list, len(start_end_list))
    # print(BACKGROUND_THREAD_list, len(BACKGROUND_THREAD_list))
    # print(SEMAPHORES_list, len(SEMAPHORES_list))
    # print(LATEST_DETECTED_DEADLOCK_list, len(LATEST_DETECTED_DEADLOCK_list))
    # print(TRANSACTIONS_list, len(TRANSACTIONS_list))
    # print(FILE_IO_list, len(FILE_IO_list))
    # print(INSERT_BUFFER_AND_ADAPTIVE_HASH_INDEX_list, len(INSERT_BUFFER_AND_ADAPTIVE_HASH_INDEX_list))
    # print(LOG_list, len(LOG_list))
    # print(BUFFER_POOL_AND_MEMORY_list, len(BUFFER_POOL_AND_MEMORY_list))
    # print(ROW_OPERATIONS_list, len(ROW_OPERATIONS_list))

    # 记录每个模块的范围
    BACKGROUND_THREAD_list_range = []
    SEMAPHORES_list_range = []
    LATEST_DETECTED_DEADLOCK_list_range = []
    TRANSACTIONS_list_range = []
    FILE_IO_list_range = []
    INSERT_BUFFER_AND_ADAPTIVE_HASH_INDEX_list_range = []
    LOG_list_range = []
    BUFFER_POOL_AND_MEMORY_list_range = []
    ROW_OPERATIONS_list_range = []

    # 进行范围的划分
    for i in range(len(start_end_list)):
        if TRANSACTIONS_list[i] == 0:
            TRANSACTIONS_list[i] = FILE_IO_list[i]
        if LATEST_DETECTED_DEADLOCK_list[i] == 0:
            LATEST_DETECTED_DEADLOCK_list[i] = TRANSACTIONS_list[i]
        BACKGROUND_THREAD_list_range.append((BACKGROUND_THREAD_list[i], SEMAPHORES_list[i]))
        SEMAPHORES_list_range.append((SEMAPHORES_list[i], LATEST_DETECTED_DEADLOCK_list[i]))
        LATEST_DETECTED_DEADLOCK_list_range.append((LATEST_DETECTED_DEADLOCK_list[i], TRANSACTIONS_list[i]))
        TRANSACTIONS_list_range.append((TRANSACTIONS_list[i], FILE_IO_list[i]))
        FILE_IO_list_range.append((FILE_IO_list[i], INSERT_BUFFER_AND_ADAPTIVE_HASH_INDEX_list[i]))
        INSERT_BUFFER_AND_ADAPTIVE_HASH_INDEX_list_range.append((INSERT_BUFFER_AND_ADAPTIVE_HASH_INDEX_list[i], LOG_list[i]))
        LOG_list_range.append((LOG_list[i], BUFFER_POOL_AND_MEMORY_list[i]))
        BUFFER_POOL_AND_MEMORY_list_range.append((BUFFER_POOL_AND_MEMORY_list[i], ROW_OPERATIONS_list[i]))
        ROW_OPERATIONS_list_range.append((ROW_OPERATIONS_list[i], end_num_list[i]))

    # 打印行号
    # print(start_end_list, len(start_end_list))
    # print(BACKGROUND_THREAD_list_range, len(BACKGROUND_THREAD_list_range))
    # print(SEMAPHORES_list_range, len(SEMAPHORES_list_range))
    # print(LATEST_DETECTED_DEADLOCK_list_range, len(LATEST_DETECTED_DEADLOCK_list_range))
    # print(TRANSACTIONS_list_range, len(TRANSACTIONS_list_range))
    # print(FILE_IO_list_range, len(FILE_IO_list_range))
    # print(INSERT_BUFFER_AND_ADAPTIVE_HASH_INDEX_list_range, len(INSERT_BUFFER_AND_ADAPTIVE_HASH_INDEX_list_range))
    # print(LOG_list_range, len(LOG_list_range))
    # print(BUFFER_POOL_AND_MEMORY_list_range, len(BUFFER_POOL_AND_MEMORY_list_range))
    # print(ROW_OPERATIONS_list_range, len(ROW_OPERATIONS_list_range))

    return log_list, engine_status_list_list_clean, BACKGROUND_THREAD_list_range, \
           SEMAPHORES_list_range, LATEST_DETECTED_DEADLOCK_list_range, TRANSACTIONS_list_range, FILE_IO_list_range, \
           INSERT_BUFFER_AND_ADAPTIVE_HASH_INDEX_list_range, LOG_list_range, BUFFER_POOL_AND_MEMORY_list_range, \
           ROW_OPERATIONS_list_range


def analysis_model():
    # 分析err_log数据
    global log_err_path
    log_list, engine_status_list_list_clean, BACKGROUND_THREAD_list_range, \
    SEMAPHORES_list_range, LATEST_DETECTED_DEADLOCK_list_range, TRANSACTIONS_list_range, FILE_IO_list_range, \
    INSERT_BUFFER_AND_ADAPTIVE_HASH_INDEX_list_range, LOG_list_range, BUFFER_POOL_AND_MEMORY_list_range, \
    ROW_OPERATIONS_list_range = analysis_errlog(log_err_path)

    # 1, 进行LOG模块分析
    engine_log_list = []
    for i in LOG_list_range:
        mid_list = {}
        for ii in range(i[0], i[1]):
            mid = analysis_LOG(engine_status_list_list_clean[ii])
            if mid != 0:
                mid_list.update(mid)
        engine_log_list.append(mid_list)
    # for i in engine_log_list:
    #     print(i)
    # print(len(engine_log_list))

    # 2 进行semaphores分析
    engine_semaphores_list = []
    for i in SEMAPHORES_list_range:
        mid_list = {}
        cnt = 0
        cnt_1 = 0
        cnt_2 = 0
        for ii in range(i[0], i[1]):
            mid = analysis_SEMAPHORES(engine_status_list_list_clean[ii])
            if mid != 0:
                mid_list.update(mid)
            if "created in file buf0buf.cc" in engine_status_list_list_clean[ii]:
                cnt = cnt + 1
            if "created in file btr0sea" in engine_status_list_list_clean[ii]:
                cnt_1 = cnt_1 + 1
            if "created in file dict0dict" in engine_status_list_list_clean[ii]:
                cnt_2 = cnt_2 + 1
        mid_list["buf0buf"] = cnt
        mid_list["btr0sea"] = cnt_1
        mid_list["dict0dict"] = cnt_2
        engine_semaphores_list.append(mid_list)
    # for i in engine_semaphores_list:
    #     print(i)
    # print(len(engine_semaphores_list))

    # 3 对file i/o 进行分析
    engine_file_io_list = []
    for i in FILE_IO_list_range:
        mid_list = {}
        for ii in range(i[0], i[1]):
            mid = analysis_FILE_I_O(engine_status_list_list_clean[ii])
            if mid != 0:
                mid_list.update(mid)
        engine_file_io_list.append(mid_list)
    # for i in engine_file_io_list:
    #     print(i)
    # print(len(engine_file_io_list))


    # 4 对 INSERT BUFFER AND ADAPTIVE HASH INDEX 进行分析
    engine_insert_buferr_and_AHI_index = []
    for i in INSERT_BUFFER_AND_ADAPTIVE_HASH_INDEX_list_range:
        mid_list = {}
        sum_size = 0
        occupy_size = 0
        for ii in range(i[0], i[1]):
            mid = analysis_INSERT_BUFFER_AND_ADAPTIVE_HASH_INDEX(engine_status_list_list_clean[ii])
            if mid != 0:
                mid_list.update(mid)
            if "merged operations" in engine_status_list_list_clean[ii]:
                mid_ii = ii + 1
                merge_array = engine_status_list_list_clean[mid_ii].split(", ")
                # print(merge_array)
                merged_operations = int(merge_array[0].split(" ")[2]) + int(merge_array[1].split(" ")[2]) + int(merge_array[2].split(" ")[1])
                mid_list["merged_operations"] = merged_operations
            if "discarded operations" in engine_status_list_list_clean[ii]:
                mid_ii = ii + 1
                dismerge_array = engine_status_list_list_clean[mid_ii].split(", ")
                # print(dismerge_array)
                dismerged_operations = int(dismerge_array[0].split(" ")[2]) + int(dismerge_array[1].split(" ")[2]) + int(dismerge_array[2].split(" ")[1])
                mid_list["discarded_operations"] = dismerged_operations
            if "Hash table size" in engine_status_list_list_clean[ii]:
                hash_table_array = engine_status_list_list_clean[ii].split(", ")
                sum_size = sum_size + int(hash_table_array[0].split(" ")[3])
                occupy_size = occupy_size + int(hash_table_array[1].split(" ")[3])
        mid_list["hash_table_size"] = sum_size
        mid_list["node_heap"] = occupy_size
        engine_insert_buferr_and_AHI_index.append(mid_list)
    # for i in engine_insert_buferr_and_AHI_index:
    #     print(i)
    # print(len(engine_insert_buferr_and_AHI_index))

    # 5 对buffer pool进行分析
    engine_buffer_pool_list = []
    for i in BUFFER_POOL_AND_MEMORY_list_range:
        mid_list = {}
        for ii in range(i[0], i[1]):
            # 不记录各个buffer pool的详细信息，只记录总体信息
            if "INDIVIDUAL BUFFER POOL INFO" in engine_status_list_list_clean[ii]:
                break
            mid = analysis_BUFFER_POOL_AND_MEMORY(engine_status_list_list_clean[ii])
            if mid != 0:
                mid_list.update(mid)
        engine_buffer_pool_list.append(mid_list)
    # for i in engine_buffer_pool_list:
    #     print(i)
    # print(len(engine_buffer_pool_list))

    # 6 对transactions 进行分析
    engine_transactions_list = []
    for i in TRANSACTIONS_list_range:
        mid_list = {}
        lock_wait_sum = 0
        lock_wait_num = 0
        # print(i)
        for ii in range(i[0], i[1]):
            mid = analysis_TRANSACTIONS(engine_status_list_list_clean[ii])
            if mid != 0:
                mid_list.update(mid)
            if "LOCK WAIT" in engine_status_list_list_clean[ii]:
                lock_wait_sum = lock_wait_sum + int(engine_status_list_list_clean[ii].split(", ")[0].split(" ")[2])
                lock_wait_num = lock_wait_num + 1
        mid_list["lock_wait_sum"] = lock_wait_sum
        mid_list["lock_wait_num"] = lock_wait_num
        engine_transactions_list.append(mid_list)
    # for i in engine_transactions_list:
    #     print(i)
    # print(len(engine_transactions_list))

    # 7 对row operations进行分析
    engine_row_operations_list = []
    for i in ROW_OPERATIONS_list_range:
        mid_list = {}
        for ii in range(i[0], i[1]):
            mid = analysis_ROW_OPERATIONS(engine_status_list_list_clean[ii])
            if mid != 0:
                mid_list.update(mid)
        engine_row_operations_list.append(mid_list)
    # for i in engine_row_operations_list:
    #     print(i)
    # print(len(engine_row_operations_list))

    return_dict = {}
    return_dict["log"] = log_list
    return_dict["LOG"] = engine_log_list
    return_dict["file_io"] = engine_file_io_list
    return_dict["row_operations"] = engine_row_operations_list
    return_dict["buffer_pool"] = engine_buffer_pool_list

    return_dict["insert_AHI"] = engine_insert_buferr_and_AHI_index
    return_dict["semaphores"] = engine_semaphores_list
    return_dict["transactions"] = engine_transactions_list
    return return_dict


if __name__ == "__main__":
    model_dict = analysis_model()
    # for i in model_dict:
    #     print(i, model_dict[i])

    print("---------------\n")
    for i in model_dict["file_io"]:
        print(i)
