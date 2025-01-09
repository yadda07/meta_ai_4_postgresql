import requests

class DeepSeekAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def query(self, prompt: str) -> str:
        """
        Envoie une requête à l'API DeepSeek.
        
        Args:
            prompt (str): La question ou l'instruction à envoyer à l'API.
            
        Returns:
            str: La réponse de l'API.
        """
        url = 'https://api.deepseek.com/v1/chat/completions'
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            response = requests.post(url, json=data, headers=self.headers)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                raise Exception(f"Erreur API DeepSeek: {response.status_code}, {response.text}")
        except Exception as e:
            raise Exception(f"Erreur lors de la requête à DeepSeek: {str(e)}")