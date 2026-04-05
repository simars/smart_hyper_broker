#!/bin/bash
set -e

echo "Starting frontend locally in DEBUG mode..."
NODE_OPTIONS='--inspect' npm run dev
