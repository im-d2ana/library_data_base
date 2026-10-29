import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="library",
        user="postgres",
        password="password",
        host="localhost",
        port="5435"
    )