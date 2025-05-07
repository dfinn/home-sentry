# home-sentry-watcher setup

### Background

Watcher component for the Home Sentry system.  Fetches images from the camera sources, runs object detection to look for person detections, and sends notifications.

### Installation
1) Install libgeos (https://libgeos.org/), needed by the Shapely package:
    ```
    sudo apt-get install libgeos-dev
    ```

2) Determine which version of the requirements file to use:
    - The Jetson Nano with Jetpack 4.4 / 4.6 uses only Python version 3.6.  The supplied requirements_python3.6_jetson_nano.txt will install dependencies appropriate for this Python version.  PyTorch/Torchvision will not be installed; see the section below for manual installation of those to take advantage of the CUDA backend.

    - Otherwise, use the requirements_python3.8.txt for a Python 3.8 installation.  This will use the CPU backend, or the MPS backend if detected (Apple M1/M2/M3 chips, etc).

3) Install Python dependencies -- recommend setting up a virtual environment and installing needed requirements there. Here's an example:
    ```
    python3.8 -m venv env
    source env/bin/activate
    pip install -r requirements_python3.8.txt
    ```

4) Installing with CUDA Optimized PyTorch For Jetson: 
    - Optional - if you're running Home Sentry on a Jetson (Nano, etc), you'll want to take advantage of the CUDA optimized version of PyTorch and TorchVision for significantly improved inference speeds.  Please refer to:
    https://forums.developer.nvidia.com/t/pytorch-for-jetson/72048

### Launching
To launch the Watcher service, run main.py and specify the directory where your [configuration files](../config-files.MD) are located. The Watcher service will run forever until manually terminated, looking for detections and sending notifications. Example:

    python main.py /home-sentry-config


### Testing a specified input file

In this mode, you can specify a single input file that will be processed and the results will be shown on the console. Run the process_file.py script and specify the config directory and the file name. Example:

```commandline
python process_file.py /home-sentry-config image.jpg
```