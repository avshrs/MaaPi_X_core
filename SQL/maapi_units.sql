create table maapi_units
    (
      id          SERIAL PRIMARY KEY,
      u_name        VARCHAR(60) NOT NULL,
      u_sign        VARCHAR(10) NOT NULL,
      u_description     VARCHAR(200)
      );

INSERT INTO maapi_units VALUES (default, 'Temperature', 'C', '');
INSERT INTO maapi_units VALUES (default, 'Humidity', '%', '');
INSERT INTO maapi_units VALUES (default, 'Accuracy', '%', '');
INSERT INTO maapi_units VALUES (default, 'Pressure', 'hPa', '');
INSERT INTO maapi_units VALUES (default, 'Sealevel-Pressure', 'hPa', '');
INSERT INTO maapi_units VALUES (default, 'Altitude', 'm', '');
INSERT INTO maapi_units VALUES (default, 'Light-Level', 'lux', '');
INSERT INTO maapi_units VALUES (default, 'Relay', '1/0', '');
INSERT INTO maapi_units VALUES (default, 'Sun-Energy', 'W/m2', '');
INSERT INTO maapi_units VALUES (default, 'Percent', '%', '');
INSERT INTO maapi_units VALUES (default, 'MegaBytes', 'MB', '');
INSERT INTO maapi_units VALUES (default, 'KiloBytes', 'KB', '');
INSERT INTO maapi_units VALUES (default, 'GigaBytes', 'GB', '');
INSERT INTO maapi_units VALUES (default, 'Wats', 'W', '');
INSERT INTO maapi_units VALUES (default, 'Volts', 'V', '');
INSERT INTO maapi_units VALUES (default, 'Amperes', 'A', '');
 

