"""
Vercel Serverless Entry Point for FastAPI.
"""
from app.api import app

# Vercel expects the app to be named 'app' or 'handler'
# This module re-exports the FastAPI app for Vercel's Python runtime
