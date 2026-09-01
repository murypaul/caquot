# Caquot - Logiciel d'indexation d'image patrimoniale par intelligence artificielle.

=== ARCHIVE === Ce document est gardé à titre d'archivage des premières
décisions et pistes du projet.

---

## Finalité

Avoir un logiciel, utilisable par des institutions culturelles, qui permet
'ingérer un thésaurus ou un vocabulaire contrôlé et de fournir une indexation
fiable basée sur leurs termes. Caquot se concentre principalement sur les
représentations des supports photographiques, noir et blanc et couleur. Il doit
être capable de traiter de sujet allant de la période du début de la
photographie (1ère moitié du XIXe s.) jusqu'à nos jours.

L'objectif n'est pas de se substituer à l'expertise humaine, mais de fournir
une base de travail à peu près solide. Sur des fonds importants, il peut
s'écouler des années avant qu'un opérateur humain ne se penche sur la
description fine d'un item. Automatiser ce premier niveau d'indexation, même
imparfait, permet d'offrir une capacité de recherche et de traitement
immédiate, sans attendre le passage humain. La vérification de fiabilité
intervient ensuite, en interne, selon la méthode choisie par l'institution - le
plus souvent par sondage d'un pourcentage des notices.

## Philosophie

Caquot se veut libre et utilisable par tous. Il est pensé pour pouvoir être
utilisé purement en local. Néanmoins, si l'utilisateur le souhaite, il peut
faire appel à une API d'un LLM extérieur.

## Périmètre

- Caquot indexe uniquement le contenu représenté sur l'image (sujets,
personnes, lieux, objets), et non les caractéristiques techniques du support ou
du procédé photographique.
- Le contenu représenté ne se limite pas aux objets et sujets dénombrables :
les éléments non dénombrables (matière, ambiance, phénomènes naturels,
brouillard, neige, fumée...) font pleinement partie du périmètre d'indexation
dès lors qu'ils figurent dans le thésaurus fourni. Une part importante du sens
d'une photographie tient à ce type d'élément, qui échapperait à une indexation
limitée aux seuls objets identifiables.
- Aucun prétraitement image (restauration, amélioration de contraste...) n'est
prévu. Caquot part du principe que la numérisation fournie par l'institution
est de qualité suffisante ; la responsabilité de la qualité des documents
numériques incombe à l'institution.

## Fonctionnement

### Thésaurus

- Le thésaurus est fourni par l'opérateur en début de campagne, au format CSV.
- Une v1 impose un format de colonnes attendu, que l'opérateur doit respecter
(mapping libre des colonnes envisagé comme amélioration de v2).
- Une campagne = une langue (FR_fr). Le multilingue n'est pas géré au sein
d'une même campagne.

Le thésaurus se présente sous le format suivant :

id | label | parent_id | path | notes (facultatif)

identifiant stable du terme | terme | identifiant du terme parent | chemin
complet du terme, permettant de le contextualiser | notes explicatives ou de
contextualisation

Le thésaurus fourni par l'opérateur peut avoir été élagué de termes jugés hors
périmètre (ex. noms de personnes, de lieux), ce qui peut laisser des
`parent_id` orphelins (pointant vers un terme supprimé). Ce n'est pas traité
comme une erreur : `parent_id` n'est stocké qu'à titre indicatif et n'est
jamais parcouru par le pipeline, le contexte hiérarchique utile étant déjà
porté intégralement par la colonne `path`. En base, `parent_id` n'est donc pas
contraint par une clé étrangère.

### Pipeline de traitement

1. Agent d'embedding image : chaque image versée dans la campagne est
vectorisée (ex. modèle CLIP).
2. Agent de description (LLM Vision) : décrit l'image en langage naturel.
3. Agent de rapprochement (FAISS ?) : rapproche, dans un même espace vectoriel
CLIP, l'embedding de l'image et les embeddings des termes du thésaurus, et
propose une liste de 10 à 20 termes (nombre configurable) avec un taux de
confiance pour chacun. Pour la v1, ce rapprochement se fait par similarité
classique (ex. similarité cosinus) directement dans l'espace CLIP. Un
rapprochement combiné, faisant en plus intervenir la description en langage
naturel (agent de description) embeddée par un modèle de texte et comparée au
thésaurus dans ce même espace textuel, est envisagé ; un rapprochement par
fine-tuning sur des corpus déjà indexés est également envisagé pour une version
ultérieure.
4. Agent de validation : décide des termes retenus en croisant le taux de
confiance et la cohérence avec la description en langage naturel.

### Schéma de données (SQLite)

- `THESAURUS(thesaurus_id, name, parent_id, path, note)` - un terme du
thésaurus. `thesaurus_id` reprend directement l'identifiant stable fourni dans
le CSV. `parent_id` est une auto-référence vers `thesaurus_id` (nullable pour
les termes racine) et porte la hiérarchie.
- `IMAGE(image_id, name)` - une image versée dans la campagne. `name` est le
chemin du fichier dans le dossier de la campagne (contrainte d'unicité). Les
fichiers restent sur disque ; seul le chemin est référencé en base, aucune
image n'est dupliquée en BLOB.
- `CLIP_MODEL(clip_model_id, name, publication_date)` - les modèles CLIP
utilisés au fil de la campagne (ex. passage ultérieur de `ViT-B-32` à
`ViT-H-14`), pour tracer avec quel modèle chaque embedding a été produit.
- `IMAGE_VECTORS(image_vectors_id, image_id, vectors, clip_model_id)` - un
embedding d'image (`vectors` : vecteur sérialisé en BLOB). Contrainte
`UNIQUE(image_id, clip_model_id)`.
- `THESAURUS_VECTORS(thesaurus_vectors_id, thesaurus_id, vectors, clip_model_id)` -
même chose côté thésaurus. Contrainte `UNIQUE(thesaurus_id, clip_model_id)`.
- `IMAGE_THESAURUS(image_id, thesaurus_id, confidence_level, statut)` -
résultat du rapprochement entre une image et un terme : score de similarité
(`confidence_level`) et statut de la décision (`statut` ∈
`to_be_checked | selected | rejected | manually_selected | manually_rejected`).
Clé primaire composite `(image_id, thesaurus_id)`.

Un vecteur d'image et un vecteur de terme ne sont comparables entre eux que
s'ils proviennent du même `clip_model_id` : le script de rapprochement doit
systématiquement filtrer sur ce critère avant tout calcul de similarité.

### Export

Les notices indexées sont exportées en CSV, avec une colonne de taux de
confiance.

### Gouvernance de la fiabilité

Caquot pourra proposer un outil d'aide au sondage qualité (ex. génération d'un
échantillon représentatif selon le taux de confiance) pour faciliter la
vérification humaine en institution. La traçabilité de la génération IA (quelle
version du thésaurus, quel modèle, quelle notice a été relue/corrigée) est,
dans un premier temps, considérée comme une responsabilité de l'institution
utilisatrice, et non une fonctionnalité portée par le logiciel.

Un risque spécifique au rapprochement par embeddings doit être anticipé : deux
éléments visuellement proches dans l'espace vectoriel (formes, composition,
ouleurs) ne sont pas nécessairement proches sémantiquement. Ce type de
rapprochement « plausible mais faux » peut, sur un fonds patrimonial ancien
(photographie ethnographique, coloniale, etc.), produire des associations de
termes inappropriées, voire perpétuer des préjugés. Le taux de confiance seul
ne suffit pas à écarter ce risque, puisqu'un rapprochement peut être
formellement bien noté (haute similarité cosinus) sans être pertinent. Ce
risque est une limite connue du système, et non un simple défaut de jeunesse à
corriger plus tard. Il est du ressort de l'institution de définir sa politique
de traitement vis-à-vis de ces limites, Caquot ne peut en être tenu pour
responsable.

## Interface

Une interface en ligne de commande (CLI) est privilégiée pour la v1, plus
simple à développer. Une interface graphique (desktop ou web) reste envisagée à
terme ; l'arbitrage entre les deux dépendra des contraintes de simplicité de
déploiement et de performance (le web permettrait un accès depuis n'importe
quel poste du réseau, mais implique une stack technique plus complexe).

## Architecture technique (v1)

- Langage : Python.
- Modèles locaux : via Ollama (agent de description vision).
- Embeddings image : open_clip, avec un modèle CLIP multilingue (encodeur texte
XLM-RoBERTa) pour que l'espace vectoriel couvre correctement le français des
termes du thésaurus. Prototype v1 : `ViT-B-32` /
`xlm-roberta-base-laion5B-s13B-b90k` (léger, adapté à un premier pipeline
fonctionnel sur la configuration de référence). Piste d'amélioration ultérieure
(qualité, à réévaluer une fois le pipeline validé, même démarche que pour
l'agent de description) : `ViT-H-14` /
`frozen-xlm-roberta-large-laion5B-s13B-b90k`, nettement plus précis mais plus
coûteux en calcul.
- Rapprochement : calcul de similarité classique (numpy), sans base vectorielle
dédiée dans un premier temps.
- Stockage : base locale simple (ex. SQLite).
- Matériel de référence pour le développement : i7-10700, 64 Go DDR4, RTX 3060
Ti, SSD


## Divers

Le projet dispose d'un répertoire github : https://github.com/murypaul/caquot