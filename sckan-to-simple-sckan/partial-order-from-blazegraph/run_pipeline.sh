#!/bin/bash
# Neural Connectivity Data Conversion Workflow
# =============================================
# This script runs the complete data conversion pipeline for the neural connectivity dataset, including:
# 1. Running a SPARQL query against a Blazegraph server to extract the relevant data.
# 2. Formatting the raw SPARQL JSON output into a structured format.
# 3. Converting the formatted data into RDF-star format.
# 4. Validating the conversion results.
# 5. Constructing the partial order with RDF-star in Stardog (with region-layer pairs).
# Usage:
#   ./run_pipeline.sh    

set -e  # Exit on any error

echo "Neural Connectivity Data Conversion Pipeline"
echo "=============================================="
echo

# Step 0: Run Blazegraph Query
echo "Step 0: Running Blazegraph Query..."
echo "Starting Blazegraph server..."

# Check if blazegraph.jar exists
if [ ! -f "Blazegraph/blazegraph.jar" ]; then
    echo "Error: blazegraph.jar not found in Blazegraph/ directory"
    exit 1
fi

# Check if blazegraph.jnl exists
if [ ! -f "Blazegraph/blazegraph.jnl" ]; then
    echo "Error: blazegraph.jnl not found in Blazegraph/ directory"
    echo "Please copy blazegraph.jnl to the Blazegraph/ directory"
    exit 1
fi

# Store the current directory
ORIGINAL_DIR="$PWD"

# Create a temporary directory with a safe path (no special characters)
TEMP_BG_DIR="/tmp/blazegraph-$$"
mkdir -p "$TEMP_BG_DIR"

# Copy blazegraph files to temp directory to avoid path issues with commas
echo "Setting up Blazegraph in temporary directory..."
cp "Blazegraph/blazegraph.jar" "$TEMP_BG_DIR/"
cp "Blazegraph/blazegraph.jnl" "$TEMP_BG_DIR/"

# Start Blazegraph from the temp directory
cd "$TEMP_BG_DIR"
nohup java -server -Xmx4g -jar blazegraph.jar > blazegraph.log 2>&1 &
BLAZEGRAPH_PID=$!
cd "$ORIGINAL_DIR"

echo "Blazegraph server started (PID: $BLAZEGRAPH_PID) in $TEMP_BG_DIR"
echo "Waiting for Blazegraph to be ready..."

# Wait for Blazegraph to start (check if it's responding)
MAX_ATTEMPTS=30
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -s http://localhost:9999/blazegraph/namespace > /dev/null 2>&1; then
        echo "Blazegraph is ready!"
        break
    fi
    echo "Waiting for Blazegraph to start... ($((ATTEMPT+1))/$MAX_ATTEMPTS)"
    sleep 2
    ATTEMPT=$((ATTEMPT+1))
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo "Error: Blazegraph failed to start within expected time"
    echo "Check $TEMP_BG_DIR/blazegraph.log for details"
    kill $BLAZEGRAPH_PID 2>/dev/null || true
    rm -rf "$TEMP_BG_DIR"
    exit 1
fi

# Run SPARQL query
echo "Running SPARQL query from sparql/sckan-partial-order.rq...(this may take a minute or so..)"
SPARQL_QUERY=$(cat sparql/sckan-partial-order.rq)

# Try to execute the query and capture both the response and errors
HTTP_CODE=$(curl -X POST http://localhost:9999/blazegraph/namespace/kb/sparql \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -H "Accept: application/sparql-results+json" \
    --data-urlencode "query=$SPARQL_QUERY" \
    -w "%{http_code}" \
    -s \
    -o data/partial-order-unformatted.json)

echo "HTTP Response Code: $HTTP_CODE"

# Check if file has content
if [ ! -s data/partial-order-unformatted.json ]; then
    echo "Warning: Query returned empty response"
    echo "Checking what's in the file..."
    cat data/partial-order-unformatted.json
    echo ""
    echo "Checking available namespaces..."
    curl -s http://localhost:9999/blazegraph/namespace
    echo ""
    kill $BLAZEGRAPH_PID 2>/dev/null || true
    rm -rf "$TEMP_BG_DIR"
    exit 1
fi

echo "Query results saved to data/partial-order-unformatted.json"

# Stop Blazegraph server
echo "Stopping Blazegraph server..."
kill $BLAZEGRAPH_PID 2>/dev/null || true
sleep 2
echo "Blazegraph server stopped"

# Clean up temporary directory
echo "Cleaning up temporary directory..."
rm -rf "$TEMP_BG_DIR"
echo

# Step 1: Format the raw SPARQL JSON
echo "Step 1: Formatting SPARQL JSON..."
python main.py format data/partial-order-unformatted.json data/export-poset-formatted.json
echo

# Step 2: Convert to RDF-star format
echo "Step 2: Converting to RDF-star format..."
python main.py convert data/export-poset-formatted.json output/neural-connectivity-rdfstar.ttl
echo

# Step 3: Validate the conversion
echo "Step 3: Validating conversion..."
python main.py validate
echo

# Step 4: Construct Partial Order with RDF Star in Stardog
echo "Step 4: Constructing Partial Order with RDF Star in Stardog..."
python main.py construct-partial-order
echo

echo "Pipeline completed successfully!"
echo
echo "Output files:"
echo "   - data/export-poset-formatted.json (formatted input)"
echo "   - output/neural-connectivity-rdfstar.ttl (RDF-star output)"
echo "   - ../input_ttl/partial-order-rdfstar.ttl (partial order with region-layer pairs)"
echo
echo "Next step:"
echo "   Run load-simple-sckan.py manually to complete the Simple SCKAN loading process"
