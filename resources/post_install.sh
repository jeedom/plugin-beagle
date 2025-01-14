cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"

if [ -d "$SCRIPT_DIR/python_venv/bin" ]; then
  echo "patch pybluez on debian >= 12"
  sudo $SCRIPT_DIR/python_venv/bin/python3 -m pip install --force-reinstall --upgrade git+https://github.com/pybluez/pybluez.git#egg=pybluez
else
  echo "patch pybluez on debian 11"
  sudo pip3 install git+https://github.com/pybluez/pybluez.git#egg=pybluez
fi

sudo rfkill unblock all >/dev/null 2>&1
sudo hciconfig hci0 up >/dev/null 2>&1
sudo hciconfig hci1 up >/dev/null 2>&1
sudo hciconfig hci2 up >/dev/null 2>&1
