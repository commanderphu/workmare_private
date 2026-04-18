#!/bin/bash
# Einmaliges Server-Setup – als workmate User ausführen
set -e

echo "=== Workmate Private – Server Setup ==="

# Docker installieren
sudo apt-get update -qq
sudo apt-get install -y docker.io docker-compose-v2 certbot ufw

# workmate User zu Docker-Gruppe hinzufügen
sudo usermod -aG docker workmate

# Firewall konfigurieren
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Deploy-Verzeichnis anlegen
sudo mkdir -p /opt/workmate-private/nginx/conf.d
sudo chown -R workmate:workmate /opt/workmate-private

echo "=== Setup abgeschlossen ==="
echo "Nächste Schritte:"
echo "  1. /opt/workmate-private/.env anlegen"
echo "  2. /opt/workmate-private/firebase-credentials.json kopieren"
echo "  3. /opt/workmate-private/nginx/conf.d/workmate.conf anpassen (Domain eintragen)"
echo "  4. docker compose -f docker-compose.prod.yml up -d"
echo "  5. certbot --nginx -d <domain>"
