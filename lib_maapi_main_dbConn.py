#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################
import psycopg2
import logging, os
from datetime import datetime as dt, timedelta
import MaaPi_Config as Config


pwd =os.getcwd()
logging.basicConfig(
    filename=f'{pwd}/log/Maapi_logger.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %H:%M:%S')


class MaaPiDBConnection():
    def __init__(self):
        self.objectname         = "Database"
        self.filters_           = {}
        self.orders_            = {}
        self.columns_           = {}
        self.columns_var        = {}
        self.table_             = {}


        self.config             = Config.MaapiVars()
        self.Maapi_dbName       =self.config.maapiDbName
        self.Maapi_dbUser       =self.config.maapiDbUser
        self.Maapi_dbHost       =self.config.maapiDbHost
        self.Maapi_dbPasswd     =self.config.maapiDbpass

        try:
            self.conn = psycopg2.connect(f"dbname='{self.Maapi_dbName}' user='{self.Maapi_dbUser}' host='{self.Maapi_dbHost}' password='{self.Maapi_dbPasswd}'")
        except (Exception, psycopg2.DatabaseError) as error:
            self.logPrintOnly("ERROR",f'Connection error {error}')

    def logPrintOnly(self, level, msg):
        try:
            time= "{0:0>2}:{1:0>2}:{2:0>2} - {3:0>6}".format(dt.now().hour,dt.now().minute,dt.now().second,dt.now().microsecond)

            msg_ = str(msg).replace("'","")
            msg__ = str(msg_).replace('\"', '')
            print(f"MaaPi  |  {self.name:<17}  |  {level:^6}  |  {time:<16}  |  {msg}")
        except:
            pass

    def insertRaw(self, where, what):
        try:
            string_ = f"INSERT INTO {where} VALUES ({','.join(what)}) "
            x = self.conn.cursor()
            x.execute(f"{string_}")
            self.conn.commit()
            x.close()
        except Exception() as e:
            self.logPrintOnly("ERROR",f'Insert RAW error: {error}')

    def createTable(self, name, list):
        try:
            string_ = f"CREATE TABLE {NAME}  ({','.join(what)}) "
            x = self.conn.cursor()
            x.execute(f"{string_}")
            self.conn.commit()
            x.close()
        except Exception() as e:
            self.logPrintOnly("ERROR",f'CREATE TABLE ERROR {error}')

    def clearTable(self, name, where):
        try:
            string_ = f"truncate table {name} where {where}"
            x = self.conn.cursor()
            x.execute(f"{string_}")
            self.conn.commit()
            x.close()
        except Exception() as e:
            self.logPrintOnly("ERROR",f'CLEAR TABLE ERROR {error}')

    def reindexTable(self, name):
        try:
            string_ = f"reindex table {name} "
            x = self.conn.cursor()
            x.execute(f"{string_}")
            self.conn.commit()
            x.close()
        except Exception() as e:
            self.logPrintOnly("ERROR",f'REINDEX TABLE ERROR {error}')

    def updateRaw(self, where, what, when):
        try:
            string_ = f"UPDATE {where} SET {what} WHERE {when}"
            x = self.conn.cursor()
            x.execute(f"{string_}")
            self.conn.commit()
            x.close()
        except Exception() as e:
            self.logPrintOnly("ERROR",f'UPDATE RAW ERRROR {error}')

    def cleanSocketServerList(self,board_id):
        try:
            string_ = f"DELETE FROM maapi_running_socket_servers WHERE ss_board_id={board_id}"
            x = self.conn.cursor()
            x.execute(f"{string_}")
            self.conn.commit()

            string_ = f"DELETE FROM maapi_running_py_scripts WHERE py_board_id={board_id}"
            x = self.conn.cursor()
            x.execute(f"{string_}")
            self.conn.commit()
            x.close()
        except Exception() as e:
            self.logPrintOnly("ERROR",f'CLEAN SOCKET SERVER LIST {error}')

    def deleteRow(self, table, condition):
        try:
            string_ = f"DELETE FROM {table} WHERE {condition}"
            x = self.conn.cursor()
            x.execute(f"{string_}")
            self.conn.commit()
            x.close()
        except Exception() as e:
            self.logPrintOnly("ERROR",f'DELETE RAW ERROR {error}')

    def clean_logs(self):
        try:
            string_ = "DELETE FROM maapi_logs WHERE log_timestamp < NOW() - INTERVAL '1 days'"
            x = self.conn.cursor()
            x.execute(f"{string_}")
            self.conn.commit()
            x.close()
        except EnvironmentError() as e:
            self.logPrintOnly("ERROR",f'CLEAN LOGS ERROR {error}')

    def insert_readings(self,device_id,insert_value,sensor_type,status):
        try:
            x = self.conn.cursor()
            x.execute("SELECT dev_value, dev_rom_id, dev_collect_values_to_db "
                    "FROM devices "
                    f"WHERE dev_id='{device_id}' "
                    "AND dev_status = True")
            devices_data = x.fetchone()
            try:
                x.execute("UPDATE devices "
                        f"SET dev_value_old={devices_data[0]} "
                        f"WHERE dev_id='{device_id}' "
                        "AND dev_status=True")
                self.conn.commit()
            except Exception as e:
                self.logPrintOnly("ERROR",f'insert readings - update device {error}')

            if status is True:
                x.execute("UPDATE devices "
                            f"SET dev_value={(1 if insert_value==True else (0 if insert_value==False else insert_value))}, "
                            f"dev_interval_queue = {False}, "
                            "dev_last_update=NOW(), "
                            "dev_read_error='ok' "
                            f"WHERE dev_id='{device_id}' and dev_status=True")
                self.conn.commit()
                if devices_data[2]:
                    x.execute(f"INSERT INTO maapi_dev_rom_{devices_data[1].replace('-', '_')}_values "
                                f"VALUES (default,{device_id}, default, "
                                f"{(1 if insert_value==True else (0 if insert_value==False else insert_value))})")
                    self.conn.commit()
            else:
                x.execute("UPDATE devices "
                        "SET dev_interval_queue = {2}, dev_value={0}, dev_read_error='Error' "
                        "WHERE dev_id='{1}' and dev_status=True".format(9999,device_id,False))
                self.conn.commit()
            x.close()
        except Exception() as e:
            self.logPrintOnly("ERROR",f'insert readings {error}')

    def select_last_nr_of_values(self,dev_id,range_nr):
            try:
                x = self.conn.cursor()
                x.execute("SELECT dev_rom_id "
                        "FROM devices "
                        "WHERE dev_id={0}".format(dev_id))
                dev_rom_id = x.fetchone()[0]
                x.execute("SELECT dev_read_error "
                        "FROM devices "
                        "WHERE dev_id={0}".format(dev_id))
                error = x.fetchone()[0]
                values_history=[]

                if error == "ok":
                    x.execute("SELECT "
                            "dev_value, dev_timestamp "
                            "FROM maapi_dev_rom_{0}_values "
                            "order by dev_timestamp desc limit  {1}".format(dev_rom_id.replace("-", "_"), range_nr))
                    values_history_temp = x.fetchall()
                    for i in range(int(range_nr)):
                        values_history.append(values_history_temp[i][0])

                return  values_history
                x.close()
            except:
                self.logPrintOnly("ERROR",f'select last nr of values {error}')

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
            x = self.conn.cursor()
            try:
                x.execute(query)
            except Exception as e:
                pass
            table_data = x.fetchall()

            if self.columns_var == '*':
                x.execute("SELECT column_name "
                          "FROM information_schema.columns "
                          "WHERE table_name='{0}' ".format(name))
                table_names = x.fetchall()

                for row_s in range(len(table_data)):
                    sensor_rows = {}
                    i = 0
                    for r_s in table_data[row_s]:
                        sensor_rows[table_names[i][0]] = r_s
                        i += 1
                    table_data_dict[table_data[row_s][0]] = sensor_rows
            else:
                if self.columns_[1]== "*":
                    self.columns_=list(self.columns_)
                    x.execute("SELECT column_name "
                            "FROM information_schema.columns "
                            "WHERE table_name='{0}' ".format(name))
                    table_names_tmp = x.fetchall()
                    table_names = [(self.columns_[0],),]+table_names_tmp
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
                            sensor_rows[table_names[i]]= r_s
                            i += 1
                    table_data_dict[table_data[row_s][0]] = sensor_rows
            self.conn.commit()
            x.close()
            return table_data_dict
        except Exception as error:
           select_last_nr_of_values







