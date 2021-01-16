""" LPGL - IUT Metz
Zachary Arnaise
"""

import sys
import os.path
import falcon
import sqlalchemy.orm

from resources import ResourceGraphQL
from schema import schema


if not os.path.isfile("/db/movies.db"):
    print("ERREUR: Accès à la db SQLite impossible, aucun fichier trouvé.")
    sys.exit(1)

# Init ORM
engine = sqlalchemy.create_engine("sqlite:////db/movies.db", echo=True)
sessionmaker = sqlalchemy.orm.sessionmaker(bind=engine)
scoped_session = sqlalchemy.orm.scoped_session(sessionmaker)

# Init serveur Falcon
app = falcon.API()
app.add_route(
    uri_template="/graphql",
    resource=ResourceGraphQL(schema=schema, scoped_session=scoped_session),
)
