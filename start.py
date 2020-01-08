import click

"""
      - Start the database server

      - Create schema

      - Run the scraper

      - Retrieve data for a specific date (output-> CSV file)
"""

def start_database(type='postgres'):
    """Start database server"""
    print(f"Start {type} database")
    pass

def create_schema(name):
    """Create schema in strarted database and checkout scraper to this schema"""
    pass

def run_scraper():
    """Run scraper"""
    pass

def get_data(from_date=None, to_date=None):
    pass

if __name__ == '__main__':
    start_database()