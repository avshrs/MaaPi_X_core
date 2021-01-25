create table maapi_sensors_list  
        (
            id                    SERIAL PRIMARY KEY,
            s_user_id             INT NOT NULL,                    -- used to sort sensor list
            s_name                VARCHAR(20) NOT NULL,
            s_description         VARCHAR(200),
            s_dev_id              VARCHAR(60) UNIQUE NOT NULL,
            s_sensor_id           VARCHAR(60) UNIQUE NOT NULL,
            s_created             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            s_enabled             BOOLEAN NOT NULL,
            s_board_location_id   INT NOT NULL,                                     -- from board list table
            s_dev_library_id      INT NOT NULL,                                     -- from library table 
            s_unit_id             INT NOT NULL,                                     -- from unit table
            s_value_adjust        REAL DEFAULT 0,
            s_last_update         TIMESTAMP,
            s_status              VARCHAR(10),
            s_read_interval       INT DEFAULT 60,  
            
            s_data_col_con_e      BOOLEAN,
            s_dcc_ref_sens_e      BOOLEAN,
            s_dcc_ref_sens_id     INT,                                             -- from sensor list table
            s_dcc_min_e           BOOLEAN,   
            s_dcc_min             REAL,
            s_dcc_max_e           BOOLEAN,   
            s_dcc_max             REAL,
            s_dcc_if_conf_fail_e  BOOLEAN,
            s_dcc_if_conf_fail    REAL,
            
            s_additional_dev1_id   INT,                                             -- from sensor list table
            s_additional_dev2_id   INT,                                             -- from sensor list table  
            s_additional_dev3_id   INT,                                             -- from sensor list table

            s_additional_expres1   TEXT,
            s_additional_expres2   TEXT,

            s_location             VARCHAR(60), 
            s_group_id             INT,                                             -- from group list table                  
            );

