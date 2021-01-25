create table maapi_groups
    (
      id          SERIAL PRIMARY KEY,
      g_name        VARCHAR(60) NOT NULL,
      g_description     VARCHAR(200),
      g_enabled         BOOLEAN,
      );

