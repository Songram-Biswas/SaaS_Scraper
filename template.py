import os
from pathlib import Path

project_name = "markdown_extractor_api"

list_of_files = [
    f"{project_name}/app/__init__.py",
    f"{project_name}/app/main.py",
    f"{project_name}/app/api/__init__.py",
    f"{project_name}/app/api/deps.py",
    f"{project_name}/app/api/endpoints/__init__.py",
    f"{project_name}/app/api/endpoints/auth.py",
    f"{project_name}/app/api/endpoints/extract.py",
    f"{project_name}/app/api/endpoints/webhooks.py",
    f"{project_name}/app/core/__init__.py",
    f"{project_name}/app/core/config.py",
    f"{project_name}/app/core/database.py",
    f"{project_name}/app/middleware/__init__.py",
    f"{project_name}/app/middleware/rate_limit.py",
    f"{project_name}/app/models/__init__.py",
    f"{project_name}/app/models/user.py",
    f"{project_name}/app/models/api_key.py",
    f"{project_name}/app/schemas/__init__.py",
    f"{project_name}/app/schemas/extraction.py",
    f"{project_name}/app/schemas/api_key.py",
    f"{project_name}/app/services/__init__.py",
    f"{project_name}/app/services/extractor.py",
    f"{project_name}/frontend/index.html",
    f"{project_name}/.env",
    f"{project_name}/Dockerfile",
    f"{project_name}/.gitignore",
    f"{project_name}/requirements.txt",
    f"{project_name}/test_db.py",
    f"{project_name}/README.md"
]

for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)

    if filedir != "":
        os.makedirs(filedir, exist_ok=True)

    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath, "w") as f:
            pass