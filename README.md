# Caquot - Indexation automatisée d'images patrimoniales depuis un thésaurus

## De quoi parle-t-on

Caquot est une application Python légère qui s'utilise depuis un terminal.

Son but est **d'accélérer le flux de travail d'indexation d'images depuis un**
**thésaurus**, voire de produire des descriptions automatisées. Les données
produites sont destinées à être intégrées dans un système de gestion de base de
données.

Elle s'adresse en priorité aux institutions culturelles, publiques ou privées,
chargées d'étudier des collections photographiques.

Le fonctionnement est garanti sous Linux. Windows 11 est pris en charge mais
est encore en phase de test.

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


## Installation et mode d'emploi

### Prérequis

Caquot nécessite **Python 3.12, 3.13 ou 3.14** en **64 bits**.

Configuration :
- Windows 11 ou Linux, 64 bits,
- RAM : 8 Go recommandés,
- GPU : recommandé pour accélérer la vectorisation et permettre l'utilisation
de modèles plus lourds,
- Espace disque : 4 Go minimum (10 Go pour le grand modèle),
- internet pour l'installation et le premier téléchargement d'un modèle
(`huggingface.co` doit être accessible depuis le réseau de l'établissement)

**Vos images ne quittent jamais votre ordinateur.**

### Installation Windows 11

#### Étape 1 : installer Python

Caquot est écrit en Python, qu'il faut installer une seule fois.
**Versions acceptées : 3.12, 3.13 ou 3.14, en 64 bits.**

Si Python est déjà installé sur votre poste, passez à l'étape 2 : au premier
lancement, Caquot vérifie lui-même la version et vous prévient si elle ne
convient pas.

Sinon, deux possibilités :

- **Depuis le Microsoft Store** : cherchez **Python Install Manager**,
installez-le, puis ouvrez le **Terminal** (clic droit sur le bouton Démarrer ->
Terminal) et tapez `py install 3.14`, puis Entrée.
- **Depuis python.org** : page "Downloads" -> *Windows installer (64-bit)*
d'une version 3.14, puis suivez l'installateur en laissant les options par
défaut.

#### Étape 2 : télécharger Caquot

1. Ouvrez la page des versions publiées :
https://github.com/murypaul/caquot/releases
2. Sous la version la plus récente (étiquette **Latest**), ouvrez la rubrique
**Assets** et cliquez sur **Source code (zip)**.
3. Dans votre dossier Téléchargements, faites un clic droit sur le fichier
`caquot-<version>.zip` (par exemple `caquot-1.2.0.zip`) -> **Propriétés**. Si
une case **Débloquer** apparaît en bas, cochez-la puis validez : cela évite
les avertissements de sécurité au lancement.
4. Clic droit sur le ZIP -> **Extraire tout…**, et indiquez comme destination un
emplacement **court**, par exemple `C:\Caquot`.

Deux précautions :

- Évitez le `Bureau`, les `Documents` et tout dossier synchronisé par OneDrive :
un chemin trop long peut faire échouer l'installation (Caquot vous prévient si
c'est le cas).
- Ne lancez pas Caquot depuis l'intérieur du fichier ZIP : il faut l'extraire.

#### Étape 3 : premier lancement

1. Ouvrez `C:\Caquot`, puis le dossier `caquot-<version>` qu'il contient
(par exemple `caquot-1.2.0`).
2. Double-cliquez sur `Lancer-Caquot-Windows.bat`.
3. Si Windows affiche un avertissement, choisissez **Informations**
**complémentaires** puis **Exécuter quand même**, ou **Exécuter**. Ce message
apparaît pour tout fichier téléchargé qui n'est pas signé par un éditeur
commercial.
4. Une fenêtre s'ouvre : Caquot installe ses composants (environ 1 Go,
plusieurs Go si l'ordinateur a une carte graphique NVIDIA, détectée
automatiquement). **Cela dure de 5 à 20 minutes. Ne fermez pas la fenêtre.**
5. L'installation est terminée quand le **MENU PRINCIPAL** s'affiche.

Les fois suivantes, le même double-clic ouvre directement le menu. Si
l'installation est interrompue (coupure réseau…), relancez simplement le
programme : elle reprend du début.

#### Étape 4 : se servir des menus

Caquot s'utilise au clavier, la souris ne sert pas :

- tapez le **chiffre** de votre choix, puis **Entrée** ;
- aux questions `(O/N)`, tapez `O` pour oui ou `N` pour non, puis Entrée ;
- `0` ramène au menu précédent.

Quand Caquot demande un fichier ou un dossier, une fenêtre de sélection s'ouvre.
Si vous ne la voyez pas, cherchez-la dans la barre des tâches.

Attention : dans cette fenêtre noire, **Ctrl+C n'est pas "copier"** : il
interrompt le programme.

#### Étape 5 : premier essai complet

Préparez un dossier contenant quelques images (`.jpg`, `.jpeg`, `.png`, `.tif`
ou `.tiff`).

1. **Charger le thésaurus d'exemple.** Tapez `1` (Gérer les thésauri), puis `1`
(Charger). Sélectionnez `th-representation.csv` dans
`C:\Caquot\caquot-<version>\sample\thesaurus`. Donnez-lui un nom, par exemple
`Garnier`. Vérifiez l'aperçu et tapez `O`. Tapez `0` pour revenir.
2. **Charger un modèle.** Tapez `2` (Gérer les modèles), `1` (Charger), puis `1`
(modèle léger). À la question "Télécharger", tapez `O` : environ 1,5 Go.
**Rien ne s'affiche pendant le téléchargement** : attendez le retour au menu.
Tapez `0` pour revenir.
3. **Vectoriser le thésaurus.** Tapez `3` (Vectorisation), puis `1`. Sans carte
graphique, comptez quelques minutes pour les 4 848 termes du thésaurus
d'exemple.
4. **Vectoriser vos images.** Toujours dans ce menu, tapez `2`, puis `1`
(nouveau lot), et choisissez votre dossier d'images. Les fichiers illisibles
sont signalés à la fin. Tapez `0` pour revenir.
5. **Rapprocher.** Tapez `4` (Rapprochement / Export), puis `1`.
6. **Exporter.** Tapez `2`, choisissez un dossier de destination, puis répondez
`N` pour tout exporter. Le fichier s'appelle `caquot_export-` suivi de la
date et de l'heure.

> **Ouvrir l'export dans Excel** : un double-clic place tout dans la première
> colonne. Ouvrez plutôt Excel, onglet **Données** -> **À partir d'un fichier
> texte/CSV**, origine **65001 : Unicode (UTF-8)**, délimiteur **Virgule**.

Pendant les traitements longs, laissez la fenêtre ouverte et évitez la mise en
veille de l'ordinateur. Le travail déjà effectué est enregistré au fur et à
mesure (toutes les 20 images).

### Linux

Cloner le dépôt :
```bash
sudo apt install python3-venv python3-tk # (Debian / Ubuntu / Mint)
git clone https://github.com/murypaul/caquot.git
cd caquot
```

Lancer :
```bash
./run.sh
```

### Ajouter un thésaurus

Il faut commencer par ajouter un thésaurus en base. Le seul format accepté
actuellement est un tableur `csv` (séparateur : "," ou ";" et encodé en UTF-8
ou Windows-1252) avec les colonnes suivantes :
"ID", "LABEL", "PARENT_ID", "PATH", "NOTES" où
ID = identifiant du terme
LABEL = le terme
PARENT_ID = identifiant du terme parent
PATH = chemin hiérarchique complet ("transport > véhicule > voiture")
NOTES = notes permettant de contextualiser le terme (peut être vide)

| /!\ Il est vivement recommandé de préparer votre thésaurus, de retirer les
| termes que le modèle ne pourrait pas associer de façon fiable (lieux
| géographiques, noms propres, noms de groupes, etc.).
| **La qualité des résultats dépend directement de la qualité du contexte**
| **donné à chaque terme**.

Un thésaurus d'essai est disponible dans `sample/thesaurus/th-representation.csv`.
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

- CLIP ViT-B/32 XLM-R BASE - LAION-5B (env. 1,5 Go)
- CLIP ViT-H/14 F-XLM-R LARGE - LAION-5B (env. 4,8 Go)

D'autres modèles peuvent être trouvés sur le site :
[HuggingFace](https://huggingface.co/models?library=open_clip)

Dans ce second cas, attention à prendre un modèle adapté à la langue de votre
thésaurus.

### Vectoriser

Une fois le thésaurus et le modèle chargé dans la base de données du logiciel,
il est nécessaire de vectoriser les termes du thésaurus.

Puis, vous pouvez vectoriser les images que vous souhaitez.
**Attention, ne déplacez pas vos images entre deux sessions si vous comptez les**
**vectoriser à nouveau avec un autre modèle.** Le logiciel garde en mémoire le
chemin de l'image et non pas une copie de celle-ci. 

Les formats acceptés sont : `.jpg`, `.jpeg`, `.png`, `.tif`, `.tiff`.
Les sous-dossiers ne sont pas parcourus et les fichiers illisibles sont signalés.

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

L'export vous fournit un tableur `csv` (encodage : UTF-8, séparateur ",") qu'il
vous suffira d'importer dans votre base de données.
Il y référence les identifiants des termes des thésauri utilisés, le score de
similarité et le modèle utilisé par chaque terme. A vous de décider, lors de
votre import, si vous souhaitez référencer ces métadonnées de production.

Le tableur regroupe par numéro d'inventaire en se basant sur le nommage des
fichiers. Il est actuellement adapté à la norme "Musée de France"
(`[année].[lot].[objet/sous-lot](.[objet])` - ex. 2026.1.5 ou 2026.1.5.1) et
considère un nommage au format suivant :
- 2026_1_5_1.png > 2026.1.5.1 (un suffixe après un tiret `-POS` est ignoré)

Tout format de nommage *hors-norme* est repris tel quel comme identifiant.

Par son architecture même, Caquot n'est pas pensé pour du stockage à long terme
de vos données, il est donc fortement conseillé de les exporter et de garder
des copies externes.

### Mettre à jour

Téléchargez la nouvelle version depuis la page des versions et extrayez-la à
côté de l'ancienne (par exemple `C:\Caquot\caquot-1.3.0`). Copiez-y le dossier
`data` de l'ancienne version si vous souhaitez récupérer des données, puis
lancez `Lancer-Caquot-Windows.bat` (ou `./run.sh` sous Linux) : les composants
sont réinstallés au premier lancement. Lisez les notes de version : elles
peuvent contenir des instructions.
Une fois la nouvelle version vérifiée, supprimez l'ancien dossier. 

### Supprimer les données du projet

#### Linux

Supprimer la base de données :
```bash
rm data/data.db
```
Supprimer les données des modèles :
```bash
rm -rf data/models
```

#### Windows

Supprimer la base de données :
Mettre à la corbeille le fichier `data.db` dans le dossier `data/`.

Supprimer les données des modèles :
Mettre à la corbeille le dossier `data/models`.

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