import warnings

import psycopg
from psycopg.rows import dict_row


class DatabaseManager:
    instance: 'DatabaseManager'
    connection_string: str

    def __new__(cls, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DatabaseManager, cls).__new__(cls)
            # cls.instance.connection_string = kwargs["connection_string"]
            cls.instance.__init(**kwargs)
        return cls.instance

    def __init(self, **kwargs):
        if 'connection_string' in kwargs:
            self.connection_string = kwargs["connection_string"]
        elif 'config_dict' in kwargs:
            self.connection_string = ' '.join(map('='.join, kwargs["config_dict"].items()))
        else:
            raise Exception("connection_string or config_dict must be provided as a keyword argument")
        with psycopg.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                if cur.closed or conn.closed or conn.broken:
                    raise Exception("cannot connect to the database")
                # else:
                #     print("connected to the database successfully")
                cur.execute("select table_name from information_schema.tables where table_schema='public'")
                tables = [table[0] for table in cur.fetchall()]
                self.columns = {}
                for table in tables:
                    cur.execute(f"select column_name from information_schema.columns where table_name='{table}'")
                    self.columns[table] = [column[0] for column in cur.fetchall()]

    def run_query(self, query: str, args: tuple = None, *, return_result: bool = True):
        with psycopg.connect(self.connection_string) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query, args)
                conn.commit()
                if return_result and cur.rowcount > 0:
                    # return tuple2dict(cur)
                    return cur.fetchall()

    def add_user(self, user_id: str | int,
                 profile_image_url: str,
                 location: str,
                 description: str,
                 verified: bool,
                 username: str,
                 number_of_followers: int,
                 number_of_following: int):
        """

        :param user_id:
        :param profile_image_url:
        :param location:
        :param description:
        :param verified:
        :param username:
        :param number_of_followers:
        :param number_of_following:
        :return: an integer representing the result of the query
        -1: the user already exists in the database
        0 : the user is added to the database successfully
        """
        # check if user already exists or not
        if self.run_query("select * from users where twitter_id = %s", (user_id,)):
            return -1
        self.run_query("insert into users (twitter_id, profile_image_url, location_, description, verified, "
                       "username, number_of_followers, number_of_following) "
                       "values (%s, %s, %s, %s, %s, %s, %s, %s)",
                       (user_id, profile_image_url, location, description, verified, username, number_of_followers,
                        number_of_following), return_result=False)
        return 0

    def add_tweet(self, tweet_id: str | int,
                  text: str,
                  image_url: str,
                  date: str,
                  number_of_likes: int,
                  number_of_retweets: int,
                  number_of_replies: int,
                  number_of_quotes: int,
                  user_id: str | int):
        self.run_query("insert into tweets (tweet_id, tweet_text, image_url, tweet_date, user_id, number_of_likes, "
                       "number_of_retweets, number_of_replies, number_of_quotes) "
                       "values (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                       (tweet_id, text, image_url, date, user_id, number_of_likes, number_of_retweets,
                        number_of_replies, number_of_quotes), return_result=False)

    # @tuple2dict('users')
    def find_the_users_with_incomplete_tweets(self):
        return self.run_query("select * from users where is_finished = false")

    def set_user_finished(self, user_id: str | int):
        self.run_query("update users set is_finished = true where twitter_id = %s", (user_id,), return_result=False)

    def find_the_last_tweet_of_the_user(self, user_id: str | int) -> str:
        return self.run_query("select tweet_id from tweets where user_id = %s order by tweet_date desc limit 1",
                              (user_id,))[0]['tweet_id']

    def pop_next_unprocessed_user(self) -> str:
        """
        :return: the username of the next user to be processed
        """
        username = self.run_query("select username from unprocessed_users limit 1")
        if username is not None:
            username_ = username[0]["username"]
            self.run_query("delete from unprocessed_users where username = %s",
                           (username_,),
                           return_result=False)
            return username_

    def push_users_to_queue(self, usernames: list[str]):
        for username in usernames:
            try:
                self.run_query("insert into unprocessed_users (username) values (%s)", (username,), return_result=False)
            except psycopg.errors.UniqueViolation:
                warnings.warn(f"{username} is already in the queue -- skipping")

    def get_columns_names(self, table_name: str):
        with psycopg.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(f"select * from {table_name} limit 0")
                return [desc[0] for desc in cur.description]


if __name__ == '__main__':
    from config import connection_info

    manager = DatabaseManager(config_dict=connection_info)
    a = DatabaseManager(config_dict=connection_info)
    manager.run_query("truncate table users cascade")
    print("number of rows in tweets table:", manager.run_query("select count(*) from tweets"))
    user_id = 'user_id{}'
    manager.add_user(user_id=user_id.format(1), profile_image_url="image", location="location",
                     description="description",
                     verified=True, username="username1", number_of_followers=1, number_of_following=1)

    manager.add_user(user_id=user_id.format(2), profile_image_url="image", location="location",
                     description="description",
                     verified=True, username="username2", number_of_followers=1, number_of_following=1)

    manager.add_tweet(tweet_id=1, text="text", image_url="image", date="date", number_of_likes=1, number_of_retweets=1,
                      number_of_replies=1, number_of_quotes=1, user_id=user_id.format(1))
    for i in range(10):
        manager.add_tweet(tweet_id=i + 2, text="text", image_url="image", date="date", number_of_likes=1,
                          number_of_retweets=1,
                          number_of_replies=1, number_of_quotes=1, user_id=user_id.format(2))

    print(manager.run_query("select * from users"))

    if incomplete_users := manager.find_the_users_with_incomplete_tweets():
        print(*[(i, type(i)) for i in incomplete_users], sep="\n")
    else:
        print("no incomplete users")
