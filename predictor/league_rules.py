# predictor/league_rules.py

class LeagueRules:
    def __init__(self, n_ascens=2, n_playoff=4, n_descens=5):
        self.n_ascens = n_ascens
        self.n_playoff = n_playoff
        self.n_descens = n_descens

    def classify(self, classificacio_dict):
        # Retorna equips ordenats per punts i, en cas d'empat, criteri secundari
        ordenats = sorted(classificacio_dict.items(), key=lambda x: (-x[1]['PUNTS'], x[0]))
        posicions = [equip for equip, _ in ordenats]
        return posicions

    def assign_categories(self, posicions):
        # Retorna dict amb les llistes d'equips a cada zona
        return {
            "ascens": posicions[:self.n_ascens],
            "playoff": posicions[self.n_ascens:self.n_ascens + self.n_playoff],
            "descens": posicions[-self.n_descens:],
            "mantenen": posicions[self.n_ascens + self.n_playoff : -self.n_descens]
        }
