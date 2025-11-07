#!/bin/bash

echo "🔍 Monitoring ELK Stack..."

# Vérification des containers
docker-compose ps

# Vérification de la santé Elasticsearch
curl -s "http://localhost:9200/_cluster/health?pretty"

# Statistiques des index
echo -e "\n📊 Statistiques des index:"
curl -s "http://localhost:9200/_cat/indices/mozilla-*?v&s=index"

# Comptage des documents
echo -e "\n📄 Nombre de documents:"
curl -s "http://localhost:9200/mozilla-builds-*/_count" | jq '.count'

# Espace disque
echo -e "\n💾 Utilisation disque:"
curl -s "http://localhost:9200/_cat/allocation?v"