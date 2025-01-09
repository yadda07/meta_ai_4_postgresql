import psycopg2
from psycopg2.extras import RealDictCursor

class DBConnector:
    def __init__(self, db_params: dict):
        self.db_params = db_params

    def connect(self):
        """Établit une connexion à la base de données."""
        return psycopg2.connect(**self.db_params)

    def execute_query(self, query: str):
        """
        Exécute une requête SQL et retourne les résultats.
        
        Args:
            query (str): La requête SQL à exécuter.
            
        Returns:
            list: Les résultats de la requête.
        """
        with self.connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                if query.lower().strip().startswith('select'):
                    return cur.fetchall()
                return "Requête exécutée avec succès"