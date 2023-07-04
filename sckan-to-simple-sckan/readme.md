# Simple SCKAN Loading Process

The python script that generates and loads the Simple SCKAN into Stardog server is called `load-simple-sckan.py`.

### **Prerequisites**

The script assumes that you are running Python 3.3 or newer. Make sure that Stardog server is running, and all the input turtle files are available under ./input_ttl directory. The script also assumes that you have the pystradog wrapper library installed.

* If you want to load Simple SCKAN using Stardog local host, please install Stardog for your system.
  * [Stardog Installation and Setup](https://docs.stardog.com/install-stardog/)
* You need to install [pystardog](https://pypi.org/project/pystardog/) which is a python wrapper for communicating with Stardog HTTP server.
  * Install pystardog from PyPI: `pip install pystardog`

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
