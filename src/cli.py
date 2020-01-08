import os
import io
import configparser

import click
from scraper import Feed
from clients import PostgresClient, MongoClient
from parsers import ReutersParser
from datetime import datetime
from collections import namedtuple

CONFIG_FILE = "config.ini"

def create_config(path):
    """
    Create a config file
    """
    cfgfile = open(path, 'w')
    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "parser", "ReutersParser")
    config.set("Settings", "client", "PostgresClient")
    config.set("Settings", "schema", "")
    config.write(cfgfile)
    cfgfile.close()

def crud_config(path):
    """
    Create, read, update, delete config
    """
    if not os.path.exists(path):
        create_config(path)

    config = configparser.ConfigParser()
    config.read(path)

    # Read from config file
    parser = config.get("Settings", "parser")
    client = config.get("Settings", "client")
    schema = config.get("Settings", "schema")

    Setting = namedtuple('Settings', ['parser', 'client', 'schema'])

    return Setting(parser, client, schema)

def change_setting(path, section, value):
    config = configparser.ConfigParser()
    config.read(path)
    config.set("Settings", section, value)
    with open(path, "w") as config_file:
        config.write(config_file)


@click.group()
def cli():
    pass

@click.command()
@click.option('--client', default=None, help="The database client that will be used for the scraper, 'PostgresClient' or 'MongoClient' ")
@click.option('--schema', default=None, help='Name of the database where the data will be saved')
def run_scraper(client, schema):
    """Run scraper"""
    if schema:
        change_setting(CONFIG_FILE, 'schema', schema)
    if client:
        change_setting(CONFIG_FILE, 'client', schema)
    setting = crud_config(CONFIG_FILE)
    client = eval(setting.client)()
    parser = eval(setting.parser)()
    schema = setting.schema
    f = Feed(
        url="http://feeds.reuters.com/reuters/topNews",
        body_news_parser=parser,
        database_client=client,
        schema=schema
    )
    f.run()
    click.echo('scraper has been run')

@click.command()
@click.option('--start', default=None, help="Start period fo select data string in format <YYYY-MM-DD HH24:MI:SS> ")
@click.option('--end', default=None, help="End period fo select data string in format <YYYY-MM-DD HH24:MI:SS> ")
@click.option('--schema', default=None, help='Name of the database where the data will be saved')
@click.option('--filename', default=None, help='Name for export file')
def export(start, end, schema, filename):
    """
    Export data to csv
    """
    if schema:
        change_setting(CONFIG_FILE, 'schema', schema)
    setting = crud_config(CONFIG_FILE)
    schema = setting.schema
    client = eval(setting.client)()
    parser = eval(setting.parser)()
    dt_start = None
    if start:
        dt_start = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')

    dt_end = None
    if end:
        dt_end = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')

    f = Feed(
        url="http://feeds.reuters.com/reuters/topNews",
        body_news_parser=parser,
        database_client=client,
        schema=schema
    )
    f.export_to_file(from_date=dt_start, to_date=dt_end, filename=filename)


@click.command()
@click.argument('name')
def create_schema(name):
    """
    Create schema and change scraper to new schema
    """
    change_setting(CONFIG_FILE, 'schema', name)
    setting = crud_config(CONFIG_FILE)
    client = eval(setting.client)()
    client.create_schema(name)

cli.add_command(run_scraper)
cli.add_command(export)
cli.add_command(create_schema)

if __name__ == '__main__':
    cli()