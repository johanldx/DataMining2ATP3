import os
import json
import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.preprocessing import StandardScaler, RobustScaler

class DataProcessor():
    def __init__(self):
        self.data = None
        self.df = None
        self._configure_progress_bar()

    def _configure_progress_bar(self):
        """Configure tqdm pour afficher les barres de progression dans Pandas."""
        tqdm.pandas()

    def load(self, data: dict):
        """Charge les données depuis un dictionnaire."""
        try:
            self.data = data
            print("Dataset chargé depuis le dictionnaire fourni.")
        except Exception as e:
            raise Exception(f"Erreur lors du chargement du dataset depuis le dictionnaire : {e}")
        return self

    def load_from_file(self, file_path: str):
        """Charge un fichier JSON."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                self.data = json.load(file)
            print(f"Dataset chargé depuis : {file_path}")
        except Exception as e:
            raise Exception(f"Erreur lors du chargement du dataset : {e}")
        return self

    def clean_missing_and_outliers(self):
        """Nettoyage des données : suppression des valeurs manquantes et identification des valeurs aberrantes."""
        if self.data is None:
            raise Exception("Il n'y a pas de données chargées.")
        
        stations = self.data
        if not stations:
            raise Exception("Aucun résultat trouvé dans les données.")
        
        print("Nettoyage des valeurs manquantes et aberrantes...")
        self.df = pd.DataFrame(tqdm(stations, desc="Création du DataFrame"))
        
        self.df.replace("", np.nan, inplace=True)
        
        self.df["latitude"] = self.df["latitude"].astype(float) / 100000
        self.df["longitude"] = self.df["longitude"].astype(float) / 100000
        
        numeric_cols = ["latitude", "longitude"]
        for col in numeric_cols:
            scaler = RobustScaler()
            self.df[col] = scaler.fit_transform(self.df[[col]])
        
        print("Nettoyage terminé.")
        return self

    def prepare_data(self):
        """Préparation des données : normalisation et transformation des colonnes."""
        if self.df is None:
            raise Exception("Les données doivent être nettoyées avant d'être préparées.")
        
        print("Préparation des données...")
        
        numeric_cols = ["latitude", "longitude"]
        scaler = StandardScaler()
        self.df[numeric_cols] = scaler.fit_transform(self.df[numeric_cols])
        
        self.df["services"] = self.df["services"].progress_apply(
            lambda x: ", ".join(json.loads(x)["service"]) if x else np.nan
        )
        
        def extract_prices(prix):
            try:
                prix_list = json.loads(prix) if isinstance(prix, str) else prix
                if isinstance(prix_list, list):
                    return {item["@nom"]: float(item["@valeur"]) for item in prix_list}
            except (json.JSONDecodeError, TypeError, KeyError):
                pass
            return {}
        
        self.df["prix"] = self.df["prix"].progress_apply(extract_prices)
        
        prix_df = self.df["prix"].apply(pd.Series)
        self.df = pd.concat([self.df, prix_df], axis=1)
        self.df.drop(columns=["prix"], inplace=True)
        
        self.df["horaires"] = self.df["horaires"].progress_apply(
            lambda x: "; ".join(
                [
                    f"{j.get('@nom', 'Inconnu')} {j['horaire'].get('@ouverture', 'N/A')}-{j['horaire'].get('@fermeture', 'N/A')}"
                    for j in (json.loads(x)["jour"] if isinstance(x, str) and "jour" in json.loads(x) else [])
                    if isinstance(j, dict) and "horaire" in j and isinstance(j["horaire"], dict)
                ]
            ) if x else np.nan
        )
        
        print("Préparation des données terminée.")
        return self

    def summarize_data(self):
        """Résumé des données : génère des statistiques descriptives sur les colonnes clés."""
        if self.df is None:
            raise Exception("Les données doivent être nettoyées et préparées avant d'être résumées.")
        
        print("Résumé des données :")
        summary = self.df.describe(include="all")
        print(summary)
        return self

    def save(self, file_path: str="data/dataset.json"):
        """Sauvegarde les données nettoyées."""
        if self.df is None:
            raise Exception("Aucune donnée nettoyée à sauvegarder. Exécutez les étapes précédentes d'abord.")
        
        try:
            self.df.to_json(file_path, orient="records", force_ascii=False, indent=4)
            print(f"Données nettoyées sauvegardées dans : {file_path}")
        except Exception as e:
            raise Exception(f"Erreur lors de la sauvegarde des données : {e}")
        return self

if __name__ == '__main__':
    processor = DataProcessor()
    processor.load_from_file("/data/row_dataset.json") \
        .clean_missing_and_outliers() \
        .prepare_data() \
        .summarize_data() \
        .save()
