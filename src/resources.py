""" LPGL - IUT Metz
Zachary Arnaise

Code basé sur cet exemple:
https://github.com/alecrasmussen/falcon-graphql-server/blob/master/falcon_graphql_server.py
"""


import json
from collections import OrderedDict
from functools import partial

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

        self._resp_forbidden = partial(
            self._resp_error,
            status=falcon.HTTP_403,
            reason="Access denied.",
        )
        self._resp_not_found = partial(
            self._resp_error,
            status=falcon.HTTP_404,
            reason="Object not found.",
        )
        self._resp_method_not_allowed = partial(
            self._resp_error,
            status=falcon.HTTP_405,
            reason="Method not allowed. Must be one of: GET, POST, OPTIONS.",
        )
        self._resp_variables_invalid_json = partial(
            self._resp_error,
            status=falcon.HTTP_400,
            reason="Variables are invalid JSON.",
        )
        self._resp_extensions_invalid_json = partial(
            self._resp_error,
            status=falcon.HTTP_400,
            reason="Extensions are invalid JSON.",
        )
        self._resp_body_invalid_json = partial(
            self._resp_error,
            status=falcon.HTTP_400,
            reason="POST body is invalid JSON.",
        )
        self._resp_no_query_provided = partial(
            self._resp_error,
            status=falcon.HTTP_400,
            reason="Must provide query string.",
        )

    @staticmethod
    def _resp_error(resp: falcon.Response, status: str, reason: str):
        """Construit un objet `Response` pour décrire une erreur.

        Le contenu renvoyé suit le format d'erreur tel que défini dans la spec
        GraphQL: https://spec.graphql.org/draft/#sec-Errors.Error-result-format
        """
        resp = resp if resp else falcon.Response()
        resp.status = status
        resp.body = json.dumps({"errors": [{"message": reason}]})
        return resp

    def on_put(self: object, req: falcon.Request, resp: falcon.Response):
        "Handles PUT requests. Not supported."
        self._resp_method_not_allowed(resp=resp)

    def on_patch(self: object, req: falcon.Request, resp: falcon.Response):
        "Handles PATCH requests. Not supported."
        self._resp_method_not_allowed(resp=resp)

    def on_delete(self: object, req: falcon.Request, resp: falcon.Response):
        "Handles DELETE requests. Not supported."
        self._resp_method_not_allowed(resp=resp)

    def on_options(self: object, req: falcon.Request, resp: falcon.Response):
        "Handles OPTIONS requests. No content."
        resp.status = falcon.HTTP_204

    def on_head(self: object, req: falcon.Request, resp: falcon.Response):
        "Handles HEAD requests. No content."
        resp.status = falcon.HTTP_204

    def on_get(self: object, req: falcon.Request, resp: falcon.Response):
        "Handles GET requests."
        # Traitement de la query
        if req.params and "query" in req.params and req.params["query"]:
            query = str(req.params["query"])
        else:
            self._resp_no_query_provided(resp=resp)
            return

        # Traitement variables, si spécifiées
        variables = ""
        if "variables" in req.params and req.params["variables"]:
            try:
                variables = json.loads(
                    str(req.params["variables"]), object_pairs_hook=OrderedDict
                )
            except json.decoder.JSONDecodeError:
                self._resp_variables_invalid_json(resp=resp)
                return

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
        else:
            raise RuntimeError

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
                self._resp_variables_invalid_json(resp=resp)
                return

        # Traitement nom d'opération, si spécifié dans les params URL
        operationName = None
        if "operationName" in req.params and req.params["operationName"]:
            operationName = str(req.params["operationName"])

        # Traitement si requête au format JSON
        if req.content_type and "application/json" in req.content_type:
            if req.content_length is None or req.content_length == 0:
                self._resp_body_invalid_json(resp=resp)
                return

            # Lecture du corps de la requête et parse du JSON
            raw_json = req.stream.read().decode("utf-8")
            try:
                req.context["post_data"] = json.loads(
                    raw_json, object_pairs_hook=OrderedDict
                )
            except json.decoder.JSONDecodeError:
                self._resp_body_invalid_json(resp=resp)
                return

            # Si pas de query dans l'URL, on essaye depuis le JSON
            if query is None:
                if "query" in req.context["post_data"]:
                    query = str(req.context["post_data"]["query"])
                else:
                    self._resp_no_query_provided(resp=resp)
                    return

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
                        self._resp_variables_invalid_json(resp=resp)
                        return
                else:
                    variables = ""

            # Si pas de nom d'opération dans l'URL, on essaye depuis le JSON
            if operationName is None:
                if "operationName" in req.context["post_data"]:
                    postData = req.context["post_data"]
                    operationName = str(postData["operationName"])

        # Traitement si requête au format GraphQL
        elif req.content_type and "application/graphql" in req.content_type:
            # Lecture du corps de la requête
            req.context["post_data"] = req.stream.read().decode("utf-8")

            # Si pas de query dans l'URL, on essaye de la récupérer ici
            if query is None:
                if req.context["post_data"]:
                    query = str(req.context["post_data"])
                else:
                    self._resp_no_query_provided(resp=resp)
                    return

        # Si on a pas de query à ce stade, c'est dû à un Content-Type autre
        # que JSON ou GraphQL et/ou rien dans les params de l'URL
        elif query is None:
            self._resp_no_query_provided(resp=resp)
            return

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
        else:
            raise RuntimeError
