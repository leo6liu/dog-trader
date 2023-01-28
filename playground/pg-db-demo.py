import os
import psycopg2

# get environment variables
PG_HOST = os.getenv('PG_HOST')
PG_PORT = os.getenv('PG_PORT')
PG_DB_NAME = os.getenv('PG_DB_NAME')
PG_USERNAME = os.getenv('PG_USERNAME')
PG_PASSWORD = os.getenv('PG_PASSWORD')

# check for missing environment variables
if PG_HOST == None or PG_PORT == None or PG_DB_NAME == None or PG_USERNAME == None or PG_PASSWORD == None:
    print('[ ERROR ] Environment variables PG_HOST, PG_PORT, PG_DB_NAME, PG_USERNAME, or PG_PASSWORD not found.')
    print('[ INFO ] Exiting...')
    quit()

# connect to db
conn = psycopg2.connect("host='{}' port='{}' dbname='{}' user='{}' password='{}'".format(PG_HOST, PG_PORT, PG_DB_NAME, PG_USERNAME, PG_PASSWORD))

# open a cursor to perform database operations
cur = conn.cursor()

# select all rows from public.bars_minute
cur.execute("SELECT * FROM public.bars_minute")

# retrieve and print query results
records = cur.fetchall()
print(records)

# close db connection
conn = None