# AI Issue Labeler

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A GitHub Action that uses AI to automatically label your GitHub issues. Stop manually labeling issues and let AI do the work for you!

This action reads the title and body of a newly created issue, sends it to an AI model, and applies the suggested labels to the issue. It can even create new labels if they don't exist in your repository.

## How It Works

When an issue is created, this action is triggered. It performs the following steps:

1.  **Gathers Context**: It collects the issue's title, body, and all existing labels in your repository.
2.  **AI Analysis**: It sends this information to a specified AI model, guided by a configurable prompt.
3.  **Generates Labels**: The AI returns a list of suggested labels based on the issue's content.
4.  **Creates Missing Labels**: If any suggested labels don't already exist, the action creates them automatically.
5.  **Applies Labels**: Finally, it applies the full set of suggested labels to the issue.

## Usage

To use this action in your repository, create a new workflow file in `.github/workflows/`, for example, `labeler.yml`.

```yaml
# .github/workflows/labeler.yml
name: AI Issue Labeler

on:
  issues:
    types: [opened]

permissions:
  issues: write
  contents: read

jobs:
  label:
    runs-on: ubuntu-latest
    steps:
      - name: AI Issue Labeler
        uses: YOUR_USERNAME/YOUR_REPONAME@v1 # Replace with your repo and a specific version
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          api-key: ${{ secrets.AI_API_KEY }}
          base-url: ${{ secrets.AI_BASE_URL }}
          # Optional inputs below
          # model: 'gpt-4o'
          # prompt: 'Your custom prompt here. Use {issue_title}, {issue_body}, and {existing_labels}.'
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
| `prompt`         | A custom prompt template to guide the AI. You can use `{issue_title}`, `{issue_body}`, and `{existing_labels}` as placeholders. | `false`  | `'Analyze the issue title and body to suggest suitable labels. Here are the existing labels in the repository: {existing_labels}. Return a JSON array of strings. Issue Title: {issue_title} Issue Body: {issue_body}'` |


## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have ideas for improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

