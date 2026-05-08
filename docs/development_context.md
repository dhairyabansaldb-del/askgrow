# Development Context & Decisions Audit

This document tracks the technical evolution, architectural decisions, failures, and rationales for the Mutual Fund Chatbot project. It serves as the "ground truth" for the current state of development (end of Phase 1.5).

---

## 1. Project Foundation (Phase 1.1)

### Decisions
- **Language**: Python 3.9+ was chosen for robust ecosystem support (LangChain, ChromaDB).
- **Environment**: Virtual environment (`venv`) used to isolate dependencies.

### Challenges & Failures
- **The "Greenlet" Incident**: During installation, `chromadb` dependencies failed because the Windows environment lacked MSVC build tools.
- **Resolution**: Switched to a binary-only installation strategy for problematic packages using `--only-binary :all:`. This bypassed the need for local compilation.

---

## 2. Data Ingestion & Extraction (Phase 1.2)

### Architectural Decisions
- **Source Selection**: Targeting Groww.in as the primary data aggregator.
- **Extraction Strategy**: Instead of traditional HTML/CSS scraping (which is fragile and slow), we implemented **JSON extraction** by targeting the `<script id="__NEXT_DATA__">` tag.
- **Rationale**: Groww uses Next.js. The server-side props are embedded as a pure JSON object. Extracting this provides 100% accurate, structured data (40+ fields) with zero HTML parsing noise.

### Failures & Refinements
- **The "Aggressive Cleaner" Mistake**: The first iteration of the data cleaner stripped 88% of data, removing things like SIP returns and manager experience.
- **Pivot**: Redesigned the `cleaner.py` with a **conservative philosophy**: Only strip platform-internal noise (Groww IDs, VRO analytics, null blocks). We kept everything a retail user or support agent could plausibly ask about.

---

## 3. Knowledge Representation (Phase 1.3)

### Architectural Decisions
- **Sectional Factual Chunking**: We rejected standard LangChain `RecursiveCharacterTextSplitter`.
- **Rationale**: Character-based splitting is "blind" to structure. It might split a fund manager's name from their education. Our custom chunker splits by **logical groups** (Basics, Costs, Rules, Performance, Risk).
- **Context Injection**: Every chunk is prefixed with the Fund Name and Category.
- **Rationale**: If a search retrieves only the "Risk Metrics" chunk, the LLM must still know which fund it belongs to without searching twice.

---

## 4. Vectorization Strategy (Phase 1.4)

### Decisions
- **Model Selection**: `BAAI/bge-small-en-v1.5`.
- **Rationale**: We compared `all-MiniLM` (too simple) and `bge-large` (too heavy at 1.3GB). `bge-small` (~130MB) offers SOTA retrieval accuracy for its size, fitting perfectly into Railway's resource limits.
- **Asymmetric Instruction**: Implemented the `bge` requirement of using a specific query instruction prefix (`Represent this sentence for searching relevant passages: `) only during retrieval, not during ingestion.

---

## 5. Persistence & Retrieval (Phase 1.5)

### Decisions
- **Database**: ChromaDB (PersistentClient).
- **Idempotent Upserts**: We use deterministic MD5 hashes (Fund Name + Section) as record IDs.
- **Rationale**: This allows the "Refresh" button (Phase 1.6) to re-run the pipeline and overwrite existing data without creating duplicates or requiring a DB wipe.

### Challenges & Failures
- **Numpy Truthiness Error**: The verification script failed initially because it tried to evaluate the "truthiness" of a numpy array returned by ChromaDB.
- **Resolution**: Refined the check to use explicit `is not None` and `len()` checks.

---

## 6. Current Technical State Summary

| Component | Status | Technology |
|---|---|---|
| **Pipeline** | Complete (1.1 - 1.5) | Python 3.9 |
| **Data Source** | 5 HDFC Direct Growth Funds | Groww JSON Payload |
| **Records** | 40 Factual Chunks | Sectional Format |
| **Embeddings** | 384-dimensional | bge-small-en-v1.5 |
| **Vector Store** | Persistent local storage | ChromaDB |

---

## 7. Upcoming Architectural Shift (Completed in Phase 1.6)

- **Decision**: Implemented an automated **GitHub Actions Workflow** (`weekly_ingestion.yml`) running every Monday at 10:00 AM IST, instead of using a constant background task like `APScheduler` or a manual UI trigger.
- **Rationale**: 
  1. Offloads the heavy CPU/RAM spikes (scraping, embedding) away from the production FastAPI server.
  2. Ensures the database updates even if the backend container is asleep.
  3. Provides a clean audit trail (commits) of data changes over time.
- **Implementation**: A master orchestrator script (`ingest_all.py`) runs the 5 sub-phases and GitHub Actions commits the modified `chroma_db` back to the repository.
