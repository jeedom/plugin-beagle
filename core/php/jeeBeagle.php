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
require_once dirname(__FILE__) . "/../../../../core/php/core.inc.php";

if (!jeedom::apiAccess(init('apikey'), 'beagle')) {
    echo __('Vous n\'etes pas autorisé à effectuer cette action', __FILE__);
    die();
}

if (init('test') != '') {
    echo 'OK';
    die();
}

$result = json_decode(file_get_contents("php://input"), true);
if (!is_array($result)) {
    die();
}

if (isset($result['learn_mode'])) {
    if ($result['learn_mode'] == 1) {
        config::save('include_mode', 1, 'beagle');
        event::add('beagle::includeState', array(
            'mode' => 'learn',
            'state' => 1)
        );
    } else {
        config::save('include_mode', 0, 'beagle');
        event::add('beagle::includeState', array(
            'mode' => 'learn',
            'state' => 0)
        );
    }
}

if (isset($result['devices'])) {
    foreach ($result['devices'] as $key => $datas) {
        if (!isset($datas['uuid'])) {
            continue;
        }
        $beagle = beagle::byLogicalId($datas['uuid'], 'beagle');
        if (!is_object($beagle)) {
            if ($datas['data']['type'] != 'binding') {
                continue;
            }
            log::add('beagle','debug','This is a learn for ' . $key);
            $beagle = beagle::createFromDef($datas);
            if (!is_object($beagle)) {
                log::add('beagle', 'debug', __('Aucun équipement trouvé pour : ', __FILE__) . secureXSS($datas['uuid']));
                continue;
            }
            sleep(1);
            log::add('beagle','debug','Answer learn if needed');
            $beagle->binding();
            event::add('jeedom::alert', array(
                'level' => 'warning',
                'page' => 'beagle',
                'message' => '',
            ));
            event::add('beagle::includeDevice', $beagle->getId());
        }
        if (isset($datas['data']['paired'])){
            $beagle->setConfiguration('paired',$datas['data']['paired']);
            $beagle->save();
            event::add('beagle::includeDevice', $beagle->getId());
        }
        if (isset($datas['data']['firmware'])){
            if ($beagle->getConfiguration('firmware','') != $datas['data']['firmware']){
                $beagle->setConfiguration('firmware',$datas['data']['firmware']);
                $beagle->save();
            }
        }
        if (!$beagle->getIsEnable()) {
            continue;
        }
        foreach ($beagle->getCmd('info') as $cmd) {
            $logicalId = $cmd->getLogicalId();
            if ($logicalId == '') {
                continue;
            }
            $path = explode('::', $logicalId);
            $value = $datas;
            foreach ($path as $key) {
                if (!isset($value[$key])) {
                    continue (2);
                }
                $value = $value[$key];
            }
            if (!is_array($value)) {
                if ($cmd->getSubType() == 'numeric') {
                    $value = round($value, 2);
                }
                $cmd->event($value);
            }
        }
    }
}
