from abc import ABC, abstractmethod
from collections import namedtuple

# tuple for visual using data get from db
Feed = namedtuple('Feed', ['id', 'url', 'parser'])

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
    def get_news(self) -> dict:
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
