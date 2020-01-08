import csv
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod
from typing import List
from db_clients.abc_client import News


class ABCType(ABC):
    """An abstract class with a single method, for saving news to file"""

    @abstractmethod
    def save(cls, news: List[News], filename: str = None) -> None:
        pass


class CSVType(ABCType):
    def save(self, news: List[News], filename=None):
        """
        Save data to file
        """

        if not filename:
            # saves the file to the default folder ../output
            path = Path(__file__).parent.parent.joinpath("output")
            filename = path.joinpath(
                f"output_news_{datetime.now().timestamp()}.csv"
            ).absolute()

        with open(filename, "w") as csvfile:
            writer = csv.writer(csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            # for a header use fields from 'News'
            writer.writerow(list(News._fields))
            writer.writerows(news)


if __name__ == "__main__":
    # from db_clients.postgres import PostgresClient
    # client=database_client=PostgresClient(host='localhost', schema='test')
    # news = client.get_news()
    # path = Path(__file__).parent.parent.joinpath("output")
    # CSVType().save(news)
    pass

