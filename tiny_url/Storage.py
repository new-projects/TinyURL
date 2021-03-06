import sqlalchemy as db
from colorama import Fore
from tiny_url.Configuration import Configuration


class Storage:
    def __init__(self, configuration: Configuration):
        self.engine = self._init_engine(configuration)
        self._init_datamodel()

    def add_link(self, tiny_url, full_url):
        try:
            with self.engine.connect() as connection:
                metadata = db.MetaData()
                url_mapping = db.Table('url_mapping', metadata, autoload=True, autoload_with=self.engine)
                statement = db.insert(url_mapping).values(tiny=tiny_url, full=full_url)
                connection.execute(statement)
        except Exception as e:
            print(Fore.RED + str(e) + Fore.RESET)

    def get_full(self, tiny_url):
        with self.engine.connect() as connection:
            metadata = db.MetaData()
            url_mapping = db.Table('url_mapping', metadata, autoload=True, autoload_with=self.engine)
            query = db.select([url_mapping.c.full]).where(url_mapping.c.tiny == tiny_url)
            result_proxy = connection.execute(query)
            result = result_proxy.fetchone()
            return result[0]

    def get_all_link(self):
        with self.engine.connect() as connection:
            metadata = db.MetaData()
            url_mapping = db.Table('url_mapping', metadata, autoload=True, autoload_with=self.engine)
            query = db.select([url_mapping])
            result_proxy = connection.execute(query)
            return result_proxy.fetchall()

    def _init_engine(self, configuration: Configuration):
        with open(configuration.postgres_secrets) as secrets:
            secrets = secrets.read().strip()
            # db.create_engine('dialect+driver://user:pass@host:port/db')
            return db.create_engine("postgresql://{secrets}@{postgres_host}/tiny_url".format(
                secrets=secrets, postgres_host=configuration.postgres_host))

    def _init_datamodel(self):
        with self.engine.connect():
            metadata = db.MetaData()
            if 'url_mapping' not in metadata:
                db.Table(
                    'url_mapping', metadata,
                    db.Column('tiny', db.String, primary_key=True),
                    db.Column('full', db.String)
                )
                metadata.create_all(self.engine)
