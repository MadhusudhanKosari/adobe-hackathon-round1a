# Round 1A: Basic PDF Outline Extraction

## Overview

This project implements a **basic PDF outline extractor** leveraging statistical font-size analysis. The tool processes input PDF files and extracts document headings and structure, producing JSON outlines useful for downstream applications.

The solution is packaged as a Docker container that runs a command-line interface, taking PDF files from an input folder and outputting JSON files into an output folder.

---

## Features

- Robust font size-based heading detection using `pdfplumber` and `pypdf`  
- Extracts document metadata (title if available)  
- Outputs clean JSON files with heading levels (H1, H2, H3), text, and page numbers  
- Command-line Docker container for easy cross-platform execution  
- Prepared for hackathon submission with Dockerized build

---

## Requirements

- Docker installed on host machine  
- Test PDF files to analyze

---

## Installation & Build

Clone the repository:
git clone https://github.com/MadhusudhanKosari/adobe-hackathon-round1a.git
cd adobe-hackathon-round1a

Build the Docker image:

docker build --platform linux/amd64 -t pdf-extractor-1a:latest .

---

## Usage Instructions

1. Place PDF files you want to process into the `input/` folder.

2. Run the Docker container to process all PDFs:

- On Windows (PowerShell):

docker run --rm -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output --network none pdf-extractor-1a:latest


- On Windows (CMD):

docker run --rm -v %cd%\input:/app/input -v %cd%\output:/app/output --network none pdf-extractor-1a:latest

3. After execution, JSON output files appear in the `output/` folder.

---

## Sample Output Format

Each JSON file contains:

{
"title": "Document Title",
"outline": [
{ "level": "H1", "text": "Introduction", "page": 1 },
{ "level": "H2", "text": "Background", "page": 2 },
...
]
}

---

## Troubleshooting

- **No PDF files found:** Check `input/` folder contains PDFs and they are not corrupted.
- **Docker command errors on Windows:** Use correct volume mount syntax (`%cd%` or `${PWD}`) and run one line without backslashes.
- **Permission issues:** Run Docker as Administrator if on Windows.
- **Output folder empty:** Ensure Docker has folder access permissions.

---

## Submission Notes

- Confirm `Dockerfile`, `main.py`, `pdf_extractor.py`, `requirements.txt`, and folders (`input/`, `output/`) are in root.
- Make sure the container builds and runs successfully producing `.json` files.
- Include this README in your repository for judges’ clarity.

---

## Contact

For issues or questions, contact:  
K. Madhusudhan – [23211a05e8@bvrit.ac.in]


