import click
import os

@click.group()
def cli():
    pass


@click.command()
@click.option('--type', default='postgres', help='The type of database')
def start_server(type):
    """Start server database and scraper"""
    cmd = ['docker-compose build', 'docker-compose -f docker-compose.yml up -d']
    for c in cmd:
        os.system(c)
    click.echo(f"Start project with {type} database")

@click.command()
@click.argument('name')
def create_schema(name):
    """Create schema and change scraper to new schema"""
    cmd = f'docker-compose exec scraper /usr/local/bin/python /app/cli.py create-schema {name}'
    os.system(cmd)

@click.command()
def run_scraper():
    """Run scraper"""
    cmd = f'docker-compose exec scraper /usr/local/bin/python /app/cli.py run-scraper'
    os.system(cmd)

@click.command()
@click.option('--start', default=None, help="Start period fo select data string in format <YYYY-MM-DD HH24:MI:SS> ")
@click.option('--end', default=None, help="End period fo select data string in format <YYYY-MM-DD HH24:MI:SS> ")
@click.option('--schema', default=None, help='Name of the database where the data will be saved')
@click.option('--filename', default=None, help='Name for export file')
def export(start, end, schema, filename):
    """Export data to CSV, the data will be saved in the folder 'output'"""
    cmd = f'docker-compose exec scraper /usr/local/bin/python /app/cli.py export '
    if start:
        cmd = cmd + f" --start '{start}' "
    if end:
        cmd = cmd + f" --end '{end}' "
    if schema:
        cmd = cmd + f" --schema '{schema}' "
    if filename:
        cmd = cmd + f" --filename '{filename}' "
    os.system(cmd)
    print(cmd)

@click.command()
def stop_server():
    """Stop server"""
    cmd = "docker-compose -f docker-compose.yml down"
    os.system(cmd)


cli.add_command(start_server)
cli.add_command(create_schema)
cli.add_command(run_scraper)
cli.add_command(export)
cli.add_command(stop_server)

if __name__ == '__main__':
    cli()