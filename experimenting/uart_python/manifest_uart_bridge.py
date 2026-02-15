# manifest_uart_bridge.py

# Include everything the default Pico board needs
include("$(PORT_DIR)/boards/manifest.py")

# Freeze our custom code (the folder this manifest is in)
freeze(".", "main.py")
