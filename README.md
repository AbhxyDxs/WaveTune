# WaveTune
## Gesture Controlled Music Player

- **Python**
- **PyQt5**
- **OpenCV**
- **Tensorflow**

## Getting Started

Follow these steps to get WaveTune up and running on your system:

1. **Python and OpenCV :**
    - Install the latest Python Vesrion and Setup OpenCV.  
    - WaveTune uses cv2, providing Python bindings to access the functionality of OpenCV in a Python environment.  
    - After  installing python, download OpenCV's latest release from  [here](https://opencv.org/releases/)
    - Extract it to  a folder (e.g., `C:\opencv`)
    - Add the bin folder in opencv (e.g., `C:\opencv\build\bin`) to the  System Environment Variable Path.

2. **Clone the Repository:**
   ```bash
   git clone https://github.com/AbhxyDxs/WaveTune.git
   cd WaveTune
   ```

3. **Setup python environment:**
   ```bash
   python -m venv venv
   ```
   - On Windows activate  the virtual environment via
   ```bash
   .\venv\Scripts\activate
   ```
   - On  Linux or MacOS activate  the virtual environment via
   ```bash
   source venv/bin/activate
   ```

4. **Install Dependencies:**
   ```bash
   pip install -r req.txt
   ```

5. **Run WaveTune:**
   ```bash
   python main.py
   ```

4. **Start Gesturing:**
   Interact with the music player using predefined gestures.
