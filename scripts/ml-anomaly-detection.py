#!/usr/bin/env python3
from elasticsearch import Elasticsearch
from sklearn.ensemble import IsolationForest
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta

class MozillaAnomalyDetector:
    def __init__(self, es_host='localhost:9200'):
        self.es = Elasticsearch(['http://elasticsearch:9200'])
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.1,
            random_state=42
        )
        self.features = [
            'elapsed_time',
            'step_count', 
            'exit_code',
            'has_failure'
        ]
    
    def fetch_build_data(self, days=30):
        """Récupère les données de build depuis Elasticsearch"""
        query = {
            "size": 1000,
            "query": {
                "range": {
                    "@timestamp": {
                        "gte": f"now-{days}d/d"
                    }
                }
            }
        }
        
        response = self.es.search(
            index="mozilla-builds-*",
            body=query
        )
        
        builds = []
        for hit in response['hits']['hits']:
            source = hit['_source']
            builds.append({
                'build_id': source.get('build_id'),
                'elapsed_time': source.get('elapsed_time', 0),
                'step_count': len(source.get('steps', [])),
                'exit_code': source.get('exit_code', 0),
                'has_failure': 1 if source.get('result_status') in ['failure', 'cancelled'] else 0,
                'timestamp': source.get('@timestamp')
            })
        
        return pd.DataFrame(builds)
    
    def train_model(self):
        """Entraîne le modèle de détection d'anomalies"""
        print("📊 Récupération des données d'entraînement...")
        df = self.fetch_build_data(30)
        
        if len(df) < 10:
            print("❌ Pas assez de données pour l'entraînement")
            return
        
        # Préparation des features
        X = df[self.features].fillna(0)
        
        print(f"🤖 Entraînement sur {len(X)} builds...")
        self.model.fit(X)
        
        # Prédictions
        predictions = self.model.predict(X)
        df['anomaly_score'] = self.model.decision_function(X)
        df['is_anomaly'] = predictions == -1
        
        anomaly_count = df['is_anomaly'].sum()
        print(f"🔍 {anomaly_count} anomalies détectées sur {len(df)} builds")
        
        return df
    
    def detect_realtime_anomalies(self):
        """Détecte les anomalies en temps réel"""
        # Récupère les builds des dernières 24h
        query = {
            "size": 100,
            "query": {
                "range": {
                    "@timestamp": {
                        "gte": "now-24h/h"
                    }
                }
            },
            "sort": [{"@timestamp": "desc"}]
        }
        
        response = self.es.search(
            index="mozilla-builds-*", 
            body=query
        )
        
        anomalies = []
        for hit in response['hits']['hits']:
            source = hit['_source']
            build_features = [
                source.get('elapsed_time', 0),
                len(source.get('steps', [])),
                source.get('exit_code', 0),
                1 if source.get('result_status') in ['failure', 'cancelled'] else 0
            ]
            
            prediction = self.model.predict([build_features])
            if prediction[0] == -1:
                anomalies.append({
                    'build_id': source.get('build_id'),
                    'slave': source.get('slave'),
                    'timestamp': source.get('@timestamp'),
                    'anomaly_score': self.model.decision_function([build_features])[0],
                    'reason': 'Comportement anormal détecté'
                })
        
        return anomalies

if __name__ == "__main__":
    detector = MozillaAnomalyDetector('localhost:9200')
    trained_data = detector.train_model()
    
    if trained_data is not None:
        anomalies = detector.detect_realtime_anomalies()
        print(f"🚨 {len(anomalies)} anomalies détectées récemment:")
        for anomaly in anomalies:
            print(f"  - Build {anomaly['build_id']} sur {anomaly['slave']}")