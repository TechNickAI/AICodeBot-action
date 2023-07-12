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
aicodebot -V
aicodebot configure

# Run a code review on the current commit
review_output=$(aicodebot review -c ${GITHUB_SHA} --output-format=json) || {
    echo "Error: aicodebot review command failed. Output was:"
    echo $review_output
    exit 1
}
review_status=$(echo $review_output | jq -r '.review_status')
review_comments=$(echo $review_output | jq -r '.review_comments')

# Magic to set the output variables for github workflows
echo "{review_status}={$review_status}" >>$GITHUB_STATE
echo "{review_comments}={$review_comments}" >>$GITHUB_STATE

if [[ $review_status == "PASSED" ]]; then
    # TOOD: Add thumbs up reaction to the commit
    echo "👍 Code review passed!"
    echo "Comments: $review_comments"
    exit 0
elif [[ $review_status == "FAILED" ]]; then
    # TODO: Leave a comment with the review_comments
    echo "🛑 Code review failed!"
    echo "Comments: $review_comments"

    # Fail the action
    exit 1
elif [[ $review_status == "COMMENTS" ]]; then
    # TODO: Leave a comment with the review_comments
    echo "🤔 Code review has comments. Please review the suggestions"
    echo "Comments: $review_comments"
    exit 1
fi
