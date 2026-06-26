# Phase 2 - Environment Setup and Dependencies

## Objective

The objective of Phase 2 was to prepare the Python environment and install all required libraries for YOLO object detection development.

## Virtual Environment Setup

A dedicated Python virtual environment was created to isolate project dependencies.

Commands used:

```bash
python3 -m venv venv
source venv/bin/activate
```

## Installed Packages

The following packages were installed:

* ultralytics
* opencv-python
* numpy
* pillow
* requests
* python-dotenv

## Package Verification

Verification commands:

```bash
pip show ultralytics
pip show opencv-python
pip show numpy
pip show pillow
pip show requests
pip show python-dotenv
```

All required packages were successfully installed and verified.

## Configuration

The requirements.txt file was updated to document project dependencies.

## Expected Outcome

The environment is now capable of:

* Running YOLOv8 models
* Processing images
* Sending API requests
* Managing configuration variables

## Status

Completed
