#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################
import logging
import os
import time
import psycopg2
import MaaPi_Config as Config
from datetime import datetime as dt
import queue

pwd = os.getcwd()
logging.basicConfig(
    filename=f'{pwd}/log/Maapi_logger.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %H:%M:%S')


class MaaPiDBConnection():
    def __init__(self):
        self.objectname = "Database"
        self.filters_ = {}
        self.orders_ = {}
        self.columns_ = {}
        self.queuecommitQuery = queue.Queue()
        self.queuefetchoneQuery = {}
        self.queuefetchallQuery = {}
        self.columns_var = {}
        self.table_ = {}
        self.config = Config.MaapiVars()
        self.Maapi_dbName = self.config.maapiDbName
        self.Maapi_dbUser = self.config.maapiDbUser
        self.Maapi_dbHost = self.config.maapiDbHost
        self.Maapi_dbPasswd = self.config.maapiDbpass
        self.db_string = (
            f"dbname='{self.Maapi_dbName}' "
            f"user='{self.Maapi_dbUser}' "
            f"host='{self.Maapi_dbHost}' "
            f"password='{self.Maapi_dbPasswd}'"
            )
        self.cur = object
        self.conn = object
        self.dbInnit(False)
        self.isRunning = True


    def logPrintOnly(self, level, msg):
        """Print logs to console"""
        try:
            time = (
                f"{dt.now().hour:0>2}:{dt.now().minute:0>2}:"
                f"{dt.now().second:0>2} - {dt.now().microsecond:0>6}"
                )
            print(
                f"MaaPi  |  {self.name:<17}  |  {level:^6}  |  "
                f"{time:<16}  |  {msg}"
                )
        except:
            pass

    def dbInnit(self, state):
        if state:
            time.sleep(0.1)
            try:
                self.conn.close()
            except:
                self.logPrintOnly("ERROR", f'DB not connected')
        try:
            self.conn = psycopg2.connect(self.db_string)
        except (Exception, psycopg2.DatabaseError) as error:
            self.logPrintOnly("ERROR", f'Insert RAW error: {error}')
        else:
            self.isRunning = True


    def commitQuery(self, query):
        """insert row data to dabase"""
        self.queuecommitQuery.put(query)
        try:
            while not self.queuecommitQuery.empty():
                with self.conn.cursor() as cur:
                    cur.execute(f"{(self.queuecommitQuery.queue)[0]}")
                    self.conn.commit()
                    self.queuecommitQuery.get()

        except (Exception, psycopg2.DatabaseError) as error:
            self.logPrintOnly("ERROR", f'commitQuery error: {error}')
            self.insertRaw("maapi_logs", ("default", f"'ERROR'", f"'DBconnect'","now()",f"'{error}'", f"'{self.maapiLocation}'"))
            self.dbInnit(True)


    def fetchoneQuery(self, query):
        """insert row data to dabase"""
        try:
            with self.conn.cursor() as cur:
                cur.execute(f"{query}")
                temp = cur.fetchone()
                self.queuefetchoneQuery[query] = temp
                return temp
        except (Exception, psycopg2.DatabaseError) as error:
            temp = []
            self.logPrintOnly("ERROR", f'fetchoneQuery error: {error}')
            self.dbInnit(True)
            try:
                temp = self.queuefetchallQuery[query]
            except:
                pass
            return temp

    def fetchallQuery(self, query):
        """insert row data to dabase"""
        try:
            with self.conn.cursor() as cur:
                cur.execute(f"{query}")
                temp = cur.fetchall()
                self.queuefetchoneQuery[query] = temp
                return temp
        except (Exception, psycopg2.DatabaseError) as error:
            temp = []
            self.logPrintOnly("ERROR", f'fetchallQuery error: {error}')
            self.dbInnit(True)
            try:
                temp = self.queuefetchoneQuery[query]
            except:
                pass
            return temp

    def insertRaw(self, where, what):
        """Prepare query string"""
        try:
            query = f"INSERT INTO {where} VALUES ({','.join(what)}) "
            self.commitQuery(query)
        except Exception as error:
            self.logPrintOnly("ERROR", f'Insert RAW error: {error}')

    def createTable(self, name, what):
        try:
            query = f"CREATE TABLE {name}  ({','.join(list)}) "
            self.commitQuery(query)
        except Exception() as error:
            self.logPrintOnly("ERROR", f'CREATE TABLE ERROR {error}')

    def clearTable(self, name, where):
        try:
            query = f"truncate table {name} where {where}"
            self.commitQuery(query)
        except Exception() as error:
            self.logPrintOnly("ERROR", f'CLEAR TABLE ERROR {error}')

    def reindexTable(self, name):
        try:
            query = f"reindex table {name} "
            self.commitQuery(query)
        except Exception() as error:
            self.logPrintOnly("ERROR", f'REINDEX TABLE ERROR {error}')

    def updateRaw(self, where, what, when):
        try:
            query = f"UPDATE {where} SET {what} WHERE {when}"
            self.commitQuery(query)
        except Exception() as error:
            self.logPrintOnly("ERROR", f'UPDATE RAW ERRROR {error}')

    def cleanSocketServerList(self, board_id):
        try:
            query = f"DELETE FROM maapi_running_socket_servers WHERE ss_board_id={board_id}"
            self.commitQuery(query)
            query_ = f"DELETE FROM maapi_running_py_scripts WHERE py_board_id={board_id}"
            self.commitQuery(query_)
        except Exception() as error:
            self.logPrintOnly("ERROR", f'CLEAN SOCKET SERVER LIST {error}')

    def deleteRow(self, table, condition):
        try:
            query = f"DELETE FROM {table} WHERE {condition}"
            self.commitQuery(query)
        except Exception() as error:
            self.logPrintOnly("ERROR", f'DELETE RAW ERROR {error}')

    def clean_logs(self):
        try:
            query = "DELETE FROM maapi_logs WHERE log_timestamp < NOW() - INTERVAL '1 days'"
            self.commitQuery(query)
        except EnvironmentError() as error:
            self.logPrintOnly("ERROR", f'CLEAN LOGS ERROR {error}')

    def insert_readings(self, device_id, insert_value, sensor_type, status):
        try:
            query = (
                "SELECT dev_value, dev_rom_id, dev_collect_values_to_db "
                "FROM devices "
                f"WHERE dev_id='{device_id}' "
                "AND dev_status = True"
                )
            devices_data = self.fetchoneQuery(query)
            try:
                query = (
                    "UPDATE devices "
                    f"SET dev_value_old={devices_data[0]} "
                    f"WHERE dev_id='{device_id}' "
                    "AND dev_status=True"
                    )
                self.commitQuery(query)
            except Exception as error:
                self.logPrintOnly("ERROR", f'insert readings - update device {error}')
            try:
                if status is True:
                    date = dt.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                    query = (
                        "UPDATE devices "
                        f"SET dev_value={(1 if insert_value == True else (0 if insert_value == False else insert_value))}, "
                        f"dev_interval_queue = {False}, "
                        f"dev_last_update= TIMESTAMP '{date}', "
                        "dev_read_error='ok' "
                        f"WHERE dev_id='{device_id}' and dev_status=True"
                        )
                    self.commitQuery(query)
                    if devices_data[2]:

                        query = (
                            f"INSERT INTO maapi_dev_rom_{devices_data[1].replace('-', '_')}_values "
                            f"VALUES (default,{device_id}, TIMESTAMP '{date}', "
                            f"{(1 if insert_value==True else (0 if insert_value == False else insert_value))})"
                            )
                        self.commitQuery(query)
                else:
                    query = (
                        "UPDATE devices "
                        f"SET dev_value={insert_value}, "
                        "dev_read_error='Error' "
                        f"WHERE dev_id='{device_id}' "
                        )
                    self.commitQuery(query)
            except:
                pass
        except Exception() as error:
            self.logPrintOnly("ERROR", f'insert readings {error}')

    def select_last_nr_of_values(self, dev_id, range_nr):
        try:
            query = (
                "SELECT dev_rom_id "
                "FROM devices "
                f"WHERE dev_id={dev_id}"
                )
            query2 = (
                "SELECT dev_read_error "
                "FROM devices "
                f"WHERE dev_id={dev_id}"
                )
            error = (self.fetchoneQuery(query2))[0]
            values_x = []
            values_y = []
            if error == "ok":
                dev_rom_id = (self.fetchoneQuery(query))[0]
                query3 = (
                    "SELECT dev_value, dev_timestamp "
                    f"FROM maapi_dev_rom_{dev_rom_id.replace('-', '_')}_values "
                    f"order by dev_timestamp desc limit {range_nr}"
                    )
                values_history_temp = self.fetchallQuery(query3)
                for i in range(int(range_nr)):
                    values_x.append(values_history_temp[i][0])
            return values_x
        except:
            return []
            self.logPrintOnly("ERROR", f'select last nr of values {error}')

    def select_last_timeRange_of_values(self, dev_id, seconds):
        try:
            query = (
                "SELECT dev_rom_id "
                "FROM devices "
                f"WHERE dev_id={dev_id}"
                )
            query2 = (
                "SELECT dev_read_error "
                "FROM devices "
                f"WHERE dev_id={dev_id}"
                )
            error = (self.fetchoneQuery(query2))[0]
            values_history = []
            values_x = []
            values_y = []
            if error == "ok":
                dev_rom_id = (self.fetchoneQuery(query))[0]
                query3 = (
                    f"SELECT dev_value, dev_timestamp "
                    f"FROM maapi_dev_rom_{dev_rom_id.replace('-', '_')}_values "
                    f"where dev_timestamp >= now() - interval '{seconds} seconds' order by dev_timestamp "
                    )
                values_history_temp = self.fetchallQuery(query3)
                for i in range(len(values_history_temp)):
                    values_x.append(values_history_temp[i][0])
                    values_y.append(values_history_temp[i][1])
            return (values_x, values_y)
        except:
            return []
            self.logPrintOnly("ERROR", f'select last nr of values {error}')

    def columns(self, *args):
        self.columns_ = args
        return self

    def filters_eq(self, **kwargs):
        self.filters_ = kwargs
        return self

    def order_by(self, *args):
        self.orders_ = args
        return self

    def if_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def table(self, *args):
        if len(args) != 1:
            raise ValueError(
                ".get_table('table name') should only have a table name")
        self.table_ = args[0]
        return self

    def get(self):
        if self.columns_:
            c_len = len(self.columns_)
            c_i = 1
            columns = " "
            for c in self.columns_:
                if c_len > 1:
                    columns += "{0}".format(c)
                    if c_i < c_len:
                        columns += ", "
                    c_i += 1
                else:
                    columns += "{0}".format(c)
        else:
            columns = "*"
            self.columns_var = "*"
        query = "SELECT {0} FROM {1} ".format(columns, self.table_)
        if self.filters_:
            f_len = len(self.filters_)
            f_i = 1
            query += "WHERE "
            for i in self.filters_:
                if f_i == 1:
                    if self.if_number(self.filters_[i]):
                        query += " {0} = {1}".format(i, self.filters_[i])
                    else:
                        query += " {0} = '{1}'".format(i, self.filters_[i])
                else:
                    query += " and "
                    if self.if_number(self.filters_[i]):
                        query += " {0} = {1}".format(i, self.filters_[i])
                    else:
                        query += " {0} = '{1}'".format(i, self.filters_[i])
                f_i += 1
        if self.orders_:
            try:
                self.orders_[1]
            except:
                query += " ORDER BY {0}".format(self.orders_[0])
            else:
                if self.orders_[1] == "asc" or self.orders_[1] == "ASC" or self.orders_[1] == "desc" or self.orders_[1] == "DESC":
                    query += " ORDER BY {0} {1}".format(self.orders_[0],
                                                        self.orders_[1])
                else:
                    raise ValueError(
                        "order_by Second Value should be empty or ASC or DESC but get: '{0}'".
                        format(self.orders_[1]))
        query += ";"
        data = self.exec_query_select(query, self.table_)
        self.filters_ = {}
        self.orders_ = {}
        self.columns_ = {}
        self.columns_var = {}
        self.table_ = {}
        return data

    def exec_query_select(self, query, name):
        table_data_dict = {}
        try:
            table_data = self.fetchallQuery(query)
            if self.columns_var == '*':
                query2 = (
                    "SELECT column_name "
                    "FROM information_schema.columns "
                    f"WHERE table_name='{name}' "
                    )
                table_names = self.fetchallQuery(query2)
                for row_s in range(len(table_data)):
                    sensor_rows = {}
                    i = 0
                    for r_s in table_data[row_s]:
                        sensor_rows[table_names[i][0]] = r_s
                        i += 1
                    table_data_dict[table_data[row_s][0]] = sensor_rows
            else:
                if self.columns_[1] == "*":
                    self.columns_ = list(self.columns_)
                    query3 = (
                        "SELECT column_name "
                        "FROM information_schema.columns "
                        f"WHERE table_name='{name}' "
                        )
                    table_names_tmp = self.fetchallQuery(query3)
                    table_names = [(self.columns_[0],),] + table_names_tmp
                else:
                    table_names = self.columns_

                for row_s in range(len(table_data)):
                    sensor_rows = {}
                    i = 0
                    if isinstance(table_names[i], tuple):
                        for r_s in table_data[row_s]:
                            sensor_rows[table_names[i][0]] = r_s
                            i += 1
                    else:
                        for r_s in table_data[row_s]:
                            sensor_rows[table_names[i]] = r_s
                            i += 1
                    table_data_dict[table_data[row_s][0]] = sensor_rows
            return table_data_dict
        except Exception as error:

            return []
