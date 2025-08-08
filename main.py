import json
import os
from typing import List

from dotenv import load_dotenv
from github import (
    Github,
    GithubException,
)
from pydantic import (
    BaseModel,
    Field,
)
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

# 加载.env文件
load_dotenv()

# 全局配置变量
GITHUB_TOKEN = os.environ.get("INPUT_GITHUB-TOKEN")
API_KEY = os.environ.get("INPUT_API-KEY")
BASE_URL = os.environ.get("INPUT_BASE-URL")
MODEL = os.environ.get("INPUT_MODEL", "gpt-4o")
PROMPT_TEMPLATE = os.environ.get(
    "INPUT_PROMPT",
    'Analyze the issue title and body to suggest suitable labels. '
    'Here are the existing labels in the repository: {existing_labels}. '
    'Return a JSON array of strings. '
    'Issue Title: {issue_title} '
    'Issue Body: {issue_body}'
)
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")
GITHUB_EVENT_PATH = os.environ.get("GITHUB_EVENT_PATH")


class IssueLabels(BaseModel):
    labels: List[str] = Field(..., description="A list of relevant labels for the GitHub issue.")


# 定义 agent
ai_provider = OpenAIProvider(api_key=API_KEY, base_url=BASE_URL)
ai_model = OpenAIModel(MODEL, provider=ai_provider)
model = ai_model
ai_agent = Agent(model, output_type=IssueLabels)


def main():
    # 初始化 GitHub 客户端
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(GITHUB_REPOSITORY)

    # 加载 issue 数据
    with open(GITHUB_EVENT_PATH, 'r') as f:
        event_data = json.load(f)

    issue_number = event_data['issue']['number']
    issue = repo.get_issue(number=issue_number)
    issue_title = issue.title
    issue_body = issue.body or ""

    # 获取现有标签
    try:
        existing_labels = [label.name for label in repo.get_labels()]
        print(f"Existing labels in the repo: {existing_labels}")
    except GithubException as e:
        print(f"Error fetching labels: {e}")
        existing_labels = []

    prompt = PROMPT_TEMPLATE.format(
        existing_labels=", ".join(existing_labels),
        issue_title=issue_title,
        issue_body=issue_body
    )

    print("Sending prompt to AI...")
    try:
        ai_response = ai_agent.run_sync(prompt)
        suggested_labels = ai_response.output.labels
        print(f"AI suggested labels: {suggested_labels}")
    except Exception as e:
        print(f"Error calling AI service: {e}")
        return

    # 只使用已存在的标签
    final_labels = []
    existing_labels_lower = [l.lower() for l in existing_labels]

    for label_name in suggested_labels:
        if label_name.lower() in existing_labels_lower:
            # 找到原始大小写的标签名
            original_label = next(l for l in existing_labels if l.lower() == label_name.lower())
            final_labels.append(original_label)
        else:
            print(f"Label '{label_name}' does not exist in repository, skipping.")

    # 应用标签到 issue
    if final_labels:
        try:
            print(f"Applying labels to issue #{issue_number}: {final_labels}")
            current_labels = [label.name for label in issue.get_labels()]
            all_labels = list(set(current_labels + final_labels))
            issue.set_labels(*all_labels)
            print("Labels applied successfully.")
        except GithubException as e:
            print(f"Failed to apply labels: {e}")
    else:
        print("No valid labels to apply.")


if __name__ == "__main__":
    main()
