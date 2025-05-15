# predictor/simulator.py

import numpy as np
import copy
from collections import defaultdict
from .features import Features
from .league_rules import LeagueRules

class MonteCarloSimulator:
    def __init__(self, config, rules: LeagueRules):
        self.n_simulacions = config.N_SIMULACIONS
        self.rules = rules
        self.config = config

    def simulate_season(self, classificacio, historic, partits):
        equips = classificacio['NOM'].tolist()
        comptador = {e: defaultdict(int) for e in equips}
        n_equips = len(equips)
        features = Features(classificacio, historic, self.config.ULTIMES_N_PARTITS_FORMA)

        # Simula n vegades
        for _ in range(self.n_simulacions):
            clf = {row['NOM']: {"PUNTS": int(row['PUNTS'])} for _, row in classificacio.iterrows()}
            # Simula totes les jornades restants
            for _, row in partits.iterrows():
                local, visitant = row['EQUIP_LOCAL'], row['EQUIP_VISITANT']

                # --- Factors --- #
                forma_local = features.get_recent_stats(local)
                forma_visitant = features.get_recent_stats(visitant)
                pos_local = features.get_posicio(local)
                pos_vis = features.get_posicio(visitant)

                # --- Probabilitat de victòria local/empat/derrota --- #
                base_home = self.config.PES_LOCAL
                score_local = (self.config.PES_FORMA_RECIENT * forma_local['W'] +
                               base_home +
                               self.config.PES_CLASSIFICACIO * (1 - pos_local / n_equips))
                score_visitant = (self.config.PES_FORMA_RECIENT * forma_visitant['W'] +
                                  self.config.PES_CLASSIFICACIO * (1 - pos_vis / n_equips))

                # Possible millora: sumar motivació per objectiu proper (descens/ascens)
                total = score_local + score_visitant
                prob_win = np.clip(score_local / total, 0, 0.98)
                prob_loss = np.clip(score_visitant / total, 0, 0.98)
                prob_draw = np.clip(1 - prob_win - prob_loss, 0.01, 0.25)

                # Simulació del resultat

                # Asegura que sumen 1 amb una petita normalització
                probs = np.array([prob_win, prob_draw, prob_loss])
                probs = np.clip(probs, 0, 1)  # Evita valors negatius/rars
                probs = probs / probs.sum()    # Normalitza sempre a suma 1

                resultat = np.random.choice(['W', 'D', 'L'], p=probs)
                
                if resultat == 'W':
                    clf[local]['PUNTS'] += 3
                elif resultat == 'D':
                    clf[local]['PUNTS'] += 1
                    clf[visitant]['PUNTS'] += 1
                elif resultat == 'L':
                    clf[visitant]['PUNTS'] += 3

            # Ordena la classificació final i assigna categories
            posicions = self.rules.classify(clf)
            cats = self.rules.assign_categories(posicions)
            for cat, equips_cat in cats.items():
                for e in equips_cat:
                    comptador[e][cat] += 1
            # Extra: guarda la posició final exacta per analítica detallada
            for i, equip in enumerate(posicions):
                comptador[equip][f"pos_{i+1}"] += 1

        # Calcula percentatges finals
        summary = {}
        for e in equips:
            summary[e] = {
                "ascens": round(100 * comptador[e]["ascens"] / self.n_simulacions, 2),
                "playoff": round(100 * comptador[e]["playoff"] / self.n_simulacions, 2),
                "mantenen": round(100 * comptador[e]["mantenen"] / self.n_simulacions, 2),
                "descens": round(100 * comptador[e]["descens"] / self.n_simulacions, 2),
                "posicions": {f"{i+1}": comptador[e][f"pos_{i+1}"] for i in range(n_equips)},
            }
        return summary
