# Projet_OPA
Projet OPA - DataScientest


### A. Objectif :
Notre Projet Bot Trading a pour obectif de prédire les **Décisions d'Achat / Vente d'une Paire de Crypto**.

Pour cela nous mettons à disposition un **Dashboard** qui présente des fonctionalités suivantes :
- Lister les Cours d'une Paire donnée sur les 6 derniers mois
- Charger les données Historiques d'une Paire afin d'y effectuer une Prédiction / Simulation 
- Simuler les décisions d'Achat / Vente sur une période donnée.
 
La Simulation propose 2 méthodes : 
- **Méthode 1** : Algorithme qui déduit les décisions d'Achat / Vente en croisant plusieurs Indicateurs Techniques Trading ( RSI, TRIX, ..) à un instant T.
- **Méthode 2** : Machine Learning de Classification qui prédit les décisions d'achat / Vente à partir de l'historique des Indicateurs Techniques Trading ( RSI, TRIX, ..)

*Par la suite un API sera implémenté pour les prises de Décisions d'Achat / Vente en Temps réel*

### B. Images :
Notre Application utilise plusieurs images : 
- **Mongo** : Pour le stockage des données Historiques
- **Redis** : pour le stockage mémoire de la liste de toutes les paires de Crypto
- **arnoldyoussa/trading_opa** : Pour la mise à disposition d'un Dashboard Bot Trading

### C. Deploiement :
L'installation de notre Dashboard Trading sur vos serveurs est possible avec les techno suivantes : 
- **Docker Compose** : 
	- Step 1 : Télécharger le répertoire DockerCompose
	- Step 2 : Lancer la commande SHELL "Docker Compose up"
	
- **Kubernetes k3s**:
	- Step 1 : Télécharger le répertoire Kubernetes
	- Step 2 : Lancer la commande SHELL "./Kubernetes/Deploy_opa.sh
 
### D. Visualisation :
Pour visualiser le **Dashboard**, il suffit d'aller à la page **127.0.0.1:8050**

PS : si vous le souhaitez, vous pouvez consulter votre **base Mongo** via le lien **127.0.0.1:27017**
	
 
***Point d'attention:
Utiliser 127.0.0.1 si vous êtes en local.
Sinon utiliser l'adresse IP de votre machine distante.***
