from bs4 import BeautifulSoup
from html2text import HTML2Text
from abc import ABC, abstractmethod


class ABCParser(ABC):
    """An abstract class with a single method, for cleaning data from HTML"""

    @classmethod
    @abstractmethod
    def cleaned_data(cls, text: str) -> str:
        pass

class ReutersParser(ABCParser):
    """
    Class for parsing body news at reuters.com
    """

    headline_block = ('h1', {'class': 'ArticleHeader_headline'})
    body_block = ('div', {'class': 'StandardArticleBody_body'})

    garbage_blocks = [
        ('div', {'class': 'RelatedCoverage_related-coverage-module'}),
    ]

    @classmethod
    def cleaned_data(cls, text: str) -> str:
        """
        return clean text news body
        """
        soup = BeautifulSoup(text, features="html.parser")

        # clear target text from unused blocks
        for b in cls.garbage_blocks:
            block = soup.find(*b)
            if block:
                block.clear()

        headline = soup.find(*cls.headline_block)
        body = soup.find(*cls.body_block)
        # use to clear HTML tags
        parser = HTML2Text()
        parser.ignore_images = True
        parser.ignore_links = True
        data = parser.handle(str(headline) + str(body))
        return data
