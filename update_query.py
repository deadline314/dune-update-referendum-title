import os
import requests
import json
from tqdm import tqdm
import pandas as pd
import time

# Read title cache from 'data.parquet'
parquet_file = 'data.parquet'
if os.path.exists(parquet_file):
    df = pd.read_parquet(parquet_file)
else:
    df = pd.DataFrame(columns=['id', 'title'])
df['id'] = df['id'].astype(str)

# Define Header(Please notice API KEY)
dune_headers = {
    'Content-Type': 'application/json',
    'X-DUNE-API-KEY': 'API key' # replace to your API key
}

# Start the query execution (POST request)
url_execute = "https://api.dune.com/api/v1/query/3745369/execute"
execute_response = requests.request("POST", url_execute, headers=dune_headers)

# Check if the execution POST was successful before proceeding
if execute_response.status_code != 200:
    print(f"Error executing the query: {execute_response.json()}")
    exit(1)

# Optionally wait for a certain time to ensure the query execution completes
time.sleep(5)  # Wait 10 seconds (adjust as necessary)

# Sent GET to get the max referenda number after execution
dune_url = "https://api.dune.com/api/v1/query/3745369/results"
response = requests.get(dune_url, headers=dune_headers)
response_data = response.json()
referenda_id = response_data['result']['rows'][0]['referenda_id']

polkadot_headers = {'x-network': 'polkadot'}

titles = []
new_rows = []
for post_id in tqdm(range(referenda_id + 1)):
    post_id = str(post_id)
    if post_id in df['id'].values:
        title = df.loc[df['id'] == post_id, 'title'].iloc[0]
        titles.append((post_id, title.replace('\'', '\"')))
        continue

    polkadot_url = f"https://api.polkassembly.io/api/v1/posts/on-chain-post?proposalType=referendums_v2&postId={post_id}"
    response = requests.get(polkadot_url, headers=polkadot_headers)
    data = response.json()

    # Check if the title exists in the response
    if 'title' in data:
        title = data['title']
        new_rows.append({'id': post_id, 'title': title})
        titles.append((str(post_id), title.replace('\'', '\"')))

# Update the DataFrame and save back to the parquet file if new rows are added
if new_rows:
    new_df = pd.DataFrame(new_rows)
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_parquet(parquet_file, index=False)

# Construct the SQL query
values = ',\n'.join([f"({int(id)}, '{title}')" for id, title in titles])
query_sql = f"""SELECT * FROM (VALUES\n{values}\n) AS t(id, title)"""
data = {
    "query_id": 3745381,
    "query_sql": query_sql
}

# Sent PATCH to update Dune Query
update_url = "https://api.dune.com/api/v1/query/3745381"
response = requests.patch(update_url, headers=dune_headers, data=json.dumps(data))
print(response.json())
