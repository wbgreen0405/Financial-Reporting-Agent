# ⚙️ Setup Guide

## Prerequisites

- Python 3.9+
- Access to Microsoft Fabric and OneLake
- SQL Server or Lakehouse instance
- Required Python packages (see `requirements.txt`)

## Environment Setup

### Step 1: Clone the repository
```bash
git clone https://github.com/wbgreen0405/Financial-Reporting-Agent.git
cd Financial-Reporting-Agent
```

### Step 2: Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Fabric credentials

Update the `Helper/Credentials.py` file with your access tokens and keys.

