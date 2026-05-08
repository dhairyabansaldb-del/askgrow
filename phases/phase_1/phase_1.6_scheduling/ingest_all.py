"""
Phase 1.6 - Master Ingestion Orchestrator

This script is the entry point for the GitHub Actions automated workflow.
It sequentially executes all the phases of the data pipeline:
1. Phase 1.2: Scraper -> Downloads raw JSON data
2. Phase 1.2: Cleaner -> Removes unnecessary data, formats nicely
3. Phase 1.3: Chunker -> Breaks cleaned data into self-contained factual chunks
4. Phase 1.4: Embedder -> Generates vector embeddings for each chunk
5. Phase 1.5: DB Manager -> Upserts embeddings into ChromaDB
"""

import sys
import os
import importlib.util
import time

def run_script(script_path, module_name, run_func_name):
    """Dynamically import and run a script's main function."""
    print(f"\n{'='*80}")
    print(f"Starting: {module_name} ({script_path})")
    print(f"{'='*80}")
    
    start_time = time.time()
    original_cwd = os.getcwd()
    
    try:
        # Change working directory to the script's directory so relative imports/paths work
        script_dir = os.path.dirname(script_path)
        os.chdir(script_dir)
        sys.path.insert(0, script_dir)
        
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        # Execute the specified runner function
        run_func = getattr(module, run_func_name)
        run_func()
        
        elapsed = time.time() - start_time
        print(f"\n[OK] Completed {module_name} in {elapsed:.2f} seconds.")
    except Exception as e:
        print(f"\n[x] FAILED {module_name}: {str(e)}")
        os.chdir(original_cwd)
        sys.exit(1)
    finally:
        # Clean up path and restore original working directory
        if script_dir in sys.path:
            sys.path.remove(script_dir)
        os.chdir(original_cwd)

def main():
    print("Mutual Fund Chatbot - Master Ingestion Pipeline")
    total_start_time = time.time()
    
    # Define paths relative to this script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    phase_1_dir = os.path.dirname(script_dir)
    
    # 1. Scraper
    scraper_path = os.path.join(phase_1_dir, "phase_1.2_scraping", "scraper.py")
    run_script(scraper_path, "scraper", "run_scraper")
    
    # 2. Cleaner
    cleaner_path = os.path.join(phase_1_dir, "phase_1.2_scraping", "cleaner.py")
    run_script(cleaner_path, "cleaner", "run_cleaner")
    
    # 3. Chunker
    chunker_path = os.path.join(phase_1_dir, "phase_1.3_chunking", "chunker.py")
    run_script(chunker_path, "chunker", "run_chunker")
    
    # 4. Embedder
    embedder_path = os.path.join(phase_1_dir, "phase_1.4_embedding", "embedder.py")
    run_script(embedder_path, "embedder", "run_embedder")
    
    # 5. DB Manager
    db_manager_path = os.path.join(phase_1_dir, "phase_1.5_vector_storage", "db_manager.py")
    run_script(db_manager_path, "db_manager", "run_db_manager")
    
    total_elapsed = time.time() - total_start_time
    print(f"\n{'*'*80}")
    print(f"PIPELINE COMPLETE: All phases executed successfully in {total_elapsed:.2f} seconds.")
    print(f"{'*'*80}")

if __name__ == "__main__":
    main()
