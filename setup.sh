#!/bin/bash
# ============================================================================
# LAYER 3: MANUAL DEPENDENCY SETUP (Fallback)
# ============================================================================
# Usage: ./setup.sh
#
# This is a manual fallback for environments where auto-install fails.
# Part of 4-layer dependency defense strategy.
#
# NOTE: Prefer using Makefile: make install

set -e  # Exit on any error

echo "🔧 Vibe Agency - Environment Setup"
echo "=================================="
echo ""
echo "ℹ️  Tip: Use 'make install' for a better experience!"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "⚠️  Warning: Python $PYTHON_VERSION detected (recommended: 3.11+)"
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "⚠️  uv not found. Installing uv..."
    pip install uv
    echo "✅ uv installed"
fi

# Install dependencies with uv
echo ""
echo "📦 Installing dependencies with uv..."
uv sync --all-extras

# Install and activate pre-commit hooks
echo ""
echo "🪝 Setting up pre-commit hooks..."
uv run pre-commit install
echo "✅ Pre-commit hooks activated"

# Validate knowledge bases
echo ""
echo "🔍 Validating knowledge bases..."
if [ -f "validate_knowledge_index.py" ]; then
    uv run python validate_knowledge_index.py
else
    echo "⚠️  validate_knowledge_index.py not found (skipping)"
fi

# Success
echo ""
echo "✅ Environment ready!"
echo ""
echo "Next steps:"
echo "  make test                        # Run tests (recommended)"
echo "  make lint                        # Check code quality"
echo "  ./vibe-cli run <project-id>      # Run a project"
echo ""
echo "Or use Makefile commands:"
echo "  make help                        # See all available commands"
echo ""
