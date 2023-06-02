#!/bin/bash

if [ ! -f "/data/tiles/planet-import-complete" ]; then
    echo "Import not complete, running import..."
    ./run.sh import
else
    echo "Import is complete, skipping import..."
    ./run.sh run
fi
