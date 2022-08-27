"""OpenCTI Identity operations"""

import json
from typing import TYPE_CHECKING

from ..utils.constants import IdentityTypes
from . import _generate_uuid5

if TYPE_CHECKING:
    from ..api.opencti_api_client import OpenCTIApiClient

__all__ = [
    "Identity",
]


class Identity:
    """Identity domain object"""

    def __init__(self, api: "OpenCTIApiClient"):
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
            spec_version
            created_at
            updated_at
            createdBy {
                ... on Identity {
                    id
                    standard_id
                    entity_type
                    parent_types
                    spec_version
                    identity_class
                    name
                    description
                    roles
                    contact_information
                    x_opencti_aliases
                    created
                    modified
                    objectLabel {
                        edges {
                            node {
                                id
                                value
                                color
                            }
                        }
                    }
                }
                ... on Organization {
                    x_opencti_organization_type
                    x_opencti_reliability
                }
                ... on Individual {
                    x_opencti_firstname
                    x_opencti_lastname
                }
            }
            objectMarking {
                edges {
                    node {
                        id
                        standard_id
                        entity_type
                        definition_type
                        definition
                        created
                        modified
                        x_opencti_order
                        x_opencti_color
                    }
                }
            }
            objectLabel {
                edges {
                    node {
                        id
                        value
                        color
                    }
                }
            }
            externalReferences {
                edges {
                    node {
                        id
                        standard_id
                        entity_type
                        source_name
                        description
                        url
                        hash
                        external_id
                        created
                        modified
                        importFiles {
                            edges {
                                node {
                                    id
                                    name
                                    size
                                    metaData {
                                        mimetype
                                        version
                                    }
                                }
                            }
                        }
                    }
                }
            }
            revoked
            confidence
            created
            modified
            identity_class
            name
            description
            x_opencti_aliases
            contact_information
            ... on Individual {
                x_opencti_firstname
                x_opencti_lastname
            }
            ... on Organization {
                x_opencti_organization_type
                x_opencti_reliability
            }
            importFiles {
                edges {
                    node {
                        id
                        name
                        size
                        metaData {
                            mimetype
                            version
                        }
                    }
                }
            }
        """

    @staticmethod
    def generate_id(name: str, identity_class: str) -> str:
        """
        Generate a STIX compliant UUID5.

        :param name: Identity name
        :param identity_class: Identity class vocab type
        :return: A Stix compliant UUID5
        """

        data = {
            "name": name.lower().strip(),
            "identity_class": identity_class,
        }

        return _generate_uuid5("identity", data)

    """
        List Identity objects

        :param types: the list of types
        :param filters: the filters to apply
        :param search: the search keyword
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of Identity objects
    """

    def list(self, **kwargs):
        types = kwargs.get("types", None)
        filters = kwargs.get("filters", None)
        search = kwargs.get("search", None)
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
            "info", "Listing Identities with filters " + json.dumps(filters) + "."
        )
        query = (
            """
                        query Identities($types: [String], $filters: [IdentitiesFiltering], $search: String, $first: Int, $after: ID, $orderBy: IdentitiesOrdering, $orderMode: OrderingMode) {
                            identities(types: $types, filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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
                "types": types,
                "filters": filters,
                "search": search,
                "first": first,
                "after": after,
                "orderBy": order_by,
                "orderMode": order_mode,
            },
        )
        return self._api.process_multiple(result["data"]["identities"], with_pagination)

    """
        Read a Identity object

        :param id: the id of the Identity
        :param filters: the filters to apply if no id provided
        :return Identity object
    """

    def read(self, **kwargs):
        id = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self._api.log("info", "Reading Identity {" + id + "}.")
            query = (
                """
                            query Identity($id: String!) {
                                identity(id: $id) {
                                    """
                + (
                    custom_attributes
                    if custom_attributes is not None
                    else self._default_attributes
                )
                + """
                    }
                }
             """
            )
            result = self._api.query(query, {"id": id})
            return self._api.process_multiple_fields(result["data"]["identity"])
        elif filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            else:
                return None
        else:
            self._api.log(
                "error", "[opencti_identity] Missing parameters: id or filters"
            )
            return None

    """
        Create a Identity object

        :param name: the name of the Identity
        :return Identity object
    """

    def create(self, **kwargs):
        type = kwargs.get("type", None)
        stix_id = kwargs.get("stix_id", None)
        created_by = kwargs.get("createdBy", None)
        object_marking = kwargs.get("objectMarking", None)
        object_label = kwargs.get("objectLabel", None)
        external_references = kwargs.get("externalReferences", None)
        revoked = kwargs.get("revoked", None)
        confidence = kwargs.get("confidence", None)
        lang = kwargs.get("lang", None)
        created = kwargs.get("created", None)
        modified = kwargs.get("modified", None)
        name = kwargs.get("name", None)
        description = kwargs.get("description", "")
        contact_information = kwargs.get("contact_information", None)
        roles = kwargs.get("roles", None)
        x_opencti_aliases = kwargs.get("x_opencti_aliases", None)
        x_opencti_organization_type = kwargs.get("x_opencti_organization_type", None)
        x_opencti_reliability = kwargs.get("x_opencti_reliability", None)
        x_opencti_firstname = kwargs.get("x_opencti_firstname", None)
        x_opencti_lastname = kwargs.get("x_opencti_lastname", None)
        x_opencti_stix_ids = kwargs.get("x_opencti_stix_ids", None)
        update = kwargs.get("update", False)

        if type is not None and name is not None and description is not None:
            self._api.log("info", "Creating Identity {" + name + "}.")
            input_variables = {
                "stix_id": stix_id,
                "createdBy": created_by,
                "objectMarking": object_marking,
                "objectLabel": object_label,
                "externalReferences": external_references,
                "revoked": revoked,
                "confidence": confidence,
                "lang": lang,
                "created": created,
                "modified": modified,
                "name": name,
                "description": description,
                "contact_information": contact_information,
                "roles": roles,
                "x_opencti_aliases": x_opencti_aliases,
                "x_opencti_stix_ids": x_opencti_stix_ids,
                "update": update,
            }
            if type == IdentityTypes.ORGANIZATION.value:
                query = """
                    mutation OrganizationAdd($input: OrganizationAddInput) {
                        organizationAdd(input: $input) {
                            id
                            standard_id
                            entity_type
                            parent_types
                        }
                    }
                """
                input_variables[
                    "x_opencti_organization_type"
                ] = x_opencti_organization_type
                input_variables["x_opencti_reliability"] = x_opencti_reliability
                result_data_field = "organizationAdd"
            elif type == IdentityTypes.INDIVIDUAL.value:
                query = """
                    mutation IndividualAdd($input: IndividualAddInput) {
                        individualAdd(input: $input) {
                            id
                            standard_id
                            entity_type
                            parent_types
                        }
                    }
                """
                input_variables["x_opencti_firstname"] = x_opencti_firstname
                input_variables["x_opencti_lastname"] = x_opencti_lastname
                result_data_field = "individualAdd"
            else:
                query = """
                    mutation IdentityAdd($input: IdentityAddInput) {
                        identityAdd(input: $input) {
                            id
                            standard_id
                            entity_type
                            parent_types
                        }
                    }
                """
                input_variables["type"] = type
                result_data_field = "identityAdd"
            result = self._api.query(
                query,
                {
                    "input": input_variables,
                },
            )
            return self._api.process_multiple_fields(result["data"][result_data_field])
        else:
            self._api.log("error", "Missing parameters: type, name and description")

    """
        Import an Identity object from a STIX2 object

        :param stixObject: the Stix-Object Identity
        :return Identity object
    """

    def import_from_stix2(self, **kwargs):
        stix_object = kwargs.get("stixObject", None)
        extras = kwargs.get("extras", {})
        update = kwargs.get("update", False)
        if stix_object is not None:
            type = "Organization"
            if "identity_class" in stix_object:
                if stix_object["identity_class"] == "individual":
                    type = "Individual"
                elif stix_object["identity_class"] == "class":
                    type = "Sector"
                elif stix_object["identity_class"] == "system":
                    type = "System"

            # Search in extensions
            if "x_opencti_aliases" not in stix_object:
                stix_object["x_opencti_aliases"] = self._api.get_attribute_in_extension(
                    "aliases", stix_object
                )
            if "x_opencti_organization_type" not in stix_object:
                stix_object[
                    "x_opencti_organization_type"
                ] = self._api.get_attribute_in_extension(
                    "organization_type", stix_object
                )
            if "x_opencti_reliability" not in stix_object:
                stix_object[
                    "x_opencti_reliability"
                ] = self._api.get_attribute_in_extension("reliability", stix_object)
            if "x_opencti_organization_type" not in stix_object:
                stix_object[
                    "x_opencti_organization_type"
                ] = self._api.get_attribute_in_extension(
                    "organization_type", stix_object
                )
            if "x_opencti_firstname" not in stix_object:
                stix_object[
                    "x_opencti_firstname"
                ] = self._api.get_attribute_in_extension("firstname", stix_object)
            if "x_opencti_lastname" not in stix_object:
                stix_object[
                    "x_opencti_lastname"
                ] = self._api.get_attribute_in_extension("lastname", stix_object)
            if "x_opencti_stix_ids" not in stix_object:
                stix_object[
                    "x_opencti_stix_ids"
                ] = self._api.get_attribute_in_extension("stix_ids", stix_object)

            return self.create(
                type=type,
                stix_id=stix_object["id"],
                createdBy=extras.get("created_by_id"),
                objectMarking=extras.get("object_marking_ids", []),
                objectLabel=extras.get("object_label_ids", []),
                externalReferences=extras.get("external_references_ids", []),
                revoked=stix_object.get("revoked"),
                confidence=stix_object.get("confidence"),
                lang=stix_object.get("lang"),
                created=stix_object.get("created"),
                modified=stix_object.get("modified"),
                name=stix_object["name"],
                description=self._api.stix2.convert_markdown(stix_object["description"])
                if "description" in stix_object
                else "",
                contact_information=self._api.stix2.convert_markdown(
                    stix_object["contact_information"]
                )
                if "contact_information" in stix_object
                else None,
                roles=stix_object.get("roles"),
                x_opencti_aliases=self._api.stix2.pick_aliases(stix_object),
                x_opencti_organization_type=stix_object.get(
                    "x_opencti_organization_type"
                ),
                x_opencti_reliability=stix_object.get("x_opencti_reliability"),
                x_opencti_firstname=stix_object.get("x_opencti_firstname"),
                x_opencti_lastname=stix_object.get("x_opencti_lastname"),
                x_opencti_stix_ids=stix_object.get("x_opencti_stix_ids"),
                update=update,
            )
        else:
            self._api.log("error", "[opencti_identity] Missing parameters: stixObject")
