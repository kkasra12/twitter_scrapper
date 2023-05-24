# Introduction
in this project, we will get the information about the Twitter users and their tweets.

The key features of this project is:
We save the requested information in the database after each request, 
so that we can resume the process from the place we left.

Since the number of requests to the Twitter API is limited, we cannot get much information in a single run.
So we can run the program multiple times and get the information in multiple runs.
And this program will resume the process from the place we left.

# how to use
## set up the database
Since we use `psycopg` in this project, you need to use `postgresql` on your system. 
Unless if you want to change the DBMS, you need to change the `database_manager.py` file. '
In order to do so, please don't change the input or output of the functions in the `DatabaseManager` class.
In most cases, you just need to change the `__init__` and `run_query` function.

## set up the project
1. install the requirements `pip install -r requirements.txt`
2. copy and paste `config_sample.py` and rename it to `config.py`
3. fill the `config.py` file with your own information, I hope you can find enough comments in the file.
4. run the `initialize_database.py` file to create the tables in the database.
5. (optional) run the `database_manager.py` file to check if the database is working properly.
6. (optional) run the `twitter_api.py` file to check if the Twitter API (bearer token) is working properly.
7. run the `main.py`.


