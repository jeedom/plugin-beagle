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

try {
	require_once __DIR__ . '/../../../../core/php/core.inc.php';
	include_file('core', 'authentification', 'php');

	if (!isConnect('admin')) {
		throw new Exception(__('401 - Accès non autorisé', __FILE__));
	}
	ajax::init();

	if (init('action') == 'changeIncludeState') {
		beagle::changeIncludeState(init('state'), init('mode'));
		ajax::success();
	}

	if (init('action') == 'getModelListParam') {
		ajax::success(beagle::getModelListParam(init('conf')));
	}

	if (init('action') == 'pairing') {
		/** @var beagle */
		$beagle = beagle::byId(init('id'));
		if (!is_object($beagle)) {
			ajax::success(array());
		}
		ajax::success($beagle->binding());
	}

	if (init('action') == 'askscenes') {
		/** @var beagle */
		foreach (beagle::byType('beagle') as $eqLogic) {
			$eqLogic->getscenes(init('type'));
		}
		ajax::success();
	}

	if (init('action') == 'askgroups') {
		/** @var beagle */
		foreach (beagle::byType('beagle') as $eqLogic) {
			$eqLogic->getgroups();
		}
		ajax::success();
	}

	if (init('action') == 'autoDetectModule') {
		/** @var beagle */
		$eqLogic = beagle::byId(init('id'));
		if (!is_object($eqLogic)) {
			throw new Exception(__('Beagle eqLogic non trouvé : ', __FILE__) . init('id'));
		}
		if (init('createcommand') == 1) {
			foreach ($eqLogic->getCmd() as $cmd) {
				$cmd->remove();
			}
		}
		$eqLogic->applyModuleConfiguration();
		ajax::success();
	}



	throw new Exception(__('Aucune méthode correspondante à : ', __FILE__) . init('action'));
	/*     * *********Catch exeption*************** */
} catch (Exception $e) {
	ajax::error(displayException($e), $e->getCode());
}
