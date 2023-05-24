drop table if exists tweets;
drop table if exists users cascade ;
drop table if exists unprocessed_users;
drop function if exists increment_user_tweets_count();
drop function if exists find_the_users_with_incomplete_tweets(int);

create table if not exists unprocessed_users(
    id serial primary key,
    username varchar(255) not null unique);

create table if not exists users (
    id                       serial primary key,
    twitter_id               varchar(255)  not null unique,
    profile_image_url        varchar(255)  not null,
    location_                varchar(255),
    description              varchar,
    verified                 boolean       not null,
    username                 varchar(255)  not null unique,
    link_page                varchar(255)  generated always as ('https://twitter.com/' || username) stored,
    number_of_followers      int           not null,
    number_of_following      int           not null,
    is_finished              boolean       not null default false,
    number_of_fetched_tweets int default 0 not null);


create table tweets (
    id                 serial primary key,
    tweet_id           varchar(255) not null unique,
    tweet_text         varchar,
    image_url          varchar(255),
    tweet_date         varchar(255) not null,
    user_id            varchar(255) references users (twitter_id) on delete cascade,
    number_of_likes    int          not null,
    number_of_retweets int          not null,
    number_of_replies  int          not null,
    number_of_quotes   int          not null);
create or replace function increment_user_tweets_count()
    returns trigger
    language plpgsql
as
$$
begin
    update users
    set number_of_fetched_tweets = number_of_fetched_tweets + 1
    where twitter_id = NEW.user_id;
    return NEW;
end;
$$;

create trigger update_user_tweets_count
    after insert
    on tweets
    for each row
execute function increment_user_tweets_count();
