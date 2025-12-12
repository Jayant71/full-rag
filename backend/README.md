---
title: RAG Backend API
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# RAG Backend API

FastAPI backend for the RAG (Retrieval-Augmented Generation) system.

## Features

- Document ingestion with LlamaParse
- Vector storage with Qdrant
- Chat with context retrieval
- BYOK (Bring Your Own Keys) support

## Environment Variables

Set these in your Space settings:

- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_SERVICE_KEY` - Your Supabase service role key
- `DATABASE_TYPE` - `sqlite` or `postgres`
- `STORAGE_TYPE` - `local`, `s3`, or `supabase`
- `FRONTEND_URL` - Your frontend URL for CORS
