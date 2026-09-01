import csv 
import os 
import psycopg2

CSV_DIR = "../1-lh_nautical_csv"
SCHEMA_FILE = "../Questao2/schema.sql" 

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "lighthouse",
    "user": "postgres",
    "password": "lighthouse123",
}

def create_schema(cur):
    with open(SCHEMA_FILE, "r", encoding = "utf-8") as f:
        cur.execute(f.read())

def load_csv_into_table(cur,table_name, filepath):
    with open(filepath, "r", encoding= "utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)

        columns= ",".join(header)
        copy_sql =f"COPY {table_name}({columns}) FROM STDIN WITH (FORMAT CSV, NULL '')"
        cur.copy_expert(copy_sql,f)

def main ():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try: 
        create_schema(cur)
        conn.commit()
        csv_files = [f for f in os.listdir(CSV_DIR) if f.lower().endswith(".csv")]

        for csv_file in sorted(csv_files):
            table_name = os.path.splitext(csv_file)[0]
            filepath = os.path.join(CSV_DIR,csv_file)

            load_csv_into_table(cur,table_name,filepath)

        conn.commit()
        print("Carga concluída")

    except Exception as e:
        conn.rollback()
        print(f"Erro durante a carga: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
