class OpenCTIApiTrash:
    """OpenCTIApiTrash"""

    def __init__(self, api):
        self.api = api

    def restore(self, operation_id: str):
        query = """
            mutation DeleteOperationRestore($id: ID!) {
                deleteOperationRestore(id: $id)
            }
           """
        self.api.query(
            query,
            {
                "id": operation_id,
            },
        )

    def delete(self, **kwargs):
        """Delete a role given its ID

        :param id: ID for the role on the platform.
        :type id: str
        """
        id = kwargs.get("id", None)
        if id is None:
            self.api.admin_logger.error("[opencti_role] Missing parameter: id")
            return None

        query = """
            mutation DeleteOperationConfirm($id: ID!) {
                deleteOperationConfirm(id: $id) {
            }
        """
        self.api.query(
            query,
            {
                "id": id,
            },
        )
