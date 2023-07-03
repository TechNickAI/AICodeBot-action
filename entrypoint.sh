#!/bin/bash

set -eu

# Check if required inputs are set
if [[ -z "${INPUT_OPENAI_API_KEY}" ]]; then
    echo "Error: The OPENAI_API_KEY is not set. Please set it as an environment variable."
    exit 1
fi

# Export inputs as environment variables
export OPENAI_API_KEY=${INPUT_OPENAI_API_KEY}
export COMMENT_SEVERITY_LEVEL=${INPUT_COMMENT_SEVERITY_LEVEL:-info}
export FAIL_ON_ERROR=${INPUT_FAIL_ON_ERROR:-false}
export ENABLE_GIF_REACTIONS=${INPUT_ENABLE_GIF_REACTIONS:-false}

# Run aicodebot in the context of the repository
cd ${GITHUB_WORKSPACE}
aicodebot review -c ${GITHUB_SHA}
