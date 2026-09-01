# Caquot - Indexation automatisée d'images patrimoniales depuis un thésaurus

## De quoi parle-t-on

Caquot est une application python légère, accessible en CLI.

Son but est **d'accelérer le flux de travail d'indexation d'images depuis un**
**thésaurus**, voire de produire des descriptions automatisées. Les données
produites sont destinées à être intégrées dans un système de gestion de base de
données.

### Généralités

Se basant sur des centaines de millions de paires image-texte collectées sur
internet, un modèle "CLIP" est capable de "vectoriser" une image, c'est-à-dire
traduire la représentation d'une image en une suite de coordonnées
mathématiques dans l'espace vectoriel du modèle. Ces coordonnées peuvent
ensuite être rapprochées de coordonnées d'un terme ou d'une autre image : cela
permet de mettre sur un même plan une image de chat et le mot "chat". Ce
fonctionnement est, dans ce projet, élargi à un thésaurus : chaque terme est
vectorisé l'un après l'autre et ses coordonnées sont stockées dans une base de
données. Ensuite, l'utilisateur fourni des images, elles sont vectorisées une à
une et leurs coordonnées stockées dans la même base de données. Puis, un script
rapproche les coordonnées "image" des coordonnées "thésaurus" et une sélection
des *n* candidats les plus proches est faite et est stockée dans une autre
table. Enfin, l'export récupère chaque image et extrait le numéro d'inventaire
contenu dans le nom du fichier, crée un fichier *csv* et y inscrit le numéro
d'inventaire, la liste des identifiants des termes du thésaurus, le score de
similarité pour chaque terme, ainsi que le modèle CLIP utilisé.

Améliorations futures : Un grand modèle de langage (LLM) avec une capacité
"vision" décrit succinctement chaque image, et cette production est ensuite
stockée dans la base de données. Une fois que le modèle CLIP a vectorisé chaque
image et que le rapprochement donne une liste des *n* termes les plus proches,
un second LLM vision regarde l'image et compare la description aux termes issus
du rapprochement, puis il sélectionne à son tour, dans le lot, les quelques
termes les plus adéquats.


## Mode d'emploi

A faire à l'installation
```
cd dossier/du/dépôt
python3 -m venv venv # crée un environnement python
source venv/bin/activate # active l'environnement
pip install -r requirements.txt # installe les dépendances
```

Avant toute utilisation, il faut activer l'environnement python
`source venv/bin/activate`

Lancer la vectorisation
`python3 embed.py`

Lancer l'alignement des vectorisations
`python3 alignment.py`

Exporter les données
`python3 export.py`


Supprimer toutes les données du projet
`rm data/data.db`