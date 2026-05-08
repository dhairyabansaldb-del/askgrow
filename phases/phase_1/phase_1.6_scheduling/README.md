# Phase 1.6: Automated Scheduling - Documentation

## Summary
Phase 1.6 automates the data ingestion pipeline using GitHub Actions, ensuring the ChromaDB knowledge base remains current on a weekly schedule.

## Files
- `ingest_all.py` - A master orchestrator script that sequentially runs the 5 sub-phases. It alters the working directory internally so it can be called from anywhere.
- `../../.github/workflows/weekly_ingestion.yml` - The GitHub Actions workflow file that triggers the automation.
- `../../requirements.txt` - Required by the GitHub Action to install dependencies.

## Workflow Overview
1.  **Trigger:** The GitHub Action is triggered by a cron schedule (every Monday at 10:00 AM IST) or manually via `workflow_dispatch`.
2.  **Execution:** The action checks out the code, sets up Python 3.9, installs dependencies, and runs `ingest_all.py`.
3.  **Persistence:** Any resulting changes to raw data, chunks, embeddings, and the `chroma_db` database are committed back to the repository.
4.  **Deployment:** The backend service (Phase 2), running on Railway or a similar platform, will automatically pull these latest commits and serve the fresh database.

## Running Locally
You can run the full pipeline locally to verify it works end-to-end:
```bash
cd phases/phase_1/phase_1.6_scheduling
..\venv\Scripts\python.exe ingest_all.py
```
This process takes ~1-2 minutes depending on network speed.
