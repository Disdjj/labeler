# AI Issue and Discussion Labeler

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A GitHub Action that uses AI to automatically label your GitHub issues and discussions. Stop manually labeling content and let AI do the work for you!

This action reads the title and body of newly created issues or discussions, sends it to an AI model, and applies the suggested labels to the content. It works with both GitHub Issues and GitHub Discussions.

## How It Works

When an issue or discussion is created, this action is triggered. It performs the following steps:

1.  **Gathers Context**: It collects the content's title, body, and all existing labels in your repository.
2.  **AI Analysis**: It sends this information to a specified AI model, guided by a configurable prompt.
3.  **Generates Labels**: The AI returns a list of suggested labels based on the content.
4.  **Applies Labels**: Finally, it applies the suggested labels to the issue or discussion using the appropriate GitHub API (REST API for issues, GraphQL API for discussions).

## Usage

To use this action in your repository, create a new workflow file in `.github/workflows/`, for example, `labeler.yml`.

```yaml
# .github/workflows/labeler.yml
name: AI Issue and Discussion Labeler

on:
  issues:
    types: [opened, edited, reopened]
  discussion:
    types: [created, edited]

permissions:
  issues: write
  discussions: write
  contents: read

jobs:
  label:
    runs-on: ubuntu-latest
    steps:
      - name: AI Issue and Discussion Labeler
        uses: Disdjj/labeler@v1.0.5 # Replace with your repo and a specific version
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          api-key: ${{ secrets.AI_API_KEY }}
          base-url: ${{ secrets.AI_BASE_URL }}
          # Optional inputs below
          # model: 'gpt-4o'
          # prompt: 'Your custom prompt here. Use {content_type}, {content_title}, {content_body}, and {existing_labels}.'
```

### Prerequisites

You need to add the following secrets to your repository's settings (`Settings > Secrets and variables > Actions`):

*   `AI_API_KEY`: Your API key for the AI service you are using.
*   `AI_BASE_URL`: The base URL for the AI service. For example, for OpenAI, it would be `https://api.openai.com/v1`.

## Inputs

| Name             | Description                                                                                                        | Required | Default                                                                                                                                                                     |
| ---------------- | ------------------------------------------------------------------------------------------------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `github-token`   | The GitHub token to authenticate with the GitHub API.                                                              | `true`   | `N/A`                                                                                                                                                                       |
| `api-key`        | The API key for your AI service.                                                                                   | `true`   | `N/A`                                                                                                                                                                       |
| `base-url`       | The base URL of your AI service provider.                                                                          | `true`   | `N/A`                                                                                                                                                                       |
| `model`          | The specific AI model to use for generating labels.                                                                | `false`  | `gpt-4o`                                                                                                                                                                    |
| `prompt`         | A custom prompt template to guide the AI. You can use `{content_type}`, `{content_title}`, `{content_body}`, and `{existing_labels}` as placeholders. | `false`  | `'Analyze the {content_type} title and body to suggest suitable labels. Here are the existing labels in the repository: {existing_labels}. Return a JSON array of strings. {content_type} Title: {content_title} {content_type} Body: {content_body}'` |

## Features

- **Dual Support**: Works with both GitHub Issues and GitHub Discussions
- **AI-Powered**: Uses advanced AI models to analyze content and suggest relevant labels
- **Flexible Configuration**: Customizable prompts and AI model selection
- **Automatic Detection**: Automatically detects whether the content is an issue or discussion
- **GraphQL Integration**: Uses GitHub's GraphQL API for discussion labeling
- **REST API Support**: Uses GitHub's REST API for issue labeling

## GitHub Discussions Support

This action supports GitHub Discussions through the GraphQL API. When a discussion is created or edited, the action will:

1. Detect that the event is a discussion (not an issue)
2. Use GraphQL queries to fetch discussion information and repository labels
3. Apply the AI-suggested labels using the `addLabelsToLabelable` GraphQL mutation

**Note**: Make sure your repository has GitHub Discussions enabled and that the GitHub token has the necessary permissions (`discussions: write`).

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have ideas for improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

