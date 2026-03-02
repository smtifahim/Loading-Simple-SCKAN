#!/usr/bin/env python3

import json

def convert_to_proper_rdf_star(input_file="export-poset-formatted.json", output_file="neural-connectivity-rdfstar.ttl"):
    """Convert JSON to proper RDF-star format with unique quoted triples"""
    
    # Load the JSON data
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    print("Converting to proper RDF-star format with unique statements...")
    print(f"Processing {len(data['results']['bindings'])} entries...")
    
    # Generate TTL content
    ttl_lines = [
        "@prefix ex: <http://tempid.org/> .",
        "",
        "# Neural connectivity data using RDF-star",
        "# Each JSON entry becomes a unique quoted triple with connection ID",
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
        
        # Create a unique connection identifier to make each quoted triple unique
        connection_id = f"http://tempid.org/connection/{connection_count}"
        connection_count += 1
        
        # Create RDF-star quoted triple with unique connection ID
        # Format: << connectionID ex:connects region1 >> ex:to region2 .
        quoted_triple = f"<< <{connection_id}> ex:connects <{region1}> >>"
        
        # Main connection
        ttl_lines.append(f"{quoted_triple} ex:to <{region2}> .")
        ttl_lines.append(f"{quoted_triple} ex:via <{neuron}> .")
        
        # Add layer information if present
        if layer1:
            ttl_lines.append(f"{quoted_triple} ex:fromLayer <{layer1}> .")
        if layer2:
            ttl_lines.append(f"{quoted_triple} ex:toLayer <{layer2}> .")
        
        ttl_lines.append("")  # Empty line for readability
    
    # Write to new TTL file
    with open(output_file, 'w') as f:
        f.write('\n'.join(ttl_lines))
    
    print(f"Created {output_file} with {connection_count} unique RDF-star statements")
    
    return connection_count

def create_rdfstar_sparql_query():
    """Create SPARQL query for the RDF-star format"""
    
    sparql_content = """# SPARQL query for RDF-star neural connectivity data
# Each connection has a unique ID to preserve layer pairings

PREFIX ex: <http://tempid.org/>

SELECT DISTINCT ?neuron ?region1 ?layer1 ?region2 ?layer2 
WHERE {
  # Find the quoted triple pattern
  << ?connectionId ex:connects ?region1 >> ex:to ?region2 .
  << ?connectionId ex:connects ?region1 >> ex:via ?neuron .
  
  # Get layer information for this specific connection
  OPTIONAL { << ?connectionId ex:connects ?region1 >> ex:fromLayer ?layer1 }
  OPTIONAL { << ?connectionId ex:connects ?region1 >> ex:toLayer ?layer2 }
}
ORDER BY ?neuron ?region1 ?region2"""
    
    with open('query-rdfstar-connectivity.sparql', 'w') as f:
        f.write(sparql_content)
    
    print("Created query-rdfstar-connectivity.sparql")
    
    return count

if __name__ == "__main__":
    import sys
    
    # Handle command line arguments
    input_file = sys.argv[1] if len(sys.argv) > 1 else "export-poset-formatted.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "neural-connectivity-rdfstar.ttl"
    
    # Convert to proper RDF-star format
    count = convert_to_proper_rdf_star(input_file, output_file)
    
    # Create corresponding query
    create_rdfstar_sparql_query()
    
    print("\n" + "="*60)
    print("RDF-STAR SOLUTION SUMMARY:")
    print("="*60)
    print("True RDF-star format using quoted triples")
    print("Each JSON entry gets a unique connection ID")
    print("Layer pairing information is preserved")
    print("Compatible with Stardog's RDF-star support")
    print(f"Total connections: {count}")
    print("\nFiles created:")
    print(f"- {output_file} (RDF-star format)")
    print("- query-rdfstar-connectivity.sparql (matching query)")
