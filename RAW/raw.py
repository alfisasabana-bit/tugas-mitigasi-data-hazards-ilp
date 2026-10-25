
name: Run RAW Analysis

on:
  workflow_dispatch:
  push:
    paths:
      - "RAW/**"
      - ".github/workflows/run-raw.yml"

jobs:
  raw-analysis:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install matplotlib networkx

      - name: Run RAW Analysis
        run: |
          python RAW/raw.py
