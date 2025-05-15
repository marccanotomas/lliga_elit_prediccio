# predictor/features.py

import pandas as pd
from collections import defaultdict

class Features:
    def __init__(self, classificacio, historic, ultim_n_partits=5):
        self.classificacio = classificacio
        self.historic = historic
        self.ultim_n_partits = ultim_n_partits
        self.forma_equips = self._calcula_forma_equips()

    def _calcula_forma_equips(self):
        forma = defaultdict(list)
        for _, row in self.historic.iterrows():
            local, visitant = row['EQUIP_LOCAL'], row['EQUIP_VISITANT']
            gl, gv = row['GOLS_LOCAL'], row['GOLS_VISITANT']
            if pd.isnull(gl) or pd.isnull(gv): continue

            # Resultat
            if gl > gv:
                forma[local].append('W')
                forma[visitant].append('L')
            elif gl < gv:
                forma[local].append('L')
                forma[visitant].append('W')
            else:
                forma[local].append('D')
                forma[visitant].append('D')
        return forma

    def get_recent_stats(self, equip):
        partits = self.forma_equips.get(equip, [])
        recents = partits[-self.ultim_n_partits:]
        n = len(recents)
        w = recents.count('W') / n if n else 0
        d = recents.count('D') / n if n else 0
        l = recents.count('L') / n if n else 0
        return {'W': w, 'D': d, 'L': l}

    def get_posicio(self, equip):
        row = self.classificacio[self.classificacio['NOM'] == equip]
        if not row.empty:
            return int(row.iloc[0]['POS'])
        return None

    def get_forma_local_visitant(self, equip, home=True):
        # Més endavant: podem diferenciar resultats local/visitant!
        # Ara mateix retorna la forma general
        return self.get_recent_stats(equip)
