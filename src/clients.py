import psycopg2
import pymongo
from abc import ABC, abstractmethod
from collections import namedtuple
from typing import List
from datetime import datetime

# tuple for visual using data get from db
Feed = namedtuple("Feed", ["id", "url", "parser"])
News = namedtuple("News", ['title', 'short_description', 'posted', 'url', 'hash', 'full_description'])

class DBClientABC(ABC):
    """
    Class for implementation clients for work with different databases
    """

    @abstractmethod
    def save_feed(self, url, parser=None):
        pass

    @abstractmethod
    def get_feed_by_url(self, url) -> Feed:
        pass

    @abstractmethod
    def save_news(self, data) -> None:
        pass

    @abstractmethod
    def get_news(self, from_date: datetime = None, to_date: datetime = None ) -> List[News]:
        pass

    @abstractmethod
    def create_schema(self, name: str) -> None:
        pass

    @abstractmethod
    def save_scraper_info(self, scraper_info, by_user=False):
        pass

    @abstractmethod
    def get_last_posted_date(self):
        pass


class PostgresClient(DBClientABC):
    """
    Client for working with PostgresDB
    """

    def __init__(
            self,
            dbname="postgres",
            user="postgres",
            password="scraper",
            host="db",
            schema="rsscraper",
    ):
        self._dbname = dbname
        self._host = host
        self._password = password
        self._user = user
        self._schema = schema
        self._connection = None

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"{self.__class__.__name__}({self._dbname}, {self._host}, ******, {self._user}, {self._schema})"

    def _get_connection(self):
        if not self._connection:
            conn = psycopg2.connect(
                user=self._user, password=self._password, host=self._host
            )
            self._connection = conn
        return self._connection

    def save_feed(self, url, parser=None) -> Feed:
        conn = self._get_connection()

        SQL_INSERT_FEED = f"""
        INSERT INTO {self._schema}.feeds
        (url, body_parser)
        VALUES(%s, %s) RETURNING id;
        """

        with conn:
            with conn.cursor() as cur:
                cur.execute(SQL_INSERT_FEED, (url, parser))
                (id,) = cur.fetchone()
                return Feed(id, url, parser)

    def get_feed_by_url(self, url, **kwargs):
        conn = self._get_connection()

        SQL_SELECT_FEED = f"""
        SELECT id, url, body_parser FROM {self._schema}.feeds as f
        WHERE f.url = %s
        """

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(SQL_SELECT_FEED, (url,))
                    row = cur.fetchone()
                    if row:
                        id, url, parser = row
                        return Feed(id, url, parser)
                    else:
                        return self.save_feed(
                            url=url, parser=kwargs.get("parser", None)
                        )
        except psycopg2.errors.UndefinedTable:
            self.create_schema()
            return self.save_feed(url=url, parser=kwargs.get("parser", None))

    def save_news(self, news) -> None:

        SQL_INSERT_NEWS = f"""
        INSERT INTO {self._schema}.news
        (feed_id, title, short_description, posted, url, hash, full_description)
        VALUES(%s, %s, %s, %s, %s, %s, %s);
        """

        conn = self._get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.executemany(
                    SQL_INSERT_NEWS,
                    [
                        (
                            n.feed.id,
                            n.title,
                            n.short_description,
                            n.posted,
                            n.url,
                            n.hash,
                            n.full_description,
                        )
                        for n in news
                    ],
                )

    def save_scraper_info(self, scraper_info, by_user=False):

        SQL = f"""INSERT INTO {self._schema}.scraper_info
                (date_run, count, by_user, url, feed_id)
                VALUES(%s, %s, %s, %s, %s);
                """
        conn = self._get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(SQL, scraper_info)

    def get_news(
            self, from_date: datetime = None, to_date: datetime = None
    ) -> List[News]:
        SQL = f"""
              SELECT title, short_description, posted, url, hash, full_description 
              FROM {self._schema}.news
              """
        # generate a condition where if select dates
        WHERE = None

        if from_date and to_date:
            WHERE = f"\nWHERE posted between  TO_TIMESTAMP('{from_date.strftime('%Y-%m-%d %H:%M:%S')}', 'YYYY-MM-DD HH24:MI:SS') and TO_TIMESTAMP('{to_date.strftime('%Y-%m-%d %H:%M:%S')}', 'YYYY-MM-DD HH24:MI:SS') "
        elif from_date:
            WHERE = f"\nWHERE posted >= TO_TIMESTAMP('{from_date.strftime('%Y-%m-%d %H:%M:%S')}', 'YYYY-MM-DD HH24:MI:SS')"
        elif to_date:
            WHERE = f"\nWHERE posted <= TO_TIMESTAMP('{to_date.strftime('%Y-%m-%d %H:%M:%S')}', 'YYYY-MM-DD HH24:MI:SS')"

        if WHERE:
            SQL = SQL + WHERE

        conn = self._get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(SQL)
                result = cur.fetchall()
                return [News(*r) for r in result]

    def get_last_posted_date(self):
        max_date = None
        self.create_schema()
        SQL = f"select max(n.posted) from {self._schema}.news n"
        conn = self._get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(SQL)
                (max_date,) = cur.fetchone()
                return max_date

    def create_schema(self, name: str = None) -> None:
        """
        Creates a new schema if the schema exists do nothing
        """
        if name:
            self._schema = name

        conn = self._get_connection()

        DDL = f"""
        -- DROP SCHEMA {self._schema};

        CREATE SCHEMA {self._schema} AUTHORIZATION postgres;


        -- Drop table

        -- DROP TABLE {self._schema}.feeds;

        CREATE TABLE  {self._schema}.feeds (
            id serial NOT NULL,
            url varchar NULL,
            body_parser varchar NULL,
            CONSTRAINT feeds_pk PRIMARY KEY (id)
        );
        CREATE INDEX feeds_url_idx ON {self._schema}.feeds USING btree (url);

        -- Drop table

        -- DROP TABLE {self._schema}.scraper_info;

        CREATE TABLE  {self._schema}.scraper_info (
            id serial NOT NULL,
            date_run date NULL,
            count int4 NULL,
            by_user bool NULL DEFAULT false,
            url varchar NULL,
            feed_id int4 NULL,
            CONSTRAINT scraper_info_pk PRIMARY KEY (id),
            CONSTRAINT scraper_info_fk FOREIGN KEY (feed_id) REFERENCES {self._schema}.feeds(id)
        );

        -- Drop table

        -- DROP TABLE {self._schema}.news;

        CREATE TABLE {self._schema}.news (
            id serial NOT NULL,
            feed_id int4 NOT NULL,
            title varchar NULL,
            short_description varchar NULL,
            posted timestamp NULL,
            url varchar NULL,
            hash varchar NULL,
            full_description text NULL,
            CONSTRAINT news_pk PRIMARY KEY (id),
            CONSTRAINT news_fk FOREIGN KEY (feed_id) REFERENCES {self._schema}.feeds(id) ON UPDATE CASCADE ON DELETE CASCADE
        );
        """
        with conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(DDL)
                    conn.commit()
                except psycopg2.errors.DuplicateSchema:
                    pass

    def close(self):
        conn = self._get_connection()

        if not conn.closed:
            conn.close()


class MongoClient(DBClientABC):
    """
    Client for working with MongoDB
    """

    def __init__(self, host="db", port=27017, schema="rsscraper"):
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
        if not result:
            resp = self.save_feed(url)
            return Feed(resp.inserted_id, "url", None)
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
        return last_dt


if __name__ == "__main__":
    pass

