import requests


class TwitterApi:
    def __init__(self, bearer_token: str, number_of_retries: int = 3):
        self.bearer_token = bearer_token
        self.number_of_retries = number_of_retries

    def bearer_oauth(self, r):
        """
        Method required by bearer token authentication.
        """

        r.headers["Authorization"] = f"Bearer {self.bearer_token}"
        r.headers["User-Agent"] = "v2UserLookupPython"
        return r

    def connect_to_endpoint(self, url, caller_function: str = ""):
        number_of_tries = 0
        for _ in range(self.number_of_retries):
            response = requests.request("GET", url, auth=self.bearer_oauth, )
            if response.status_code != 200:
                raise Exception(f"Request returned an error while calling {caller_function}: "
                                f"{response.status_code=} {response.text=}")
            return response.json()
        else:
            raise Exception(f"Request was not successful after {self.number_of_retries} tries"
                            f" while calling {caller_function}")

    def get_user(self, username: str, user_fields: list[str] = None):
        if user_fields is None:
            user_fields = ["description",
                           "created_at",
                           "entities",
                           "id",
                           "location",
                           "name",
                           "pinned_tweet_id",
                           "profile_image_url",
                           "protected",
                           "public_metrics",
                           "url",
                           "username",
                           "verified"]
        # Specify the usernames that you want to lookup below
        # You can enter up to 100 comma-separated values.
        # usernames = "usernames=TwitterDev,TwitterAPI"
        # User fields are adjustable, options include:
        # created_at, description, entities, id, location, name,
        # pinned_tweet_id, profile_image_url, protected,
        # public_metrics, url, username, verified, and withheld
        url = "https://api.twitter.com/2/users/by?usernames={}&user.fields={}".format(username, ",".join(user_fields))
        json_response = self.connect_to_endpoint(url)
        if "data" not in json_response:
            print(f"json_response: {json_response}")
            raise Exception(f"json_response does not contain data")
        data = {"protected": json_response["data"][0].get("protected"),
                "verified": json_response["data"][0].get("verified"),
                "username": json_response["data"][0].get("username"),
                "followers_count": json_response["data"][0]["public_metrics"].get("followers_count"),
                "following_count": json_response["data"][0]["public_metrics"].get("following_count"),
                "tweet_count": json_response["data"][0]["public_metrics"].get("tweet_count"),
                "location": json_response["data"][0].get("location"),
                "description": json_response["data"][0].get("description"),
                "name": json_response["data"][0].get("name"),
                "created_at": json_response["data"][0].get("created_at"),
                "profile_image_url": json_response["data"][0].get("profile_image_url"),
                "id": json_response["data"][0].get("id")}
        return data

    def get_last_tweets(self, user_id: str, number_of_tweets: int,
                        fields: list[str] = None,
                        expansions: list[str] = None):
        # by default, we need:
        # - text
        # - image url
        # - number of likes
        # - number of retweets
        # - number of comments
        # - date
        if fields is None:
            fields = ['created_at',
                      'text',
                      'public_metrics',
                      'attachments']

        if expansions is None:
            expansions = ["attachments.media_keys"]
        url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results={number_of_tweets}" \
              f"&tweet.fields={','.join(fields)}" \
              f"&expansions={','.join(expansions)}" \
              f"&media.fields=url"
        json_response = self.connect_to_endpoint(url)
        # media_keys_to_url = {item["media_key"]: item["url"] for item in json_response["includes"]["media"]}
        media_keys_to_url = {}
        if "includes" in json_response and "media" in json_response["includes"]:
            for item in json_response["includes"]["media"]:
                media_keys_to_url[item["media_key"]] = item.get("url")
        data = []
        for tweet in json_response["data"]:
            data.append({"text": tweet["text"],
                         "number_of_likes": tweet["public_metrics"]["like_count"],
                         "number_of_retweets": tweet["public_metrics"]["retweet_count"],
                         "number_of_replies": tweet["public_metrics"]["reply_count"],
                         "number_of_quotes": tweet["public_metrics"]["quote_count"],
                         "date": tweet["created_at"],
                         "id": tweet["id"]})
            if "attachments" in tweet and "media_keys" in tweet["attachments"]:
                data[-1]["image_url"] = media_keys_to_url.get(tweet['attachments']["media_keys"][0])
            else:
                data[-1]["image_url"] = None
        return data


if __name__ == "__main__":
    from config import bearer_token

    user_id = "1524407286910930944"

    api = TwitterApi(bearer_token)
    # print(api.get_user("culturaltutor"))
    data = api.get_last_tweets(user_id, 10)
    print(*data, sep="\n--\n")
