#!/usr/bin/env python3
"""
Convert raw SPARQL JSON export to formatted SPARQL JSON results structure.

This script takes a basic JSON file with SPARQL query results and converts it
to the standard SPARQL JSON results format used by the other scripts in this project.
- Fahim Imam, November 5, 2025
"""

import json
import sys
from typing import Dict, Any, List

def format_sparql_json(input_file: str, output_file: str) -> None:
    """
    Convert raw SPARQL JSON to formatted SPARQL JSON results structure.
    
    Args:
        input_file: Path to the input JSON file
        output_file: Path to the output formatted JSON file
    """
    
    print(f"Reading raw JSON data from: {input_file}")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}")
        sys.exit(1)
    
    # Handle different input formats
    if isinstance(raw_data, dict) and 'head' in raw_data and 'results' in raw_data and 'bindings' in raw_data['results']:
        # Full SPARQL JSON format with head - preserve complete structure
        print("Data is already in proper SPARQL JSON format with head section.")
        formatted_data = raw_data
    elif isinstance(raw_data, dict) and 'results' in raw_data and 'bindings' in raw_data['results']:
        print("Data has results but missing head section - adding standard head section.")
        # Add a standard head section for SPARQL JSON format
        formatted_data = {
            "head": {
                "vars": ["s", "region_1", "layer_1", "region_2", "layer_2"]
            },
            "results": raw_data["results"]
        }
    else:
        # Convert to SPARQL JSON results format
        print("Converting to SPARQL JSON results format...")
        
        # Handle different possible input formats
        if isinstance(raw_data, list):
            # If it's a list of bindings
            bindings = []
            for item in raw_data:
                binding = {}
                for key, value in item.items():
                    if isinstance(value, str):
                        binding[key] = {
                            "type": "uri" if value.startswith("http") else "literal",
                            "value": value
                        }
                    elif isinstance(value, dict) and "value" in value:
                        # Already formatted binding
                        binding[key] = value
                    else:
                        binding[key] = {
                            "type": "literal",
                            "value": str(value)
                        }
                bindings.append(binding)
            
            formatted_data = {
                "head": {
                    "vars": ["s", "region_1", "layer_1", "region_2", "layer_2"]
                },
                "results": {
                    "bindings": bindings
                }
            }
        
        elif isinstance(raw_data, dict):
            # If it's a dictionary, try to extract bindings
            if 'bindings' in raw_data:
                # Direct bindings array
                bindings = raw_data['bindings']
            elif any(key.startswith(('s', 'region', 'layer')) for key in raw_data.keys()):
                # Single binding object
                binding = {}
                for key, value in raw_data.items():
                    if isinstance(value, str):
                        binding[key] = {
                            "type": "uri" if value.startswith("http") else "literal",
                            "value": value
                        }
                    elif isinstance(value, dict) and "value" in value:
                        binding[key] = value
                    else:
                        binding[key] = {
                            "type": "literal",
                            "value": str(value)
                        }
                bindings = [binding]
            else:
                print("Error: Unable to determine input format.")
                sys.exit(1)
            
            formatted_data = {
                "head": {
                    "vars": ["s", "region_1", "layer_1", "region_2", "layer_2"]
                },
                "results": {
                    "bindings": bindings
                }
            }
        
        else:
            print("Error: Unsupported input format.")
            sys.exit(1)
    
    # Ensure all bindings have proper type information
    for binding in formatted_data['results']['bindings']:
        for key, value in binding.items():
            if isinstance(value, dict) and 'value' in value:
                if 'type' not in value:
                    # Infer type from value
                    if value['value'].startswith('http'):
                        value['type'] = 'uri'
                    else:
                        value['type'] = 'literal'
    
    # Write formatted data
    print(f"Writing formatted SPARQL JSON to: {output_file}")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)
    
    binding_count = len(formatted_data['results']['bindings'])
    print(f"Successfully formatted {binding_count} SPARQL result bindings")
    
    # Show sample of the data
    if binding_count > 0:
        sample = formatted_data['results']['bindings'][0]
        print("\nSample binding:")
        for key, value in sample.items():
            print(f"  {key}: {value.get('value', 'N/A')[:60]}...")

def main():
    """Main function with command line interface."""
    
    if len(sys.argv) != 3:
        print("Usage: python format_sparql_json.py <input_file> <output_file>")
        print("\nExamples:")
        print("  python format_sparql_json.py export-poset.json export-poset-formatted.json")
        print("  python format_sparql_json.py raw-sparql-results.json formatted-results.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print("SPARQL JSON Formatter")
    print("=" * 50)
    
    format_sparql_json(input_file, output_file)
    
    print("\nConversion completed successfully!")
    print(f"Output file: {output_file}")
    print("\nYou can now use this formatted file with other scripts in the project:")
    print("  - convert_to_rdfstar.py")
    print("  - debug_sparql.py") 
    print("  - test_*.py scripts")

if __name__ == "__main__":
    main()
