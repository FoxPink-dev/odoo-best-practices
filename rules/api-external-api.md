---
priority: SHOULD
tags: [api, external, json-rpc, xml-rpc]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "Design external API integration"
    includes: ["controllers/*.py", "tests/*.py"]
---
# External API Patterns

## Description

Odoo provides external API access via JSON-RPC and XML-RPC. JSON-RPC is recommended for modern integrations. Always use the `execute_kw` endpoint with explicit model, method, arguments, and keyword arguments. Use `authenticate` or session-based auth.

## JSON-RPC (Recommended)

```python
import json
import random
import requests

ODOO_URL = "https://myinstance.odoo.com"
DB = "mydb"
USERNAME = "admin"
PASSWORD = "admin"

# Authenticate
url = f"{ODOO_URL}/jsonrpc"
headers = {"Content-Type": "application/json"}

# Login to get user ID (uid)
payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "service": "common",
        "method": "login",
        "args": [DB, USERNAME, PASSWORD],
    },
    "id": random.randint(0, 1000000000),
}
response = requests.post(url, json=payload, headers=headers)
uid = response.json()["result"]

# Search and read records
payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "service": "object",
        "method": "execute_kw",
        "args": [
            DB, uid, PASSWORD,
            "res.partner",
            "search_read",
            [[["customer_rank", ">", 0]]],
            {"fields": ["name", "email", "phone"], "limit": 10},
        ],
    },
    "id": random.randint(0, 1000000000),
}
response = requests.post(url, json=payload, headers=headers)
partners = response.json()["result"]
```

## XML-RPC (Legacy)

```python
import xmlrpc.client

url = "https://myinstance.odoo.com"
db = "mydb"
username = "admin"
password = "admin"

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
partners = models.execute_kw(
    db, uid, password,
    "res.partner", "search_read",
    [[["customer_rank", ">", 0]]],
    {"fields": ["name", "email"], "limit": 10},
)
```

## Incorrect

```python
# Using raw psycopg2 to access Odoo DB externally
import psycopg2

conn = psycopg2.connect("dbname=mydb user=odoo password=odoo")
cur = conn.cursor()
cur.execute("SELECT name, email FROM res_partner")
# Bypasses all Odoo security, ORM, computed fields, and business logic
```

## Rationale

- JSON-RPC is more readable and supported by modern tools vs XML-RPC
- Always use `execute_kw` — never directly query the database
- Database-level access bypasses ORM security, computed fields, and business logic
- Use `search_read` for combined search+read in one call (avoids N+1)
- API calls respect Odoo's security rules (ACL and record rules)
- For batch operations, prefer `write` and `create` with multi-record arrays

## References

- https://www.odoo.com/documentation/19.0/developer/reference/external_api.html
