# Semantic Column Classifier & Parser (IIT Madras Hack)

##  Overview
This project solves the challenge of processing unlabelled data columns in raw CSV files. It uses a custom-built pipeline to automatically:
1.  **Classify** columns into semantic types (Phone Number, Company Name, Country, Date, Other).
2.  **Parse & Normalize** the data (e.g., splitting phone numbers into Country/Number, or separating Company Names from Legal Suffixes).
3.  **Connect** to AI Agents via a Model Context Protocol (MCP) server.

##  Project Structure
```text
/
├── predict.py           # Part A: CLI tool for semantic column classification
├── parser.py            # Part B: CLI tool for parsing Phone and Company data
├── server.py            # Part C: MCP Server (AI Connector)
├── utils.py             # Shared logic for feature extraction and parsing
├── requirements.txt     # Python dependencies
├── README.md            # Documentation
└── Training_data/       # Dataset used for lookup and logic validation
    ├── company.csv
    ├── phone.csv
    ├── countries.txt
    ├── legal.txt
    └── dates.csv
```
# Setup & Installation
Prerequisites: Python 3.10+

## Clone the Repository

Install Dependencies Run the following command to install the necessary libraries:

Bash

```pip install -r requirements.txt```
# Usage Instructions
Part A: Semantic Classification (predict.py)
This script takes a file path and a specific column name, analyzes the values based on regex patterns and dictionary lookups, and returns the semantic label.

Command:

Bash

```python predict.py --input <path_to_file> --column <column_name>```
Example:

Bash

```python predict.py --input Training_data/phone.csv --column number```
# Output: phoneNumber
Part B: Parsing & Normalization (parser.py)
This script automatically scans the input file, identifies the most probable "Phone" and "Company" columns, and generates a standardized output.csv.

Command:

Bash

```python parser.py --input <path_to_file>```
Output Behavior:

Phone Parsing: Splits international numbers into Country and Number using the Google phonenumbers library.

Company Parsing: Identifies legal suffixes (e.g., "Pvt Ltd", "Inc") using a longest-match algorithm and separates them into Name and Legal fields.

Example:

Bash

```python parser.py --input Training_data/company.csv```
# Result: Creates 'output.csv' with columns: CompanyName, Name, Legal
# Part C: MCP Layer (server.py)
A FastMCP server that acts as a connector for AI agents (like Claude Desktop). It allows the AI to list files, run predictions, and execute the parser.

Run the Server (Developer Mode):

Bash

```mcp dev server.py```
Claude Desktop Configuration: Add this to your claude_desktop_config.json:

JSON

```
{
  "mcpServers": {
    "tresata-processor": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```
# Approach & Architecture
Feature Extraction (utils.py):

Regex Engine: Detects patterns for ISO Dates and International Phone formats.

Knowledge Base: Utilizes pycountry and a curated legal.txt for entity recognition.

Scoring System: Calculates a probability score (0-100%) for each category per column.

Parsing Logic:

Phone: Validates numbers against global standards to extract region codes.

Company: Uses suffix stripping logic. It specifically handles edge cases (like "Group Inc" vs "Inc") by prioritizing longer suffixes first.

# Requirements
Pandas (Data processing)

Phonenumbers (Google's lib port)

Python-dateutil (Robust date parsing)

Pycountry (ISO country standards)

Mcp (Model Context Protocol SDK)


---

### **Copy this into `requirements.txt`**

```text
pandas
phonenumbers
python-dateutil
pycountry
mcp
argparse
