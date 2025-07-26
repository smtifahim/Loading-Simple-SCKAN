# SCKAN to Simple SCKAN Transformation

The Python script that automates the loading process of Simple SCKAN for the Stardog server is called `load-simple-sckan.py`. It generates all the necessary files needed for Simple SCKAN and loads them into the Stardog server. Additionally, the script generates and saves the `simple-sckan.ttl` and `npo-simple-sckan-merged.ttl` under the `generated_ttl` directory. Observing the [Sample Output](#sample-output) section should provide the undestanding of the overall process.

### **Prerequisites**

The script assumes that you are running Python 3.3 or newer. Make sure that Stardog server is running, and all the input turtle files are available under ./input_ttl directory. The script also assumes that you have the pystradog wrapper library installed.

* If you don't have Stardog installed, please install Stardog for your system.

  * Link to [Stardog Installation and Setup](https://docs.stardog.com/install-stardog/).
  * To know more about accessing and running Simple SCKAN Queries via Stardog, [please review the documentation linked here](https://docs.stardog.com/install-stardog/).
* You need to install [pystardog](https://pypi.org/project/pystardog/) which is a python wrapper for communicating with Stardog HTTP server.

  * `Install pystardog from PyPI: `pip install pystardog`

You will need to specify the current endpoint, username, and password  in `load-simple-sckan.py` script for the Stardog DB server. Look for the comment `# Stardog DB connection details using stradog cloud endpoint` at the upper section of the script.

* 'endpoint': 'https://sd-c1e74c63.stardog.cloud:5820'
* 'user-name': 'sparc-admin'
* 'password': use the password stored in your 1Password account
  * If you don't have 1Password setup for FDI Lab, ask the FDI Lab system admin for the Stardog account's password.

### Input Files

After each [Pre-release or Release of SCKAN](https://github.com/SciCrunch/NIF-Ontology/releases) we need to replace the turtle files under the `input_ttl` directory with the corresponing files used in the SCKAN release. For now, this is a manual process that  involves the following steps:

* Download the file where the name ends with `sckan.zip` from the release link and extract the files
* Under the directory called `data` , select and copy the following 5 files:
  * (1) `npo-merged.ttl`
  * (2) `npo-merged-reasoned.ttl`
  * (3) `uberon.ttl`
  * (4) `uberon-reasoned.ttl`
  * (5)  `prov-record.ttl`
* Paste the four files above under `input_ttl`.

The other input files required for the transformation process are the following. Please note: the following files don't need to be updated unless there are changes in the specification of NPO's relational properties.

* `input_ttl/simple-sckan-properties.ttl` and `sparql-query/simple-sckan-constructs.rq`

  * The `simple-sckan-properties.ttl` contains the annotation properties along with their hierarcies that are used for sckan to simple-sckan transformation. The description of the [Simple SCKAN properties are listed here](https://github.com/SciCrunch/sparc-curation/blob/master/docs/simple-sckan/readme.md#simple-sckan-properties).
  * Updating these files would require the knowledge of updated relational properties used in NPO for SCKAN.
    * Add or update any prefixes in `sparql-query/simple-sckan-constructs.rq` based on the updated  `npo-merged.ttl`.
  * Otherwise, these two files do not need to be replaced or updated too frequently.
* The INSERT queries to simplify the queries for `part of`, `surrounds`, `supplies` relations. 
  * These queries are stored under `sparql-query` directory
  * simplified-partial order query is stored under `sparql-query/simplified-partial-order-queries.rq` which is used to simplify the partial order representation of axonal paths using an rdf-star relation called `hasNextNode`. 

### Output Files

After running `load-simple-sckan.py` the follwing files will be generated under `generated_ttl` dierctory:

* `simple-sckan.ttl` - this will contain the simplified rdf triples based on the inputs of npo-merged.ttl and the SPARQL Construct query specified in `sparql-query/simple-sckan-constructs.rq`
* `npo-simple-sckan-merged.ttl` - this file contains the statements form `simple-sckan.ttl` and `npo-merged.ttl` merged into a single file. This will be used to submit the SCKAN contents as part of the [CFDE data distillary knoweledge graph](https://github.com/TaylorResearchLab/CFDE_DataDistillery/blob/main/user_guide/CFDE_DataDistillery_UserGuide.md) echo system.
* After the loading process, a new database named `NPO-SIMPLE-SCKAN-TEST` will be created on the stardog server. It is recommended that you test the new database with the existing NPO queries stored in Stardog server before updating/replacing the exiting NPO database.

### Sample Output

```
The Simple SCKAN loading process started.
There are 8 steps in this process (Step 0 to Step 7).

Step 0: Checking Stardog server status..
        Server Status: Stardog server is running and able to accept traffic.
Step 0: Done!

Step 1: Creating a new database called 'NPO-SIMPLE-SCKAN-TEST'
        The new database 'NPO-SIMPLE-SCKAN-TEST' is created.
Step 1: Done!

Step 2: Importing namespace prefixes...
Step 2: Done!

Step 3: Adding NPO to the database. Please wait...
        Adding npo-merged.ttl to the database.
        Adding npo-merged-reasoned.ttl to the database.
Step 3: Done!

Step 4: Generating simple-sckan.ttl. Please wait...
        Running simple-sckan construct query.
        Saving query results as simple-sckan.ttl
        File saved at: ./generated_ttl/simple-sckan.ttl
Step 4: Done!

Step 5: Adding Simple SCKAN to the database. Please wait...
        The new database 'simple-sckan' is created.
        Adding simple-sckan-properties.ttl to the database...done!
        Adding simple-sckan.ttl to the database...done!
Step 5: Done!

Step 6: Saving npo-simple-sckan-merged.ttl...
        File saved at: ./generated_ttl/npo-simple-sckan-merged.ttl
Step 6: Done!

Step 7: Adding UBERON to the database. Please wait...
        Adding uberon.ttl to the database.
        Adding uberon-reasoned.ttl to the database.
Step 7: Done!

End of program execution. All steps executed successfully.
```
