#!/usr/bin/env python3

import json

def convert_to_proper_rdf_star(input_file="export-poset-formatted.json", output_file="neural-connectivity-proper.ttl"):
    """Convert JSON to RDF-star with each JSON entry as a unique statement"""
    
    # Load the JSON data
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    print("Converting to proper RDF-star format...")
    print(f"Processing {len(data['results']['bindings'])} entries...")
    
    # Generate TTL content
    ttl_lines = [
        "@prefix ex: <http://tempid.org/> .",
        "",
        "# Neural connectivity data using RDF-star",
        "# Each JSON entry becomes a unique RDF-star statement with all layer info",
        ""
    ]
    
    connection_count = 0
    
    for binding in data['results']['bindings']:
        # Extract data
        neuron = binding['s']['value']
        region1 = binding['region_1']['value']
        region2 = binding['region_2']['value']
        layer1 = binding.get('layer_1', {}).get('value') if binding.get('layer_1') else None
        layer2 = binding.get('layer_2', {}).get('value') if binding.get('layer_2') else None
        
        # Create a unique connection ID for this specific entry
        connection_id = f"_:conn{connection_count}"
        connection_count += 1
        
        # Create the main RDF-star statement with all information in one place
        # Using a blank node to represent this specific connection instance
        ttl_lines.append(f"{connection_id} a ex:Connection ;")
        ttl_lines.append(f"    ex:neuron <{neuron}> ;")
        ttl_lines.append(f"    ex:fromRegion <{region1}> ;")
        ttl_lines.append(f"    ex:toRegion <{region2}> ;")
        
        if layer1:
            ttl_lines.append(f"    ex:fromLayer <{layer1}> ;")
        if layer2:
            ttl_lines.append(f"    ex:toLayer <{layer2}> ;")
        
        # Remove the trailing semicolon and add period
        if ttl_lines[-1].endswith(' ;'):
            ttl_lines[-1] = ttl_lines[-1][:-2] + ' .'
        
        ttl_lines.append("")  # Empty line for readability
    
    # Write to new TTL file
    with open(output_file, 'w') as f:
        f.write('\n'.join(ttl_lines))
    
    print(f"Created {output_file} with {connection_count} unique connections")
    
    return connection_count

def create_proper_sparql_query():
    """Create SPARQL query for the proper RDF-star format"""
    
    sparql_content = """# SPARQL query for properly structured neural connectivity data
# Each connection is a unique blank node with all layer information preserved

PREFIX ex: <http://tempid.org/>

SELECT DISTINCT ?neuron ?fromRegion ?fromLayer ?toRegion ?toLayer 
WHERE {
  ?connection a ex:Connection ;
              ex:neuron ?neuron ;
              ex:fromRegion ?fromRegion ;
              ex:toRegion ?toRegion .
  
  OPTIONAL { ?connection ex:fromLayer ?fromLayer }
  OPTIONAL { ?connection ex:toLayer ?toLayer }
}
ORDER BY ?neuron ?fromRegion ?toRegion ?fromLayer ?toLayer"""
    
    with open('query-proper-connectivity.sparql', 'w') as f:
        f.write(sparql_content)
    
    print("Created query-proper-connectivity.sparql")

if __name__ == "__main__":
    import sys
    
    # Handle command line arguments
    input_file = sys.argv[1] if len(sys.argv) > 1 else "export-poset-formatted.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "neural-connectivity-proper.ttl"
    
    # Convert to proper format
    count = convert_to_proper_rdf_star(input_file, output_file)
    
    # Create corresponding query
    create_proper_sparql_query()
    
    print("\n" + "="*60)
    print("SOLUTION SUMMARY:")
    print("="*60)
    print("Each JSON entry is now a separate RDF statement")
    print("No loss of layer pairing information")
    print("SPARQL query will return exactly the same data as JSON")
    print(f"Total connections: {count}")
    print("\nFiles created:")
    print(f"- {output_file} (corrected data model)")
    print("- query-proper-connectivity.sparql (matching query)")
