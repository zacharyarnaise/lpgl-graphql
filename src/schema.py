""" LPGL - IUT Metz
Zachary Arnaise
"""

import graphene
from schema_types import PersonType


class Query(graphene.ObjectType):
    """Query, objet principal GraphQL.
    """

    person = graphene.Field(PersonType)

    def resolve_person(parent: object, info: graphene.ResolveInfo):
        return PersonType(id=1337, test="foobar")


schema = graphene.Schema(
    query=Query,
    types=[
        PersonType,
    ],
)
