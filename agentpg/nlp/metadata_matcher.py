from fuzzywuzzy import fuzz
from collections import defaultdict

class MetadataMatcher:
    def __init__(self):
        self.table_keywords = defaultdict(set)
        self.column_keywords = defaultdict(set)

    def compute_metadata_keywords(self, metadata: list):
        """Extrait les mots-clés des métadonnées."""
        for row in metadata:
            schema = row.get('schema')
            table_name = row.get('table')
            column_name = row.get('nom_attr')
            description = row.get('description', '').lower()
            
            # Mots-clés de la table
            self.table_keywords[(schema, table_name)].add(table_name.lower())
            if description:
                desc_words = description.split()
                self.table_keywords[(schema, table_name)].update(desc_words)
            
            # Mots-clés des colonnes
            self.column_keywords[(schema, table_name, column_name)].add(column_name.lower())
            if description:
                desc_words = description.split()
                self.column_keywords[(schema, table_name, column_name)].update(desc_words)

    def find_matches(self, keywords: list, threshold: float = 0.6) -> dict:
        """
        Trouve les correspondances entre les mots-clés et les métadonnées.
        
        Args:
            keywords (list): Les mots-clés à comparer.
            threshold (float): Le seuil de correspondance.
            
        Returns:
            dict: Les tables et colonnes correspondantes.
        """
        matches = {'tables': [], 'columns': []}

        for (schema, table), table_keywords in self.table_keywords.items():
            score = max(fuzz.ratio(kw, tk) / 100 for kw in keywords for tk in table_keywords)
            if score > threshold:
                matches['tables'].append({
                    'schema': schema,
                    'table': table,
                    'score': score
                })

        for (schema, table, column), col_keywords in self.column_keywords.items():
            score = max(fuzz.ratio(kw, ck) / 100 for kw in keywords for ck in col_keywords)
            if score > threshold:
                matches['columns'].append({
                    'schema': schema,
                    'table': table,
                    'column': column,
                    'keywords': list(col_keywords),
                    'score': score
                })

        # Tri par score
        matches['tables'].sort(key=lambda x: x['score'], reverse=True)
        matches['columns'].sort(key=lambda x: x['score'], reverse=True)

        return matches