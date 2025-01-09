class MetadataAnalyzer:
    def __init__(self, db_connector):
        self.db_connector = db_connector

    def get_metadata_attributes(self):
        """Récupère les métadonnées depuis la table metadata.attributs."""
        query = """
            SELECT id, "schema", "table", nom_attr, type, contraint, relation, description
            FROM metadata.attributs
        """
        return self.db_connector.execute_query(query)

    def get_column_description(self, schema: str, table: str, column: str):
        """Récupère la description d'une colonne spécifique."""
        query = f"""
            SELECT description
            FROM metadata.attributs
            WHERE "schema" = '{schema}' AND "table" = '{table}' AND nom_attr = '{column}'
        """
        result = self.db_connector.execute_query(query)
        return result[0]['description'] if result else "Aucune description disponible"