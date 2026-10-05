from setuptools import setup, find_packages

setup(
    name="konig-framework",
    version="2.0.0",
    description="KONIG Framework — Enterprise Autonomous Agent Orchestration Engine",
    author="Hianto / KONIG Ecosystem",
    author_email="contact@konig.dev",
    packages=find_packages(),
    py_modules=["cli", "main"],
    install_requires=[
        "pydantic>=2.5.0",
        "pyyaml>=6.0.1",
        "python-dotenv>=1.0.1",
        "rich>=13.7.0",
        "click>=8.1.7",
        "litellm>=1.20.0",
        "httpx>=0.26.0",
    ],
    entry_points={
        "console_scripts": [
            "konig=cli:main",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
