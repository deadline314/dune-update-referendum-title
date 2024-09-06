# Dune to Polkassembly Data Fetcher

This script fetches the latest referendum data from Dune's API and then retrieves the corresponding title from Polkassembly's API for a given referendum. It also maintains a local cache of referendum titles to avoid redundant API calls.

## Prerequisites

Before you can run this script, you will need the following:

- Python 3.x installed
- Necessary Python packages:
  - `requests`
  - `pandas`
  - `pyarrow` (required for Parquet support in `pandas`)
  - `tqdm`
  
You can install the necessary packages using the following command:

```bash
pip install requests pandas pyarrow tqdm
```

A valid API key for Dune Analytics. You can replace the placeholder X-DUNE-API-KEY in the script with your actual key.

# Script Overview
## Libraries Used
`os`: For file operations.
`requests`: To make HTTP requests to both Dune and Polkassembly APIs.
`json`: To handle JSON data.
`tqdm`: To provide a progress bar for looping through referenda IDs.
`pandas`: For handling data storage in .parquet format.
`time`: To add delays between API calls.

## Process Workflow
Data Caching:
1. The script loads a cache of previously fetched titles from a data.parquet file if it exists.
* If the file does not exist, it creates a new DataFrame.
2. Dune Query Execution:
* Sends a POST request to execute a Dune query (query_id: 3745369).
* Waits for the query execution to complete and retrieves the latest referendum_id.
3. Fetch Titles from Polkassembly:
* Loops through all referendum_id values, checking if the title is cached in the parquet file. If not, it fetches the title using the Polkassembly API.
* New titles are appended to the DataFrame and saved back to data.parquet.
4. Update Dune SQL Query:
* Constructs an SQL query in the format of:
```SQL
SELECT * FROM (VALUES
(id, 'title'),
(id, 'title')
) AS t(id, title)
```
* Sends a PATCH request to update a Dune query with this SQL.

# How to Run
Ensure you have the correct API keys and headers set up for Dune and Polkassembly. Replace the placeholder in the code:
```python
dune_headers = {
    'Content-Type': 'application/json',
    'X-DUNE-API-KEY': 'your-dune-api-key-here'
}
```
Run the script:
```bash
python your_script.py
```
The script will fetch the latest referendum_id, retrieve any uncached titles from Polkassembly, and update the Dune SQL query accordingly.

