""" LPGL - IUT Metz
Zachary Arnaise
"""

import graphene


class PersonType(graphene.ObjectType):
    id = graphene.ID()
    test = graphene.String()
