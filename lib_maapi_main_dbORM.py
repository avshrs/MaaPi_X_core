#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################
import psycopg2
from datetime import datetime as dt, timedelta
import MaaPi_Config as Config
#import lib_maapi_main_logger          as MaapiLogger

class MaaPiDBConnection():

    def __init__(self):
        self.filters_           = {}
        self.orders_            = {}
        self.columns_           = {}
        self.columns_var        = {}
        self.table_             = {}
        self.config             = Config.MaapiVars()
        Maapi_dbName            =self.config.maapiDbName
        Maapi_dbUser            =self.config.maapiDbUser
        Maapi_dbHost            =self.config.maapiDbHost
        Maapi_dbPasswd          =self.config.maapiDbpass
        #self.maapilogger        = MaapiLogger.Logger()
        # self.maapilogger.name   = "DB Connect."

        try:
            self.conn = psycopg2.connect("dbname='{0}' user='{1}' host='{2}' password='{3}'".format(Maapi_dbName,Maapi_dbUser,Maapi_dbHost,Maapi_dbPasswd))
        except (Exception, psycopg2.DatabaseError) as error:
        #    self.maapilogger.log(1,error)
            pass

    def __del__(self):
        self.conn.close()


    def queue(self,dev_id,status,board_id):
        try:
            x = self.conn.cursor()
            if dev_id == '*':
                x.execute("UPDATE devices "
                          "SET dev_interval_queue={0} "
                          "WHERE dev_status=TRUE "
                          "AND dev_machine_location_id = {1}".format(status,board_id))
                self.conn.commit()
            else:
                x.execute("UPDATE devices "
                          "SET dev_interval_queue={0} "
                          "WHERE dev_id={1} "
                          "AND dev_machine_location_id = {2}".format(status,dev_id,board_id))
                self.conn.commit()
            x.close()
        except Exception as e:
            print (e)


    def insertRaw(self, where, what):
        string_ = "INSERT INTO {where} VALUES  ({what})".format(where=where, what=",".join(what))
        # self.maapilogger.log("DEBUG",string_)
        x = self.conn.cursor()
        x.execute(f"{string_}")
        self.conn.commit()

    def cleanSocketServerList(self):
        string_ = "DELETE FROM maapi_running_socket_servers WHERE ss_port>0"
        # self.maapilogger.log("DEBUG",string_)
        x = self.conn.cursor()
        x.execute(f"{string_}")
        self.conn.commit()
        string_ = "DELETE FROM maapi_running_py_scripts WHERE py_pid>0"
        # self.maapilogger.log("DEBUG",string_)
        x = self.conn.cursor()
        x.execute(f"{string_}")
        self.conn.commit()


    def clean_logs(self):
        string_ = "DELETE FROM maapi_logs WHERE log_timestamp < NOW() - INTERVAL '1 days'"
        # self.maapilogger.log("DEBUG",string_)
        x = self.conn.cursor()
        x.execute(f"{string_}")
        self.conn.commit()



    def insert_readings(self,device_id,insert_value,sensor_type,status):
            # self.maapilogger.log("DEBUG",f"Insert  id: {0:<10} DevID: {device_id:<8} Status:{status:<30} \tValue: {insert_value} ")

            # get values
            x = self.conn.cursor()
            x.execute("SELECT dev_value, dev_rom_id, dev_collect_values_to_db "
                      "FROM devices "
                      "WHERE dev_id='{0}' "
                      "AND dev_status = True".format(device_id))
            devices_data = x.fetchone()
            try:
                x.execute("UPDATE devices "
                          "SET dev_value_old={0} "
                          "WHERE dev_id='{1}' "
                          "AND dev_status=True".format(devices_data[0],device_id))
                self.conn.commit()
            except Exception as e:
                print(e)

            if status is True:
                x.execute("UPDATE devices "
                            "SET dev_value={0}, dev_interval_queue = {2}, dev_last_update=NOW(), dev_read_error='ok' "
                            "WHERE dev_id='{1}' and dev_status=True".format((1 if insert_value==True else (0 if insert_value==False else insert_value)),device_id,False))
                self.conn.commit()
                # if collcect to db
                if devices_data[2]:
                    x.execute("INSERT INTO maapi_dev_rom_{0}_values "
                                "VALUES (default,{1},default,{2})".format(devices_data[1].replace("-", "_"), device_id,(1 if insert_value==True else (0 if insert_value==False else insert_value))))
                    self.conn.commit()
            else:
                x.execute("UPDATE devices "
                          "SET dev_interval_queue = {2}, dev_value={0}, dev_read_error='Error' "
                          "WHERE dev_id='{1}' and dev_status=True".format(9999,device_id,False))
                self.conn.commit()


    def select_last_nr_of_values(self,dev_id,range_nr):
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
                print (e)

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
        except Exception as error:
           print (error)

        return table_data_dict



