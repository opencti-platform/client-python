class OpenCTIApiPublicDashboard:
    """OpenCTIApiPublicDashboard"""

    def __init__(self, api):
        self.api = api

    def delete(self, **kwargs):
        id = kwargs.get("id", None)
        query = """
            mutation PublicDashboardDelete($id: ID!) {
                publicDashboardDelete(id: $id)
            }
           """
        self.api.query(
            query,
            {
                "id": id,
            },
        )
