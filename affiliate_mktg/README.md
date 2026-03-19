# Affiliate Marketing Package

Refactored layout of the AffiliateMktg project into a single package with clear modules.

## Package layout

- **`core/`** – Domain models and enums: `models`, `enums`, `model_response` (PA-API response types).
- **`config/`** – Configuration loaders: `loader` (blog + Starlette), `amazon_loader`.
- **`utils/`** – Shared utilities: `common`, `logging_setup`, `json_response`.
- **`amazon/`** – Amazon PA-API and link flow: `links_generator`, `links_manager`.
- **`blog/`** – Blog generation and Blogger: `blog_generator`, `blog_service`, `blog_manager`.
- **`search/`** – Search index: `search_index_manager`.
- **`mcp/`** – MCP server and tool invoker: `server`, `mcp_wrapper`.
- **`api/`** – Starlette app and middleware: `app_links`, `middleware`.

## Entry points

- **Streamlit UI:** `streamlit run app.py` (from project root).
- **Starlette API:** `python run.py` or `uvicorn app_links:app --host 0.0.0.0 --port 8000` (root `app_links.py` re-exports the app).
- **CLI:** `python main.py`.

Run from the project root (`AffiliateMktg`) so that `affiliate_mktg` is on `PYTHONPATH`.
