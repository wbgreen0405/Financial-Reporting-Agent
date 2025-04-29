# 💼 Microsoft Fabric Financial Reporting Agent

Welcome to the official documentation site for the **Financial Reporting Agent**, powered by **Microsoft Fabric**, **Vanna AI**, and **GPT-4**.

---

## 📖 Overview

The Financial Reporting Agent project is designed to transform wealth management data analysis by consolidating diverse financial datasets into Microsoft Fabric's OneLake architecture. It enables users to perform **natural language queries** over financial data, powered by a **Retrieval-Augmented Generation (RAG)** system and interactive dashboards.

---

## ✨ Key Features

- **Natural Language Querying**: Seamlessly convert English questions into SQL using Vanna AI + GPT-4.
- **Real-Time Dashboards**: Instantly visualize portfolio, asset, and transaction data.
- **Scalable Storage**: OneLake's lakehouse and warehouse architecture ensures efficient data management.
- **AI-Enhanced Insights**: Retrieval-Augmented Generation (RAG) architecture enriches query responses.

---

## 🛠 How It Works

1. Data is ingested from Azure SQL and storage systems into Microsoft Fabric OneLake.
2. Fabric organizes the data across a lakehouse and warehouse structure.
3. Vanna AI and GPT-4 interpret user questions and generate SQL queries dynamically.
4. Results are retrieved, analyzed, and visualized on real-time dashboards.

---

## 🏗 Project Structure

- **CreateDataWarehouse/**: SQL schema and data insertion scripts
- **RAGToSQL/**: Training and inference modules for RAG
- **LangchainFabrics/**: LangChain integration for enhanced query generation
- **requirements.txt**: Python environment setup
- **Architecture Diagram**: Visual overview of the system

---

## 🚀 Getting Started

Check the [README](../README.md) for setup instructions to clone the repository, set up Microsoft Fabric, and start training your financial RAG system!

---

## 📬 Contact

Have a question or want to contribute?  
Open an issue or start a discussion on our [GitHub repository](https://github.com/your-repo/issues).

---
