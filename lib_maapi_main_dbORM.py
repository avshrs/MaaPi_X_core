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
        self.filters_            = {}
        self.orders_            = {}
        self.columns_           = {}
        self.columns_var        = {}
        self.table_             = {}
        self.config              = Config.MaapiVars()
        self.Maapi_dbName            =self.config.maapiDbName
        self.Maapi_dbUser            =self.config.maapiDbUser
        self.Maapi_dbHost            =self.config.maapiDbHost
        self.Maapi_dbPasswd          =self.config.maapiDbpass


    def queue(self,dev_id,status,board_id):
        try:
            try:

                conn = psycopg2.connect(f"dbname='{self.Maapi_dbName}' user='{self.Maapi_dbUser}' host='{self.Maapi_dbHost}' password='{self.Maapi_dbPasswd}'")
            except (Exception, psycopg2.DatabaseError) as error:
                pass
            else:
                x = conn.cursor()
                if dev_id == '*':
                    x.execute("UPDATE devices "
                            "SET dev_interval_queue={0} "
                            "WHERE dev_status=TRUE "
                            "AND dev_machine_location_id = {1}".format(status,board_id))
                    conn.commit()
                else:
                    x.execute("UPDATE devices "
                            "SET dev_interval_queue={0} "
                            "WHERE dev_id={1} "
                            "AND dev_machine_location_id = {2}".format(status,dev_id,board_id))
                    conn.commit()
                x.close()
            finally:
                try:
                    conn.close()
                except:
                    pass
        except Exception() as e:
            pass


    def insertRaw(self, where, what):
        try:
            try:

                conn = psycopg2.connect(f"dbname='{self.Maapi_dbName}' user='{self.Maapi_dbUser}' host='{self.Maapi_dbHost}' password='{self.Maapi_dbPasswd}'")
            except (Exception, psycopg2.DatabaseError) as error:
                pass
            else:
                string_ = f"INSERT INTO {where} VALUES ({','.join(what)}) "
                x = conn.cursor()
                x.execute(f"{string_}")
                conn.commit()
                x.close()
            finally:
                try:
                    conn.close()
                except:
                    pass
        except Exception() as e:
            pass

    def createTable(self, name, list):
        try:
            try:
                conn = psycopg2.connect(f"dbname='{self.Maapi_dbName}' user='{self.Maapi_dbUser}' host='{self.Maapi_dbHost}' password='{self.Maapi_dbPasswd}'")
            except (Exception, psycopg2.DatabaseError) as error:
                pass
            else:
                string_ = f"CREATE TABLE {NAME}  ({','.join(what)}) "
                x = conn.cursor()
                x.execute(f"{string_}")
                conn.commit()
                x.close()
            finally:
                try:
                    conn.close()
                except:
                    pass
        except Exception() as e:
            pass

    def clearTable(self, name, where):
        try:
            try:
                conn = psycopg2.connect(f"dbname='{self.Maapi_dbName}' user='{self.Maapi_dbUser}' host='{self.Maapi_dbHost}' password='{self.Maapi_dbPasswd}'")
            except (Exception, psycopg2.DatabaseError) as error:
                pass
            else:
                string_ = f"truncate table {name} where {where}"
                x = conn.cursor()
                x.execute(f"{string_}")
                conn.commit()
                x.close()
            finally:
                try:
                    conn.close()
                except:
                    pass
        except Exception() as e:
            pass



    def reindexTable(self, name):
        try:
            try:
                conn = psycopg2.connect(f"dbname='{self.Maapi_dbName}' user='{self.Maapi_dbUser}' host='{self.Maapi_dbHost}' password='{self.Maapi_dbPasswd}'")
            except (Exception, psycopg2.DatabaseError) as error:
                pass
            else:
                string_ = f"reindex table {name} "
                x = conn.cursor()
                x.execute(f"{string_}")
                conn.commit()
                x.close()
            finally:
                try:
                    conn.close()
                except:
                    pass
        except Exception() as e:
            pass

    def updateRaw(self, where, what, when):
        try:
            try:
                conn = psycopg2.connect(f"dbname='{self.Maapi_dbName}' user='{self.Maapi_dbUser}' host='{self.Maapi_dbHost}' password='{self.Maapi_dbPasswd}'")
            except (Exception, psycopg2.DatabaseError) as error:
                pass
            else:
                string_ = f"UPDATE {where} SET {what} WHERE {when}"
                x = conn.cursor()
                x.execute(f"{string_}")
                conn.commit()
                x.close()
            finally:
                try:
                    conn.close()
                except:
                    pass
        except Exception() as e:
            pass

# update maapi_running_py_scripts set py_board_id = 5 where py_pid=4344;

    def cleanSocketServerList(self,board_id):
        try:
            try:
                conn = psycopg2.connect(f"dbname='{self.Maapi_dbName}' user='{self.Maapi_dbUser}' host='{self.Maapi_dbHost}' password='{self.Maapi_dbPasswd}'")
            except (Exception, psycopg2.DatabaseError) as error:
                pass
            else:
                string_ = f"DELETE FROM maapi_running_socket_servers WHERE ss_board_id={board_id}"
                x = conn.cursor()
                x.execute(f"{string_}")
                conn.commit()

                string_ = f"DELETE FROM maapi_running_py_scripts WHERE py_board_id={board_id}"
                x = conn.cursor()
                x.execute(f"{string_}")
                conn.commit()
                x.close()
            finally:
                try:
                    conn.close()
                except:
                    pass
        except Exception() as e:
            pass


    def deleteRow(self, table, condition):
        try:
            try:
                conn = psycopg2.connect(f"dbname='{self.Maapi_dbName}' user='{self.Maapi_dbUser}' host='{self.Maapi_dbHost}' password='{self.Maapi_dbPasswd}'")
            except (Exception, psycopg2.DatabaseError) as error:
                pass
            else:
                string_ = f"DELETE FROM {table} WHERE {condition}"
                x = conn.cursor()
                x.execute(f"{string_}")
                conn.commit()
            finally:
                try:
                    conn.close()
                except:
                    pass
        except Exception() as e:
            pass


    def clean_logs(self):
        try:
            try:
                conn = psycopg2.connect(f"dbname='{self.Maapi_dbName}' user='{self.Maapi_dbUser}' host='{self.Maapi_dbHost}' password='{self.Maapi_dbPasswd}'")
            except (Exception, psycopg2.DatabaseError) as error:
                pass
            else:
                string_ = "DELETE FROM maapi_logs WHERE log_timestamp < NOW() - INTERVAL '1 days'"
                x = conn.cursor()
                x.execute(f"{string_}")
                conn.commit()
                x.close()
            finally:
                try:
                    conn.close()
                except:
                    pass
        except EnvironmentError() as e:
            pass


    def insert_readings(self,device_id,insert_value,sensor_type,status):
        try:
            try:
                conn = psycopg2.connect(f"dbname='{self.Maapi_dbName}' user='{self.Maapi_dbUser}' host='{self.Maapi_dbHost}' password='{self.Maapi_dbPasswd}'")
            except (Exception, psycopg2.DatabaseError) as error:
                pass
            else:
                x = conn.cursor()
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
                    conn.commit()
                except Exception as e:
                    print(e)

                if status is True:
                    x.execute("UPDATE devices "
                                f"SET dev_value={(1 if insert_value==True else (0 if insert_value==False else insert_value))}, "
                                f"dev_interval_queue = {False}, "
                                "dev_last_update=NOW(), "
                                "dev_read_error='ok' "
                                f"WHERE dev_id='{device_id}' and dev_status=True")
                    conn.commit()
                    if devices_data[2]:
                        x.execute(f"INSERT INTO maapi_dev_rom_{devices_data[1].replace('-', '_')}_values "
                                    f"VALUES (default,{device_id}, default, "
                                    f"{(1 if insert_value==True else (0 if insert_value==False else insert_value))})")
                        conn.commit()
                else:
                    x.execute("UPDATE devices "
                            "SET dev_interval_queue = {2}, dev_value={0}, dev_read_error='Error' "
                            "WHERE dev_id='{1}' and dev_status=True".format(9999,device_id,False))
                    conn.commit()
                x.close()
            finally:
                try:
                    conn.close()
                except:
                    pass
        except Exception() as e:
            pass


    def select_last_nr_of_values(self,dev_id,range_nr):
            try:
                conn = psycopg2.connect(f"dbname='{self.Maapi_dbName}' user='{self.Maapi_dbUser}' host='{self.Maapi_dbHost}' password='{self.Maapi_dbPasswd}'")
            except (Exception, psycopg2.DatabaseError) as error:
                pass
            else:
                x = conn.cursor()
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
            finally:
                try:
                    conn.close()
                except:
                    pass

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
            try:
                conn = psycopg2.connect(f"dbname='{self.Maapi_dbName}' user='{self.Maapi_dbUser}' host='{self.Maapi_dbHost}' password='{self.Maapi_dbPasswd}'")
            except (Exception, psycopg2.DatabaseError) as error:
                pass
            else:
                x = conn.cursor()
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
                conn.commit()
                x.close()
            finally:
                try:
                    conn.close()
                except:
                    pass

        except Exception as error:
           pass
        return table_data_dict





