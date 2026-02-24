import csv
import random
import string
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

def generate_test_data(file_path: str, num_rows: int = 1_000_000):
    """Generates a CSV file with mock data."""
    if os.path.exists(file_path):
        logger.info(f"Test data file '{file_path}' already exists. Skipping generation.")
        return

    logger.info(f"Generating {num_rows} rows of test data into '{file_path}' (this may take a moment)...")
    
    start_time = datetime.now()
    
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Header is usually not copied directly in copy_expert with CSV if handled properly, 
        # but let's be explicit and just write raw data without header to make STDIN copy simpler.
        # Format: id, name, email, score, created_at
        
        batch_size = 10000
        rows = []
        for i in range(1, num_rows + 1):
            name = generate_random_string(15)
            email = f"{name.lower()}@example.com"
            score = round(random.uniform(0.0, 100.0), 2)
            created_at = (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat()
            
            rows.append([i, name, email, score, created_at])
            
            if i % batch_size == 0:
                writer.writerows(rows)
                rows = []
                
        # Write any remaining
        if rows:
            writer.writerows(rows)

    duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"Successfully generated {num_rows} rows in {duration:.2f} seconds.")
