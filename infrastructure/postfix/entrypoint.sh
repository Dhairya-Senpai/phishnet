#!/bin/bash
set -e

echo "Starting Phishnet Postfix ingestion service..."

# Write env vars into pipe script environment
cat > /etc/postfix/pipe_env << ENVEOF
PHISHNET_API_URL=${PHISHNET_API_URL:-http://backend:8000}
PHISHNET_API_KEY=${PHISHNET_API_KEY:-change-me-in-production}
ENVEOF

# Auto-upgrade configuration for newer Postfix versions
postfix upgrade-configuration 2>/dev/null || true

# Set compatibility level to suppress warnings
postconf compatibility_level=3.6 2>/dev/null || true

# Fix permissions
postfix set-permissions 2>/dev/null || true

# Verify config
postfix check

echo "Postfix listening on port 2525..."
exec postfix start-fg