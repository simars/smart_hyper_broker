#!/bin/bash
set -e

echo "Running frontend test suite..."
npm run test --if-present
