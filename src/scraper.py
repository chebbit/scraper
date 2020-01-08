import feedparser
import requests
from time import mktime
from datetime import datetime
import hashlib
from tldextract import extract
from parsers import ReutersParser
from clients import PostgresClient, MongoClient
from filetypes import ABCType, CSVType


def save_to_file(data, filename=None):
    pass


class News:
    """
    A class for interacting with news, used as a container
    """

    def __init__(self, feed, title, short_description, posted, url):
        self.feed = feed
        self.title = title
        self.short_description = short_description
        self.posted = posted
        self.url = url
        self.full_description = None

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"(\"{self.title}\", \"{self.posted}\", \"{self.url}\")"

    @property
    def hash(self):
        # generate hash by news URL
        return (hashlib.sha1(self.url.encode("utf8")).hexdigest(),)

    def download_full_description(self):
        # download news body from news URL
        r = requests.get(self.url)
        if r.status_code == 200:
            body_parser = self.feed.body_news_parser
            self.full_description = body_parser.cleaned_data(r.text)


class Feed():

    """Class for working with rss, parsing and saving in the database"""

    def __init__(self, url, body_news_parser, database_client, schema=None, filetype: ABCType=None):
        self._url = url
        self.body_news_parser = body_news_parser
        # use domain name as name of schema if schema is None
        self._schema = schema or extract(url).domain
        database_client._schema = self._schema
        self._database_client = database_client
        self._news = []
        self._filetype = filetype or CSVType()

    @property
    def id(self):
        """return id when the id is None, get it from  database"""
        if not "_id" in self.__dict__:
            client = self._database_client
            feed = client.get_feed_by_url(url=self._url)
            self._id = feed.id
        return self._id

    @property
    def news(self):
        """return all news from URL at now"""
        if not self._news:
            self.parse()
        return self._news

    @property
    def only_new_news(self):
        """return only fresh news, in current realization based on DateTime last posted news"""
        last_date = self._database_client.get_last_posted_date()
        last_news = self.news
        if last_date:
            # filter only new news by posted date
            last_news = [news for news in self.news if news.posted > last_date]
        return last_news

    def parse(self):
        """parsing RSS by URL and save found items to ._news"""
        feed = feedparser.parse(self._url)
        news = []

        for item in feed.entries:
            news.append(
                News(
                    self,
                    item.title,
                    item.description,
                    datetime.fromtimestamp(mktime(item.published_parsed)),
                    item.link,
                )
            )

        self._news = news

    def save_news_to_db(self, by_user: bool = False) -> None:
        """ saving news to database, will be saved only new news"""
        client = self._database_client
        news = self.only_new_news
        client.save_scraper_info(
            (datetime.now(), len(news), by_user, self._url, self.id)
        )
        if news:
            # download fulltext description news by url for all item in list
            for n in self.news:
                n.download_full_description()

            client.save_news(news)
            print(f"{len(news)} news saved to the schema {self._schema}")
        else:
            print(f"no new news")

    def export_to_file(self, from_date=None, to_date=None, filename=None):
        """
        Get data from database and saves it to file
        """
        client = self._database_client
        news = client.get_news(from_date, to_date)
        print(f"exported {len(news)} news")
        self._filetype.save(news, filename)


    def run(self):
        self.parse()
        self.save_news_to_db()

