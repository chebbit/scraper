import psycopg2
from .abc_client import DBClientABC, Feed

class PostgresClient(DBClientABC):
    """
    Client for working with PostgresDB
    """

    def __init__(
        self,
        dbname="postgres",
        user="postgres",
        password="alabama",
        host="localhost",
        schema="rsscraper",
    ):
        self._dbname = dbname
        self._host = host
        self._password = password
        self._user = user
        self._schema = schema
        self._connection = None

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

    def get_news(self, from_date=None, to_date=None) -> dict:
        SQL = f"""
              SELECT id, feed_id, title, short_description, posted, url, hash, full_description 
              FROM {self._schema}.news
              """
        conn = self._get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(SQL)
                return cur.fetchall()

    def get_last_posted_date(self):
        SQL = f"select max(n.posted) from {self._schema}.news n"
        conn = self._get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(SQL)
                (max_date,) = cur.fetchone()
                return max_date

    def create_schema(self, name: str = None) -> None:
        if name:
            self._schema = name

        print(f"schema={name}")
        conn = self._get_connection()
        # print(conn)
        #
        # cur = conn.cursor()

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
            posted date NULL,
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
