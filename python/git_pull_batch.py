import os
import subprocess
import requests
from dotenv import load_dotenv

# 加载环境变量（可选：用于存储敏感信息）
load_dotenv()


def clone_repository(repo_url, repo_name, clone_dir='.'):
    """
    克隆仓库到指定目录
    :param repo_url: 仓库地址 (ssh/http)
    :param repo_name: 仓库名称
    :param clone_dir: 克隆目标目录
    :return: 是否克隆成功
    """
    # 创建目标目录（如果不存在）
    os.makedirs(clone_dir, exist_ok=True)

    # 构建完整的本地路径
    local_path = os.path.join(clone_dir, repo_name)

    # 检查仓库是否已存在
    if os.path.exists(local_path):
        print(f"Skipping {repo_name}: already exists in {local_path}")
        return False

    # 执行 git clone 命令
    try:
        print(f"Cloning {repo_name} from {repo_url}...")
        result = subprocess.run(
            ['git', 'clone', repo_url, local_path],
            capture_output=True,
            text=True,
            check=True  # 如果失败会抛出异常
        )
        print(f"Success: {repo_name} cloned to {local_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error cloning {repo_name}: {e.stderr.strip()}")
        return False


def main():
    # 从环境变量或配置文件中读取参数（推荐方式）
    gitlab_url = os.getenv('GITLAB_URL', 'https://gitlab.com')
    group_id = os.getenv('GROUP_ID')  # 必须设置
    api_token = os.getenv('GITLAB_TOKEN')  # 必须设置
    clone_dir = os.getenv('CLONE_DIR', './repositories')  # 克隆目标目录

    # 获取仓库列表（与之前代码一致）
    url = f"{gitlab_url}/api/v4/groups/{group_id}/projects"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    params = {
        "per_page": 100  # 根据需要调整分页大小
    }

    all_projects = []
    page = 1
    while True:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Failed to fetch projects: {response.text}")
            break
        projects = response.json()
        all_projects.extend(projects)

        next_page = response.headers.get("X-Next-Page")
        if not next_page:
            break
        page = int(next_page)
        params["page"] = page

    # 遍历仓库并克隆
    for project in all_projects:
        name = project["name"]
        git_url = project["ssh_url_to_repo"]  # 或使用 "http_url_to_repo"

        # 处理 HTTPS URL 的认证（可选）
        if git_url.startswith('https://'):
            # 如果使用 HTTP/S，需提供凭据
            username = os.getenv('GITLAB_USERNAME')
            password = os.getenv('GITLAB_PASSWORD') or os.getenv('GITLAB_TOKEN')
            if not username or not password:
                print(f"Skipping {name}: HTTP authentication required but not provided.")
                continue

            # 构建带凭证的 URL
            git_url = f"https://{username}:{password}@{git_url.split('://')[1]}"

        # 执行克隆
        clone_success = clone_repository(git_url, name, clone_dir)
        if not clone_success:
            print(f"Failed to clone {name}")


if __name__ == "__main__":
    main()