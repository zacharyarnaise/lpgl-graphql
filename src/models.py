""" LPGL - IUT Metz
Zachary Arnaise
"""

from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import UniqueConstraint, relation

Base = declarative_base()


class Person(Base):
    """Représente une personne."""

    __tablename__ = "person"
    id = Column(Integer, primary_key=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    dateOfBirth = Column(Date, nullable=False)
    dateOfDeath = Column(Date)


class PersonRole(Base):
    """Représente les rôles qu'une personne peut avoir (acteur, réalisateur, ...)."""

    __tablename__ = "person_roles"
    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    movie_persons = relation("MoviePersons", back_populate="PersonRole")


class MoviePersons(Base):
    """Lien entre `Movie` `Person`, `PersonRole` (relation many-to-many)."""

    __tablename__ = "movie_persons"
    id = Column(Integer, primary_key=True)

    movie = relation("Movie", back_populates="MoviePersons")
    movieId = Column(Integer, ForeignKey("movie.id"), nullable=False)

    person = relation("Person")
    personId = Column(Integer, ForeignKey("device.id"), nullable=False)

    role = relation("PersonRole", back_populates="MoviePersons")
    roleId = Column(Integer, ForeignKey("person_roles.id"), nullable=False)

    __table_args__ = (UniqueConstraint(movieId, personId, roleId),)


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
    movie_persons = relation("MoviePersons", back_populate="Movie")
