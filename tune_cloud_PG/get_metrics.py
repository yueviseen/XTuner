# -*- coding: gbk -*-

"""
基于规则的数据库调参
"""
import os
import shutil
import requests
import psycopg2
import pymysql
import time
from ip_24 import *
from multiprocessing import Process

def get_metrics_PG():

    conn = psycopg2.connect(host="127.0.0.1", user=user, password=password, database=database_wiki, port=i_port)
    cursor = conn.cursor()
    dict_stat = {}

    #  对pg_stat_database的相关数据库进行metrics抽取
    cursor.execute("select * from pg_stat_database where datname = 'wikipedia'")
    res = cursor.fetchall()

    # 该状态的0，1，20不加入计算
    list_pg_stat_database = ['datid',  'datname', 'numbackends', 'xact_commit', 'xact_rollback',
                             'blks_read', 'blks_hit', 'tup_returned', 'tup_fetched', 'tup_inserted',
                             'tup_updated', 'tup_deleted', 'conflicts', 'temp_files', 'temp_bytes',
                             'deadlocks', 'checksum_failures', 'checksum_last_failure','blk_read_time', 'blk_write_time', 'stats_reset']
    cnt = 0
    # print(res)
    # print(len(list_pg_stat_database))
    # print(len(res[0]))
    for i_res in res:
        for ii_res in i_res:
            if cnt == 0 or cnt == 1 or cnt == 20:
                cnt = cnt + 1
                continue
            else:
                key = "pg_stat_database_" + list_pg_stat_database[cnt]
                if ii_res is None:
                    ii_res = 0
                dict_stat[key] = ii_res
                # print(ii_res, list_pg_stat_database[cnt])
                cnt = cnt + 1
    # print(dict_stat)
    # print(len(dict_stat))

    # 获取pg_stat_bgwriter的metrics
    cursor.execute("select * from pg_stat_bgwriter")
    res = cursor.fetchall()
    # 该状态的10不加入状态
    list_pg_stat_bgwriter = [
        'checkpoints_timed', 'checkpoints_req', 'checkpoint_write_time',
        'checkpoint_sync_time', 'buffers_checkpoint', 'buffers_clean',
        'maxwritten_clean', 'buffers_backend', 'buffers_backend_fsync', 'buffers_alloc', 'stats_reset'
    ]
    cnt = 0
    # print(res)
    # print(len(list_pg_stat_bgwriter))
    # print(len(res[0]))
    for i_res in res:
        for ii_res in i_res:
            if cnt == 10:
                cnt = cnt + 1
                continue
            else:
                key = "pg_stat_bgwriter_" + list_pg_stat_bgwriter[cnt]
                if ii_res is None:
                    ii_res = 0
                dict_stat[key] = ii_res
                cnt = cnt + 1
    # print(dict_stat)
    # print(len(dict_stat))

    # 获取pg_stat_archiver的相关metrics
    cursor.execute("select * from pg_stat_archiver")
    res = cursor.fetchall()
    # 该状态的0, 3加入状态
    list_pg_stat_archiver = [
        'archived_count', 'last_archived_wal', 'last_archived_time', 'failed_count', 'last_failed_wal', 'last_failed_time', 'stats_reset'
    ]
    cnt = 0
    # print(res)
    # print(len(list_pg_stat_archiver))
    # print(len(res[0]))
    for i_res in res:
        for ii_res in i_res:
            if cnt != 0 and cnt != 3:
                cnt = cnt + 1
                continue
            else:
                key = "pg_stat_archiver_" + list_pg_stat_archiver[cnt]
                if ii_res is None:
                    ii_res = 0
                dict_stat[key] = ii_res
                cnt = cnt + 1
    # print(dict_stat)
    # print(len(dict_stat))

    # 获取pg_stat_database_conflicts相关的metrics
    cursor.execute("select * from pg_stat_database_conflicts where datname='wikipedia'")
    res = cursor.fetchall()
    # 该状态的0, 1不加入状态
    list_pg_stat_database_conflicts = [
        'datid', 'datname', 'confl_tablespace', 'confl_lock', 'confl_snapshot', 'confl_bufferpin', 'confl_deadlock'
    ]
    cnt = 0
    # print(res)
    # print(len(list_pg_stat_database_conflicts))
    for i_res in res:
        for ii_res in i_res:
            if cnt == 0 or cnt == 1:
                cnt = cnt + 1
                continue
            else:
                key = "pg_stat_database_conflicts_" + list_pg_stat_database_conflicts[cnt]
                if ii_res is None:
                    ii_res = 0
                dict_stat[key] = ii_res
                # print(ii_res, list_pg_stat_database[cnt])
                cnt = cnt + 1
    # print(dict_stat)
    # print(len(dict_stat))


    # 获取index的相关netrics
    cursor.execute("select * from pg_stat_user_indexes")
    res_1 = cursor.fetchall()
    # 该状态的0, 1, 2, 3, 4不加入状态
    list_pg_stat_user_indexes = [
        'relid', 'indexrelid', 'schemaname', 'relname', 'indexrelname', 'idx_scan', 'idx_tup_read', 'idx_tup_fetch'
    ]
    cursor.execute("select * from pg_statio_user_indexes")
    res_2 = cursor.fetchall()
    # 该状态的0, 1, 2不加入状态
    list_pg_statio_user_indexes = [
        'relid', 'indexrelid', 'schemaname',  'relname', 'indexrelname', 'idx_blks_read', 'idx_blks_hit'
    ]


    # print(res_1)
    # print(len(list_pg_stat_user_indexes))
    # print(len(res_1[0]))
    for i_res in res_1:
        cnt = 0
        for ii_res in i_res:
            if cnt == 0 or cnt == 1 or cnt == 2 or cnt == 3 or cnt == 4:
                cnt = cnt + 1
                continue
            else:
                key = i_res[3] + "_" + i_res[4] + "_" + list_pg_stat_user_indexes[cnt]
                if ii_res is None:
                    ii_res = 0
                dict_stat[key] = ii_res
                cnt = cnt + 1
    # print(dict_stat)
    # print(len(dict_stat))
    #
    #
    # print(res_2)
    # print(len(dict_stat))
    # print(len(list_pg_statio_user_indexes))
    for i_res in res_2:
        cnt = 0
        for ii_res in i_res:
            if cnt == 0 or cnt == 1 or cnt == 2 or cnt == 3 or cnt == 4:
                cnt = cnt + 1
                continue
            else:
                key = i_res[3] + "_" + i_res[4] + "_" + list_pg_statio_user_indexes[cnt]
                if ii_res is None:
                    ii_res = 0
                dict_stat[key] = ii_res
                cnt = cnt + 1
    print("1111111111111111")
    print(len(dict_stat))

    # # 获取pg_stat_user_tables 的metrics
    # cursor.execute("select * from pg_stat_user_tables")
    # res = cursor.fetchall()
    # # 该状态的0, 1, 2, 14, 15, 16,17不加入状态
    # list_pg_stat_user_tables = [
    #     'relid',  'schemaname',   'relname',   'seq_scan', 'seq_tup_read', 'idx_scan',
    #     'idx_tup_fetch',  'n_tup_ins', 'n_tup_upd', 'n_tup_del', 'n_tup_hot_upd',
    #     'n_live_tup', 'n_dead_tup', 'n_mod_since_analyze',  'last_vacuum',
    #     'last_autovacuum', 'last_analyze', 'last_autoanalyze', 'vacuum_count',
    #     'autovacuum_count', 'analyze_count', 'autoanalyze_count'
    # ]
    # cnt = 0
    # print(res)
    # for i_res in res:
    #     cnt = 0
    #     for ii_res in i_res:
    #         if cnt == 0 or cnt == 1 or cnt == 2 or cnt == 14 or cnt == 15 or cnt == 16 or cnt == 17:
    #             cnt = cnt + 1
    #             continue
    #         else:
    #             key = i_res[2] + "_" + list_pg_stat_user_tables[cnt]
    #             if ii_res is None:
    #                 ii_res = 0
    #             dict_stat[key] = ii_res
    #             # print(ii_res, list_pg_stat_database[cnt])
    #             cnt = cnt + 1
    # print(dict_stat)
    # print(len(dict_stat))
    #
    # # 获取"select * from pg_statio_user_tables"的相关信息metrics
    # cursor.execute("select * from pg_statio_user_tables")
    # res = cursor.fetchall()
    # # 该状态的0, 1, 2, 8,9,10,11不加入状态
    # list_pg_statio_user_tables = [
    #     'relid', 'schemaname',  'relname',  'heap_blks_read',
    #     'heap_blks_hit',  'idx_blks_read',  'idx_blks_hit',
    #     'toast_blks_read', 'toast_blks_hit', 'tidx_blks_read',
    #     'tidx_blks_hit'
    # ]
    # cnt = 0
    # print(res)
    # print(len(list_pg_statio_user_tables))
    # for i_res in res:
    #     cnt = 0
    #     for ii_res in i_res:
    #         if cnt == 0 or cnt == 1 or cnt == 2 or cnt == 7 or cnt == 8 or cnt == 9 or cnt == 10:
    #             cnt = cnt + 1
    #             continue
    #         else:
    #             key = i_res[2] + "_" + list_pg_statio_user_tables[cnt]
    #             if ii_res is None:
    #                 ii_res = 0
    #             dict_stat[key] = ii_res
    #             # print(ii_res, list_pg_stat_database[cnt])
    #             cnt = cnt + 1
    # print(dict_stat)
    # print(len(dict_stat))

    cursor.close()
    conn.close()

    return dict_stat

if __name__ == '__main__':
    get_metrics_PG()
