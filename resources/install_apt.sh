PROGRESS_FILE=/tmp/dependancy_beagle_in_progress
if [ ! -z $1 ]; then
	PROGRESS_FILE=$1
fi
touch ${PROGRESS_FILE}
echo 0 > ${PROGRESS_FILE}
echo "********************************************************"
echo "*             Installation des dépendances             *"
echo "********************************************************"
sudo apt-get update
echo 10 > ${PROGRESS_FILE}
sudo apt-get -y install python3-pip python3-setuptools
echo 20 > ${PROGRESS_FILE}
sudo apt-get install python3-dev
echo 25 > ${PROGRESS_FILE}
sudo pip3 install requests
echo 35 > ${PROGRESS_FILE}
sudo pip3 install pyserial
echo 45 > ${PROGRESS_FILE}
sudo pip3 install pyudev
echo 75 > ${PROGRESS_FILE}
sudo pip3 install wheel
echo 80 > ${PROGRESS_FILE}
sudo pip3 install cryptography
echo 99 > ${PROGRESS_FILE}
sudo hciconfig hci0 up >/dev/null 2>&1
sudo hciconfig hci1 up >/dev/null 2>&1
sudo hciconfig hci2 up >/dev/null 2>&1
echo 100 > ${PROGRESS_FILE}
echo "********************************************************"
echo "*             Installation terminée                    *"
echo "********************************************************"
rm ${PROGRESS_FILE}
