# This script assumes that the stardog server is running on the localhost, and the input turtle files are located under ./input_ttl directory. 
# It geneates the files necessary for simple sckan based on npo.ttl input file. It connects with Stardog DB server and loads the necessary data.
# This script also assumes that stardog python wrapper is installed in your system.
# (version: 1.0; @Author: Fahim Imam)


import os
import sys
import requests
import subprocess
import stardog
from turtle_utilities import fixURIPrefixes 

## Stardog DB connection details using local host 
# conn_details = {
#   'endpoint': 'http://localhost:5820',
#   'username': 'admin',
#   'password': 'admin'
# }

## Stardog DB connection details using scicrunch endpoint
# conn_details = {
#   'endpoint': 'https://stardog.scicrunch.io:5821',
#   'username': 'admin',
#   'password': 'password from 1password'
# }

# Stardog DB connection details using stradog cloud endpoint
conn_details = {
  'endpoint': 'https://sd-c1e74c63.stardog.cloud:5820',
  'username': 'sparc-admin',
  'password': 'w8399Hzj78exJkaebz'
}

db_name = 'NPO-SIMPLE-SCKAN-TEST'


# input files needed for simple-sckan
input_files = {
    'npo.ttl'                    : './input_ttl/npo-merged.ttl',
    'npo-reasoned.ttl'           : './input_ttl/npo-merged-reasoned.ttl',
    'prefixes.ttl'               : './input_ttl/prefixes.ttl',
    'uberon.ttl'                 : './input_ttl/uberon.ttl',
    'uberon-reasoned.ttl'        : './input_ttl/uberon-reasoned.ttl',
    'simple-sckan-properties.ttl': './input_ttl/simple-sckan-properties.ttl',
    'simple-sckan-constructs.rq' : './sparql-query/simple-sckan-constructs.rq',
    'simplified-partonomy.rq'    : './sparql-query/simplified-partonomy.rq'
    
}

# generated output files for simple-sckan
generated_files = {
    'simple-sckan.ttl'             : './generated_ttl/simple-sckan.ttl',
    'npo-simple-sckan-merged.ttl'  : './generated_ttl/npo-simple-sckan-merged.ttl',
    'npo-stardog-graph.trig'       : './generated_ttl/npo-stardog-graph.trig'
}


def checkServerStatus(admin):
    if (admin.healthcheck()):
        print ("        Server Status: Stardog server is running and able to accept traffic.")
    else:
        print ("        Server Status: Stardog server is NOT running. Please start the server and try again.")
        exit();

# checking if the named database already exists        
def checkDBExists(admin, db_name):
        for database in admin.databases():
            if database.name == db_name:
                return True
        return False

def createNewDatabase(admin, db_name):
    if checkDBExists(admin, db_name):
        print ("        Dropping the existing database named '" + db_name + "'")
        db = admin.database(db_name)
        db.drop()
    db = admin.new_database(db_name)
    print ("        The new database '" + db_name + "' is created.")
    return db

print ("\nThe Simple SCKAN loading process started.\nThere are 8 steps in this process (Step 0 to Step 7).")    
with stardog.Admin(**conn_details) as admin:  
    
    print ("\nStep 0: Checking Stardog server status..")
    checkServerStatus(admin)
    print ("Step 0: Done!")
    
    print ("\nStep 1: Creating a new database called '" + db_name + "'")
    db = createNewDatabase(admin, db_name)
    print ("Step 1: Done!")
        
    print ("\nStep 2: Importing namespace prefixes...")
    db.import_namespaces(stardog.content.File(input_files['npo.ttl']))
    print ("Step 2: Done!")

print ("\nStep 3: Adding NPO to the database. Please wait...")
with stardog.Connection(db_name, **conn_details) as conn:
    # removeMultipleRDFSLabels (input_files['npo.ttl'], input_files['npo.ttl']) # fixes multiple labels for rdfs:label.
    conn.begin()
    print ("        Adding npo-merged.ttl to the database.")    
    conn.add(stardog.content.File(input_files['npo.ttl']))
    print ("        Adding npo-merged-reasoned.ttl to the database.")    
    conn.add(stardog.content.File(input_files['npo-reasoned.ttl']))
    conn.commit()
print ("Step 3: Done!")
       
    # Run SPARQL construct query from file on the web
    # query_url = "https://example.com/sparql-query.rq"
    # query = stardog.content.File('./sparql-query/simple-sckan-constructs.rq')

print ("\nStep 4: Generating simple-sckan.ttl. Please wait...")
with open(input_files['simple-sckan-constructs.rq'], 'r') as file:
    query = file.read()
    print ("        Running simple-sckan construct query.")
    result = conn.graph(query)

    ## Save result in turtle format in generated_ttl folder    
    print ("        Saving query results as simple-sckan.ttl")
    
    if not os.path.exists("generated_ttl"):
        os.mkdir("generated_ttl")
    
    with open(generated_files['simple-sckan.ttl'], "wb") as result_file:
        result_file.write(result)
        # fix URI Prefixes in the generated simple-sckan.ttl
        fixURIPrefixes (generated_files['simple-sckan.ttl'], generated_files['simple-sckan.ttl'])
        result_file.close()
        print ("        File saved at: " + generated_files['simple-sckan.ttl'])
print ("Step 4: Done!")
            
## Step 5 begins.
print ("\nStep 5: Adding Simple SCKAN to the database. Please wait...")
# temporarily creating a database called 'simple sckan'  
db_ss = createNewDatabase(admin, 'simple-sckan')
db_ss.import_namespaces(stardog.content.File(input_files['npo.ttl']))

conn_ss = stardog.Connection('simple-sckan', **conn_details)
conn_ss.begin()

print ("        Adding simple-sckan-properties.ttl to the database...", end="")
conn_ss.add(stardog.content.File(input_files['simple-sckan-properties.ttl']))
print ("done!")

print ("        Adding simple-sckan.ttl to the database...", end="")
conn_ss.add(stardog.content.File(generated_files['simple-sckan.ttl']))
print("done!") 
conn_ss.commit()

with open(generated_files['simple-sckan.ttl'], "wb") as result_file:
    result_file.write(conn_ss.export())
    # fix URI Prefixes in the generated simple-sckan.ttl
    fixURIPrefixes (generated_files['simple-sckan.ttl'], generated_files['simple-sckan.ttl'])
    # result_file.close()   

# adding simple-sckan.ttl to the database.
conn.begin()
conn.add (stardog.content.File(generated_files['simple-sckan.ttl'])) #addig simple sckan to the database
conn.commit()
db_ss.drop() # simple-sckan database is no longer needed to be there in the database. it will be merged with npo in the databse in the next step. 
conn_ss.close()
print ("Step 5: Done!")
    
## Step 6 begins.
print ("\nStep 6: Saving npo-simple-sckan-merged.ttl...")
with open(generated_files['npo-simple-sckan-merged.ttl'], "wb") as result_file:
    result_file.write (conn.export())
    fixURIPrefixes (generated_files['npo-simple-sckan-merged.ttl'], generated_files['npo-simple-sckan-merged.ttl'])
    # removeMultipleRDFSLabels (generated_files['npo-simple-sckan-merged.ttl'], generated_files['npo-simple-sckan-merged.ttl']) # fixes multiple labels for rdfs:label.
    result_file.close()
    print ("        File saved at: " + generated_files['npo-simple-sckan-merged.ttl'])
print ("Step 6: Done!")


print ("\nStep 7: Adding UBERON to the database. Please wait...")
conn.begin()

print ("        Adding uberon.ttl to the database.")
conn.add(stardog.content.File(input_files['uberon.ttl']))

print ("        Adding uberon-reasoned.ttl to the database.")
conn.add(stardog.content.File(input_files['uberon-reasoned.ttl']))

conn.commit()
print ("Step 7: Done!")

print ("\nStep 8: Executing insert query for simplified partonomy. Please wait...")
with open(input_files['simplified-partonomy.rq'], 'r') as file:
    query = file.read()
    print ("        Running insert query.")
    conn.update(query)
print ("Step 8: Done!")

# print ("\nStep 8: Saving the database as a local file...")
# # with open(generated_files['npo-stardog-graph.ttl'], "wb") as result_file:
# #     result_file.write (conn.export()) # saves only in ttl
# #     result_file.close()
# output_file = generated_files['npo-stardog-graph.trig']
# command = f'stardog data export --format trig {db_name} {output_file}'
# subprocess.run(command, shell=True)
# print ("        File saved at: " + generated_files['npo-stardog-graph.trig'])
# print ("Step 8: Done!")
        
print ("\nEnd of program execution. All steps executed successfully.\n\n")
conn.close()

# Run SPARQL select query from file on the web
# query_url = "https://example.com/sparql-query.rq"
# query = requests.get(query_url).text
# result = conn.select(query, accept="text/turtle").raw
