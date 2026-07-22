from setuptools import setup, find_packages

setup(
    name="ai_evaluation",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "numpy>=1.20.0",
        "scikit-learn>=1.0.0",
    ],
    description="Evaluation framework for the Nutrition Scanner AI agents.",
)
