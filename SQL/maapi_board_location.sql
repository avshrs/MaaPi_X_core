create table maapi_board_location 
        (
            id                    SERIAL PRIMARY KEY,
            b_name                VARCHAR(20) NOT NULL,
            b_description         VARCHAR(200),
            b_ipv4                VARCHAR(200) NOT NULL,
            b_location            VARCHAR(200),
            b_enabled             BOOLEAN NOT NULL,
            );

