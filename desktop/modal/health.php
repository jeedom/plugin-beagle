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

if (!isConnect('admin')) {
	throw new Exception('401 Unauthorized');
}
$eqLogics = beagle::byType('beagle');
$plugin = plugin::byId('beagle');
?>
<legend><i class="fa fa-table"></i> {{Mes devices Odace SFSP}}</legend>
<table class="table table-condensed tablesorter" id="table_healthbeagle">
	<thead>
		<tr>
			<th>{{Image}}</th>
			<th>{{Odace SFSP}}</th>
			<th>{{ID}}</th>
			<th>{{Modèle}}</th>
			<th>{{Firmware}}</th>
			<th>{{Uuid}}</th>
			<th>{{Mac}}</th>
			<th>{{Dernière communication}}</th>
			<th>{{Date création}}</th>
		</tr>
	</thead>
	<tbody>
		<?php
		foreach ($eqLogics as $eqLogic) {
			if (!in_array(substr($eqLogic->getConfiguration('device', ''), 0, 5), array('scene', 'group'))) {
				$image = $plugin->getPathImgIcon();
				if (file_exists(__DIR__ . '/../../core/config/devices/' . $eqLogic->getConfiguration('device') . '/' . $eqLogic->getConfiguration('device') . '.png')) {
					$image = 'plugins/beagle/core/config/devices/' . $eqLogic->getConfiguration('device') . '/' . $eqLogic->getConfiguration('device') . '.png';
				}
				echo '<tr>';
				echo '<td><img src="' . $image . '" height="55" width="55"/></td>';
				echo '<td><span>' . $eqLogic->getHumanName(true) . '</span></td>';
				echo '<td><span class="label label-info" style="font-size : 1em; cursor : default;">' . $eqLogic->getId() . '</span></td>';
				echo '<td><span class="label label-info" style="font-size : 1em;cursor:default;">' . $eqLogic->getConfiguration('device') . '</span></td>';
				echo '<td><span class="label label-info" style="font-size : 1em;cursor:default;">' . $eqLogic->getConfiguration('firmware') . '</span></td>';
				echo '<td><span class="label label-info" style="font-size : 1em;cursor:default;">' . $eqLogic->getLogicalId() . '</span></td>';
				echo '<td><span class="label label-info" style="font-size : 1em;cursor:default;">' . $eqLogic->getConfiguration('mac') . '</span></td>';
				echo '<td><span class="label label-info" style="font-size : 1em;cursor:default;">' . $eqLogic->getStatus('lastCommunication') . '</span></td>';
				echo '<td><span class="label label-info" style="font-size : 1em;cursor:default;">' . $eqLogic->getConfiguration('createtime') . '</span></td></tr>';
			}
		}
		?>
	</tbody>
</table>

<legend><i class="fas fa-image"></i> {{Mes scènes Odace SFSP}}</legend>
<table class="table table-condensed tablesorter" id="table_healthbeagle">
	<thead>
		<tr>
			<th>{{Image}}</th>
			<th>{{Odace SFSP}}</th>
			<th>{{ID}}</th>
			<th>{{Modèle}}</th>
			<th>{{Uuid}}</th>
			<th>{{Date création}}</th>
		</tr>
	</thead>
	<tbody>
		<?php
		foreach ($eqLogics as $eqLogic) {
			if (in_array($eqLogic->getConfiguration('device', ''), array('scene'))) {
				$image = $plugin->getPathImgIcon();
				if (file_exists(__DIR__ . '/../../core/config/devices/' . $eqLogic->getConfiguration('device') . '/' . $eqLogic->getConfiguration('device') . '.png')) {
					$image = 'plugins/beagle/core/config/devices/' . $eqLogic->getConfiguration('device') . '/' . $eqLogic->getConfiguration('device') . '.png';
				}
				echo '<tr>';
				echo '<td><img src="' . $image . '" height="55" width="55"/></td>';
				echo '<td><span>' . $eqLogic->getHumanName(true) . '</span></td>';
				echo '<td><span class="label label-info" style="font-size : 1em; cursor : default;">' . $eqLogic->getId() . '</span></td>';
				echo '<td><span class="label label-info" style="font-size : 1em;cursor:default;">' . $eqLogic->getConfiguration('device') . '</span></td>';
				echo '<td><span class="label label-info" style="font-size : 1em;cursor:default;">' . $eqLogic->getLogicalId() . '</span></td>';
				echo '<td><span class="label label-info" style="font-size : 1em;cursor:default;">' . $eqLogic->getConfiguration('createtime') . '</span></td></tr>';
			}
		}
		?>
	</tbody>
</table>

<legend><i class="fas fa-list-alt"></i> {{Mes groupes Odace SFSP}}</legend>
<table class="table table-condensed tablesorter" id="table_healthbeagle">
	<thead>
		<tr>
			<th>{{Image}}</th>
			<th>{{Odace SFSP}}</th>
			<th>{{ID}}</th>
			<th>{{Modèle}}</th>
			<th>{{Uuid}}</th>
			<th>{{Date création}}</th>
		</tr>
	</thead>
	<tbody>
		<?php
		foreach ($eqLogics as $eqLogic) {
			if (in_array(substr($eqLogic->getConfiguration('device', ''), 0, 5), array('group'))) {
				$image = $plugin->getPathImgIcon();
				if (file_exists(__DIR__ . '/../../core/config/devices/' . $eqLogic->getConfiguration('device') . '/' . $eqLogic->getConfiguration('device') . '.png')) {
					$image = 'plugins/beagle/core/config/devices/' . $eqLogic->getConfiguration('device') . '/' . $eqLogic->getConfiguration('device') . '.png';
				}
				echo '<tr>';
				echo '<td><img src="' . $image . '" height="55" width="55"/></td>';
				echo '<td><span>' . $eqLogic->getHumanName(true) . '</span></td>';
				echo '<td><span class="label label-info" style="font-size : 1em; cursor : default;">' . $eqLogic->getId() . '</span></td>';
				echo '<td><span class="label label-info" style="font-size : 1em;cursor:default;">' . $eqLogic->getConfiguration('device') . '</span></td>';
				echo '<td><span class="label label-info" style="font-size : 1em;cursor:default;">' . $eqLogic->getLogicalId() . '</span></td>';
				echo '<td><span class="label label-info" style="font-size : 1em;cursor:default;">' . $eqLogic->getConfiguration('createtime') . '</span></td></tr>';
			}
		}
		?>
	</tbody>
</table>