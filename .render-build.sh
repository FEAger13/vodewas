#!/bin/bash
echo "🧹 Cleaning build cache..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir

echo "✅ Build complete"
