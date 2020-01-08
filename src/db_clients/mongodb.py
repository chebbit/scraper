import pymongo
from datetime import datetime
from typing import List
from .abc_client import DBClientABC, Feed, News


class MongoClient(DBClientABC):
    """
    Client for working with MongoDB
    """

    def __init__(self, host="mongo_scraper", port=27017, schema="rsscraper"):
        self._host = host
        self._port = port
        self._connection = None
        self._db = None
        self._schema = schema

    @property
    def connetion(self):
        if not self._connection:
            self._connection = pymongo.MongoClient()
        return self._connection

    @property
    def db(self):
        if not self._db:
            self.create_schema()
        return self._db

    def save_feed(self, url, parser=None):
        db = self.db
        feeds = db["feeds"]

        data = {"url": url, "parser": parser}
        result = feeds.insert_one(data)
        return result

    def get_feed_by_url(self, url):
        db = self.db
        feeds = db["feeds"]
        result = feeds.find_one({"url": url})
        print(f"result={result}")
        if not result:
            result = self.save_feed(url)
        return Feed(result["_id"], result["url"], result["parser"])

    def save_news(self, news) -> None:
        db = self.db
        collection = db["news"]
        data = [
            {
                "feed_id": n.feed.id,
                "title": n.title,
                "short_description": n.short_description,
                "posted": n.posted,
                "url": n.url,
                "hash": n.hash,
                "full_description": n.full_description,
            }
            for n in news
        ]
        result = collection.insert_many(data)

    def get_news(self, from_date: datetime = None, to_date: datetime = None ) -> List[News]:
        db = self.db
        news = db["news"]
        result = []

        if from_date and to_date:
            documents = news.find({'posted': {'$lt': to_date, '$gt': from_date}})
        elif to_date:
            documents = news.find({'posted': {'$lt': to_date}})
        elif from_date:
            documents = news.find({'posted': {'$gt': from_date}})
        else:
            documents = news.find()

        for n in documents:
            result.append(
                News(
                    n["title"],
                    n["short_description"],
                    n["posted"],
                    n["url"],
                    n["hash"],
                    n["full_description"],
                )
            )
        return result

    def create_schema(self, name: str = None) -> None:
        if name:
            self._schema = name

        if not self._db:
            conn = self.connetion
            self._db = conn[f"{self._schema}"]
        return self._db

    def save_scraper_info(self, scraper_info, by_user=False):
        db = self.db
        scraper = db["scraper_info"]
        data = {
            "run_date": scraper_info[0],
            "count": scraper_info[1],
            "by_user": scraper_info[2],
            "url": scraper_info[3],
            "feed_id": str(scraper_info[4]),
        }
        scraper.insert_one(data)

    def get_last_posted_date(self):
        db = self.db
        news = db["news"]
        last_dt = None
        try:
            last_dt = (
                news.find().sort("posted", pymongo.DESCENDING).limit(1)[0]["posted"]
            )
        except IndexError:
            pass
        print(f"last_dt={last_dt}")
        return last_dt


if __name__ == "__main__":
    pass
