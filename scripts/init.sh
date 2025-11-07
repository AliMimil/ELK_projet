#!/bin/bash

echo "🚀 Initialisation du projet ELK Mozilla..."

# Création des dossiers
mkdir -p elasticsearch/{data,config}
mkdir -p logstash/{config,pipeline,patterns}
mkdir -p kibana/config
mkdir -p filebeat
mkdir -p data/raw_logs

# Copie des fichiers de configuration
echo "📁 Copie des configurations..."

# Donnez les permissions
chmod -R 755 elasticsearch/data
chmod 644 logstash/pipeline/*.conf 2>/dev/null || true

# Démarrage des containers
echo "🐳 Démarrage des containers Docker..."
docker-compose up -d

echo "⏳ Attente du démarrage d'Elasticsearch..."
sleep 30

# Vérification du statut
echo "🔍 Vérification du statut des services..."
docker-compose ps

# Test Elasticsearch
echo "🧪 Test de connexion Elasticsearch..."
curl -X GET "localhost:9200/_cat/health?v" || echo "Elasticsearch pas encore prêt"

echo "✅ Initialisation terminée!"
echo "📊 Kibana: http://localhost:5601"
echo "🔍 Elasticsearch: http://localhost:9200"
echo "📝 Logstash: http://localhost:9600"

# Instructions
echo ""
echo "📋 Prochaines étapes:"
echo "1. Placez vos fichiers logs dans ./data/raw_logs/"
echo "2. Vérifiez les index dans Kibana: Management > Stack Management > Index Patterns"
echo "3. Créez un index pattern 'mozilla-builds-*'"
echo "4. Commencez à explorer vos données!"