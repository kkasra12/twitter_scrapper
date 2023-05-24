import pandas as pd

from config import connection_info
from database_manager import DatabaseManager
import argparse

# use argparse to get the csv file
parser = argparse.ArgumentParser()
parser.add_argument("--file", '-f', help="the csv file to be imported", required=True)
parser.add_argument("--column", '-c', help="the column name of the usernames", default="Screen name")
args = parser.parse_args()
file_path = args.file
column_name = args.column

df = pd.read_csv(file_path)
usernames = df[column_name].tolist()

manager = DatabaseManager(config_dict=connection_info)
print("adding users to the database...")
manager.push_users_to_queue(usernames)
print(f"{len(usernames)} users added to the database successfully")
