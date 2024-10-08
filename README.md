# AICodeBot Code Review GitHub Action 🤖

## Your AI-powered code review assistant

This GitHub Action utilizes AICodeBot, an AI-powered coding assistant, to review code in commits and pull requests. It is designed to make
your code review process more efficient and thorough. This action is built to work with existing code bases at the git-commit level, aiming
to enhance the effectiveness of your code review process.

## Features

* Automated Code Review: This action will automatically review your code whenever a commit or pull request is made, providing feedback and suggestions for improvement.
* Context-Aware: The action uses the context of your repository to provide relevant and useful feedback.
* Easy Integration: Simply add this action to your GitHub workflow and it will start reviewing your code.

## Usage

```yaml
name: AICodeBot

on: [push,pull_request]

# Permissions for the GitHub token.
# This is so the bot can comment on the commit or pull request with the results of the code review.
permissions:
  pull-requests: write
  issues: write
  contents: write

jobs:
  review:
    name: AICodeBot Code Review
    runs-on: ubuntu-latest
    timeout-minutes: 5

    steps:
      - name: Checkout Repo
        uses: actions/checkout@v3
        with:
          # Full git history is needed to get a proper list of changed files
          fetch-depth: 0

      - name: AICodeBot Code Review
        uses: TechNickAI/AICodeBot-action@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

In this example, the action is triggered whenever a push or pull request event occurs. It checks out your code and then runs the AICodeBot Code Review action.

## Setup

To use this action, you need to set up the `OPENAI_API_KEY` as a secret in your GitHub repository. This key is required for the AICodeBot to function. You can obtain this key on your [OpenAI api settings page](https://platform.openai.com/account/api-keys). Typical usage will cost < $5 a month.

To set up the OPENAI_API_KEY as a secret in your GitHub repository, you can refer to the [GitHub documentation on secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets).

## Outputs

The response will include a review_status and a review_comments.  There are three possible review_status values:

* PASSED: ✅ The code review passed
* FAILED: 🛑 At least one serious issue was found, and the action will fail
* COMMENTS: ⚠️ The code review passed, but there are some suggestions for improvement. [Real world example](https://github.com/gorillamania/AICodeBot/commit/a8ba588a5deaf9b863d5b103061a715a2924e908#commitcomment-122803771)

When a code review fails or has comments, the action will add a comment to the commit or pull request with the review_comments.

## Alignment ❤️ + 🤖

We believe that AI should be built in a way that aligns with humanity. We're building this GitHub Action from a heart-centered space, contributing to the healthy intersection of AI and humanity.
