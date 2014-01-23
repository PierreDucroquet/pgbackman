#!/usr/bin/env python
#
# Copyright (c) 2014 Rafael Martinez Guerrero (PostgreSQL-es)
# rafael@postgresql.org.es / http://www.postgresql.org.es/
#
# This file is part of PgBackMan
# https://github.com/rafaelma/pgbackman
#
# PgBackMan is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PgBackMan is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pgbackman.  If not, see <http://www.gnu.org/licenses/>.

import psycopg2
import psycopg2.extensions
from psycopg2.extras import wait_select

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

#
# Class: pg_database
#
# This class is used to interact with a postgreSQL database
# It is used to open and close connections to the database
# and to set/get some information for/of the connection.
# 

class pgbackman_db():
    """This class is used to interact with a postgreSQL database"""

    # ############################################
    # Constructor
    # ############################################

    def __init__(self, dsn):
        """ The Constructor."""

        self.dsn = dsn
        self.conn = None
        self.server_version = None

        self.pg_connect()
        self.wait_select()

        self.cur = self.conn.cursor()

        if self.conn:

            self.server_version = self.conn.server_version

            if (self.server_version >= 90000 and 'application_name=' not in self.dsn):
              
                try:
                    self.cur.execute('SET application_name TO pgbackman')
                except psycopg2.Error as e:
                    print "\n* ERROR - Could not define the application_name parameter: \n%s" % e


    # ############################################
    # Method pg_connect()
    #
    # A generic function to connect to PostgreSQL using Psycopg2
    # We will define the application_name parameter if it is not
    # defined in the DSN and the postgreSQL server version >= 9.0
    # ############################################

    def pg_connect(self):
        """A generic function to connect to PostgreSQL using Psycopg2"""

        try:
            self.conn = psycopg2.connect(self.dsn)
            
        except psycopg2.Error as e:
            print "\n* ERROR - Could not connect to the database: \n%s" % e


    # ############################################
    # Method pg_close()
    # ############################################

    def pg_close(self):
        """A generic function to close a postgreSQL connection using Psycopg2"""

        if self.cur:
            try:
                self.cur.close()
            except psycopg2.Error as e:
                print "\n* ERROR - Could not close the cursor used in this connection: \n%s" % e    

        if self.conn:
            try:
                self.conn.close() 
            except psycopg2.Error as e:
                print "\n* ERROR - Could not close the connection to the database: \n%s" % e    
                
    # ############################################
    # Method 
    # ############################################

    def set_isolation_level(self,param):
        """ set isolation level"""

        if self.conn:
            self.conn.set_isolation_level(param)

    # ############################################
    # Method 
    # ############################################

    def wait_select(self):
        """ run wait_select"""

        if self.conn:
            wait_select(self.conn)


    # ############################################
    # Method 
    # ############################################

    def add_listen(self,channel):
        '''Subscribe to a PostgreSQL NOTIFY'''

        replace_list = ['.','-']

        if self.conn:
            if self.cur:
                for i,j in enumerate(replace_list):
                    channel = channel.replace(j, '_')
                
                sql = "LISTEN %s" % channel
                print sql # debug
                self.cur.execute(sql)
                self.wait_select()
 

    # ############################################
    # Method 
    # ############################################

    def delete_listen(self,channel):
        '''Unsubscribe to a PostgreSQL NOTIFY'''

        replace_list = ['.','-']

        if self.conn:
            if self.cur:
                for i,j in enumerate(replace_list):
                    channel = channel.replace(j, '_')
                
                sql = "UNLISTEN %s" % channel
                print sql # debug
                self.cur.execute(sql)
                self.wait_select()
     

   # ############################################
    # Method 
    # ############################################

    def get_server_version(self):
        """A function to get the postgresql version of the database connection"""

        if self.conn:
            return  self.server_version


    # ############################################
    # Method 
    # ############################################

    def show_backup_servers(self):
        """A function to get a list with all backup servers available"""

        if self.conn:
            if self.cur:
                try:
                    self.cur.execute('SELECT show_backup_servers()')
                    self.conn.commit()
                    
                    data = self.cur.fetchone()[0]
                    print data
                    
                except psycopg2.Error as e:
                    print "\n* ERROR - Could not get the list with backup servers: \n* %s" % e
                    self.conn.rollback()
                    
                    
    # ############################################
    # Method 
    # ############################################

    def register_backup_server(self,hostname,domain,status,remarks):
        """A function to register a backup server"""

        if self.conn:
            if self.cur:
                try:
                    self.cur.execute('SELECT register_backup_server(%s,%s,%s,%s)',(hostname,domain,status,remarks))
                    self.conn.commit()                        

                    return True
                
                except psycopg2.Error as err:
                    print "\n* ERROR - Could not register backup server: \n* %s" % err
                    self.conn.rollback()
                except psycopg2.Warning as warn:
                    print "\n* WARNING - Could not register backup server: \n* %s" % warn
                    self.conn.rollback()


    # ############################################
    # Method 
    # ############################################
                      
    def delete_backup_server(self,server_id):
        """A function to delete a backup server"""

        if self.conn:
            if self.cur:
                try:
                    self.cur.execute('SELECT delete_backup_server(%s)',(server_id,))
                    self.conn.commit()                        
                    
                    return True

                except psycopg2.Error as err:
                    print "\n* ERROR - Could not delete backup server: \n* %s" % err
                    self.conn.rollback()
                except psycopg2.Warning as warn:
                    print "\n* WARNING - Could not delete backup server: \n* %s" % warn
                    self.conn.rollback()
                    
          
    # ############################################
    # Method 
    # ############################################

    def show_pgsql_nodes(self):
        """A function to get a list with all pgnodes defined in pgbackman"""

        if self.conn:
            if self.cur:
                try:
                    self.cur.execute('SELECT show_pgsql_nodes()')
                    
                    data = self.cur.fetchone()[0]
                    print data
                    
                except psycopg2.Error as e:
                    print "\n* ERROR - Could not get the list with backup servers: \n* %s" % e

                
    # ############################################
    # Method 
    # ############################################

    def register_pgsql_node(self,hostname,domain,port,admin_user,status,remarks):
        """A function to register a pgsql node"""

        if self.conn:
            if self.cur:
                try:
                    self.cur.execute('SELECT register_pgsql_node(%s,%s,%s,%s,%s,%s)',(hostname,domain,port,admin_user,status,remarks))
                    self.conn.commit()                        
                    
                    return True
                
                except psycopg2.Error as err:
                    print "\n* ERROR - Could not register pgsql node: \n* %s" % err
                    self.conn.rollback()
                except psycopg2.Warning as warn:
                    print "\n* WARNING - Could not register pgsql_node: \n* %s" % warn
                    self.conn.rollback()
                
           
    # ############################################
    # Method 
    # ############################################

    def delete_pgsql_node(self,node_id):
        """A function to delete a pgsql node"""

        if self.conn:
            if self.cur:
                try:
                    self.cur.execute('SELECT delete_pgsql_node(%s)',(node_id,))
                    self.conn.commit()                        
                    
                    return True
            
                except psycopg2.Error as err:
                    print "\n* ERROR - Could not delete pgsql node: \n* %s" % err
                    self.conn.rollback()
                except psycopg2.Warning as warn:
                    print "\n* WARNING - Could not delete pgsql node: \n* %s" % warn
                    self.conn.rollback()
                        
    # ############################################
    # Method 
    # ############################################

    def register_backup_job(self,backup_server,pgsql_node,dbname,minutes_cron,hours_cron, \
                                weekday_cron,month_cron,day_month_cron,backup_code,encryption, \
                                retention_period,retention_redundancy,extra_parameters,job_status,remarks):
        """A function to register a backup job"""

        if self.conn:
            if self.cur:
                try:
                    self.cur.execute('SELECT register_backup_job(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(backup_server,pgsql_node,dbname,minutes_cron,hours_cron, \
                                                                                                            weekday_cron,month_cron,day_month_cron,backup_code,encryption, \
                                                                                                            retention_period,retention_redundancy,extra_parameters,job_status,remarks))
                    self.conn.commit()                        
                    
                    return True
                
                except psycopg2.Error as err:
                    print "\n* ERROR - Could not register backup job: \n* %s" % err
                    self.conn.rollback()
                except psycopg2.Warning as warn:
                    print "\n* WARNING - Could not register backup job: \n* %s" % warn
                    self.conn.rollback()
                

    # ############################################
    # Method 
    # ############################################

    def show_backup_server_job_definitions(self,backup_server):
        """A function to get a list with all backup job definitions for a backup server"""

        if self.conn:
            if self.cur:
                try:
                    self.cur.execute('SELECT show_backup_server_job_definitions(%s)',(backup_server,))
                    
                    data = self.cur.fetchone()[0]
                    print data
            
                except psycopg2.Error as e:
                    print "\n* ERROR - Could not get the list of backup job definitions for this backup server \n* %s" % e


    # ############################################
    # Method 
    # ############################################

    def show_pgsql_node_job_definitions(self,pgsql_node):
        """A function to get a list with all backup job definitions for a PgSQL node"""

        if self.conn:
            if self.cur:
                try:
                    self.cur.execute('SELECT show_pgsql_node_job_definitions(%s)',(pgsql_node,))
                    
                    data = self.cur.fetchone()[0]
                    print data
                    
                except psycopg2.Error as e:
                    print "\n* ERROR - Could not get the list of backup job definitions for this PgSQL node\n* %s" % e

     
    # ############################################
    # Method 
    # ############################################

    def show_database_job_definitions(self,dbname):
        """A function to get a list with all backup job definitions for a database"""

        if self.conn:
            if self.cur:
                try:
                    self.cur.execute('SELECT show_database_job_definitions(%s)',(dbname,))
                    
                    data = self.cur.fetchone()[0]
                    print data
                    
                except psycopg2.Error as e:
                    print "\n* ERROR - Could not get the list of backup job definitions for this database\n* %s" % e
     
    # ############################################
    # Method 
    # ############################################

    def get_default_backup_server_parameter(self,param):
        """A function to get the default value of a configuration parameter"""

        if self.conn:
            if self.cur:
                try:
                    self.cur.execute('SELECT get_default_backup_server_parameter(%s)',(param,))
                    
                    data = self.cur.fetchone()[0]
                    return data

                except psycopg2.Error as e:
                    print "\n* ERROR - Could not get default value for parameter: \n* %s" % e

     
    # ############################################
    # Method 
    # ############################################
           
    def get_default_pgsql_node_parameter(self,param):
        """A function to get the default value of a configuration parameter"""

        if self.conn:
            if self.cur:
                try:
                    self.cur.execute('SELECT get_default_pgsql_node_parameter(%s)',(param,))
                    
                    data = self.cur.fetchone()[0]
                    return data

                except psycopg2.Error as e:
                    print "\n* ERROR - Could not get default value for parameter: \n* %s" % e
                

    # ############################################
    # Method 
    # ############################################
           
    def get_minute_from_interval(self,param):
        """A function to get a minute from an interval"""

        if self.conn:
            if self.cur:
                try:
                    self.cur.execute('SELECT get_minute_from_interval(%s)',(param,))
                    
                    data = self.cur.fetchone()[0]
                    return data
                
                except psycopg2.Error as e:
                    print "\n* ERROR - Could not get minute from interval: \n* %s" % e
                    
       
    # ############################################
    # Method 
    # ############################################
           
    def get_hour_from_interval(self,param):
        """A function to get an hour from an interval"""

        if self.conn:
            if self.cur:
                try:
                    self.cur.execute('SELECT get_hour_from_interval(%s)',(param,))
                    
                    data = self.cur.fetchone()[0]
                    return data

                except psycopg2.Error as e:
                    print "\n* ERROR - Could not get minute from interval: \n* %s" % e
                
                  
    # ############################################
    # Method 
    # ############################################
           
    def get_backup_server_fqdn(self,param):
        """A function to get the FQDN for a backup server"""

        if self.conn:
            if self.cur:
                try:
                    self.cur.execute('SELECT get_backup_server_fqdn(%s)',(param,))
                    
                    data = self.cur.fetchone()[0]
                    return data

                except psycopg2.Error as e:
                    print "\n* ERROR - Could not get the FQDN for this backup server \n* %s" % e

    # ############################################
    # Method 
    # ############################################
           
    def get_backup_server_id(self,param):
        """A function to get the ID of a backup server"""

        if self.conn:
            if self.cur:
                try:
                    self.cur.execute('SELECT get_backup_server_id(%s)',(param,))
                    
                    data = self.cur.fetchone()[0]
                    return data

                except psycopg2.Error as e:
                    print "\n* ERROR - Could not get the server ID for this backup server \n* %s" % e
                    return False
                  
    # ############################################
    # Method 
    # ############################################
           
    def get_pgsql_node_fqdn(self,param):
        """A function to get the FQDN for a PgSQL node"""

        if self.conn:
            if self.cur:
                try:
                    self.cur.execute('SELECT get_pgsql_node_fqdn(%s)',(param,))
                    
                    data = self.cur.fetchone()[0]
                    return data

                except psycopg2.Error as e:
                    print "\n* ERROR - Could not get the FQDN for this PgSQL node \n* %s" % e
                

    # ############################################
    # Method 
    # ############################################
           
    def get_pgsql_node_id(self,param):
        """A function to get the ID of a PgSQL node"""

        if self.conn:
            if self.cur:
                try:
                    self.cur.execute('SELECT get_pgsql_node_id(%s)',(param,))
                    
                    data = self.cur.fetchone()[0]
                    return data

                except psycopg2.Error as e:
                    print "\n* ERROR - Could not get the node ID for this PgSQL node \n* %s" % e
                                 

    # ############################################
    # Method 
    # ############################################
           
    def get_listen_channel_names(self,param):
        """A function to get a list of channels to LISTEN for a backup_server"""

        if self.conn:
            if self.cur:
                try:
                    list = []
                    
                    self.cur.execute('SELECT get_listen_channel_names(%s)',(param,))
                    
                    for row in self.cur.fetchall():
                        list.append(row[0])

                    return list
                
                except psycopg2.Error as e:
                    print "\n* ERROR - Could not get the listen channel names\n* %s" % e


    # ############################################
    # Method 
    # ############################################
           
    def get_next_crontab_id_to_generate(self,param):
        """A function to get the next PgSQL node ID to generate a crontab file for"""

        if self.conn:
            if self.cur:
                try:
                    self.cur.execute('SELECT get_next_crontab_id_to_generate(%s)',(param,))
                    
                    data = self.cur.fetchone()[0]
                    return data

                except psycopg2.Error as e:
                    print "\n* ERROR - Could not get the next job in the queue\n* %s" % e





    # ############################################
    # Method 
    # ############################################
           
    def generate_crontab_file(self,pgsql_node_id):
        """A function to get the crontab file for a PgSQL node"""

        if self.conn:
            if self.cur:
                try:
                    self.cur.execute('SELECT generate_crontab_file(%s)',(pgsql_node_id,))
                    
                    data = self.cur.fetchone()[0]
                    print data
                    
                except psycopg2.Error as e:
                    print "\n* ERROR - Could not generate the crontab file for this PgSQL node\n* %s" % e
