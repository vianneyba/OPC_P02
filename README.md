# Fonctionnalités

Script permettant la récupération des informations a partir du site (fictif) [Books to Scrape](http://books.toscrape.com/) de livre.

# Utilisation

## Création de l'environnement virtuel

taper: *python -m venv env*

activer l'environement: *source env/bin/activate*

installer les dependance: *pip install -r requirements.txt*

## Lancement du script

pour la récupération de tous les livres de chaque catégories (avec les couvertures):

*python3 main.py*

sans la récupération des couvertures:

*python3 main.py -ni*

pour lister les catégories:

*python3 main.py -l*

récupération d'une seule catégorie:

*python3 main.py "Sports and Games"*

