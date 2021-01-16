Serveur GraphQL - TD
===========
Projet de serveur GraphQL, développé en [Python](https://www.python.org/) :snake: et avec le framework [Falcon](https://falconframework.org/) :eagle:

Réalisé dans le cadre d'un TD en cours d'applications réparties, en Licence pro Métiers du génie logiciel à l'IUT de Metz.

---

### Utilisation
* Installer [Docker](https://www.docker.com/) sur votre machine
* Cloner le repository: `git clone https://github.com/zacharyarnaise/lpgl-graphql.git`
* Ouvrir un terminal à la racine du projet puis lancer le serveur avec la commande:
```shell
docker-compose up
```
* Le serveur GraphQL est accessible à l'adresse suivante: `http://localhost:8000/graphql`

---

### Fonctionnalités
<details>
<summary>Query qui remonte tous les films</summary>
  
Note: certains détails sont omis, voir la requête qui permet de remonter un film en fonction de son ID pour se faire une idée de tout ce qu'on peut avoir comme data avec un film.

```graphql
{
    movies {
      id
      frenchTitle
      originalTitle
      status
      statusDate
    }
}
```

**Résultat:**
```graphql
{
  "data": {
    "movies": [
      {
        "id": "1",
        "frenchTitle": "El Camino : Un film Breaking Bad",
        "originalTitle": "El Camino: A Breaking Bad Movie",
        "status": "sortie",
        "statusDate": "2019-10-11"
      },
      . . .
```
</details>
<details>
<summary>Query qui remonte toutes les personnes</summary>

```graphql
{
    persons {
      id
      fullName
      dateOfBirth
      dateOfDeath
    }
}
```

**Résultat:**
```graphql
{
  "data": {
    "persons": [
      {
        "id": "1",
        "fullName": "Alain Chabbat",
        "dateOfBirth": "1958-11-24",
        "dateOfDeath": null
      },
      {
        "id": "2",
        "fullName": "Gérard Depardieu",
        "dateOfBirth": "1948-12-27",
        "dateOfDeath": null
      },
      . . .
```
</details>
<details>
<summary>Query qui remonte tous les réalisateurs/acteurs/compositeurs</summary>
  
Pour remonter tous les acteurs il faudra utiliser `actors` et pour les compositeurs ce sera `songWriters`.

```graphql
{
    directors {
      id
      fullName
      dateOfBirth
      dateOfDeath
    }
}
```

**Résultat:**
```graphql
{
  "data": {
    "directors": [
      {
        "id": "1",
        "fullName": "Alain Chabbat",
        "dateOfBirth": "1958-11-24",
        "dateOfDeath": null
      },
      {
        "id": "5",
        "fullName": "Vince Gilligan",
        "dateOfBirth": "1967-02-10",
        "dateOfDeath": null
      },
      . . .
```
</details>
<details>
<summary>Query qui remonte un film selon son ID</summary>

```graphql
{
  movie(id: 7) {
    frenchTitle
    originalTitle
    status
    statusDate
    actors {
      id
      fullName
    }
    directors {
      id
      fullName
    }
    songWriters {
      id
      fullName
    }
  }
}
```

**Résultat:**
```graphql
{
  "data": {
    "movie": {
      "frenchTitle": "Le Cinquième Élément",
      "originalTitle": "The Fifth Element",
      "status": "sortie",
      "statusDate": "1997-05-07",
      "actors": [
        {
          "id": "23",
          "fullName": "Bruce Willis"
        },
        {
          "id": "24",
          "fullName": "Milla Jovovich"
        },
        {
          "id": "25",
          "fullName": "Gary Oldman"
        }
      ],
      "directors": [
        {
          "id": "22",
          "fullName": "Luc Besson"
        }
      ],
      "songWriters": [
        {
          "id": "21",
          "fullName": "Éric Serra"
        }
      ]
    }
  }
}
```
</details>
<details>
<summary>Query qui remonte une personne selon son ID</summary>

```graphql
{
  person(id: 1) {
    firstName
    lastName
    fullName
    dateOfBirth
    dateOfDeath
    directed {
      id
      frenchTitle
    }
    playedIn {
      id
      frenchTitle
    }
    composed {
      id
      frenchTitle
    }
  }
}
```

**Résultat:**
```graphql
{
  "data": {
    "person": {
      "firstName": "Alain",
      "lastName": "Chabbat",
      "fullName": "Alain Chabbat",
      "dateOfBirth": "1958-11-24",
      "dateOfDeath": null,
      "directed": [
        {
          "id": "1",
          "frenchTitle": "RRRrrrr!!!"
        }
      ],
      "playedIn": [
        {
          "id": "1",
          "frenchTitle": "RRRrrrr!!!"
        }
      ],
      "composed": []
    }
  }
}
```
</details>
<details>
<summary>Mutation pour ajouter une personne</summary>

```graphql
mutation testMutationPerson {
  createPerson(personData: {firstName: "Chantal", lastName: "Lauby", dateOfBirth: "1948-03-23"}) {
    person {
      fullName
      dateOfBirth
	  dateOfDeath
    }
  }
}
```

**Résultat:**
```graphql
{
  "data": {
    "createPerson": {
      "person": {
        "id": "31",
        "fullName": "Chantal Lauby",
        "dateOfBirth": "1948-03-23"
		"dateOfDeath": null
      }
    }
  }
}
```
</details>
<details>
<summary>Mutation pour ajouter un film</summary>

```graphql
mutation testMutationMovie {
  createMovie(movieData: {frenchTitle: "La Cité de la peur", originalTitle: "La Cité de la peur", status: "sortie", statusDate: "1994-03-04"}) {
    movie {
      id
      frenchTitle
      status
      statusDate
    }
  }
}
```

**Résultat:**
```graphql
{
  "data": {
    "createMovie": {
      "movie": {
        "id": "9",
        "frenchTitle": "La Cité de la peur",
        "status": "sortie",
        "statusDate": "1994-03-04"
      }
    }
  }
}
```
</details>
<details>
<summary>Query search</summary>
  
Note: la recherche fonctionne avec le prénom et nom des personnes et le titre en français et le titre original des films.

```graphql
{
  search(q: "arr") {
    __typename
    ... on PersonType {
      fullName,
      dateOfBirth,
      dateOfDeath
    }
    ... on MovieType {
      frenchTitle,
      originalTitle,
      status,
      statusDate
    }
  }
}
```

**Résultat:**
```graphql
{
  "data": {
    "search": [
      {
        "__typename": "PersonType",
        "fullName": "Dominique Farrugia",
        "dateOfBirth": "1962-09-02",
        "dateOfDeath": null
      },
      {
        "__typename": "MovieType",
        "frenchTitle": "Arrête-moi si tu peux",
        "originalTitle": "Catch Me If You Can",
        "status": "sortie",
        "statusDate": "2002-12-16"
      }
    ]
  }
}
```
</details>
<details>
<summary>Subscription</summary>

```graphql
subscription {
  newMovie {
    id
    frenchTitle
  }
}

```

**Résultat:**

**Non testé**, il manque l'implémentation d'un web socket pour rendre cette partie pleinement fonctionnelle. Inachevé par manque de temps (et de sommeil).
</details>

---

### Structure des données

[Modèle entité-association](docs/ERDiagram.png)

J'ai fait le choix d'utiliser une table de liaison `movie_persons` qui permet au besoin d'ajouter de nouveaux rôles pour des personnes (scéanristes, costumes, ...).
