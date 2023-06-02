# Utiliser une image Python officielle
FROM python:3.11.3

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers nécessaires dans le conteneur
COPY . /app
COPY ./Binance/requirements.txt /app/Binance/requirements.txt

# Installer les dépendances Python
RUN pip install --no-cache-dir -r /app/Binance/requirements.txt

# Exposer le port pour Dash
EXPOSE 8050

# Commande pour lancer l'application Dash
CMD ["python", "/app/Dash_OPA.py"]
