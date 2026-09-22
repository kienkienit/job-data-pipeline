CREATE TABLE IF NOT EXISTS jobs (
    id                 SERIAL PRIMARY KEY,
    created_date       DATE,
    job_title          TEXT,
    company            TEXT,
    salary             TEXT,
    address            TEXT,
    time               TEXT,
    link_description   TEXT,
    min_salary         DOUBLE PRECISION,
    max_salary         DOUBLE PRECISION,
    salary_unit        VARCHAR(8),
    is_negotiable      BOOLEAN,
    salary_suspicious  BOOLEAN,
    city               VARCHAR(128),
    district           TEXT,
    is_multi_location  BOOLEAN,
    job_group          VARCHAR(64)
);
