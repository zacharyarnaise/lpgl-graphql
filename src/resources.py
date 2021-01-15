""" LPGL - IUT Metz
Zachary Arnaise

Code basé sur cet exemple:
https://github.com/alecrasmussen/falcon-graphql-server/blob/master/falcon_graphql_server.py
"""


import json
from collections import OrderedDict

import falcon
import graphene
import sqlalchemy


def set_graphql_allow_header(
    req: falcon.Request, resp: falcon.Response, resource: object
):
    """Définit l'en-tête `Allow` sur les réponses faites aux requêtes
    GraphQL."""
    resp.set_header("Allow", "GET, POST, OPTIONS")


@falcon.after(set_graphql_allow_header)
class ResourceGraphQL(object):
    """Resource GraphQL, définit l'endpoint que le serveur Falcon utilisera."""

    def __init__(
        self: object,
        schema: graphene.Schema,
        scoped_session: sqlalchemy.orm.scoped_session,
    ):
        """Constructeur."""
        self.schema = schema
        self.scoped_session = scoped_session

    def on_get(self: object, req: falcon.Request, resp: falcon.Response):
        "Handles GET requests."
        # Traitement de la query
        if req.params and "query" in req.params and req.params["query"]:
            query = str(req.params["query"])

        # Traitement variables, si spécifiées
        variables = ""
        if "variables" in req.params and req.params["variables"]:
            try:
                variables = json.loads(
                    str(req.params["variables"]), object_pairs_hook=OrderedDict
                )
            except json.decoder.JSONDecodeError:
                pass

        # Traitement nom d'opération, si spécifié
        operationName = None
        if "operationName" in req.params and req.params["operationName"]:
            operationName = str(req.params["operationName"])

        # Exécution requête
        result = self.schema.execute(
            request_string=query,
            variable_values=variables,
            operation_name=operationName,
            context_value={"session": self.scoped_session},
        )

        # Traitement du résultat de la requête GraphQL
        if result.data:
            resp.status = falcon.HTTP_200
            resp.body = json.dumps({"data": result.data})
        elif result.errors:
            messages = [{"message": str(i)} for i in result.errors]
            resp.status = falcon.HTTP_400
            resp.body = json.dumps({"errors": messages})

    def on_post(self: object, req: falcon.Request, resp: falcon.Response):
        "Handles POST requests."
        # Traitement de la query, si spécifiée dans les params URL
        query = None
        if req.params and "query" in req.params and req.params["query"]:
            query = str(req.params["query"])

        # Traitement variables, si spécifiées dans les params URL
        variables = None
        if "variables" in req.params and req.params["variables"]:
            try:
                variables = json.loads(
                    str(req.params["variables"]), object_pairs_hook=OrderedDict
                )
            except json.decoder.JSONDecodeError:
                pass

        # Traitement nom d'opération, si spécifié dans les params URL
        operationName = None
        if "operationName" in req.params and req.params["operationName"]:
            operationName = str(req.params["operationName"])

        # Traitement si requête au format JSON
        if req.content_type and "application/json" in req.content_type:
            if req.content_length is None or req.content_length == 0:
                return

            # Lecture du corps de la requête et parse du JSON
            raw_json = req.stream.read().decode("utf-8")
            try:
                req.context["post_data"] = json.loads(
                    raw_json, object_pairs_hook=OrderedDict
                )
            except json.decoder.JSONDecodeError:
                pass

            # Si pas de query dans l'URL, on essaye depuis le JSON
            if query is None:
                if "query" in req.context["post_data"]:
                    query = str(req.context["post_data"]["query"])

            # Si pas de variables dans l'URL, on essaye depuis le JSON
            if variables is None:
                if (
                    "variables" in req.context["post_data"]
                    and req.context["post_data"]["variables"]
                ):
                    try:
                        variables = req.context["post_data"]["variables"]
                        if not isinstance(variables, OrderedDict):
                            variables = json.loads(
                                str(req.context["post_data"]["variables"]),
                                object_pairs_hook=OrderedDict,
                            )
                    except json.decoder.JSONDecodeError:
                        pass
                else:
                    variables = ""

            # Si pas de nom d'opération dans l'URL, on essaye depuis le JSON
            if operationName is None:
                if "operationName" in req.context["post_data"]:
                    operationName = str(req.context["post_data"]["operationName"])

        # Traitement si requête au format GraphQL
        elif req.content_type and "application/graphql" in req.content_type:
            # Lecture du corps de la requête
            req.context["post_data"] = req.stream.read().decode("utf-8")

            # Si pas de query dans l'URL, on essaye de la récupérer ici
            if query is None:
                if req.context["post_data"]:
                    query = str(req.context["post_data"])

        # Exécution requête
        result = self.schema.execute(
            request_string=query,
            variable_values=variables,
            operation_name=operationName,
            context_value={"session": self.scoped_session},
        )

        # Traitement du résultat de la requête GraphQL
        if result.data:
            resp.status = falcon.HTTP_200
            resp.body = json.dumps({"data": result.data})
        elif result.errors:
            messages = [{"message": str(i)} for i in result.errors]
            resp.status = falcon.HTTP_400
            resp.body = json.dumps({"errors": messages})
