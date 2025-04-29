# 🚀 Running the App

## Data Insertion

Insert data into Microsoft Fabric Lakehouse:
```bash
python CreateDataWarehouse/InsertToSQL.py
```

## Train the RAG Model

```bash
python RAGToSQL/TrainRAG.py
```

## Run Inference (Text-to-SQL)

```bash
python RAGToSQL/InferenceRAG.py
```

## Use LangChain Variant

```bash
python LangchainFabrics/LangChainFabrics.py
```

Make sure your connection and environment variables are properly set.
