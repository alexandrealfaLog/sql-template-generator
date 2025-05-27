import os
from pathlib import Path
from string import Template
from typing import Dict, List

import psycopg2
from dotenv import load_dotenv

from query import sql_run, get_dataset_view_query

load_dotenv()

def get_datasets() -> List[Dict[str, str]]:
    connection_params = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'port': os.getenv('DB_PORT'),
        'host': os.getenv('DB_HOST'),
    }

    try:
        with psycopg2.connect(**connection_params) as con:
            with con.cursor() as cur:
                cur.execute(get_dataset_view_query)
                return [{'view': f"'{row[0]}'", 'dataset_id': f"'{row[1]}'"} for row in cur.fetchall()]

    except psycopg2.Error as e:
        print(f"Falha ao buscar datasets: {e}")
        return []

def write_sql_response_file(output: List[str]) -> None:
    final_sql = "\n\n --=== FIM DE UMA QUERY === \n\n".join(output)

    Path("query_result.sql").write_text(final_sql, encoding="utf-8")
    pass


def process_template() -> None:
    output = []

    for row in get_datasets():
        filled_sql = Template(sql_run).substitute(
            dataset_id=row['dataset_id'],
            dataset_view_id=row['view']
        )

        output.append(f"-- Query for view: {row['view']} / dataset: {row['dataset_id']}\n{filled_sql.strip()}\n")

    write_sql_response_file(output)
    pass

if __name__ == '__main__':
    process_template()
