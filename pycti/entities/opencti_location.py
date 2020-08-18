# coding: utf-8

import json
from pycti.utils.opencti_stix2 import SPEC_VERSION


class Location:
    def __init__(self, opencti):
        self.opencti = opencti
        self.properties = """
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
                    name
                    aliases
                    description
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
                    }
                }
            }
            revoked
            confidence
            created
            modified
            name
            description
            latitude
            longitude
            precision
            x_opencti_aliases
        """

    """
        List Location objects

        :param types: the list of types
        :param filters: the filters to apply
        :param search: the search keyword
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of Location objects
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

        self.opencti.log(
            "info", "Listing Locations with filters " + json.dumps(filters) + "."
        )
        query = (
            """
            query Locations($types: [String], $filters: [LocationsFiltering], $search: String, $first: Int, $after: ID, $orderBy: LocationsOrdering, $orderMode: OrderingMode) {
                locations(types: $types, filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
                    edges {
                        node {
                            """
            + (custom_attributes if custom_attributes is not None else self.properties)
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
        result = self.opencti.query(
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
        return self.opencti.process_multiple(
            result["data"]["locations"], with_pagination
        )

    """
        Read a Location object
        
        :param id: the id of the Location
        :param filters: the filters to apply if no id provided
        :return Location object
    """

    def read(self, **kwargs):
        id = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self.opencti.log("info", "Reading Location {" + id + "}.")
            query = (
                """
                query Location($id: String!) {
                    location(id: $id) {
                        """
                + (
                    custom_attributes
                    if custom_attributes is not None
                    else self.properties
                )
                + """
                    }
                }
             """
            )
            result = self.opencti.query(query, {"id": id})
            return self.opencti.process_multiple_fields(result["data"]["location"])
        elif filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            else:
                return None
        else:
            self.opencti.log(
                "error", "[opencti_location] Missing parameters: id or filters"
            )
            return None

    """
        Create a Location object

        :param name: the name of the Location
        :return Location object
    """

    def create_raw(self, **kwargs):
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
        latitude = kwargs.get("latitude", None)
        longitude = kwargs.get("longitude", None)
        precision = kwargs.get("precision", None)
        x_opencti_aliases = kwargs.get("x_opencti_aliases", None)
        if name is not None:
            self.opencti.log("info", "Creating Location {" + name + "}.")
            query = """
                mutation LocationAdd($input: LocationAddInput) {
                    locationAdd(input: $input) {
                        id
                        standard_id
                        entity_type
                        parent_types
                    }
                }
            """
            result = self.opencti.query(
                query,
                {
                    "input": {
                        "type": type,
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
                        "latitude": latitude,
                        "longitude": longitude,
                        "precision": precision,
                        "x_opencti_aliases": x_opencti_aliases,
                    }
                },
            )
            return self.opencti.process_multiple_fields(result["data"]["locationAdd"])
        else:
            self.opencti.log("error", "Missing parameters: name")

    """
        Create a  Location object only if it not exists, update it on request

        :param name: the name of the Location
        :return Location object
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
        latitude = kwargs.get("latitude", None)
        longitude = kwargs.get("longitude", None)
        precision = kwargs.get("precision", None)
        x_opencti_aliases = kwargs.get("x_opencti_aliases", None)
        update = kwargs.get("update", False)
        custom_attributes = """
            id
            standard_id
            entity_type
            parent_types
            createdBy {
                ... on Identity {
                    id
                }
            }            
            ... on Location {
                name
                description 
                latitude
                longitude
                precision
                x_opencti_aliases
            }
        """
        object_result = self.opencti.stix_domain_object.get_by_stix_id_or_name(
            types=[type],
            stix_id=stix_id,
            name=name,
            fieldName="x_opencti_aliases",
            customAttributes=custom_attributes,
        )
        if object_result is not None:
            if update or object_result["createdById"] == created_by:
                # name
                if object_result["name"] != name:
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="name", value=name
                    )
                    object_result["name"] = name
                # description
                if (
                    self.opencti.not_empty(description)
                    and object_result["description"] != description
                ):
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="description", value=description
                    )
                    object_result["description"] = description
                # aliases
                if (
                    self.opencti.not_empty(x_opencti_aliases)
                    and object_result["x_opencti_aliases"] != x_opencti_aliases
                ):
                    if "x_opencti_aliases" in object_result:
                        new_aliases = object_result["x_opencti_aliases"] + list(
                            set(x_opencti_aliases)
                            - set(object_result["x_opencti_aliases"])
                        )
                    else:
                        new_aliases = x_opencti_aliases
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"],
                        key="x_opencti_aliases",
                        value=new_aliases,
                    )
                    object_result["x_opencti_aliases"] = new_aliases
                # latitude
                if (
                    self.opencti.not_empty(latitude)
                    and object_result["latitude"] != latitude
                ):
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="latitude", value=latitude,
                    )
                    object_result["latitude"] = latitude
                # longitude
                if (
                    self.opencti.not_empty(longitude)
                    and "longitude" in object_result
                    and object_result["longitude"] != longitude
                ):
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="longitude", value=longitude,
                    )
                    object_result["longitude"] = longitude
                # precision
                if (
                    self.opencti.not_empty(precision)
                    and "precision" in object_result
                    and object_result["precision"] != precision
                ):
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="precision", value=precision,
                    )
                    object_result["precision"] = precision
            return object_result
        else:
            return self.create_raw(
                type=type,
                stix_id=stix_id,
                createdBy=created_by,
                objectMarking=object_marking,
                objectLabel=object_label,
                externalReferences=external_references,
                revoked=revoked,
                confidence=confidence,
                lang=lang,
                created=created,
                modified=modified,
                name=name,
                description=description,
                latitude=latitude,
                longitude=longitude,
                precision=precision,
                x_opencti_aliases=x_opencti_aliases,
            )

    """
        Import an Location object from a STIX2 object

        :param stixObject: the Stix-Object Location
        :return Location object
    """

    def import_from_stix2(self, **kwargs):
        stix_object = kwargs.get("stixObject", None)
        extras = kwargs.get("extras", {})
        update = kwargs.get("update", False)
        if stix_object is not None:
            if "x_opencti_location_type" in stix_object:
                type = stix_object["x_opencti_location_type"]
            else:
                type = "Position"
            return self.create(
                type=type,
                stix_id=stix_object["id"],
                createdBy=extras["created_by_id"]
                if "created_by_id" in extras
                else None,
                objectMarking=extras["object_marking_ids"]
                if "object_marking_ids" in extras
                else [],
                objectLabel=extras["object_label_ids"]
                if "object_label_ids" in extras
                else [],
                externalReferences=extras["external_references_ids"]
                if "external_references_ids" in extras
                else [],
                revoked=stix_object["revoked"] if "revoked" in stix_object else None,
                confidence=stix_object["confidence"]
                if "confidence" in stix_object
                else None,
                lang=stix_object["lang"] if "lang" in stix_object else None,
                created=stix_object["created"] if "created" in stix_object else None,
                modified=stix_object["modified"] if "modified" in stix_object else None,
                name=stix_object["name"],
                description=self.opencti.stix2.convert_markdown(
                    stix_object["description"]
                )
                if "description" in stix_object
                else "",
                latitude=stix_object["latitude"] if "latitude" in stix_object else None,
                longitude=stix_object["longitude"]
                if "longitude" in stix_object
                else None,
                precision=stix_object["precision"]
                if "precision" in stix_object
                else None,
                x_opencti_aliases=self.opencti.stix2.pick_aliases(stix_object),
                update=update,
            )
        else:
            self.opencti.log(
                "error", "[opencti_location] Missing parameters: stixObject"
            )
