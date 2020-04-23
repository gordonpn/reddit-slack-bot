import logging
import os
from typing import List

import praw
from praw import Reddit
from praw.models import ListingGenerator
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from ..reddit_post.reddit_post import RedditPost

logger = logging.getLogger("reddit_scraper")


class RedditScraper:
    def __init__(self):
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.username = os.getenv("REDDIT_USERNAME")
        self.password = os.getenv("REDDIT_PASSWORD")
        self.user_agent = "Python script written by @gordonpn on GitHub"
        self.db_name = os.getenv("MONGO_INITDB_DATABASE")
        self.db_username = os.getenv("MONGO_NON_ROOT_USERNAME")
        self.db_password = os.getenv("MONGO_NON_ROOT_PASSWORD")
        self.db_settings = os.getenv("MONGO_SETTINGS")
        self.db_collection = os.getenv("MONGO_COLLECTION")

    def run(self):
        db = self.connect_to_db()
        subscriptions = self.check_subscriptions(db)
        reddit = self.get_reddit()
        posts = self.scrape(reddit, subscriptions)
        self.update_db(db, posts)

    def get_reddit(self) -> Reddit:
        return praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            username=self.username,
            password=self.password,
            user_agent=self.user_agent,
        )

    def connect_to_db(self) -> Database:
        logger.debug("Making connection to mongodb")
        uri: str = f"mongodb://{self.db_username}:{self.db_password}@mongo-db:27017/{self.db_name}"
        connection: MongoClient = MongoClient(uri)
        db: Database = connection[self.db_name]
        return db

    def check_subscriptions(self, db: Database) -> List[str]:
        collection: Collection = db[self.db_settings]

        # todo get list of subreddits subscribed to and return said list

        return []

    def scrape(self, reddit: Reddit, subscriptions: List[str]) -> List[RedditPost]:
        limit: int = 5
        time_filter: str = "day"
        reddit_posts: List[RedditPost] = []

        for subscription in subscriptions:
            submissions: ListingGenerator = reddit.subreddit(subscription).top(
                limit=limit, time_filter=time_filter
            )
            for submission in submissions:
                if not submission.stickied:
                    title = submission.title
                    post_id = submission.id
                    votes = submission.score
                    link = submission.url
                    is_self = submission.is_self
                    unix_time = int(submission.created_utc)
                    logger.debug(f"Parsing: post_id={post_id}")
                    a_reddit_post = RedditPost(
                        title=title,
                        subreddit=subscription,
                        id=post_id,
                        votes=votes,
                        link=link,
                        unix_time=unix_time,
                        is_self=is_self,
                        seen=False,
                    )
                    reddit_posts.append(a_reddit_post)

        return reddit_posts

    def update_db(self, db: Database, posts):
        collection: Collection = db[self.db_collection]

        # todo insert data into collection
        # update if already exists
        # if using dataclass then
        # json_data = json.loads(reddit_post.to_json())

    def clean_up_old(self):
        # todo delete posts from collection that are older than two months
        pass
