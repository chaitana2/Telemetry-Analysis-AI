# Installation Guide for Arch Linux

This guide provides specific installation instructions for Arch Linux and Arch-based distributions (Manjaro, EndeavourOS, Garuda, etc.).

## Prerequisites

### Install Python and Development Tools

```bash
# Update system
sudo pacman -Syu

# Install Python and pip
sudo pacman -S python python-pip

# Install development tools (optional but recommended)
sudo pacman -S base-devel git

# Verify installation
python --version  # Should be 3.8+
pip --version
```

### Install System Dependencies for PyQt6

PyQt6 requires some system libraries:

```bash
# Install Qt6 dependencies
sudo pacman -S qt6-base qt6-tools

# Install additional libraries for GUI
sudo pacman -S libxcb xcb-util-wm xcb-util-image xcb-util-keysyms xcb-util-renderutil
```

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/chaitana2/Telemetry-Analysis-AI.git
cd Telemetry-Analysis-AI
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
# Run tests
pytest tests/

# Launch application
python src/main.py
```

## Arch-Specific Notes

### Using AUR Packages (Optional)

If you prefer using AUR packages for some dependencies:

```bash
# Install yay (AUR helper) if not already installed
sudo pacman -S --needed git base-devel
git clone https://aur.archlinux.org/yay.git
cd yay
makepkg -si
cd ..

# Install Python packages from AUR (optional alternative to pip)
yay -S python-pandas python-numpy python-scikit-learn python-matplotlib
```

**Note**: We recommend using `pip` within a virtual environment for better dependency management.

### Troubleshooting

#### Qt Platform Plugin Error

If you encounter `qt.qpa.plugin: Could not find the Qt platform plugin`:

```bash
# Install additional Qt plugins
sudo pacman -S qt6-wayland qt6-svg

# Set environment variable
export QT_QPA_PLATFORM=xcb
```

#### Missing libxcb Libraries

If you see errors about missing `libxcb`:

```bash
sudo pacman -S libxcb xcb-proto xcb-util-cursor
```

#### Python Version Issues

Arch typically has the latest Python. If you need a specific version:

```bash
# Install pyenv for version management
yay -S pyenv

# Install specific Python version
pyenv install 3.10.0
pyenv local 3.10.0
```

## Running on Wayland

If you're using Wayland instead of X11:

```bash
# Set Qt to use Wayland
export QT_QPA_PLATFORM=wayland

# Or add to your shell rc file (~/.bashrc or ~/.zshrc)
echo 'export QT_QPA_PLATFORM=wayland' >> ~/.bashrc
```

## Performance Optimization

### Enable Hardware Acceleration

```bash
# For Intel graphics
sudo pacman -S mesa vulkan-intel

# For AMD graphics
sudo pacman -S mesa vulkan-radeon

# For NVIDIA graphics
sudo pacman -S nvidia nvidia-utils
```

## Uninstallation

```bash
# Deactivate virtual environment
deactivate

# Remove project directory
cd ..
rm -rf Telemetry-Analysis-AI
```

## Additional Resources

- [Arch Wiki - Python](https://wiki.archlinux.org/title/Python)
- [Arch Wiki - Qt](https://wiki.archlinux.org/title/Qt)
- [Project README](../README.md)
- [Contributing Guide](../CONTRIBUTING.md)

## Support

For Arch-specific issues:
- Check [Arch Linux Forums](https://bbs.archlinux.org/)
- Create an issue: https://github.com/chaitana2/Telemetry-Analysis-AI/issues/new/choose
