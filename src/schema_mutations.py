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


class MovieInput(graphene.InputObjectType):
    frenchTitle = graphene.String(required=True)
    originalTitle = graphene.String(required=True)
    status = graphene.String(required=True)
    statusDate = graphene.Date(required=True)


class CreateMovie(graphene.Mutation):
    class Arguments:
        movie_data = MovieInput(required=True)

    movie = graphene.Field(MovieType)

    def mutate(root: object, info: graphene.ResolveInfo, movie_data=None):
        session = info.context["session"]

        newMovie = models.Movie()
        newMovie.frenchTitle = movie_data.frenchTitle
        newMovie.originalTitle = movie_data.originalTitle
        # Recherche correspondance ID status
        for movieStatus in session.query(models.MovieStatus):
            if movieStatus.description == movie_data.status:
                newMovie.statusId = movieStatus.id
                break
        if not newMovie.statusId:
            raise RuntimeError

        # Ajout en base
        session.add(newMovie)
        session.commit()
        return CreateMovie(movie=newMovie)
