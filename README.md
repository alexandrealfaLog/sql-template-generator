# SQL Template Generator

Este projeto tem como objetivo gerar um arquivo `.sql` com múltiplas queries personalizadas a partir de um template base, preenchido dinamicamente com `dataset_id` e `dataset_view_id` extraídos do banco de dados PostgreSQL.

---

## 🚀 Funcionalidades

- Conecta-se ao PostgreSQL usando parâmetros do `.env`
- Busca automaticamente os `dataset_view_id` válidos
- Preenche um template SQL com os dados encontrados
- Gera um único arquivo `.sql` com todas as queries formatadas
- Pronto para execução com o `psql` ou ferramentas de BI

---

## 🛠️ Requisitos

- Python 3.7+
- PostgreSQL
- Biblioteca `psycopg2`
- Biblioteca `python-dotenv`

---

## 📦 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/alexandrealfaLog/sql-template-generator.git
cd sql-template-generator
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Crie o arquivo `.env` com os dados de conexão:

```env
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_PORT=
DB_HOST=
```
É possível rodar utilizando o arquivo up.sh
---

## 🧩 Estrutura esperada

- `sql_template.sql` → arquivo com a query SQL contendo placeholders (`$dataset_id`, `$dataset_view_id`)
- `main.py` → script Python que processa os datasets e gera `exported_queries.sql`

---

## ▶️ Como usar

```bash
python main.py
```

Ao executar, será criado o arquivo:

```
exported_queries.sql
```

> Contendo todas as queries com os valores preenchidos, prontas para execução no PostgreSQL.

---

## 📤 Executar no PostgreSQL

```bash
psql -U $DB_USER -d $DB_NAME -f exported_queries.sql
```

---

## 🧪 Exemplo de Template SQL

```sql
WITH RECURSIVE json_data AS (
  SELECT structure::json AS data
  FROM dataset_views
  WHERE dataset_id = $dataset_id
    AND "default" = TRUE
    AND id = $dataset_view_id
)
...
```

---

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

---

## 👨‍💻 Autor

Desenvolvido por [alexandre alfa](https://github.com/alexandrealfa).