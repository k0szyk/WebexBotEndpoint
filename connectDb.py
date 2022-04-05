from configparser import ConfigParser
import psycopg2
import logging

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s', filename='./WebexBotEndpoint.log', filemode='a')

def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

    
def connect(tableName, columns):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:

        params = config()
        logging.debug("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT {} FROM {};".format(columns, tableName))
        row = cur.fetchone()
        data = {}
        while row is not None:
            data[row[0]] = row[1]
            row = cur.fetchone()
        cur.close()
        conn.close()
        return data
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error("Encountered the following exception while connecting to DB: {}.".format(error))

def updateAccessToken(id, value, expiry):
    sql = """ UPDATE access_token
                SET value= %s, expiry = %s
                WHERE id = %s"""
    conn = None
    updated_rows = 0
    try:
        params = config()
        logging.debug("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(sql, (value, expiry, id))
        updated_rows = cur.rowcount
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return updated_rows