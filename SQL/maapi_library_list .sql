create table maapi_library_list 
        (
            id                    SERIAL PRIMARY KEY,
            l_name                VARCHAR(20) NOT NULL,
            l_description         VARCHAR(200),
            l_file_name           VARCHAR(200) NOT NULL,
            l_board_location_id   INT NOT NULL,                                     -- from board list table
            l_protocol            VARCHAR(5)  NOT NULL,
            l_port                INT UNIQUE NOT NULL,
            l_pid                 INT, 
            l_cpu_usage           REAL, 
            l_mem_usage           REAL,
            l_start_date          TIMESTAMP,
            l_last_responce       TIMESTAMP,
            l_status              VARCHAR(10),
            l_enabled             BOOLEAN NOT NULL,
            );

