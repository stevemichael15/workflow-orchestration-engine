import psycopg2
import os


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "workflow_engine"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres")
    )

# def get_connection():
#     return psycopg2.connect(
#         host="localhost",
#         dbname="workflow_engine",
#         user="postgres",
#         password="postgres",
#         port=5432
#     )

# def get_connection():
#     print("DB CONNECT → user=postgres, password=postgres")
#     return psycopg2.connect(
#         host="localhost",
#         dbname="workflow_engine",
#         user="postgres",
#         password="postgres",
#         port=5432
#     )