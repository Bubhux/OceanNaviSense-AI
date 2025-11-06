
# En cours de développement

<div id="top"></div>

## Menu   

1. **[Informations générales](#informations-générales)**   
2. **[Liste pré-requis](#liste-pre-requis)**   
3. **[Auteurs et contact](#auteur-contact)**   

### Projet OceanNaviSense AI

Cette application est un outil d'aide à la navigation maritime.  
Elle combine **visualisation cartographique**, **optimisation de trajectoires (routing)** et **dashboards d'aide à la décision** pour offrir une meilleure expérience de planification et de navigation en mer.  

##### Fonctionnalités prévues :  

- Génération de cartes maritimes avec **OpenLayers** et **Natural Earth**
- Interface utilisateur interactive avec **Panel** pour la visualisation des données
- Données géographiques provenant de **Natural Earth** (côtes, routes maritimes, bathymétrie)
- **Données météo-marines en temps réel** via l'API **Copernicus Marine**
- **Variables océanographiques** : courants, température de l'eau, hauteur des vagues, salinité
- **Visualisation des routes maritimes** et optimisation de trajectoires
- **Notifications d'alertes météo** (vent fort, tempêtes, conditions maritimes dangereuses)
- **Dashboard interactif** pour l'analyse des données de navigation et conditions environnementales

##### Données Copernicus Marine intégrées :

- **Courants marins** (vitesse et direction)
- **Température de surface de la mer**
- **Hauteur significative des vagues**
- **Vitesse et direction du vent en surface**
- **Salinité**
- **Glace de mer** (régions polaires)
- **Données historiques et prévisions**

##### Apports de l'analyse de données Machine Learning :  

- **Optimisation des trajectoires** en fonction des courants marins et conditions météo
- **Prédiction des conditions de navigation** basée sur les données Copernicus Marine
- **Adaptation en temps réel** aux changements météorologiques et océanographiques
- **Analyse des patterns de navigation** issus des données historiques
- **Détection proactive des risques** (zones dangereuses, conditions défavorables)
- **Optimisation multi-objectifs** (réduction du temps de trajet, consommation de carburant, sécurité accrue)

##### Objectifs du projet :  

- Fournir un prototype simple pour tester et valider le concept
- Évoluer progressivement vers une application plus complète avec des modules avancés
- Proposer un outil moderne pour aider les marins, navigateurs et passionnés de la mer
- Intégrer des données scientifiques de qualité pour une navigation plus sûre et efficac


--------------------------------------------------------------------------------------------------------------------------------


<div id="liste-pre-requis"></div>
<a href="#top" style="float: right;">Retour en haut 🡅</a>

### Liste pré-requis   

- Interpréteur **Python**, version 3.12.0 ou supérieure

- Application conçue avec les technologies suivantes :   
  &nbsp;   

  - **Python** v3.12.0 ou supérieure
  - **Python** est disponible à l'adresse suivante ➔ https://www.python.org/downloads/    
  - **Windows 11** Professionnel ou autre système d'exploitation compatible
    &nbsp;   

##### Librairies principales utilisées :  

- **Panel** ➔ Création d'interfaces web et de dashboards interactifs
- **OpenLayers** ➔ Bibliothèque JavaScript pour la visualisation cartographique
- **Natural Earth** ➔ Données géographiques de référence (côtes, frontières, bathymétrie)
- **Copernicus Marine API** ➔ Données météo-marines et océanographiques à l'adresse suivante ➔ https://marine.copernicus.eu/
- **Pandas** ➔ Manipulation et traitement des données tabulaires
- **NumPy** ➔ Calculs numériques et manipulation de matrices
- **Plotly** ➔ Visualisation interactive des données (graphiques, cartes, dashboards)
- **Scikit-learn** ➔ Outils d'analyse et de modélisation (prévisions, apprentissage automatique)
- **Xarray** ➔ Manipulation des données multidimensionnelles (netCDF)
- **Requests** ➔ Appels à l'API Copernicus Marine

##### Données géographiques :

- Site **Natural Earth** à l'adresse suivante ➔ https://www.naturalearthdata.com/  
- **Natural Earth** fournit les données de base pour la génération des cartes :
  - Côtes et frontières maritimes
  - Routes et voies de navigation
  - Données bathymétriques (profondeurs des océans)
  - Points d'intérêt maritimes

##### Configuration API Copernicus Marine :

- Inscription requise sur le portail Copernicus Marine
- Clé API nécessaire pour accéder aux services
- Sélection des produits appropriés selon la zone géographique

| - Les scripts **Python** s'exécutent depuis un terminal.                                            |
------------------------------------------------------------------------------------------------------|
| - Pour ouvrir un terminal sur **Windows**, pressez la touche ```windows + r``` et entrez ```cmd```. |
| - Sur **Mac**, pressez la touche ```command + espace``` et entrez ```terminal```.                   |
| - Sur **Linux**, vous pouvez ouvrir un terminal en pressant les touches ```Ctrl + Alt + T```.       | 

--------------------------------------------------------------------------------------------------------------------------------

<div id="auteur-contact"></div>
<a href="#top" style="float: right;">Retour en haut 🡅</a>

### Auteurs et contact 

Pour toute information supplémentaire, vous pouvez me contacter.   
**Bubhux:** bubhuxpaindepice@gmail.com