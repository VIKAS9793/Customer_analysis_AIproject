from setuptools import setup, find_packages

setup(
    name="customer_analysis_ai",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    python_requires=">=3.10",
    author="Enterprise AI Team",
    author_email="ai-team@enterprise.com",
    description="Enterprise-grade Customer Analysis AI System",
    license="Proprietary",
)
