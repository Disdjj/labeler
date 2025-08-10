import json
import os
from typing import List, Optional, Union

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
    'Analyze the {content_type} title and body to suggest suitable labels. '
    'Here are the existing labels in the repository: {existing_labels}. '
    'Return a JSON array of strings. '
    '{content_type} Title: {content_title} '
    '{content_type} Body: {content_body}'
)
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")
GITHUB_EVENT_PATH = os.environ.get("GITHUB_EVENT_PATH")


class ContentLabels(BaseModel):
    """通用的标签模型，适用于issues和discussions"""
    labels: List[str] = Field(..., description="A list of relevant labels for the GitHub content.")


class IssueLabels(ContentLabels):
    """向后兼容的issue标签模型"""
    pass


class DiscussionLabels(ContentLabels):
    """Discussion标签模型"""
    pass


# 定义 AI provider 和 model
ai_provider = OpenAIProvider(api_key=API_KEY, base_url=BASE_URL)
ai_model = OpenAIModel(MODEL, provider=ai_provider)
model = ai_model

# 创建不同类型内容的 agents
issue_agent = Agent(model, output_type=IssueLabels)
discussion_agent = Agent(model, output_type=DiscussionLabels)


def detect_event_type(event_data):
    """检测事件类型：issue 或 discussion"""
    if 'issue' in event_data:
        return 'issue'
    elif 'discussion' in event_data:
        return 'discussion'
    else:
        raise ValueError("Unknown event type: neither issue nor discussion found in event data")


def get_content_info(event_data, event_type):
    """根据事件类型获取内容信息"""
    if event_type == 'issue':
        content = event_data['issue']
        return {
            'number': content['number'],
            'title': content['title'],
            'body': content.get('body', ''),
            'type': 'Issue'
        }
    elif event_type == 'discussion':
        content = event_data['discussion']
        return {
            'number': content['number'],
            'title': content['title'],
            'body': content.get('body', ''),
            'type': 'Discussion'
        }
    else:
        raise ValueError(f"Unsupported event type: {event_type}")




def apply_labels_to_content(repo, content_info, labels, event_type):
    """为内容应用标签"""
    if event_type == 'issue':
        issue = repo.get_issue(number=content_info['number'])
        current_labels = [label.name for label in issue.get_labels()]
        all_labels = list(set(current_labels + labels))
        issue.set_labels(*all_labels)
        print(f"Labels applied to issue #{content_info['number']}: {labels}")
    elif event_type == 'discussion':
        # 获取discussion的node ID
        discussion = repo.get_discussion(number=content_info['number'])
        # 添加标签到discussion
        result = discussion.add_labels(*labels)
        if result:
            applied_labels = [label["name"] for label in result["labels"]["nodes"]]
            print(f"Labels applied to discussion #{content_info['number']}: {labels}")
            print(f"Current labels on discussion: {applied_labels}")
        else:
            print(f"Failed to apply labels to discussion #{content_info['number']}")
    else:
        raise ValueError(f"Unsupported event type: {event_type}")


def main():
    # 初始化 GitHub 客户端
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(GITHUB_REPOSITORY)
    # 加载事件数据
    with open(GITHUB_EVENT_PATH, 'r') as f:
        event_data = json.load(f)

    # 检测事件类型
    try:
        event_type = detect_event_type(event_data)
        print(f"Detected event type: {event_type}")
    except ValueError as e:
        print(f"Error: {e}")
        return

    # 获取内容信息
    try:
        content_info = get_content_info(event_data, event_type)
        print(f"Processing {content_info['type']} #{content_info['number']}: {content_info['title']}")
    except ValueError as e:
        print(f"Error: {e}")
        return

    # 获取现有标签
    try:
        existing_labels = [label.name for label in repo.get_labels()]
        print(f"Existing labels in the repo: {existing_labels}")
    except GithubException as e:
        print(f"Error fetching labels: {e}")
        existing_labels = []

    # 构建prompt
    prompt = PROMPT_TEMPLATE.format(
        content_type=content_info['type'],
        existing_labels=", ".join(existing_labels),
        content_title=content_info['title'],
        content_body=content_info['body']
    )

    # 选择合适的AI agent
    agent = issue_agent if event_type == 'issue' else discussion_agent

    print("Sending prompt to AI...")
    try:
        ai_response = agent.run_sync(prompt)
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

    # 应用标签
    if final_labels:
        try:
            apply_labels_to_content(repo, content_info, final_labels, event_type)
            print("Labels applied successfully.")
        except Exception as e:
            print(f"Failed to apply labels: {e}")
    else:
        print("No valid labels to apply.")


if __name__ == "__main__":
    main()
