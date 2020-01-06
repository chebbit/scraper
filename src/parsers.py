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

    headline_tag = ('h1', {'class': 'ArticleHeader_headline'})
    body_tag = ('div', {'class': 'StandardArticleBody_body'})

    garbage_tags = [
        ('div', {'class': 'RelatedCoverage_related-coverage-module'}),
    ]

    @classmethod
    def cleaned_data(cls, text: str) -> str:
        """
        return clean text news body
        """
        soup = BeautifulSoup(text, features="html.parser")

        # cleaned target text from unused tags
        for tag in cls.garbage_tags:
            garbage_tag = soup.find(*tag)
            if garbage_tag:
                garbage_tag.clear()

        headline = soup.find(*cls.headline_tag)
        body = soup.find(*cls.body_tag)
        parser = HTML2Text()
        parser.ignore_images = True
        parser.ignore_links = True
        cleaned_data = parser.handle(str(headline) + str(body))
        return cleaned_data
