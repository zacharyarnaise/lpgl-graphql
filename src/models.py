""" LPGL - IUT Metz
Zachary Arnaise
"""

from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation

Base = declarative_base()


class Person(Base):
    """Représente une personne."""

    __tablename__ = "person"
    id = Column(Integer, primary_key=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    dateOfBirth = Column(Date, nullable=False)
    dateOfDeath = Column(Date)

    career = relation("MoviePersons", back_populates="person")


class PersonRole(Base):
    """Représente les rôles qu'une personne peut avoir (acteur, ...)."""

    __tablename__ = "person_roles"
    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)


class MoviePersons(Base):
    """Lien entre `Movie` `Person`, `PersonRole` (relation many-to-many)."""

    __tablename__ = "movie_persons"
    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey("movie.id"), primary_key=True)
    person_id = Column(Integer, ForeignKey("person.id"), primary_key=True)
    person_role_id = Column(
        Integer, ForeignKey("person_roles.id"), nullable=False
    )

    movie = relation("Movie", back_populates="crew")
    person = relation("Person", back_populates="career")
    role = relation("PersonRole")


class MovieStatus(Base):
    """Représente l'état d'avancement d'un film."""

    __tablename__ = "movie_status"
    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)


class Movie(Base):
    """Représente un film."""

    __tablename__ = "movie"
    id = Column(Integer, primary_key=True)
    frenchTitle = Column(String, nullable=False)
    originalTitle = Column(String, nullable=False)
    statusId = Column(Integer, ForeignKey("movie_status.id"), nullable=False)
    status = relation("MovieStatus", foreign_keys=statusId)
    statusDate = Column(Date)
    crew = relation("MoviePersons", back_populates="movie")
