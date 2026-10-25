#!/usr/bin/env bash
# Stop only the F&B preview (nginx :8093 + its tunnel). The main demo preview is not touched.
[ -f /tmp/kodeerp-fnb-tunnel.pid ] && kill "$(cat /tmp/kodeerp-fnb-tunnel.pid)" 2>/dev/null; rm -f /tmp/kodeerp-fnb-tunnel.pid
[ -f /tmp/kodeerp-fnb-nginx.pid ] && kill "$(cat /tmp/kodeerp-fnb-nginx.pid)" 2>/dev/null; echo "F&B preview stopped"
