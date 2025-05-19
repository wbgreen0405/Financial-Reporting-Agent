# 🧠 Architecture Overview

This system uses Microsoft Fabric and Azure to centralize wealth management data, applying AI-based reasoning over it.

## 📊 Diagram

![Architecture](https://github.com/wbgreen0405/Financial-Reporting-Agent/blob/dev/assets/A_flowchart_diagram_in_a_hand-drawn_style_illustra.png?raw=true)

## Key Components

| Component         | Description |
|------------------|-------------|
| Microsoft Fabric | Stores and processes client portfolio and transaction data |
| OneLake          | Unified data lake and warehouse |
| Vanna AI         | Converts natural language to SQL |
| RAG + GPT-4      | Retrieval-Augmented Generation engine for contextual answers |
| LangChain        | Enables prompt chaining, memory, and multi-step reasoning |
