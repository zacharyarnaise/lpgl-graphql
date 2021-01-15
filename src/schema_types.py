""" LPGL - IUT Metz
Zachary Arnaise
"""

import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

from models import Movie, Person


class PersonType(SQLAlchemyObjectType):
    """
    type Person {
        id : ID
        firstName : String
        lastName : String
        fullName : String
        dateOfBirth : Date
        dateOfDeath : Date
        directed : [Movie]
        playedIn : [Movie]
        composed : [Movie]
    }
    """

    class Meta:
        model = Person

    fullName = graphene.String()
    directed = graphene.List(of_type=lambda: MovieType)
    playedIn = graphene.List(of_type=lambda: MovieType)
    composed = graphene.List(of_type=lambda: MovieType)

    def resolve_fullName(parent: object, info: graphene.ResolveInfo):
        # Nom complet à partir du prénom + nom de famille
        return f"{parent.firstName} {parent.lastName}"

    def resolve_directed(parent: object, info: graphene.ResolveInfo):
        return [
            assoc.movie
            for assoc in parent.career
            if assoc.role.description == "réalisateur"
        ]

    def resolve_playedIn(parent: object, info: graphene.ResolveInfo):
        return [
            assoc.movie for assoc in parent.career if assoc.role.description == "acteur"
        ]

    def resolve_composed(parent: object, info: graphene.ResolveInfo):
        return [
            assoc.movie
            for assoc in parent.career
            if assoc.role.description == "compositeur"
        ]


class MovieType(SQLAlchemyObjectType):
    """
    type Movie {
        id : ID
        frenchTitle : String
        originalTitle : String
        status : String
        statusDate : Date
        directors : [Person]
        actors : [Person]
        songWriters : [Person]
    }
    """

    class Meta:
        model = Movie
        fields = (
            "id",
            "frenchTitle",
            "originalTitle",
            "statusDate",
        )
        exclude_fields = ("statusId",)

    status = graphene.String()
    directors = graphene.List(of_type=PersonType)
    actors = graphene.List(of_type=PersonType)
    songWriters = graphene.List(of_type=PersonType)

    def resolve_status(parent: object, info: graphene.ResolveInfo):
        return parent.status.description

    def resolve_directors(parent: object, info: graphene.ResolveInfo):
        return [
            assoc.person
            for assoc in parent.crew
            if assoc.role.description == "réalisateur"
        ]

    def resolve_actors(parent: object, info: graphene.ResolveInfo):
        return [
            assoc.person for assoc in parent.crew if assoc.role.description == "acteur"
        ]

    def resolve_songWriters(parent: object, info: graphene.ResolveInfo):
        return [
            assoc.person
            for assoc in parent.crew
            if assoc.role.description == "compositeur"
        ]


class SearchResult(graphene.Union):
    class Meta:
        types = (PersonType, MovieType)
