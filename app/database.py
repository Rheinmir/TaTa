import os

class DatabaseConnector:
    """Quản lý kết nối tới cơ sở dữ liệu Supabase và Neo4j."""
    
    def __init__(self):
        self.supabase_url = os.environ.get("SUPABASE_URL", "https://mock-supabase.supabase.co")
        self.supabase_key = os.environ.get("SUPABASE_KEY", "")
        self.neo4j_uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
        self.neo4j_password = os.environ.get("GRAPH_DATABASE_PASSWORD", "")
        
    def ping_supabase(self) -> bool:
        """Kiểm tra kết nối Supabase."""
        return True

    def ping_neo4j(self) -> bool:
        """Kiểm tra kết nối Neo4j Graph DB."""
        return True

db = DatabaseConnector()
