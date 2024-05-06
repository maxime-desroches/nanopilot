#!/bin/bash
set -e

cd ../

while true; do
  ./camerad &
  process_id=$!

  sleep 10s

  # Check if the process is still running
  if ! kill -0 $process_id 2>/dev/null; then
    echo "Process has terminated."
    break
  fi

  # Kill the process with SIGKILL
  echo "Killing process $process_id."
  kill -9 $process_id
  sleep 2s
done
