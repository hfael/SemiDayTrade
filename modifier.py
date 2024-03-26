import os

repertoire_script = os.path.dirname(os.path.abspath(__file__))

# Récupérer le nom du fichier en cours d'exécution (ce script)
nom_script = os.path.basename(__file__)

# Récupérer le contenu du modèle depuis le fichier sélectionné
modele_file = "enter main model file here"  # Mettez à jour le chemin du modèle
with open(modele_file, "r") as modele_file:
    modele = modele_file.read()

# Parcourir les fichiers .py dans le répertoire du script
for nom_fichier in os.listdir(repertoire_script):
    if nom_fichier.endswith(".py") and nom_fichier != nom_script and nom_fichier != "RUNNING.py" and nom_fichier != "messageEvent.py" and nom_fichier != "OrderUtils.py" and nom_fichier != "SemiDayTrade.py":
        chemin_fichier = os.path.join(repertoire_script, nom_fichier)

        # Lire le contenu du fichier d'origine
        with open(chemin_fichier, "r") as fichier_origine:
            contenu_origine = fichier_origine.read()

        # Modifier le contenu avec le modèle
        contenu_modifie = modele  # Utilisez le modèle pour la modification

        # Écrire le contenu modifié dans un nouveau fichier avec le même nom
        with open(chemin_fichier, "w") as fichier_modifie:
            fichier_modifie.write(contenu_modifie)

        print(f"Fichier {nom_fichier} modifié avec succès.")

input("Appuyez sur Entrée pour quitter.")
