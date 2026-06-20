FROM python:3.12-alpine

WORKDIR /app

# Copy analyzer package
COPY analyzer/ /app/analyzer/
COPY knowledge/ /app/knowledge/

# Copy action entrypoint
COPY .github/actions/odoo-review/entrypoint.py /app/entrypoint.py

ENTRYPOINT ["python", "/app/entrypoint.py"]
