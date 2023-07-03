#!/bin/sh

set -euo

case "${INPUT_COMMENT_SEVERITY_LEVEL}" in
    "info")
        COMMENT_LEVEL=0
        ;;
    "warning")
        COMMENT_LEVEL=1
        ;;
    "error")
        COMMENT_LEVEL=2
        ;;
   *)
        echo "Unknown comment severity level: ${INPUT_COMMENT_SEVERITY_LEVEL}"
        exit 1
        ;;
esac

if [ "${INPUT_FAIL_ON_ERROR}" = "true" ]; then
    FAIL_ON_ERROR=1
else
    FAIL_ON_ERROR=0
fi

if [ "${INPUT_ENABLE_GIF_REACTIONS}" = "true" ]; then
    ENABLE_GIF_REACTIONS=1
else
    ENABLE_GIF_REACTIONS=0
fi

echo "Comment severity level: $COMMENT_LEVEL"
echo "Fail on error: $FAIL_ON_ERROR"
echo "Enable GIF reactions: $ENABLE_GIF_REACTIONS"
