sudo pip3 install git+https://github.com/pybluez/pybluez.git#egg=pybluez

sudo rfkill unblock all >/dev/null 2>&1
sudo hciconfig hci0 up >/dev/null 2>&1
sudo hciconfig hci1 up >/dev/null 2>&1
sudo hciconfig hci2 up >/dev/null 2>&1
