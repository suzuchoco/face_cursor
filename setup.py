# setup.py

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="face_cursor",  # パッケージ名
    version="0.1.0",  # バージョン
    author="Sn",  # 作者名
    author_email="s2222051@stu.musashino-u.ac.jp",  # 作者のメールアドレス
    description="This is an app that allows you to move the cursor using your facial movements.",  # 簡単な説明
    long_description=long_description,  # 長い説明（README.mdの内容）
    long_description_content_type="text/markdown",  # READMEの形式
    url="https://github.com/suzuchoco/face_cursor",  # GitHubリポジトリのURL
    packages=find_packages(),  # パッケージの自動検出
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Pythonのバージョン要件
)











