"""OpenCTI Kill-Chain-Phase operations"""

import json

from ..api.opencti_api_client import OpenCTIApiClient
from . import _generate_uuid5

__all__ = [
    "KillChainPhase",
]


class KillChainPhase:
    """Kill-Chain-Phase operations"""

    def __init__(self, api: OpenCTIApiClient):
        """
        Constructor.

        :param api: OpenCTI API client
        """

        self._api = api
        self._default_attributes = """
            id
            standard_id
            entity_type
            parent_types
            kill_chain_name
            phase_name
            x_opencti_order
            created
            modified
            created_at
            updated_at
        """

    @staticmethod
    def generate_id(phase_name: str, kill_chain_name: str) -> str:
        """
        Generate a STIX compliant UUID5.

        :param phase_name: Kill-Chain-Phase name
        :param kill_chain_name: Kill-Chain name
        :return: A stix compliant UUID5
        """
        data = {
            "phase_name": phase_name,
            "kill_chain_name": kill_chain_name,
        }

        return _generate_uuid5("kill-chain-phase", data)

    """
        List Kill-Chain-Phase objects

        :param filters: the filters to apply
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of Kill-Chain-Phase objects
    """

    def list(self, **kwargs):
        filters = kwargs.get("filters", None)
        first = kwargs.get("first", 500)
        after = kwargs.get("after", None)
        order_by = kwargs.get("orderBy", None)
        order_mode = kwargs.get("orderMode", None)
        custom_attributes = kwargs.get("customAttributes", None)
        get_all = kwargs.get("getAll", False)
        with_pagination = kwargs.get("withPagination", False)
        if get_all:
            first = 500

        self._api.log(
            "info", "Listing Kill-Chain-Phase with filters " + json.dumps(filters) + "."
        )
        query = (
            """
                                query KillChainPhases($filters: [KillChainPhasesFiltering], $first: Int, $after: ID, $orderBy: KillChainPhasesOrdering, $orderMode: OrderingMode) {
                                    killChainPhases(filters: $filters, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
                                        edges {
                                            node {
                                                """
            + (
                custom_attributes
                if custom_attributes is not None
                else self._default_attributes
            )
            + """
                        }
                    }
                    pageInfo {
                        startCursor
                        endCursor
                        hasNextPage
                        hasPreviousPage
                        globalCount
                    }
                }
            }
        """
        )
        result = self._api.query(
            query,
            {
                "filters": filters,
                "first": first,
                "after": after,
                "orderBy": order_by,
                "orderMode": order_mode,
            },
        )
        return self._api.process_multiple(
            result["data"]["killChainPhases"], with_pagination
        )

    """
        Read a Kill-Chain-Phase object

        :param id: the id of the Kill-Chain-Phase
        :param filters: the filters to apply if no id provided
        :return Kill-Chain-Phase object
    """

    def read(self, **kwargs):
        id = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        if id is not None:
            self._api.log("info", "Reading Kill-Chain-Phase {" + id + "}.")
            query = (
                """
                                    query KillChainPhase($id: String!) {
                                        killChainPhase(id: $id) {
                                            """
                + self._default_attributes
                + """
                    }
                }
            """
            )
            result = self._api.query(query, {"id": id})
            return self._api.process_multiple_fields(result["data"]["killChainPhase"])
        elif filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            else:
                return None
        else:
            self._api.log(
                "error", "[opencti_kill_chain_phase] Missing parameters: id or filters"
            )
            return None

    """
        Create a Kill-Chain-Phase object

        :param name: the name of the Kill-Chain-Phase
        :return Kill-Chain-Phase object
    """

    def create(self, **kwargs):
        stix_id = kwargs.get("stix_id", None)
        created = kwargs.get("created", None)
        modified = kwargs.get("modified", None)
        kill_chain_name = kwargs.get("kill_chain_name", None)
        phase_name = kwargs.get("phase_name", None)
        x_opencti_order = kwargs.get("x_opencti_order", 0)
        update = kwargs.get("update", False)

        if kill_chain_name is not None and phase_name is not None:
            self._api.log("info", "Creating Kill-Chain-Phase {" + phase_name + "}.")
            query = (
                """
                                    mutation KillChainPhaseAdd($input: KillChainPhaseAddInput) {
                                        killChainPhaseAdd(input: $input) {
                                            """
                + self._default_attributes
                + """
                    }
                }
            """
            )
            result = self._api.query(
                query,
                {
                    "input": {
                        "stix_id": stix_id,
                        "created": created,
                        "modified": modified,
                        "kill_chain_name": kill_chain_name,
                        "phase_name": phase_name,
                        "x_opencti_order": x_opencti_order,
                        "update": update,
                    }
                },
            )
            return self._api.process_multiple_fields(
                result["data"]["killChainPhaseAdd"]
            )
        else:
            self._api.log(
                "error",
                "[opencti_kill_chain_phase] Missing parameters: kill_chain_name and phase_name",
            )

    """
        Update a Kill chain object field

        :param id: the Kill chain id
        :param input: the input of the field
        :return The updated Kill chain object
    """

    def update_field(self, **kwargs):
        id = kwargs.get("id", None)
        input = kwargs.get("input", None)
        if id is not None and input is not None:
            self._api.log("info", "Updating Kill chain {" + id + "}.")
            query = """
                    mutation KillChainPhaseEdit($id: ID!, $input: [EditInput]!) {
                        killChainPhaseEdit(id: $id) {
                            fieldPatch(input: $input) {
                                id
                                standard_id
                                entity_type
                            }
                        }
                    }
                """
            result = self._api.query(
                query,
                {
                    "id": id,
                    "input": input,
                },
            )
            return self._api.process_multiple_fields(
                result["data"]["killChainPhaseEdit"]["fieldPatch"]
            )
        else:
            self._api.log(
                "error",
                "[opencti_kill_chain] Missing parameters: id and key and value",
            )
            return None

    def delete(self, **kwargs):
        id = kwargs.get("id", None)
        if id is not None:
            self._api.log("info", "Deleting Kill-Chain-Phase {" + id + "}.")
            query = """
                 mutation KillChainPhaseEdit($id: ID!) {
                     killChainPhaseEdit(id: $id) {
                         delete
                     }
                 }
             """
            self._api.query(query, {"id": id})
        else:
            self._api.log("error", "[opencti_kill_chain_phase] Missing parameters: id")
            return None
