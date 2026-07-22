from setuptools import setup, find_packages

setup(
    name="ai-agents",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "langgraph>=0.0.65",
        "httpx>=0.27.0",
        "langchain-core>=0.2.0"
    ],
)
