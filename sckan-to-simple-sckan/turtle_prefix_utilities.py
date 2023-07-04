# This script has a function called fixURIPrefixes which takes two arguments
# the input file path and output file path. The functions reads the input ttl file,
# internally stores the prefix declarations from the top portion of the ttl file, and 
# use those prefixes to replace the full URIs in the triple statements in the output ttl. 
# @Author: Fahim Imam; version 1.0

import re

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


# Testing the function  
#fixURIPrefixes('./generated_ttl/simple-sckan.ttl', './generated_ttl/simple-sckan-2.ttl')
