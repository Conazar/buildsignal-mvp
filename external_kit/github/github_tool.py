from __future__ import annotations

from typing import Any

from validation import validate_environment
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_community.utilities.github import GitHubAPIWrapper
from github import Github
config = validate_environment()


github = GitHubAPIWrapper(
    github_app_id=config.app_id,
    github_repository=config.repository,
    github_app_private_key=config.private_key_path
)
toolkit = GitHubToolkit.from_github_api_wrapper(github)

tools = toolkit.get_tools()
for tool in tools:
    print(tool.name)