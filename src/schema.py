""" LPGL - IUT Metz
Zachary Arnaise
"""

import graphene

from models import Movie, MoviePersons, Person
from schema_mutations import CreateMovie, CreatePerson
from schema_types import MovieType, PersonType, SearchResult


class Query(graphene.ObjectType):
    """Query, objet principal pour les requêtes GraphQL.

    Attributes:
        person (graphene.Field): Champ permettant l'accès à une personne
        via son ID, prénom ou nom.
        movie (graphene.Field): Champ permettant l'accès à un film
        via son ID, titre français, titre original ou status.

        persons (graphene.List): Liste de toutes les personnes, sans filtrage.
        movies (graphene.List): Liste de tous les films.
        directors (graphene.List): Liste de toutes les personnes ayant au moins
        réalisé un film.
        actors (graphene.List): Liste de toutes les personnes ayant au moins
        joué dans un film.
        songWriters (graphene.List): Liste de toutes les personnes ayant au
        moins composé la musique d'un film.
        search (graphene.List): Liste de champs pour la fonction de recherche.
    """

    person = graphene.Field(
        PersonType,
        id=graphene.Argument(type=graphene.Int, required=False),
        firstName=graphene.Argument(type=graphene.String, required=False),
        lastName=graphene.Argument(type=graphene.String, required=False),
    )

    movie = graphene.Field(
        MovieType,
        id=graphene.Argument(type=graphene.Int, required=False),
        frenchTitle=graphene.Argument(type=graphene.String, required=False),
        originalTitle=graphene.Argument(type=graphene.String, required=False),
        status=graphene.Argument(type=graphene.String, required=False),
    )

    def resolve_person(parent: object, info: graphene.ResolveInfo, **kwargs):
        """Méthode qui cherche une personne selon un ou plusieurs critères."""
        query = PersonType.get_query(info=info)

        if "id" in kwargs:
            query = query.filter(Person.id == kwargs["id"])
        if "firstName" in kwargs:
            query = query.filter(Person.firstName == kwargs["firstName"])
        if "lastName" in kwargs:
            query = query.filter(Person.lastName == kwargs["lastName"])

        return query.first()

    def resolve_movie(parent: object, info: graphene.ResolveInfo, **kwargs):
        """Méthode qui cherche un film selon un ou plusieurs critères."""
        query = MovieType.get_query(info=info)

        if "id" in kwargs:
            query = query.filter(Movie.id == kwargs["id"])
        if "frenchTitle" in kwargs:
            query = query.filter(Movie.frenchTitle == kwargs["frenchTitle"])
        if "originalTitle" in kwargs:
            query = query.filter(Movie.frenchTitle == kwargs["originalTitle"])
        if "status" in kwargs:
            query = query.filter(Movie.status == kwargs["status"])

        return query.first()

    persons = graphene.List(PersonType)
    movies = graphene.List(MovieType)
    directors = graphene.List(PersonType)
    actors = graphene.List(PersonType)
    songWriters = graphene.List(PersonType)

    def resolve_persons(root: object, info: graphene.ResolveInfo, **kwargs):
        query = PersonType.get_query(info=info)
        return query.all()

    def resolve_movies(root: object, info: graphene.ResolveInfo, **kwargs):
        query = MovieType.get_query(info=info)
        return query.all()

    def resolve_directors(root: object, info: graphene.ResolveInfo, **kwargs):
        session = info.context["session"]
        return [
            res.person
            for res in session.query(MoviePersons)
            .filter_by(person_role_id=1)
            .group_by(MoviePersons.person_id)
            .all()
        ]

    def resolve_actors(root: object, info: graphene.ResolveInfo, **kwargs):
        session = info.context["session"]
        return [
            res.person
            for res in session.query(MoviePersons)
            .filter_by(person_role_id=2)
            .group_by(MoviePersons.person_id)
            .all()
        ]

    def resolve_songWriters(root: object, info: graphene.ResolveInfo, **kwargs):
        session = info.context["session"]
        return [
            res.person
            for res in session.query(MoviePersons)
            .filter_by(person_role_id=3)
            .group_by(MoviePersons.person_id)
            .all()
        ]

    search = graphene.List(SearchResult, q=graphene.String())

    def resolve_search(root: object, info: graphene.ResolveInfo, **kwargs):
        # Requête de recherche
        q = kwargs.get("q")

        # Recherche d'une personne
        personsQuery = PersonType.get_query(info)
        persons = personsQuery.filter(
            Person.firstName.contains(q) | Person.lastName.contains(q)
        ).all()
        # Recherche d'un film
        moviesQuery = MovieType.get_query(info)
        movies = moviesQuery.filter(
            Movie.frenchTitle.contains(q) | Movie.originalTitle.contains(q)
        ).all()

        return persons + movies


class Mutations(graphene.ObjectType):
    """Mutations, objet principal pour les mutations GraphQL."""

    create_person = CreatePerson.Field()
    create_movie = CreateMovie.Field()


class Subscription(graphene.ObjectType):
    """Subscription permettant de voir les nouveau film ajoutés."""

    new_movie = graphene.Field(MovieType)

    def resolve_new_movie(root: object, info: graphene.ResolveInfo):
        import ipdb

        ipdb.set_trace()
        return root.filter(
            lambda event: event.operation == CREATED
            and isinstance(event.instance, MovieType)
        ).map(lambda event: event.instance)


schema = graphene.Schema(
    query=Query,
    mutation=Mutations,
    subscription=Subscription,
    types=[
        PersonType,
        MovieType,
    ],
)
