# Database Verification

The FPCA form writes applicant data to a PostgreSQL database on AWS RDS.
Connection credentials are stored in `databaseconnect.env` (never committed).
Use `psycopg2` to connect. The main table is `Vfa_fpca_form`.

## Connection Details

- Host: defined in `databaseconnect.env` as `DB_HOST`
- Port: defined in `databaseconnect.env` as `DB_PORT`
- Database name: defined in `databaseconnect.env` as `DB_NAME`
- Username: defined in `databaseconnect.env` as `DB_USER`
- Password: defined in `databaseconnect.env` as `DB_PASSWORD`

## Schema

There are many fields. Ignore most of them.
Just search for the following:

dob
email
firstname
lastname








## Verification Strategy

After the E2E test submits the form, query the database to verify that at least 5 fields were written correctly (e.g., first name, last name, email, phone, SSN last 4).
