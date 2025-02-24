class OpenCTIApiWorkspace:
    """OpenCTIApiWorkspace"""

    def __init__(self, api):
        self.api = api

    def delete(self, **kwargs):
        id = kwargs.get("id", None)
        query = """
            mutation WorkspaceDelete($id: ID!) {
                workspaceDelete(id: $id)
            }
           """
        self.api.query(
            query,
            {
                "id": id,
            },
        )
