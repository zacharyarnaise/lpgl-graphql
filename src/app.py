""" LPGL - IUT Metz
Zachary Arnaise
"""

import falcon
import sqlalchemy.orm

from resources import ResourceGraphQL

# Init ORM
engine = sqlalchemy.create_engine("sqlite:///../movies.db", echo=True)
sessionmaker = sqlalchemy.orm.sessionmaker(bind=engine)
scoped_session = sqlalchemy.orm.scoped_session(sessionmaker)

# Init serveur Falcon
app = falcon.API()
app.add_route(
    uri_template="/graphql",
    resource=ResourceGraphQL(scoped_session=scoped_session),
)
