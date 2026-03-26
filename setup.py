"""
Setup script for Warehouse Environment
Allows installation with: pip install -e .
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="warehouse-openenv",
    version="1.0.0",
    author="OpenEnv Hackathon Team",
    author_email="contact@hackathon.com",
    description="A real-world warehouse robot picking and sorting environment for RL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/warehouse-openenv",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "gymnasium>=0.27.0",
        "pydantic>=1.10.0",
        "PyYAML>=6.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0.0", "black>=22.0.0", "flake8>=4.0.0"],
        "rl": ["torch>=2.0.0", "stable-baselines3>=2.0.0"],
        "web": ["gradio>=4.0.0", "huggingface-hub>=0.20.0"],
        "viz": ["matplotlib>=3.5.0"],
    },
)
