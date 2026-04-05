#!/bin/bash
set -e

echo "Cleaning frontend node_modules and builds..."
rm -rf node_modules
rm -rf .next
echo "Frontend config clean complete."
