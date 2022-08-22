"""OpenCTI Report operations"""

import datetime
import json
from typing import Union

from dateutil.parser import parse

from ..api.opencti_api_client import OpenCTIApiClient
from . import _generate_uuid5

__all__ = [
    "Report",
]


class Report:
    """Report domain object"""

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
            name
            description
            report_types
            published
            objects {
                edges {
                    node {
                        ... on BasicObject {
                            id
                            entity_type
                            parent_types
                        }
                        ... on BasicRelationship {
                            id
                            entity_type
                            parent_types
                        }
                        ... on StixObject {
                            standard_id
                            spec_version
                            created_at
                            updated_at
                        }
                        ... on AttackPattern {
                            name
                        }
                        ... on Campaign {
                            name
                        }
                        ... on CourseOfAction {
                            name
                        }
                        ... on Individual {
                            name
                        }
                        ... on Organization {
                            name
                        }
                        ... on Sector {
                            name
                        }
                        ... on System {
                            name
                        }
                        ... on Indicator {
                            name
                        }
                        ... on Infrastructure {
                            name
                        }
                        ... on IntrusionSet {
                            name
                        }
                        ... on Position {
                            name
                        }
                        ... on City {
                            name
                        }
                        ... on Country {
                            name
                        }
                        ... on Region {
                            name
                        }
                        ... on Malware {
                            name
                        }
                        ... on ThreatActor {
                            name
                        }
                        ... on Tool {
                            name
                        }
                        ... on Vulnerability {
                            name
                        }
                        ... on Incident {
                            name
                        }
                        ... on StixCoreRelationship {
                            standard_id
                            spec_version
                            created_at
                            updated_at
                            relationship_type
                        }
                       ... on StixSightingRelationship {
                            standard_id
                            spec_version
                            created_at
                            updated_at
                        }
                    }
                }
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
    def generate_id(
        name: str,
        published: Union[str, datetime],
    ) -> str:
        """
        Generate a STIX compliant UUID5.

        :param name: Report name
        :param published: Publish datetime
        :return: A Stix compliant UUID5
        """

        if isinstance(published, datetime.datetime):
            published = published.isoformat()

        data = {
            "name": name.lower().strip(),
            "published": published,
        }

        return _generate_uuid5("report", data)

    """
        List Report objects

        :param filters: the filters to apply
        :param search: the search keyword
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of Report objects
    """

    def list(self, **kwargs):
        filters = kwargs.get("filters", None)
        search = kwargs.get("search", None)
        first = kwargs.get("first", 100)
        after = kwargs.get("after", None)
        order_by = kwargs.get("orderBy", None)
        order_mode = kwargs.get("orderMode", None)
        custom_attributes = kwargs.get("customAttributes", None)
        get_all = kwargs.get("getAll", False)
        with_pagination = kwargs.get("withPagination", False)
        if get_all:
            first = 100

        self._api.log(
            "info", "Listing Reports with filters " + json.dumps(filters) + "."
        )
        query = (
            """
                query Reports($filters: [ReportsFiltering], $search: String, $first: Int, $after: ID, $orderBy: ReportsOrdering, $orderMode: OrderingMode) {
                    reports(filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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
                "search": search,
                "first": first,
                "after": after,
                "orderBy": order_by,
                "orderMode": order_mode,
            },
        )
        if get_all:
            final_data = []
            data = self._api.process_multiple(result["data"]["reports"])
            final_data = final_data + data
            while result["data"]["reports"]["pageInfo"]["hasNextPage"]:
                after = result["data"]["reports"]["pageInfo"]["endCursor"]
                self._api.log("info", "Listing Reports after " + after)
                result = self._api.query(
                    query,
                    {
                        "filters": filters,
                        "search": search,
                        "first": first,
                        "after": after,
                        "orderBy": order_by,
                        "orderMode": order_mode,
                    },
                )
                data = self._api.process_multiple(result["data"]["reports"])
                final_data = final_data + data
            return final_data
        else:
            return self._api.process_multiple(
                result["data"]["reports"], with_pagination
            )

    """
        Read a Report object

        :param id: the id of the Report
        :param filters: the filters to apply if no id provided
        :return Report object
    """

    def read(self, **kwargs):
        id = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self._api.log("info", "Reading Report {" + id + "}.")
            query = (
                """
                    query Report($id: String!) {
                        report(id: $id) {
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
            return self._api.process_multiple_fields(result["data"]["report"])
        elif filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            else:
                return None

    """
        Read a Report object by stix_id or name

        :param type: the Stix-Domain-Entity type
        :param stix_id: the STIX ID of the Stix-Domain-Entity
        :param name: the name of the Stix-Domain-Entity
        :return Stix-Domain-Entity object
    """

    def get_by_stix_id_or_name(self, **kwargs):
        stix_id = kwargs.get("stix_id", None)
        name = kwargs.get("name", None)
        published = kwargs.get("published", None)
        custom_attributes = kwargs.get("customAttributes", None)
        object_result = None
        if stix_id is not None:
            object_result = self.read(id=stix_id, customAttributes=custom_attributes)
        if object_result is None and name is not None and published is not None:
            published_final = parse(published).strftime("%Y-%m-%d")
            object_result = self.read(
                filters=[
                    {"key": "name", "values": [name]},
                    {"key": "published_day", "values": [published_final]},
                ],
                customAttributes=custom_attributes,
            )
        return object_result

    """
        Check if a report already contains a thing (Stix Object or Stix Relationship)

        :param id: the id of the Report
        :param stixObjectOrStixRelationshipId: the id of the Stix-Entity
        :return Boolean
    """

    def contains_stix_object_or_stix_relationship(self, **kwargs):
        id = kwargs.get("id", None)
        stix_object_or_stix_relationship_id = kwargs.get(
            "stixObjectOrStixRelationshipId", None
        )
        if id is not None and stix_object_or_stix_relationship_id is not None:
            self._api.log(
                "info",
                "Checking StixObjectOrStixRelationship {"
                + stix_object_or_stix_relationship_id
                + "} in Report {"
                + id
                + "}",
            )
            query = """
                query ReportContainsStixObjectOrStixRelationship($id: String!, $stixObjectOrStixRelationshipId: String!) {
                    reportContainsStixObjectOrStixRelationship(id: $id, stixObjectOrStixRelationshipId: $stixObjectOrStixRelationshipId)
                }
            """
            result = self._api.query(
                query,
                {
                    "id": id,
                    "stixObjectOrStixRelationshipId": stix_object_or_stix_relationship_id,
                },
            )
            return result["data"]["reportContainsStixObjectOrStixRelationship"]
        else:
            self._api.log(
                "error",
                "[opencti_report] Missing parameters: id or stixObjectOrStixRelationshipId",
            )

    """
        Create a Report object

        :param name: the name of the Report
        :return Report object
    """

    def create(self, **kwargs):
        stix_id = kwargs.get("stix_id", None)
        created_by = kwargs.get("createdBy", None)
        objects = kwargs.get("objects", None)
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
        report_types = kwargs.get("report_types", None)
        published = kwargs.get("published", None)
        x_opencti_stix_ids = kwargs.get("x_opencti_stix_ids", None)
        update = kwargs.get("update", False)

        if name is not None and description is not None and published is not None:
            self._api.log("info", "Creating Report {" + name + "}.")
            query = """
                mutation ReportAdd($input: ReportAddInput) {
                    reportAdd(input: $input) {
                        id
                        standard_id
                        entity_type
                        parent_types
                    }
                }
            """
            result = self._api.query(
                query,
                {
                    "input": {
                        "stix_id": stix_id,
                        "createdBy": created_by,
                        "objectMarking": object_marking,
                        "objectLabel": object_label,
                        "objects": objects,
                        "externalReferences": external_references,
                        "revoked": revoked,
                        "confidence": confidence,
                        "lang": lang,
                        "created": created,
                        "modified": modified,
                        "name": name,
                        "description": description,
                        "report_types": report_types,
                        "published": published,
                        "x_opencti_stix_ids": x_opencti_stix_ids,
                        "update": update,
                    }
                },
            )
            return self._api.process_multiple_fields(result["data"]["reportAdd"])
        else:
            self._api.log(
                "error",
                "[opencti_report] Missing parameters: name and description and published and report_class",
            )

    """
        Add a Stix-Entity object to Report object (object_refs)

        :param id: the id of the Report
        :param stixObjectOrStixRelationshipId: the id of the Stix-Entity
        :return Boolean
    """

    def add_stix_object_or_stix_relationship(self, **kwargs):
        id = kwargs.get("id", None)
        stix_object_or_stix_relationship_id = kwargs.get(
            "stixObjectOrStixRelationshipId", None
        )
        if id is not None and stix_object_or_stix_relationship_id is not None:
            self._api.log(
                "info",
                "Adding StixObjectOrStixRelationship {"
                + stix_object_or_stix_relationship_id
                + "} to Report {"
                + id
                + "}",
            )
            query = """
               mutation ReportEditRelationAdd($id: ID!, $input: StixMetaRelationshipAddInput) {
                   reportEdit(id: $id) {
                        relationAdd(input: $input) {
                            id
                        }
                   }
               }
            """
            self._api.query(
                query,
                {
                    "id": id,
                    "input": {
                        "toId": stix_object_or_stix_relationship_id,
                        "relationship_type": "object",
                    },
                },
            )
            return True
        else:
            self._api.log(
                "error",
                "[opencti_report] Missing parameters: id and stixObjectOrStixRelationshipId",
            )
            return False

    """
        Remove a Stix-Entity object to Report object (object_refs)

        :param id: the id of the Report
        :param stixObjectOrStixRelationshipId: the id of the Stix-Entity
        :return Boolean
    """

    def remove_stix_object_or_stix_relationship(self, **kwargs):
        id = kwargs.get("id", None)
        stix_object_or_stix_relationship_id = kwargs.get(
            "stixObjectOrStixRelationshipId", None
        )
        if id is not None and stix_object_or_stix_relationship_id is not None:
            self._api.log(
                "info",
                "Removing StixObjectOrStixRelationship {"
                + stix_object_or_stix_relationship_id
                + "} to Report {"
                + id
                + "}",
            )
            query = """
               mutation ReportEditRelationDelete($id: ID!, $toId: String!, $relationship_type: String!) {
                   reportEdit(id: $id) {
                        relationDelete(toId: $toId, relationship_type: $relationship_type) {
                            id
                        }
                   }
               }
            """
            self._api.query(
                query,
                {
                    "id": id,
                    "toId": stix_object_or_stix_relationship_id,
                    "relationship_type": "object",
                },
            )
            return True
        else:
            self._api.log(
                "error",
                "[opencti_report] Missing parameters: id and stixObjectOrStixRelationshipId",
            )
            return False

    """
        Import a Report object from a STIX2 object

        :param stixObject: the Stix-Object Report
        :return Report object
    """

    def import_from_stix2(self, **kwargs):
        stix_object = kwargs.get("stixObject", None)
        extras = kwargs.get("extras", {})
        update = kwargs.get("update", False)
        if stix_object is not None:

            # Search in extensions
            if "x_opencti_stix_ids" not in stix_object:
                stix_object[
                    "x_opencti_stix_ids"
                ] = self._api.get_attribute_in_extension("stix_ids", stix_object)

            return self.create(
                stix_id=stix_object["id"],
                createdBy=extras.get("created_by_id"),
                objectMarking=extras.get("object_marking_ids"),
                objectLabel=extras.get("object_label_ids", []),
                objects=extras.get("object_ids", []),
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
                report_types=stix_object.get("report_types"),
                published=stix_object.get("published"),
                x_opencti_stix_ids=stix_object.get("x_opencti_stix_ids"),
                update=update,
            )
        else:
            self._api.log("error", "[opencti_report] Missing parameters: stixObject")
