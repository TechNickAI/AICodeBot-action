#!/bin/bash

set -eu

# Check if required inputs are set
if [[ -z "${INPUT_OPENAI_API_KEY:-}" ]]; then
    echo "Error: The INPUT_OPENAI_API_KEY is not set. Please set it as an environment variable."
    exit 1
fi

echo "Using OpenAI API key: ${OPENAI_API_KEY:0:5}..."
export OPENAI_API_KEY=${INPUT_OPENAI_API_KEY}

# Run aicodebot in the context of the repository
echo "Running aicodebot in ${GITHUB_WORKSPACE} on sha ${GITHUB_SHA:0:8}"
cd ${GITHUB_WORKSPACE}
aicodebot review -c ${GITHUB_SHA}
