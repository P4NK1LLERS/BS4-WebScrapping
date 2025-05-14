# BS4-WebScrapping
Script python permettant de scrapper les évènements du site internet : Big City Nantes 

# BigCityNantes Scraper

Un script Python pour extraire automatiquement les événements du site BigCityNantes et les stocker dans Firestore.

---

## Fonctionnalités

Le script repose sur deux fonctions principales :

### get_all_url()

- Parcourt toutes les pages du site BigCityNantes.
- Récupère les URLs des événements.
- Enregistre chaque URL dans la collection `url` de Firestore :
  db.collection('url').add({'url': href})

### get_all_data()

- Lit toutes les URLs enregistrées dans Firestore (collection `url`).
- Pour chaque page d'événement :
  - Envoie une requête HTTP.
  - Extrait les données suivantes :
    - Identifiant
    - Titre de l'événement
    - Date
    - Description
    - Tags (extraits du HTML)
    - Localisation (texte)
    - Coordonnées GPS (à partir d'un lien Google Maps)
    - Image (lien direct vers une image si présente)
- Enregistre chaque événement dans la collection `evenements` :
  db.collection('evenements').add(event)

---

## Prérequis

- Python 3.8 ou supérieur
- Un projet Firebase avec Firestore activé
- Un fichier `serviceAccountKey.json` contenant les identifiants du service Firebase

---

## Dépendances

Installer les bibliothèques nécessaires avec pip :

pip install requests beautifulsoup4 google-cloud-firestore

---

## Utilisation

1. Placer le fichier `serviceAccountKey.json` dans le même dossier que le script.
2. Exécuter les fonctions dans l'ordre suivant :

get_all_url()   pour récupérer les URLs
get_all_data()  pour extraire les données des événements

---

## Remarques

- Les données sont stockées dans Firestore pour une utilisation centralisée.
- Ces données peuvent ensuite être utilisées dans une application web ou mobile.
