# Caquot - Indexation automatisée d'images patrimoniales depuis un thésaurus

## De quoi parle-t-on

Caquot est une application Python légère qui s'utilise depuis un terminal.

Son but est **d'accélérer le flux de travail d'indexation d'images depuis un**
**thésaurus**, voire de produire des descriptions automatisées. Les données
produites sont destinées à être intégrées dans un système de gestion de base de
données.

Elle s'adresse en priorité aux institutions culturelles, publiques ou privées,
chargées d'étudier des collections photographiques.

Caquot devrait fonctionner sous Linux et Windows, néanmoins, son fonctionnement
n'est actuellement garanti que sous Linux.

### Généralités

Se basant sur des centaines de millions de paires image-texte collectées sur
internet, un modèle "CLIP" est capable de "vectoriser" une image, c'est-à-dire
traduire la représentation d'une image en une suite de coordonnées
mathématiques dans l'espace vectoriel du modèle. Ces coordonnées peuvent
ensuite être rapprochées de coordonnées d'un terme ou d'une autre image : cela
permet de mettre sur un même plan une image de chat et le mot "chat". Ce
fonctionnement est, dans ce projet, élargi à un thésaurus : chaque terme est
vectorisé l'un après l'autre et ses coordonnées sont stockées dans une base de
données. Ensuite, l'utilisateur fournit des images, elles sont vectorisées une
à une et leurs coordonnées stockées dans la même base de données. Puis, un
script rapproche les coordonnées "image" des coordonnées "thésaurus" et une
sélection des *n* candidats les plus proches est faite et est stockée dans une
autre table. Enfin, l'export récupère chaque image et extrait le numéro
d'inventaire contenu dans le nom du fichier, crée un fichier *csv* et y inscrit
le numéro d'inventaire, la liste des identifiants des termes du thésaurus, le
score de similarité pour chaque terme, ainsi que le modèle CLIP utilisé.

Améliorations futures : Un grand modèle de langage (LLM) avec une capacité
"vision" décrit succinctement chaque image, et cette production est ensuite
stockée dans la base de données. Une fois que le modèle CLIP a vectorisé chaque
image et que le rapprochement donne une liste des *n* termes les plus proches,
un second LLM vision regarde l'image et compare la description aux termes issus
du rapprochement, puis il sélectionne à son tour, dans le lot, les quelques
termes les plus adéquats.


## Installation

### Prérequis

Caquot nécessite **Python 3**.

Configuration :
- RAM : 8 Go recommandés
- GPU : recommandé pour accélérer la vectorisation et permettre l'utilisation
de modèles plus lourds

### Installation

Cloner le dépôt :
```bash
git clone https://github.com/murypaul/caquot.git
cd caquot
```

## Mode d'emploi

### Lancer Caquot

Linux :
```bash
./run.sh
```

Windows :
Double-clic sur `run.bat`

Au premier lancement, `run.sh`/`run.bat` crée un Environnement virtuel Python
et installe les dépendances nécessaires.

### Ajouter un thésaurus

Il faut commencer par ajouter un thésaurus en base. Le seul format accepté
actuellement est un tableur `csv` avec les colonnes suivantes :
"ID", "LABEL", "PARENT_ID", "PATH", "NOTES" où
ID = identifiant du terme
LABEL = le terme
PARENT_ID = identifiant du terme parent
PATH = chemin hiérarchique complet ("transport > véhicule > voiture")
NOTES = notes éventuelles permettant de contextualiser le terme

| /!\ Il est vivement recommandé de préparer votre thésaurus, de retirer les
| termes que le modèle ne pourrait pas associer de façon fiable (lieux
| géographiques, noms propres, noms de groupes, etc.).
| **La qualité des résultats dépend directement de la qualité du contexte**
| **donné à chaque terme**.

### Ajouter un modèle OpenCLIP

Deux modèles multilingues ont été testés et sont actuellement recommandés. Ils
sont proposés directement dans Caquot ; leurs poids seront toutefois
téléchargés lors de leur première utilisation.

D'autres modèles peuvent être trouvés sur le site :
[HuggingFace](https://huggingface.co/models?library=open_clip)

Dans ce second cas, attention à prendre un modèle adapté à la langue de votre
thésaurus.

### Vectoriser

Une fois le thésaurus et le modèle chargé dans la base de données du logiciel,
il est nécessaire de vectoriser les termes du thésaurus.

Puis, vous pouvez vectoriser les images que vous souhaitez.
Attention, ne déplacez vos images entre deux sessions si vous comptez les
vectoriser à nouveau avec un autre modèle. Le logiciel garde en mémoire le
chemin de l'image et non pas une copie de celle-ci. 

Caquot a été testé sur un fonds photographique du début du XXe s. et est pensé
pour indexer la représentation de l'image. Néanmoins, vous pouvez faire des
tentatives avec d'autres types de thésaurus (matériaux, techniques, couleurs,
etc.), peut-être que Caquot sera adapté à votre projet !

### Rapprocher

Maintenant que la base contient les vecteurs de votre thésaurus ainsi que ceux
de vos images, vous pouvez lancer le rapprochement des vecteurs.

### Exporter

L'export vous fournit un tableur `csv` qu'il vous suffira d'importer dans votre
base de données.
Il y référence les identifiants des termes des thésauri utilisés, le score de
similarité et le modèle utilisé par chaque terme. A vous de décider, lors de
votre import, si vous souhaitez référencer ces métadonnées de production.

Le tableur regroupe par numéro d'inventaire en se basant sur le nommage des
fichiers. Il est actuellement adapté à la norme "Musée de France"
(`[année].[lot].[objet/sous-lot](.[objet])` - ex. 2026.1.5 ou 2026.1.5.1) et
considère un nommage au format suivant :
- 2026_1_5_1.png > 2026.1.5.1 (suffixe `-POS` ignoré dans la detection)

Par son architecture même, Caquot n'est pas pensé pour du stockage à long terme
de vos données, il est donc fortement conseillé de les exporter et de garder
des copies externes.

### Supprimer les données du projet

Linux
```bash
rm data/data.db`
```
Windows
Mettre à la corbeille le fichier `data.db` dans le dossier `data/`.

## Développement et Contributions

### Développement

Nous sommes ouverts à tous vos projets !

Si vous avez un besoin particulier (s'adapter au nommage de vos images, ajouter
une fonctionnalité, etc.), nous serions ravis de pouvoir en discuter avec vous
et de trouver une solution. Dans ce cas là, n'hésitez pas à nous contacter.

### Contributions

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir un ticket pour
discuter de vos souhaits et ajouts.
N'oubliez pas de documenter vos apports.