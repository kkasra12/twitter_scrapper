import config
from config import connection_info
from database_manager import DatabaseManager
from twitter_api import TwitterApi


def get_next_user_to_process(database_manager: DatabaseManager) -> (str, int):
    """
    This function gets the next person to process
    it will check the database and checks if any user has less than specified number of tweets(100) and returns them.
    otherwise it will return next unprcessed user
    :return: 1. the username of the next user to be processed
             2. the number of tweets that must be fetched (= max_tweets_per_user - number_of_fetched_tweets)
             3. None if there is no tweet fetched for this user else the id of the last tweet fetched for this user.
    """
    incomplete_users = database_manager.find_the_users_with_incomplete_tweets()
    if incomplete_users:
        return incomplete_users[0]['username']
    # if there is no incomplete user, we get the next user to process
    next_user = database_manager.pop_next_unprocessed_user()
    return next_user


def process_one_user(manager: DatabaseManager, api_client: TwitterApi,
                     max_tweets_per_user: int = 100,
                     user_fields: list[str] = None,
                     tweet_fields: list[str] = None):
    """
    This function processes one user and updates the database
    if there is no user to process, it will return None
    otherwise it will return the username of the user and number of tweets fetched
    :param manager: the database manager
    :param api_client: the Twitter api client
    :param user_fields:
    :param tweet_fields:
    :param exclude_replies:
    :param retry_count:
    :param max_tweets_per_user:
    :return: None if there is no user to process,
             otherwise it will return the username of the user and number of tweets fetched
    """

    # get the user info
    username = get_next_user_to_process(database_manager=manager)
    if username is None:
        return None

    user_info = api_client.get_user(username=username, user_fields=user_fields)
    print(user_info)

    # add the user to the database
    result = manager.add_user(user_id=user_info["id"],
                              profile_image_url=user_info["profile_image_url"],
                              location=user_info["location"],
                              description=user_info["description"],
                              verified=user_info["verified"],
                              username=user_info["username"],
                              number_of_followers=user_info["followers_count"],
                              number_of_following=user_info["following_count"])
    if result == -1:
        print(f"user {username} already exists in the database")
        manager.set_user_finished(user_id=user_info["id"])
        return username
    # TODO: if the user is protected, we should not fetch the tweets
    if user_info["protected"]:
        print(f"user {user_info['username']} is protected")
    else:
        # get the tweets for the user
        tweets = api_client.get_last_tweets(user_id=user_info["id"],
                                            number_of_tweets=max_tweets_per_user,
                                            fields=tweet_fields)

        # add the tweets to the database
        for tweet in tweets:
            manager.add_tweet(tweet_id=tweet["id"],
                              text=tweet["text"],
                              image_url=tweet["image_url"],
                              date=tweet["date"],
                              number_of_likes=tweet["number_of_likes"],
                              number_of_retweets=tweet["number_of_retweets"],
                              number_of_replies=tweet["number_of_replies"],
                              number_of_quotes=tweet["number_of_quotes"],
                              user_id=user_info["id"])

    manager.set_user_finished(user_id=user_info["id"])
    return username


def main(max_tweets_per_user: int = 100):
    manager = DatabaseManager(config_dict=connection_info)
    api_client = TwitterApi(bearer_token=config.bearer_token, number_of_retries=3)
    while True:
        username = process_one_user(manager=manager, api_client=api_client,
                                    max_tweets_per_user=max_tweets_per_user)
        if username is None:
            print("no more users to process")
            break
        print(f"{username} processed")


if __name__ == '__main__':
    main()
