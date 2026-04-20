# schema.py

TABLE_SCHEMA = """
You have access to a Snowflake database with the following table:

TABLE: employees
COLUMNS:
  - employee_id   (INT)         : Unique ID for each employee
  - name          (VARCHAR)     : Full name of the employee
  - department    (VARCHAR)     : Department name — values: Engineering, Marketing, HR, Finance
  - job_title     (VARCHAR)     : Job title of the employee
  - salary        (NUMBER)      : Annual salary in USD
  - location      (VARCHAR)     : Office location — values: New York, London, Chicago
  - hire_date     (DATE)        : Date the employee was hired (format: YYYY-MM-DD)
  - is_active     (BOOLEAN)     : TRUE if currently employed, FALSE if not

SAMPLE DATA:
  ('Alice Johnson', 'Engineering', 'Senior Engineer', 95000, 'New York', '2020-03-15', TRUE)
  ('Bob Smith',     'Engineering', 'Junior Engineer', 65000, 'London',   '2022-07-01', TRUE)
  ('Iris Taylor',   'Finance',     'CFO',            120000, 'New York', '2017-04-12', TRUE)

RULES FOR QUERYING:
  - Always use uppercase for table and column names
  - For filtering boolean: use TRUE or FALSE (not 1/0)
  - For date filtering: use format 'YYYY-MM-DD'
  - Always add LIMIT 100 unless user asks for all records
"""