from setuptools import setup, find_packages

setup(
    name="finconnectai",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    python_requires=">=3.10",
    author="Vikas Sahani",
    author_email="vikassahani17@gmail.com",
    description="Enterprise-grade Financial Analytics and Connectivity AI System",
    license="Proprietary",
)
