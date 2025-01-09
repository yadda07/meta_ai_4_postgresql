import logging
from database.db_connector import DBConnector
from database.metadata_analyzer import MetadataAnalyzer
from nlp.nlp_processor import NLPProcessor
from nlp.metadata_matcher import MetadataMatcher
from api.deepseek_api import DeepSeekAPI
from smolagents import Tool, CodeAgent, HfApiModel

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExecuteSqlTool(Tool):
    """
    Outil pour exécuter des requêtes SQL sur la base de données PostgreSQL.
    """
    description = "Exécute une requête SQL sur la base de données PostgreSQL"
    name = "execute_sql"
    inputs = {
        "query": {
            "type": "string",
            "description": "La requête SQL à exécuter"
        }
    }
    output_type = "string"

    def __init__(self, db_connector):
        self.db_connector = db_connector
        super().__init__()

    def forward(self, query: str) -> str:
        """
        Exécute une requête SQL et retourne les résultats.
        
        Args:
            query (str): La requête SQL à exécuter.
            
        Returns:
            str: Les résultats de la requête ou un message d'erreur.
        """
        try:
            return str(self.db_connector.execute_query(query))
        except Exception as e:
            logger.error(f"Erreur SQL: {str(e)}")
            return f"Erreur: {str(e)}"


class AssistantBD:
    def __init__(self, deepseek_api_key: str = None):
        self.db_params = {
            "host": "11.241.258.107",
            "port": "5432",
            "dbname": "db",
            "user": "yadda",
            "password": "pwd"
        }
        
        try:
            self.db_connector = DBConnector(self.db_params)
            self.metadata_analyzer = MetadataAnalyzer(self.db_connector)
            self.nlp_processor = NLPProcessor()
            self.metadata_matcher = MetadataMatcher()
            self.deepseek_api = DeepSeekAPI(deepseek_api_key) if deepseek_api_key else None

            # Charger les métadonnées
            metadata = self.metadata_analyzer.get_metadata_attributes()
            self.metadata_matcher.compute_metadata_keywords(metadata)

            sql_tool = ExecuteSqlTool(self.db_connector)
            self.agent = CodeAgent(
                tools=[sql_tool],
                model=HfApiModel()
            )
            logger.info("Assistant initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur d'initialisation: {str(e)}")
            raise

    def poser_question(self, question: str) -> str:
        logger.info(f"Question reçue: {question}")
        
        # Analyse de la question
        analysis = self.nlp_processor.analyze_question(question)
        matches = self.metadata_matcher.find_matches(analysis['keywords'])
        
        # Construction du prompt avec les métadonnées correspondantes
        metadata_info = "\n".join([
            f"Table: {match['table']}, Colonne: {match['column']} (Score: {match['score']})"
            for match in matches['columns']
        ])
        
        prompt = f"""
        Tu es un expert en SQL PostgreSQL. Traduis et exécute la requête suivante:

        Question: {question}

        Métadonnées correspondantes:
        {metadata_info}

        Instructions:
        1. Analyse la question
        2. Crée la requête SQL appropriée en utilisant les métadonnées
        3. Utilise execute_sql avec le paramètre 'query'
        4. Retourne les résultats

        Exemple:
        Si tu veux compter les schémas:
        execute_sql(query="SELECT COUNT(DISTINCT schema_name) FROM information_schema.schemata")
        """
        
        try:
            # Essayer d'abord avec smolagents
            reponse = self.agent.run(prompt)
            logger.info("Réponse générée avec smolagents")
            return reponse
        except Exception as e:
            logger.error(f"Erreur avec smolagents: {str(e)}")
            if self.deepseek_api:
                # Basculer vers DeepSeek en cas d'échec
                logger.info("Basculement vers DeepSeek...")
                return self.deepseek_api.query(prompt)
            else:
                return f"Erreur: {str(e)} (et aucune clé API DeepSeek fournie)"

def main():
    """
    Point d'entrée principal du programme.
    """
    print("=== Assistant Base de Données PostgreSQL ===")
    print("Initialisation...")
    
    try:
        # Remplacez par votre clé API DeepSeek si disponible
        deepseek_api_key = 'sk-fac17677c6554d9cbc8f375c028588e8'
        assistant = AssistantBD(deepseek_api_key)
        print("Assistant prêt !")
        
        while True:
            try:
                question = input("\nVotre question (ou 'q' pour quitter) : ").strip()
                if question.lower() == 'q':
                    break
                    
                print("\nTraitement en cours...")
                reponse = assistant.poser_question(question)
                print(f"\nRéponse: {reponse}")
                
            except KeyboardInterrupt:
                print("\nArrêt demandé")
                break
            except Exception as e:
                print(f"\nErreur: {str(e)}")
                logger.exception("Erreur pendant l'exécution")
                
    except Exception as e:
        print(f"Erreur critique: {str(e)}")
        logger.exception("Erreur critique")
        return 1
    
    print("\nAu revoir !")
    return 0

if __name__ == "__main__":
    exit(main())