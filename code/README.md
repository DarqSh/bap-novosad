# Setup and Usage Instructions

## PC Side (Linux/macOS)

### Python Environment Setup

1. Install Python 3.12.

2. Create a virtual environment using Python 3.12:

```bash
python3.12 -m venv .venv
```

3. Activate the virtual environment:

```bash
source .venv/bin/activate
```

4. Install the required packages:

```bash
pip install -r requirements.txt
```

---

# Pico Side

## Wi-Fi Configuration

Enter the preferred Wi-Fi SSID and password inside:

```text
pico_load/secrets.py
```

---

## Uploading Files to Pico

Upload all files located inside the `pico_load` directory to the Raspberry Pi Pico.

The VSCode *MicroPico* extension is recommended.

Using the extension:
1. Connect to the Pico.
2. Open the Pico filesystem using the **Toggle Mpy FS** button.
3. Upload all files from the `pico_load` directory.

---

## Wiring

Wire all components according to the provided wiring diagram.

---

# Running the Scanning Procedure

1. Power the platform.

2. After booting, `main.py` located on the Pico starts automatically.

3. The Pico creates a Wi-Fi access point using the credentials specified in `secrets.py`.

4. Connect the PC to this Wi-Fi network.

5. Start the scanning procedure:

```bash
python pc.py
```

---

## Configuration

### Scanning Density

The scanning density can be changed by modifying the `SCAN_STEP_DEG` variable near the top of `pc.py`.

The value should be an integer multiple of `0.1`.

---

### Platform Tilt Angle

If a platform with a different tilt angle is used, modify:

```python
PLATFORM_TILT_DEG
```

inside `pc.py`.

---

### Misalignment Corrections

The corrections implemented inside the `lidarTo3D()` function may also need adjustment.

See the *Misalignment Corrections* section of the thesis for details.

---

# Point Cloud Visualisation

## Raw Point Cloud

```bash
python pcd_visualizer.py
```

## Point Cloud with Outlier Removal

```bash
python pcd_visualizer_outlier_removal.py
```

Additional instructions are provided directly in the source code comments.