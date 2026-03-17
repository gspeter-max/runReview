import lancedb

class LanceDBProvider:
    def __init__(self, uri: str):
        """
        Initialize the LanceDB provider.
        
        Args:
            uri (str): The URI to connect to the database (e.g., local path).
        """
        self.uri = uri
        self.db = lancedb.connect(uri)
