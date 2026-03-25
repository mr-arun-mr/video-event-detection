# VisionGuard AI – Video Event Detection PoC

This project is a **Proof of Concept (PoC)** for analysing video input and generating events such as:

- Human detection
- Vehicle detection
- Debug frame generation
- Event JSON generation

The project is implemented using **Python**, **OpenCV**, and **YOLOv8** (all open-source libraries).

---

## 1. Prerequisites

You must have the following installed:

- Python 3.9 or higher
- pip3 (Python package manager)

---

## 2. Install Python

### macOS / Linux

Check if Python is already installed:

```bash
python3 --version
```
## 3. Verify Python and pip3

```bash
python3 --version
pip3 --version
```

## Install Dependencies

```bash
pip3 install ultralytics opencv-python
```

## 4. Add a Test Video
Place a test video file (e.g., `sample.mp4`) in the project directory.

## 5. Run the PoC

```bash
python3 src/main.py
```

## 6. What Happens When You Run It
When the program starts:

 - The video will open and frames will be processed
 - Humans and vehicles will be detected
 - Bounding boxes will be shown on the video
 - Debug frames will be saved inside: `/frames`
 - Events will be saved inside: `/events/events.json`

## 7. Stop the Application
To stop the application, simply press `q` while the video window is active.

## 8. Technologies Used
- Python 3.9+
- OpenCV
- YOLOv8 (Ultralytics)
- JSON-based event streaming