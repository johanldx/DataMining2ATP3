import requests
import os
import json
from tqdm import tqdm

class APIClient:
    def __init__(self):
        self.__base_url = 'https://data.opendatasoft.com/api/explore/v2.1'
        self.data = None

    def list_datasets(self):
        """Liste les datasets disponibles."""
        print("Récupération de la liste des datasets...")
        try:
            response = requests.get(f'{self.__base_url}/catalog/datasets')
            response.raise_for_status()
            print("Liste des datasets récupérée avec succès.")
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Erreur de connexion: {e}")

    def get_dataset(self, dataset_name: str, file_path: str="__DEFAULT__"):
        """Télécharge un dataset et affiche une barre de progression."""
        print("Téléchargement du dataset...")
        try:
            url = f'{self.__base_url}/catalog/datasets/{dataset_name}/exports/json'
            with requests.get(url, stream=True) as response:
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))
                block_size = 1024
                
                if file_path == "__DEFAULT__":
                    file_path = '../data/row_' + dataset_name + '.json'
                
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                with open(file_path, "wb") as file, tqdm(total=total_size, unit='iB', unit_scale=True, desc="Téléchargement") as bar:
                    for data in response.iter_content(block_size):
                        file.write(data)
                        bar.update(len(data))

                with open(file_path, "r+", encoding="utf-8") as file:
                    data = json.load(file)
                    file.seek(0)
                    json.dump(data, file, indent=4, ensure_ascii=False)
                    file.truncate()

                print(f"Dataset téléchargé et sauvegardé dans : {file_path}")
                self.data = data
                return True
        except requests.RequestException as e:
            raise Exception(f"Erreur de connexion: {e}")

if __name__ == '__main__':
    client = APIClient()
    client.get_dataset("prix-des-carburants-en-france-flux-instantane-v2@opendatamef")
