# filebeat/Dockerfile
FROM docker.elastic.co/beats/filebeat:8.11.0

USER root
COPY config/filebeat.yml /usr/share/filebeat/filebeat.yml
RUN chmod 644 /usr/share/filebeat/filebeat.yml
USER filebeat