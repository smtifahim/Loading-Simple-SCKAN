#!/usr/bin/env python3
"""
Neural Connectivity RDF-star Data Conversion Tool
==================================================

Main entry point for the neural connectivity data conversion project.
This tool provides a unified interface for all conversion operations.

Usage:
    python main.py [command] [options]

Commands:
    format                  - Format SPARQL JSON to results-only format
    convert                 - Convert SPARQL JSON to RDF-star Turtle
    validate                - Run validation tests on the data
    construct-partial-order - Construct partial order with RDF* in Stardog
    help                    - Show detailed help for each command

Examples:
    python main.py format data/export-poset.json data/export-poset-formatted.json
    python main.py convert data/export-poset-formatted.json output/neural-connectivity-rdfstar.ttl
    python main.py validate
    python main.py construct-partial-order
"""

import sys
import os
from pathlib import Path
import stardog
from dotenv import load_dotenv

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables from .env file
load_dotenv()

def show_usage():
    """Show usage information."""
    print(__doc__)

def format_command(args):
    """Format SPARQL JSON to results-only format."""
    if len(args) < 2:
        print("Error: format command requires input and output file paths")
        print("Usage: python main.py format <input.json> <output.json>")
        return 1
    
    from format_sparql_json import format_sparql_json
    
    input_file = args[0]
    output_file = args[1]
    
    try:
        format_sparql_json(input_file, output_file)
        return 0
    except Exception as e:
        print(f"Error during formatting: {e}")
        return 1

def convert_command(args):
    """Convert SPARQL JSON to RDF-star Turtle."""
    if len(args) < 2:
        print("Error: convert command requires input and output file paths")
        print("Usage: python main.py convert <input.json> <output.ttl>")
        return 1
    
    # Import the correct conversion script
    try:
        from convert_to_rdfstar import convert_to_proper_rdf_star
    except ImportError:
        print("Error: convert_to_rdfstar.py not found in src/ directory")
        return 1
    
    input_file = args[0]
    output_file = args[1]
    
    try:
        convert_to_proper_rdf_star(input_file, output_file)
        return 0
    except Exception as e:
        print(f"Error during conversion: {e}")
        return 1

def validate_command(args):
    """Run validation tests on the data."""
    print("Running validation tests...")
    
    # Check if required files exist
    required_files = [
        "data/export-poset-formatted.json",
        "output/neural-connectivity-rdfstar.ttl"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\nRun the conversion process first:")
        print("   python main.py format data/export-poset.json data/export-poset-formatted.json")
        print("   python main.py convert data/export-poset-formatted.json output/neural-connectivity-rdfstar.ttl")
        return 1
    
    # Run basic validation
    import json
    
    try:
        # Validate JSON structure
        with open("data/export-poset-formatted.json", 'r') as f:
            data = json.load(f)
        
        if "results" not in data or "bindings" not in data["results"]:
            print("Invalid JSON structure in export-poset-formatted.json")
            return 1
        
        binding_count = len(data["results"]["bindings"])
        print(f"Found {binding_count} bindings in JSON data")
        
        # Check TTL file exists and has content
        ttl_path = Path("output/neural-connectivity-rdfstar.ttl")
        if ttl_path.stat().st_size == 0:
            print("TTL file is empty")
            return 1
        
        print(f"TTL file size: {ttl_path.stat().st_size:,} bytes")
        print("All validation checks passed!")
        return 0
        
    except Exception as e:
        print(f"Validation error: {e}")
        return 1

def construct_partial_order_command(args):
    """Construct Partial Order with RDF Star in Stardog."""
    print("Step 4: Constructing Partial Order with RDF Star in Stardog...")
    
    # Stardog connection details from environment variables
    # Using the same cloud endpoint as load-simple-sckan.py
    conn_details = {
        'endpoint': 'https://sd-c1e74c63.stardog.cloud:5820',
        'username': os.getenv('STARDOG_USERNAME'),
        'password': os.getenv('STARDOG_PASSWORD')
    }
    
    temp_db_name = 'temp-partial-order-rdfstar'
    input_ttl_path = './output/neural-connectivity-rdfstar.ttl'
    sparql_query_path = './sparql/construct-partial-order-rdfstar.rq'
    output_ttl_path = '../input_ttl/partial-order-rdfstar.ttl'
    
    # Check if required files exist
    if not Path(input_ttl_path).exists():
        print(f"Error: Input file not found: {input_ttl_path}")
        print("Please run Steps 1-3 first to generate the neural-connectivity-rdfstar.ttl file")
        return 1
    
    if not Path(sparql_query_path).exists():
        print(f"Error: SPARQL query file not found: {sparql_query_path}")
        return 1
    
    try:
        print("        Connecting to Stardog server...")
        with stardog.Admin(**conn_details) as admin:
            # Check if database already exists and drop it
            if temp_db_name in [db.name for db in admin.databases()]:
                print(f"        Dropping existing temporary database '{temp_db_name}'...")
                db = admin.database(temp_db_name)
                db.drop()
            
            # Create temporary database with RDF-star enabled
            print(f"        Creating temporary database '{temp_db_name}' with RDF-star support...")
            options = {"edge.properties": True}  # This enables RDF* queries
            db = admin.new_database(temp_db_name, options=options)
            print(f"        Temporary database '{temp_db_name}' created successfully.")
        
        # Load the neural-connectivity RDF-star file
        print(f"        Loading {input_ttl_path} into the database...")
        with stardog.Connection(temp_db_name, **conn_details) as conn:
            conn.begin()
            conn.add(stardog.content.File(input_ttl_path))
            conn.commit()
            print("        Data loaded successfully.")
            
            # Read and execute the CONSTRUCT query
            print(f"        Running CONSTRUCT query from {sparql_query_path}...")
            with open(sparql_query_path, 'r') as f:
                construct_query = f.read()
            
            result = conn.graph(construct_query)
            
            # Create output directory if it doesn't exist
            output_dir = Path(output_ttl_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save the results
            print(f"        Saving results to {output_ttl_path}...")
            with open(output_ttl_path, 'wb') as f:
                f.write(result)
            print(f"        Results saved successfully.")
        
        # Clean up: drop the temporary database
        print(f"        Cleaning up temporary database '{temp_db_name}'...")
        with stardog.Admin(**conn_details) as admin:
            db = admin.database(temp_db_name)
            db.drop()
            print("        Temporary database dropped.")
        
        print("\nStep 4: Done!")
        print(f"\nOutput: {output_ttl_path}")
        return 0
        
    except Exception as e:
        print(f"Error during partial order construction: {e}")
        # Try to clean up the temporary database even if there was an error
        try:
            with stardog.Admin(**conn_details) as admin:
                if temp_db_name in [db.name for db in admin.databases()]:
                    db = admin.database(temp_db_name)
                    db.drop()
                    print(f"Cleaned up temporary database '{temp_db_name}'")
        except:
            pass
        return 1

def show_help(command=None):
    """Show detailed help for commands."""
    if command == "format":
        print("""
Format Command - Convert SPARQL JSON to results-only format
===========================================================

Usage: python main.py format <input.json> <output.json>

This command takes a full SPARQL JSON export (with 'head' and 'results' sections)
and converts it to a results-only format that other scripts expect.

Examples:
    python main.py format data/export-poset.json data/export-poset-formatted.json
        """)
    elif command == "convert":
        print("""
Convert Command - Convert SPARQL JSON to RDF-star Turtle
========================================================

Usage: python main.py convert <input.json> <output.ttl>

This command converts formatted SPARQL JSON results to RDF-star Turtle format
with unique connection IDs to preserve layer pairing information.

Examples:
    python main.py convert data/export-poset-formatted.json output/neural-connectivity-rdfstar.ttl
        """)
    elif command == "validate":
        print("""
Validate Command - Run validation tests
======================================

Usage: python main.py validate

This command runs validation tests to ensure:
- Required files exist
- JSON data has correct structure
- TTL output file was generated successfully

No arguments required.
        """)
    else:
        show_usage()

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        show_usage()
        return 1
    
    command = sys.argv[1].lower()
    args = sys.argv[2:]
    
    if command == "format":
        return format_command(args)
    elif command == "convert":
        return convert_command(args)
    elif command == "validate":
        return validate_command(args)
    elif command == "construct-partial-order":
        return construct_partial_order_command(args)
    elif command == "help":
        if len(args) > 0:
            show_help(args[0])
        else:
            show_usage()
        return 0
    else:
        print(f"Unknown command: {command}")
        print("Available commands: format, convert, validate, construct-partial-order, help")
        return 1

if __name__ == "__main__":
    sys.exit(main())
