CREATE TABLE data_table (
    id SERIAL PRIMARY KEY,
    column1 VARCHAR(255),
    column2 FLOAT,
    column3 FLOAT,
    target BOOLEAN
);

CREATE TABLE test_data_table (
    id SERIAL PRIMARY KEY,
    column1 FLOAT,
    column2 FLOAT,
    column3 FLOAT,
    target BOOLEAN
);

CREATE TABLE input_data_table (
    id SERIAL PRIMARY KEY,
    column1 FLOAT,
    column2 FLOAT,
    column3 FLOAT
);