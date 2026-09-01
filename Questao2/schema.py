import csv 
import os 
from datetime import datetime

CSV_DIR = "../1-lh_nautical_csv"
OUTPUT_FILE= "schema.sql"

def is_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

def is_float(value):
    try: 
        float(value)
        return True 
    except ValueError:
        return False 

def is_datetime(value):
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ]
    for i in formats:
        try:
            datetime.strptime(value,i)
            return True
        except ValueError:
            continue 
    try:
        datetime.fromisoformat(value)
        return True 
    except ValueError:
        return False

def is_long_numeric_id(value):
    stripped = value.strip()
    return stripped.isdigit() and len(stripped) > 9

def is_boolean(value):
    return value.strip().lower() in ("true","false")

def infer_column_type(values):
    nao_vazio = [v for v in values if v is not None and v.strip() != ""]
    if not nao_vazio:
        return "TEXT"
    
    if all (is_long_numeric_id(v) for v in nao_vazio):
        return "TEXT"

    if all (is_int(v) for v in nao_vazio):
        return "INTEGER"

    if all (is_float(v) for v in nao_vazio):
        return "NUMERIC"

    if all (is_datetime(v) for v in nao_vazio):
        return "TIMESTAMP"

    if all(is_boolean(v) for v in nao_vazio):
        return "BOOLEAN"

    return "TEXT"

def infer_schema (arquivo):
    with open(arquivo, newline="", encoding ="utf-8") as f:
        reader = csv.reader(f)
        header= next(reader)
        column_values = {col: [] for col in header}

        for row in reader:
            for col, value in zip(header,row):
                column_values[col].append(value)
    schema = []
    for col in header:
        col_type = infer_column_type(column_values[col])
        schema.append ((col,col_type))
    return schema

def generate_create_table(table_name,schema):
    lines = [f"CREATE TABLE {table_name} ("]
    col_defs = []

    for col_name, col_type in schema:
        definition = f" {col_name}  {col_type}"

        if col_name.lower() == "id":
            definition += " PRIMARY KEY"
        col_defs.append(definition)

    lines.append(",\n".join(col_defs))
    lines.append(");")
    return "\n".join(lines)

def main():
    csv_files = [f for f in os.listdir(CSV_DIR) if f.lower().endswith(".csv")]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for csv_file in sorted(csv_files):
            table_name = os.path.splitext(csv_file)[0]
            filepath = os.path.join(CSV_DIR, csv_file)

            schema = infer_schema(filepath)
            create_stmt = generate_create_table(table_name, schema)

            out.write(create_stmt + "\n\n")
            print(f"Tabela '{table_name}' processada ({len(schema)} colunas).")

    print(f"\nArquivo '{OUTPUT_FILE}' gerado com sucesso.")


if __name__ == "__main__":
    main()