# This script has functions that takes two arguments: the input file path and output file path. 
# The input file is expected to be in turtle format.
# It reads the issues in the input file and replaces the lines with fixes in the output file
# as indicated in the functions defined in this script.  
# @Author: Fahim Imam; version 1.0

import re

# This function fixes the issues with multiple rdfs labels in the input turtle file.
# needs more testing -Fahim
def removeMultipleRDFSLabels(input_file, output_file):
    with open(input_file, 'r') as input_file:
        content = input_file.read()
        # For cases with a newline after the first comma
        modified_content = re.sub(r'rdfs:label\s+"([^"]+)"(?:,\n\s*"([^"]+)"(?:@en)?)?\s*;', r'rdfs:label "\g<2>";', content)
        # For cases without a newline after the first comma
        modified_content = re.sub(r'rdfs:label\s"(.+?)"\s*,\s*"(.*?)".s*;', r'rdfs:label "\g<2>";', content)
        
    with open(output_file, 'w') as output_file:
        output_file.write(modified_content)


# The functions reads the input ttl file, internally stores the prefix declarations from the top portion of the ttl file, and 
# use those prefixes to replace the full URIs in the triple statements in the output ttl.
def fixURIPrefixes(input_file, output_file):
    # Read the input file
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Extract the prefix declarations
    prefixes = []
    prefix_map = {}
    prefix_regex = re.compile(r'@prefix\s+(\w+):\s+<(.+)>')
    for line in lines:
        if line.startswith('@prefix'):
            match = prefix_regex.match(line)
            if match:
                prefix_name = match.group(1)
                prefix_uri = match.group(2)
                prefixes.append(line.strip())
                prefix_map[prefix_uri] = prefix_name

    # Replace full URIs with CURIEs in triples
    triples = []
    uri_regex = re.compile(r'<([^>]*)>')
    for line in lines:
        if not line.startswith('@prefix'):
            matches = uri_regex.findall(line)
            for uri in matches:
                if uri.startswith('http://'):
                    for prefix_uri in prefix_map:
                        if uri.startswith(prefix_uri):
                            curie = prefix_map[prefix_uri] + ':' + uri[len(prefix_uri):]
                            line = line.replace('<' + uri + '>', curie)
                            break
            triples.append(line)

    # Write the modified triples to the output file
    with open(output_file, 'w') as file:
        file.write('\n'.join(prefixes))
        file.write('\n')
        file.writelines(triples)


# Testing the functions
# fixURIPrefixes('./generated_ttl/npo-simple-sckan-merged.ttl', './generated_ttl/npo-simple-sckan-2.ttl')
# removeMultipleRDFSLabels('./input_ttl/npo-merged.ttl', './input_ttl/npo-merged-1.ttl')
# removeMultipleRDFSLabels('./generated_ttl/npo-simple-sckan-merged.ttl', './generated_ttl/npo-simple-sckan-merged.ttl')
