from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="finconnectai",
    version="0.1.0",
    author="VIKAS SAHANI",
    author_email="vikassahani17@gmail.com",
    description="FinConnectAI - Financial Connection and Analysis Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VIKAS9793/FinConnectAI",
    packages=find_packages(exclude=["tests*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.9",
    install_requires=[
        "aiohttp>=3.8.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.930",
            "isort>=5.0.0",
        ],
    },
    package_data={
        "finconnectai": ["py.typed"],
    },
)
