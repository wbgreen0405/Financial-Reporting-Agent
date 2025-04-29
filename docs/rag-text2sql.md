# 🧠 Text-to-SQL with RAG

## What is RAG?

Retrieval-Augmented Generation (RAG) allows GPT-4 to access relevant schema and metadata before generating SQL.

## Pipeline

1. Load schema and metadata from Microsoft Fabric
2. Pass metadata into context window with GPT-4
3. Use Vanna AI to convert user question to SQL
4. Execute SQL and return result

## Example

**Query:** "What are the top 3 clients by portfolio value?"

→ SQL generated:
```sql
SELECT TOP 3 client_id, SUM(asset_value) 
FROM portfolios
GROUP BY client_id
ORDER BY SUM(asset_value) DESC;
```
