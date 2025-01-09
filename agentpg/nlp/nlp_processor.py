import spacy

class NLPProcessor:
    def __init__(self):
        self.nlp = spacy.load('fr_core_news_lg')

    def analyze_question(self, question: str) -> dict:
        """
        Analyse une question pour en extraire les mots-clés et les entités.
        
        Args:
            question (str): La question à analyser.
            
        Returns:
            dict: Les mots-clés, entités, verbes et noms extraits.
        """
        doc = self.nlp(question.lower())
        keywords = set()
        entities = []

        for token in doc:
            if not token.is_stop and not token.is_punct:
                keywords.add(token.lemma_)
            if token.ent_type_:
                entities.append({
                    'text': token.text,
                    'type': token.ent_type_
                })

        return {
            'keywords': list(keywords),
            'entities': entities,
            'verbs': [token.lemma_ for token in doc if token.pos_ == 'VERB'],
            'nouns': [token.lemma_ for token in doc if token.pos_ == 'NOUN']
        }