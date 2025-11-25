import csv
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, OWL

# Create a new graph
g = Graph()

# Define namespaces
ILXTR = Namespace("http://uri.interlex.org/tgbugs/uris/readable/")
ILX_BASE = Namespace("http://uri.interlex.org/base/")
UBERON = Namespace("http://purl.obolibrary.org/obo/UBERON_")
OBO = Namespace("http://purl.obolibrary.org/obo/")

# Bind prefixes for prettier output
g.bind("ilxtr", ILXTR)
g.bind("ilx", ILX_BASE)
g.bind("UBERON", UBERON)
g.bind("obo", OBO)
g.bind("owl", OWL)

# Define the hasRegion property as an annotation property
has_region = ILXTR.hasRegion
g.add((has_region, RDF.type, OWL.AnnotationProperty))

# Read CSV and add triples
with open('region-layer-pairs.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    
    # Debug: print column names
    print(f"Column names found: {reader.fieldnames}")
    
    for row in reader:
        # Get column values - strip whitespace from column names too
        region_iri = None
        layer_iri = None
        
        for key, value in row.items():
            key_clean = key.strip()
            if 'Region' in key_clean:
                region_iri = value.strip()
            elif 'Layer' in key_clean:
                layer_iri = value.strip()
        
        # Skip empty rows
        if not region_iri or not layer_iri:
            continue
        
        # Create URIRefs
        layer = URIRef(layer_iri)
        region = URIRef(region_iri)
        
        # Declare as OWL classes
        g.add((layer, RDF.type, OWL.Class))
        g.add((region, RDF.type, OWL.Class))
        
        # Add triple: layer hasRegion region
        g.add((layer, has_region, region))

# Serialize to TTL file
output_file = 'region-layer-pairs.ttl'
g.serialize(destination=output_file, format='turtle')

print(f"Successfully created {output_file} with {len(g)} triples")
print(f"Found {len(list(g.triples((None, has_region, None))))} region-layer mappings")