<?php

/* This file is part of Jeedom.
 *
 * Jeedom is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Jeedom is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Jeedom. If not, see <http://www.gnu.org/licenses/>.
 */

/* * ***************************Includes********************************* */
require_once __DIR__  . '/../../../../core/php/core.inc.php';

class beagle extends eqLogic {
    /*     * *************************Attributs****************************** */

    public static function createFromDef($_def) {
        event::add('jeedom::alert', array(
            'level' => 'warning',
            'page' => 'beagle',
            'message' => __('Nouveau module detecté ' . $_def['data']['uuid'], __FILE__),
        ));
        if (!isset($_def['uuid']) || !isset($_def['model'])) {
            log::add('beagle', 'error', 'Information manquante pour ajouter l\'équipement : ' . print_r($_def, true));
            event::add('jeedom::alert', array(
                'level' => 'danger',
                'page' => 'beagle',
                'message' => __('Information manquante pour ajouter l\'équipement. Inclusion impossible', __FILE__),
            ));
            return false;
        }
        $device = self::devicesParameters($_def['model']);
        if (count($device) == 0) {
            log::add('beagle', 'debug', 'Pas de configuration pour ce modèle ' . print_r($_def, true));
            event::add('jeedom::alert', array(
                'level' => 'danger',
                'page' => 'beagle',
                'message' => __('Pas de configuration pour ce modèle', __FILE__),
            ));
            return false;
        }
        $beagle = beagle::byLogicalId($_def['uuid'], 'beagle');
        if (!is_object($beagle)) {
            $beagle = new beagle();
            $beagle->setName('Beagle ' . $_def['model'] . ' ' . $_def['uuid']);
        }
        $beagle->setLogicalId($_def['uuid']);
        $beagle->setEqType_name('beagle');
        $beagle->setIsEnable(1);
        $beagle->setIsVisible(1);
        $beagle->setConfiguration('device', $_def['model']);
        $beagle->setConfiguration('mac', $_def['mac']);
        $beagle->save();
        event::add('jeedom::alert', array(
            'level' => 'warning',
            'page' => 'beagle',
            'message' => __('Module inclu avec succès ' .$_def['model'].' ' . $_def['uuid'], __FILE__),
        ));
        return $beagle;
    }

    public static function generateKey() {
      $randHexStr = implode( array_map( function() { return dechex( mt_rand( 0, 15 ) ); }, array_fill( 0, 24, null ) ) );
      return $randHexStr;
  	}

    public static function dependancy_info() {
        $return = array();
        $return['progress_file'] = jeedom::getTmpFolder('beagle') . '/dependance';
        $return['state'] = 'ok';
        return $return;
    }

    public static function dependancy_install() {
        log::remove(__CLASS__ . '_update');
        return array('script' => dirname(__FILE__) . '/../../resources/install_#stype#.sh ' . jeedom::getTmpFolder('beagle') . '/dependance', 'log' => log::getPathToLog(__CLASS__ . '_update'));
    }

    public static function deamon_info() {
        $return = array();
        $return['log'] = 'beagle';
        $return['state'] = 'nok';
        $pid_file = '/tmp/beagled.pid';
        if (file_exists($pid_file)) {
            if (@posix_getsid(trim(file_get_contents($pid_file)))) {
                $return['state'] = 'ok';
            } else {
                shell_exec('sudo rm -rf ' . $pid_file . ' 2>&1 > /dev/null;rm -rf ' . $pid_file . ' 2>&1 > /dev/null;');
            }
        }
        $return['launchable'] = 'ok';
        return $return;
    }

    public static function deamon_start() {
        self::deamon_stop();
        $deamon_info = self::deamon_info();
        self::checkScenes();
        if (config::byKey('jeedomKey', 'beagle','') == ''){
            config::save('jeedomKey', self::generateKey(), 'beagle');
        }
        if ($deamon_info['launchable'] != 'ok') {
            throw new Exception(__('Veuillez vérifier la configuration', __FILE__));
        }
        $port = jeedom::getBluetoothMapping(config::byKey('port', 'beagle'));
        $beagle_path = realpath(dirname(__FILE__) . '/../../resources/beagled');
        $cmd = 'sudo /usr/bin/python3 ' . $beagle_path . '/beagled.py';
        $cmd .= ' --device ' . $port;
        $cmd .= ' --loglevel ' . log::convertLogLevel(log::getLogLevel('beagle'));
        $cmd .= ' --socketport ' . config::byKey('socketport', 'beagle');
        $cmd .= ' --sockethost 127.0.0.1';
        $cmd .= ' --callback ' . network::getNetworkAccess('internal', 'proto:127.0.0.1:port:comp') . '/plugins/beagle/core/php/jeeBeagle.php';
        $cmd .= ' --apikey ' . jeedom::getApiKey('beagle');
        $cmd .= ' --cycle ' . config::byKey('cycle', 'beagle');
        $cmd .= ' --jeedomkey ' . config::byKey('jeedomKey', 'beagle');
        log::add('beagle', 'debug', 'Lancement démon beagle : ' . $cmd);
        $result = exec($cmd . ' >> ' . log::getPathToLog('beagle') . ' 2>&1 &');
        $i = 0;
        while ($i < 5) {
            $deamon_info = self::deamon_info();
            if ($deamon_info['state'] == 'ok') {
                break;
            }
            sleep(1);
            $i++;
        }
        if ($i >= 5) {
            log::add('beagle', 'error', 'Impossible de lancer le démon beagle, vérifiez le port', 'unableStartDeamon');
            return false;
        }
        message::removeAll('beagle', 'unableStartDeamon');
        config::save('include_mode', 0, 'beagle');
        sleep(2);
    		self::sendIdToDeamon();
        return true;
    }

    public static function deamon_stop() {
        $pid_file = '/tmp/beagled.pid';
        if (file_exists($pid_file)) {
            $pid = intval(trim(file_get_contents($pid_file)));
            system::kill($pid);
        }
        system::kill('beagled.py');
        system::fuserk(config::byKey('socketport', 'beagle'));
        sleep(1);
    }

    public static function sendIdToDeamon() {
        foreach (self::byType('beagle') as $eqLogic) {
            $eqLogic->allowDevice();
            usleep(500);
        }
    }
	
	 public static function checkScenes() {
		$scenein = beagle::byLogicalId('09FFFFFF', 'beagle');
		if (!is_object($scenein)) {
			$scenein = new self();
			$scenein->setLogicalId('09FFFFFF');
			$scenein->setName('Scene In');
			$scenein->setIsEnable(1);
			$scenein->setIsVisible(1);
			$scenein->setConfiguration('device','scene');
			$scenein->setConfiguration('type','schneider');
			$scenein->setEqType_name('beagle');
			$scenein->save();
		}
		$sceneout = beagle::byLogicalId('0AFFFFFF', 'beagle');
		if (!is_object($sceneout)) {
			$sceneout = new self();
			$sceneout->setLogicalId('0AFFFFFF');
			$sceneout->setName('Scene Out');
			$sceneout->setIsEnable(1);
			$sceneout->setIsVisible(1);
			$sceneout->setConfiguration('device','scene');
			$sceneout->setConfiguration('type','schneider');
			$sceneout->setEqType_name('beagle');
			$sceneout->save();
		}
	}

    public static function devicesParameters($_device = '') {
        $return = array();
        foreach (ls(dirname(__FILE__) . '/../config/devices', '*') as $dir) {
            $path = dirname(__FILE__) . '/../config/devices/' . $dir;
            if (!is_dir($path)) {
                continue;
            }
            $files = ls($path, '*.json', false, array('files', 'quiet'));
            foreach ($files as $file) {
                try {
                    $content = file_get_contents($path . '/' . $file);
                    if (is_json($content)) {
                        $return += json_decode($content, true);
                    }
                } catch (Exception $e) {

                }
            }
        }
        if (isset($_device) && $_device != '') {
            if (isset($return[$_device])) {
                return $return[$_device];
            }
            return array();
        }
        return $return;
    }

    public static function changeIncludeState($_state, $_mode) {
        if ($_mode == 1) {
            if ($_state == 1) {
                $allowAll = config::byKey('allowAllinclusion', 'beagle');
                $value = json_encode(array('apikey' => jeedom::getApiKey('beagle'), 'cmd' => 'learnin'));
                self::socket_connection($value);
            } else {
                $value = json_encode(array('apikey' => jeedom::getApiKey('beagle'), 'cmd' => 'learnout'));
                self::socket_connection($value);
            }
        }
    }

    public function getModelListParam($_conf = '') {
  		$json = self::devicesParameters($_conf);
  		$haspairing = false;
  		$hasFirmMac = false;
  		if (isset($json['configuration'])) {
  			if (isset($json['configuration']['haspairing']) && $json['configuration']['haspairing'] == 1) {
  				$haspairing = true;
  			}
  		}
		if (!in_array($_conf,array('scene','groupe'))){
			$hasFirmMac = True;
		}
  		return [$haspairing,$hasFirmMac];
  	}

    public static function socket_connection($_value) {
        if (config::byKey('port', 'beagle', 'none') != 'none') {
            $socket = socket_create(AF_INET, SOCK_STREAM, 0);
            socket_connect($socket, '127.0.0.1', config::byKey('socketport', 'beagle'));
            socket_write($socket, $_value, strlen($_value));
            socket_close($socket);
        }
    }

    public function postSave() {
		if ($this->getConfiguration('applyDevice','') != $this->getConfiguration('device')) {
			$this->applyModuleConfiguration();
		} else {
			$this->allowDevice();
		}
	}

    public function preRemove() {
        $this->disallowDevice();
    }

    public function allowDevice() {
        $value = array('apikey' => jeedom::getApiKey('beagle'), 'cmd' => 'add');
        if ($this->getLogicalId() != '') {
            $value['device'] = array(
                'uuid' => $this->getLogicalId(),
                'model' => $this->getConfiguration('device',''),
                'mac' => $this->getConfiguration('mac',''),
                'type' => $this->getConfiguration('type',''),
            );
            $value = json_encode($value);
            self::socket_connection($value);
        }
    }

    public function disallowDevice() {
        if ($this->getLogicalId() == '') {
            return;
        }
        $value = json_encode(array('apikey' => jeedom::getApiKey('beagle'), 'cmd' => 'remove', 'device' => array('id' => $this->getLogicalId())));
        self::socket_connection($value);
    }

    public function applyModuleConfiguration() {
		    $this->setConfiguration('applyDevice', $this->getConfiguration('device'));
		    $this->save();
        if ($this->getConfiguration('device') == '') {
			       return true;
		    }
		      $device = self::devicesParameters($this->getConfiguration('device'));
		        if (!is_array($device)) {
			           return true;
		             }
		event::add('jeedom::alert', array(
			'level' => 'warning',
			'page' => 'beagle',
			'message' => __('Périphérique reconnu, intégration en cours', __FILE__),
		));
		$this->import($device);
		sleep(2);
		event::add('jeedom::alert', array(
			'level' => 'warning',
			'page' => 'beagle',
			'message' => '',
		));
	}

  public function binding() {
      if ($this->getLogicalId() == '') {
          return;
      }
      if (!in_array($this->getConfiguration('device','switch'),array('shutter','dcl','plug'))) {
          return;
      }
      $value = json_encode(array('apikey' => jeedom::getApiKey('beagle'), 'cmd' => 'bind', 'uuid' => $this->getLogicalId()));
      self::socket_connection($value);
  }
  
  public function getgroups() {
      if ($this->getLogicalId() == '') {
          return;
      }
      if (!in_array($this->getConfiguration('device','switch'),array('shutter','dcl','plug'))) {
          return;
      }
      $value = json_encode(array('apikey' => jeedom::getApiKey('beagle'), 'cmd' => 'send', 'target' => $this->getLogicalId(), 'command' => array("ac" => "groups")));
      self::socket_connection($value);
      sleep(1);
  }
  
  public function getscenes($_type) {
      if ($this->getLogicalId() == '') {
          return;
      }
      if (!in_array($this->getConfiguration('device','switch'),array('shutter','dcl','plug'))) {
          return;
      }
      $value = json_encode(array('apikey' => jeedom::getApiKey('beagle'), 'cmd' => 'send', 'target' => $this->getLogicalId(), 'command' => array("ac" => $_type)));
      self::socket_connection($value);
      sleep(1);
  }
}

class beagleCmd extends cmd {
     public function execute($_options = null) {
   		if ($this->getType() != 'action') {
   			return;
   		}
   		$data = array();
   		$eqLogic = $this->getEqLogic();
   		$values = explode(',', $this->getLogicalId());
   		foreach ($values as $value) {
   			$value = explode(':', $value);
   			if (count($value) == 2) {
   				switch ($this->getSubType()) {
   					case 'slider':
   						$data[trim($value[0])] = trim(str_replace('#slider#', $_options['slider'], $value[1]));
   						break;
   					case 'color':
   						$data[trim($value[0])] = trim(str_replace('#color#', $_options['color'], $value[1]));
   						break;
   					case 'select':
   						$data[trim($value[0])] = trim(str_replace('#select#', $_options['select'], $value[1]));
   						break;
   					default:
   						$data[trim($value[0])] = trim($value[1]);
   				}
   			}
   		}
   		if (count($data) == 0) {
   			return;
   		}
   		$value = json_encode(array('apikey' => jeedom::getApiKey('beagle'), 'cmd' => 'send', 'target' => $eqLogic->getLogicalId(), 'command' => $data));
		$socket = socket_create(AF_INET, SOCK_STREAM, 0);
  		socket_connect($socket, '127.0.0.1', config::byKey('socketport', 'beagle'));
  		socket_write($socket, $value, strlen($value));
  		socket_close($socket);

   	}

    /*     * **********************Getteur Setteur*************************** */
}
