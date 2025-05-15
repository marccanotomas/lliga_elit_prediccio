# config.py

# Nombre de simulacions Monte Carlo per defecte
N_SIMULACIONS = 10000

# Nombre de partits considerats per a calcular la forma recent
ULTIMES_N_PARTITS_FORMA = 5

# PESOS per a la probabilitat de resultat, ajustables segons importància percebuda
# (pots experimentar-hi lliurement!)

# Avantatge per ser local (típic: entre 1.05 i 1.25)
PES_LOCAL = 1.12

# Importància de la forma recent (típic: entre 0.8 i 1.5)
PES_FORMA_RECIENT = 1.1

# Pes de la classificació (posició relativa: més alt = més influència del rànquing)
PES_CLASSIFICACIO = 0.8

# Pes extra per “motivació” en cas de jugar-se l’ascens o el descens
PES_IMPORTANCIA = 1.2

# (Opcional) Factor de sort addicional (ajuda a randomitzar una mica)
FACTOR_RANDOM = 0.03  # Pots posar-ho a zero si vols simulació més determinista

# (Extensible) Pots afegir colors o config de visuals aquí també!
PRIMARY_COLOR = "#23395d"
SECONDARY_COLOR = "#FFD700"
SUCCESS_COLOR = "#2e8b57"
