# predictor/data_loader.py

import pandas as pd
import os

class DataLoader:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir

    def load_csv(self, filename):
        path = os.path.join(self.data_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Fitxer no trobat: {path}")
        df = pd.read_csv(path)
        return df

    def load_all(self):
        try:
            classificacio = self.load_csv("classificacio.csv")
            historic = self.load_csv("historic.csv")
            partits = self.load_csv("partits.csv")
            return classificacio, historic, partits
        except Exception as e:
            raise Exception(f"Error carregant dades: {e}")
