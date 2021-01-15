""" LPGL - IUT Metz
Zachary Arnaise
"""

import graphene
import sqlalchemy.orm

import models
from schema_types import MovieType, PersonType


class PersonInput(graphene.InputObjectType):
    firstName = graphene.String(required=True)
    lastName = graphene.String(required=True)
    dateOfBirth = graphene.Date(required=True)
    dateOfDeath = graphene.Date(required=False, default_value=None)


class CreatePerson(graphene.Mutation):
    class Arguments:
        person_data = PersonInput(required=True)

    person = graphene.Field(PersonType)

    def mutate(root: object, info: graphene.ResolveInfo, person_data=None):
        session = info.context["session"]

        newPerson = models.Person()
        newPerson.firstName = person_data.firstName
        newPerson.lastName = person_data.lastName
        newPerson.dateOfBirth = person_data.dateOfBirth
        if person_data.dateOfDeath is not None:
            newPerson.dateOfDeath = person_data.dateOfDeath

        # Ajout en base
        session.add(newPerson)
        session.commit()
        return CreatePerson(person=newPerson)
