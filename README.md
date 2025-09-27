
# En cours de développement

<div id="top"></div>

## Menu   

1. **[Informations générales](#informations-générales)**   
2. **[Liste pré-requis](#liste-pre-requis)**   
3. **[Auteurs et contact](#auteur-contact)**   

### Projet OceanNaviSense AI

Cette application est un outil d’aide à la navigation maritime.  
Elle combine **données météorologiques**, **optimisation de trajectoires (routing)**, **machine learning** et **dashboards d’aide à la décision** pour offrir une meilleure expérience de planification et de navigation en mer.  

##### Fonctionnalités prévues :  

- Connexion à une API météo gratuite (**OpenWeatherMap**) pour récupérer des données **actuelles et historiques**.  
- Mise en place d’une **API FastAPI** pour exposer les services (données météo, alertes, calcul de routes).  
- Interface utilisateur simple avec **Streamlit** pour la visualisation des données.  
- **Base de données** pour stocker les utilisateurs et l’historique des trajectoires.  
- **Authentification des utilisateurs**.  
- **Notifications d’alertes météo** (vent fort, tempêtes, etc.).  
- **Visualisation 3D des routes maritimes** (prévu).  

##### Apports du Machine Learning :  

- **Prédictions plus précises** des conditions optimales de navigation.  
- **Adaptation en temps réel** aux changements météorologiques.  
- **Apprentissage continu** des patterns de navigation issus des données historiques.  
- **Détection proactive des risques** (vents violents, tempêtes, zones dangereuses).  
- **Optimisation multi-objectifs** (réduction du temps de trajet, consommation de carburant, sécurité accrue).  

##### Objectifs du projet :  

- Fournir un prototype simple pour tester et valider le concept.  
- Évoluer progressivement vers une application plus complète avec des modules avancés.  
- Proposer un outil moderne pour aider les marins, navigateurs et passionnés de la mer.

--------------------------------------------------------------------------------------------------------------------------------

<div id="liste-pre-requis"></div>
<a href="#top" style="float: right;">Retour en haut 🡅</a>

### Liste pré-requis   

- Interpréteur **Python**, version 3.12.0 ou supérieure.   

- Application conçue avec les technologies suivantes :   
  &nbsp;   

  - **Python** v3.12.0 choisissez la version adaptée à votre ordinateur et système.   
  - **Python** est disponible à l'adresse suivante ➔ https://www.python.org/downloads/    
  - **Windows 11** Professionnel   
    &nbsp;   

##### Librairies principales utilisées :  

- **FastAPI** ➔ Framework pour concevoir l’API.  
- **Uvicorn** ➔ Serveur ASGI pour exécuter l’API FastAPI.  
- **Streamlit** ➔ Création d’une interface web interactive pour la visualisation des données.  
- **Requests** ➔ Consommation de l’API météo externe (OpenWeatherMap).  
- **SQLAlchemy** ➔ Gestion et persistance des données dans la base de données.  
- **Pandas** ➔ Manipulation et traitement des données tabulaires.  
- **NumPy** ➔ Calculs numériques et manipulation de matrices.  
- **Plotly** ➔ Visualisation interactive des données (graphiques, cartes, dashboards).  
- **Scikit-learn** ➔ Outils d’analyse et de modélisation (prévisions, apprentissage automatique).  
- **Pydantic** ➔ Validation et sérialisation des données (schémas de l’API). 


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