#!/bin/bash

set -eu

# Check if required inputs are set
if [[ -z "${INPUT_OPENAI_API_KEY:-}" ]]; then
    echo "🛑 The OpenAI API Key is not set. This key is REQUIRED for the AICodeBot."
    echo "You can get one for free at https://platform.openai.com/account/api-keys"
    echo
    echo "Please set it as a repository secret named 'OPENAI_API_KEY'."
    echo "For more information on how to set up repository secrets, visit:"
    echo "https://docs.github.com/en/actions/security-guides/encrypted-secrets"
    exit 1
fi

export OPENAI_API_KEY=${INPUT_OPENAI_API_KEY}
echo "Using OpenAI API key: ${OPENAI_API_KEY:0:5}..."

# Run aicodebot in the context of the repository
echo "Running aicodebot in ${GITHUB_WORKSPACE} on sha ${GITHUB_SHA:0:8}"
cd ${GITHUB_WORKSPACE}

# Set up the git configuration. Allow the user to override the safe directory
git config --global --add safe.directory /github/workspace

# Set up the aicodebot configuration from the OPENAI_API_KEY
aicodebot configure

# Run a code review on the current commit
aicodebot review -c ${GITHUB_SHA}
