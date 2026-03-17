import lancedb
from typing import List, Dict, Any, Optional

class LanceDBProvider:
    def __init__(self, uri: str):
        """
        Initialize the LanceDB provider.
        
        Args:
            uri (str): The URI to connect to the database (e.g., local path).
        """
        self.uri = uri
        self.db = lancedb.connect(uri)

    def create_table(self, name: str, schema: Any = None, data: Optional[List[Dict[str, Any]]] = None):
        """
        Create a new table in LanceDB.
        
        Args:
            name (str): Name of the table.
            schema (Any, optional): The schema of the table.
            data (List[Dict[str, Any]], optional): Initial data to insert.
        """
        table = self.db.create_table(name, schema=schema, data=data, mode="overwrite")
        
        # Ensure FTS index is created on the 'text' field if it exists
        if (data and len(data) > 0 and "text" in data[0]) or (schema and hasattr(schema, 'names') and "text" in schema.names):
            table.create_fts_index("text", replace=True)
            
        return table

    def add_documents(self, table_name: str, documents: List[Dict[str, Any]]):
        """
        Add documents to an existing table.
        
        Args:
            table_name (str): Name of the table.
            documents (List[Dict[str, Any]]): Documents to add.
        """
        table = self.db.open_table(table_name)
        table.add(documents)
        
        # Update FTS index if 'text' field is present
        if len(documents) > 0 and "text" in documents[0]:
            table.create_fts_index("text", replace=True)

    def search(self, table_name: str, query_vector: List[float], query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a hybrid search combining vector similarity and keyword-based FTS.
        
        Args:
            table_name (str): Name of the table to search.
            query_vector (List[float]): The vector to search for.
            query_text (str): The text to search for using FTS.
            limit (int): Maximum number of results to return.
            
        Returns:
            List[Dict[str, Any]]: Search results.
        """
        table = self.db.open_table(table_name)
        
        # Hybrid search in LanceDB
        results = table.search(query_type="hybrid") \
            .vector(query_vector) \
            .text(query_text) \
            .limit(limit) \
            .to_list()
            
        return results
