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

### Limites

Caquot fournit une base de travail, pas une indexation définitive. Il ne vise
en aucun cas à se substituer à l'expertise humaine : son intérêt est d'offrir
un premier niveau d'indexation immédiatement exploitable sur des fonds qui
attendraient sinon des années un passage humain. La vérification de fiabilité
(par exemple par sondage d'un pourcentage de notices) reste à la charge de
l'institution, selon sa propre méthode.

#### Un score élevé n'est pas une garantie de pertinence

Le rapprochement se fait dans un espace vectoriel où deux éléments visuellement
proches (formes, composition, couleurs, etc.) ne sont pas nécessairement
proches sémantiquement. Un terme peut donc obtenir une similarité élevée sans
être pertinent. **Le taux de similarité ne suffit pas à écarter ce risque.**

Sur des fonds anciens et sensibles (photographie ethnographique, coloniale,
etc.), ces rapprochements "plausibles mais faux" peuvent produire des
associations de termes innappropriées, voire reconduire des préjugés présents
dans les données d'entraînement du modèle. Il s'agit d'une limite connue de la
méthode, pas d'un défaut de jeunesse appellé à disparaître. Il appartient à
l'institution de définir sa politique de traitement de ces limites.


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

Un thésaurus d'essai est disponible dans `/sample/thesaurus/th-representations.csv`.
Il est extrait du *Thésaurus iconographique, système descriptif des*
*représentations* de François Garnier (1984), thésaurus utilisé par les musées
de France. Bien que ses légendes ne respectent pas encore le guide développé
ci-après, il peut être intéressant de l'utiliser comme base.

#### Guide de rédaction des notes de thésaurus

Les modèles OpenCLIP proposés par Caquot ont appris à rapprocher images et
textes à partir de centaines de millions de paires image-légende collectées sur
le web. Le texte qu'on lui soumet fonctionne d'autant mieux qu'il ressemble à
ce qu'il a vu à l'entraînement : des phrases naturelles décrivant ce qu'on voit,
pas des notices de catalogue ou des définitions brutes de dictionnaire.

Ce guide de bonnes pratiques se base sur des résultats mesurés, il n'a pas
d'autres but que de vous aider à améliorer les résultats obtenus.

##### Principe directeur

Une note de thésaurus ne doit pas définir le terme, **elle doit décrire à quoi**
**il ressemble sur une photo**. (Radford et al., 2021)

##### Quand écrire une note

Ecrivez une note quand le terme remplit au moins une de ces conditions :
- **Polysémique**. Le mot désigne deux choses visuellement différentes (ex.
"grue" : oiseau ou engin de chantier). Sans contexte, le modèle ne sait pas 
trancher. (Radford et al., 2021)
- **Visuellement ambigu ou potentiellement peu représenté** dans les données
d'entraînement. Valable pour du vocabulaire technique, des régionalisme, un
terme daté, etc.
- **Sa forme écrite ne suffit pas à en déduire l'apparence**. Un nom technique,
de matière ou de procédé, etc.

##### Quand s'abstenir

N'écrivez pas de note quand :
- **Terme univoque et/ou courant**. Ajouter du texte n'aide pas, cela ajoute un
signal/bruit redondant (ex. "vélo", "chaise").
- **Nom propre, lieu ou gentillé**. Ces noms n'ont pas de définition visuelle
stable, il est d'ailleurs conseillé de les retirer du thésaurus donné au
programme.
- **Sens du terme incertain**. Si vous n'êtes pas sûr du sens exact du terme,
une note imprécise ou erronée est pire qu'une absence de note : elle pousse le
modèle dans un mauvais sens.

Une note trop générique ou bruitée, typiquement le cas d'une définition de
dictionnaire systématique, tent à diluer la spécificité sémantique plutôt qu'à
l'améliorer (Bhattacharya et al., 2026).
Il vaut mieux **une seule bonne note ciblée que dix notes vagues** et mieux
vaut **l'absence de note qu'une note qui n'apporte rien**.

##### Quoi écrire : décrire plutôt que définir

Le contenu avec le plus d'impact positif est le **descripteur visuel concret** :
forme, matière, couleur, texture, posture, disposition, etc.

| Terme | A éviter | A privilégier |
|---|---|---|
| Agriculture | "Utiliser ce terme pour les scènes de travail agricole en général, préférer un terme plus spécifique si possible" | "Scène de travail dans les champs : labour, semailles, moisson, ou soin du bétail" |
| Dentelle | "Textile obtenu par un procédé de fabrication à la main ou à la machine" | "Tissu ajouré à motifs fins, souvent blanc ou écru et utilisé en bordure de linge" |
| Liage des herbes | "Liage des gerbes (substantif masculin) : Opération mécanique ou manuelle de ligature consistant à enserrer et fixer une quantité délimitée de tiges de céréales coupées au moyen d'un lien (paille, ficelle ou fil de fer), afin de constituer une unité de manutention transitoire appelée gerbe." | "Liage des gerbes de blé après la moisson, travail agricole traditionnel" |

##### Restez concis

Deux raisons concrètes :
- Le modèle tronque le texte au-delà d'une longueur fixe (77 tokens pour les
modèles recommandés par Caquot). Une note trop longue, ajoutée à un chemin
hiérarchique profond risque de faire disparaître une partie de l'information.
- Les modèles multilingues utilisés par Caquot font une moyenne non pondérée de
tous les mots du texte. Chaque mot ajouté compte autant que les autres dans le 
résultat final : une note trop longue ou générale dilue le poids du terme. Ce
point sera amélioré dans l'une des future version du programme.

**Limitez-vous à une quinzaine de mots et mettez l'information importante en premier.**


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
**Attention, ne déplacez vos images entre deux sessions si vous comptez les**
**vectoriser à nouveau avec un autre modèle.** Le logiciel garde en mémoire le
chemin de l'image et non pas une copie de celle-ci. 

Caquot a été testé sur un fonds photographique du début du XXe s. et est pensé
pour indexer la représentation de l'image. Néanmoins, vous pouvez faire des
tentatives avec d'autres types de thésaurus (matériaux, techniques, couleurs,
etc.), peut-être que Caquot sera adapté à votre projet !

#### Quelle qualité photo donner au programme

Il est conseillé de donner des images de bonne qualité, c'est-à-dire sans bruit
autour de l'objet (éviter tout ce qui ne concerne pas l'objet, tel que les
réserves en fond par exemple : toute distraction emmenera le modèle sur de
fausses pistes), nettes, correctement éclairées et exposées et de bonne
résolution. Néanmoins, **le modèle redimensionne et tronque de lui même l'image**
**à un format carré de 224 x 224 pixels**, ce qui constitue actuellement la
taille minimal à fournir. Une mise à jour future de Caquot prévoit de mieux
exploiter la résolution de l'image : elle sera d'abord vectorisée dans son
ensemble, puis décupée en 9 parties, qui seront vectorisée à leur tour. Lors de
l'alignement, la correspondance entre le(s) terme(s) et chacune des 9 parties
sera combinée avec celle de l'image entière, avec une pondération permettant de
mieux prendre en compte à la fois le contexte général de l'image et ses détails. 


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


### Recherche en Langage Naturel

Le projet propose une fonction **expérimentale** de recherche en langage naturel.
Elle est accessible depuis le menu principal. Dès lors, plusieurs
fonctions de recherche vous sont proposées :
- texte / image
- texte / texte
- image / image [en cours de développement]

Les résultats ne sont pas exportables, ni sauvegardables aujourd'hui, cette
fonction est encore de l'ordre de l'expérimentation.  

Ici encore, les meilleurs résultats ne sont pas forcéments les plus pertinents
(cf. Un score élevé n'est pas une garantie de pertinence).

#### Recherche texte / image

Cette fonction se rapproche beaucoup du fonctionnement général de Caquot, sauf
qu'au lieu d'un thésaurus fermé, vus pouvez utiliser n'importe quel terme ou
phrase.
Cette recherche permet de balayer **toutes** les images enregistrées dans la
base de données et d'en sortir les résultats les plus proches.

La recherche en langage naturel permet autant une recherche par terme unique que
par phrase entière. Vous pouvez aussi bien écrire `chien` que `une image d'un`
`chien noir assis à côté d'un enfant devant une maison à colombages`. Ici
encore, nous vous conseillons de suivre les recommandations de légendage
(cf. Guide de rédaction des notes de thésaurus) : soyez concis, écrivez une
recherche visuelle (couleur, forme, position), et préférez débuter votre
recherche par `une image de ...` (car cela correspond au "formatage" des
données d'entraînement des modèles proposés par Caquot).

#### Recherche texte / texte

Cette fonction permet une recherche en langage naturel dans un thésaurus. Elle
peut permettre de trouver les termes les plus adaptés lors d'une indexation
manuelle.

#### Recherche image / images [en cours de développement]

Cette fonction permet de trouver les images visuellements proches depuis une
image donnée. C'est le même principe de fonctionnement que *Google Lens* par
exemple.


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