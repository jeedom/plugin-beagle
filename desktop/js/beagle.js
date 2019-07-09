
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

 $('#bt_healthbeagle').on('click', function () {
    $('#md_modal').dialog({title: "{{Santé Beagle}}"});
    $('#md_modal').load('index.php?v=d&plugin=beagle&modal=health').dialog('open');
});

 $('.eqLogicAttr[data-l1key=configuration][data-l2key=device]').on('change', function () {
  if($('.eqLogicAttr[data-l1key=id]').value() != ''){
    $('#img_device').attr("src",'plugins/beagle/core/config/devices/'+ $(this).value() + '/'+ $(this).value() + '.png');
  }else{
    $('#img_device').attr("src",'plugins/beagle/plugin_info/beagle_icon.png');
  }
  getModelListParam($(this).value());
});

$('#bt_pairing').on('click', function () {
	$.ajax({// fonction permettant de faire de l'ajax
            type: "POST", // méthode de transmission des données au fichier php
            url: "plugins/beagle/core/ajax/beagle.ajax.php", // url du fichier php
            data: {
                action: "pairing",
				id : $('.eqLogicAttr[data-l1key=id]').value(),
            },
            dataType: 'json',
            error: function (request, status, error) {
            handleAjaxError(request, status, error);
        },
        success: function (data) { // si l'appel a bien fonctionné
        }
    });
});

 $('.changeIncludeState').on('click', function () {
	var mode = $(this).attr('data-mode');
	var state = $(this).attr('data-state');
	changeIncludeState(state, mode);
});

$("#table_cmd").sortable({axis: "y", cursor: "move", items: ".cmd", placeholder: "ui-state-highlight", tolerance: "intersect", forcePlaceholderSize: true});

function addCmdToTable(_cmd) {
    if (!isset(_cmd)) {
        var _cmd = {configuration: {}};
    }
    if (!isset(_cmd.configuration)) {
        _cmd.configuration = {};
    }
    var tr = '<tr class="cmd" data-cmd_id="' + init(_cmd.id) + '">';
    tr += '<td>';
    tr += '<span class="cmdAttr" data-l1key="id" style="display:none;"></span>';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="name" style="width : 140px;" placeholder="{{Nom}}">';
    tr += '</td>';
    tr += '<td>';
    tr += '<span class="type" type="' + init(_cmd.type) + '">' + jeedom.cmd.availableType() + '</span>';
    tr += '<span class="subType" subType="' + init(_cmd.subType) + '"></span>';
    tr += '</td>';
	
  tr += '<td>';
  tr += '<input class="tooltips cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="minValue" placeholder="{{Min}}" title="{{Min}}" style="width:30%;display:inline-block;">';
  tr += '<input class="tooltips cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="maxValue" placeholder="{{Max}}" title="{{Max}}" style="width:30%;display:inline-block;">';
  tr += '<input class="cmdAttr form-control input-sm" data-l1key="unite" placeholder="Unité" title="{{Unité}}" style="width:30%;display:inline-block;margin-left:2px;">';
  tr += '<input class="tooltips cmdAttr form-control input-sm expertModeVisible" data-l1key="configuration" data-l2key="listValue" placeholder="{{Liste de valeur|texte séparé par ;}}" title="{{Liste}}">';
  tr += '<span><label class="checkbox-inline"><input type="checkbox" class="cmdAttr checkbox-inline" data-l1key="isVisible" checked/>{{Afficher}}</label></span> ';
  tr += '<span><label class="checkbox-inline"><input type="checkbox" class="cmdAttr checkbox-inline" data-l1key="isHistorized" checked/>{{Historiser}}</label></span> ';
  tr += '<span><label class="checkbox-inline"><input type="checkbox" class="cmdAttr" data-l1key="display" data-l2key="invertBinary"/>{{Inverser}}</label></span> ';
  tr += '</td>';
    tr += '<td>';
    if (is_numeric(_cmd.id)) {
        tr += '<a class="btn btn-default btn-xs cmdAction" data-action="configure"><i class="fa fa-cogs"></i></a> ';
        tr += '<a class="btn btn-default btn-xs cmdAction" data-action="test"><i class="fa fa-rss"></i> {{Tester}}</a>';
    }
    tr += '<i class="fa fa-minus-circle pull-right cmdAction cursor" data-action="remove"></i>';
    tr += '</td>';
    tr += '</tr>';
    $('#table_cmd tbody').append(tr);
    $('#table_cmd tbody tr:last').setValues(_cmd, '.cmdAttr');
    if (isset(_cmd.type)) {
        $('#table_cmd tbody tr:last .cmdAttr[data-l1key=type]').value(init(_cmd.type));
    }
    jeedom.cmd.changeType($('#table_cmd tbody tr:last'), init(_cmd.subType));
}

$('body').on('beagle::includeState', function (_event,_options) {
	if (_options['mode'] == 'learn') {
		if (_options['state'] == 1) {
			if($('.include').attr('data-state') != 0){
				$.hideAlert();
				$('.include:not(.card)').removeClass('btn-default').addClass('btn-success');
				$('.include').attr('data-state', 0);
				$('.include').empty().append('<i class="fa fa-spinner fa-pulse"></i><br/><span>{{Arrêter Scan}}</span>');
				$('#div_inclusionAlert').showAlert({message: '{{Vous êtes en mode scan. Recliquez sur le bouton scan pour sortir de ce mode (sinon le mode restera actif une minute)}}', level: 'warning'});
			}
		} else {
			if($('.include').attr('data-state') != 1){
				$.hideAlert();
				$('.include:not(.card)').addClass('btn-default').removeClass('btn-success btn-danger');
				$('.include').attr('data-state', 1);
				$('.include').empty().append('<i class="fa fa-bullseye"></i><br/><span>{{Lancer Scan}}</span>');
			}
		}
	}
});

$('body').off('beagle::includeDevice').on('beagle::includeDevice', function (_event,_options) {
  if (modifyWithoutSave) {
    $('#div_inclusionAlert').showAlert({message: '{{Un périphérique vient d\'être inclu. Veuillez réactualiser la page}}', level: 'warning'});
  } else {
    if (_options == '') {
      window.location.reload();
    } else {
      window.location.href = 'index.php?v=d&p=beagle&m=beagle&id=' + _options;
    }
  }
});

$('#bt_autoDetectModule').on('click', function () {
  var dialog_title = '{{Recharge configuration}}';
  var dialog_message = '<form class="form-horizontal onsubmit="return false;"> ';
  dialog_title = '{{Recharger la configuration}}';
  dialog_message += '<label class="control-label" > {{Sélectionner le mode de rechargement de la configuration ?}} </label> ' +
  '<div> <div class="radio"> <label > ' +
  '<input type="radio" name="command" id="command-0" value="0" checked="checked"> {{Sans supprimer les commandes}} </label> ' +
  '</div><div class="radio"> <label > ' +
  '<input type="radio" name="command" id="command-1" value="1"> {{En supprimant et recréant les commandes}}</label> ' +
  '</div> ' +
  '</div><br>' +
  '<label class="lbl lbl-warning" for="name">{{Attention, "En supprimant et recréant" va supprimer les commandes existantes.}}</label> ';
  dialog_message += '</form>';
  bootbox.dialog({
    title: dialog_title,
    message: dialog_message,
    buttons: {
      "{{Annuler}}": {
        className: "btn-danger",
        callback: function () {
        }
      },
      success: {
        label: "{{Démarrer}}",
        className: "btn-success",
        callback: function () {
          if ($("input[name='command']:checked").val() == "1"){
            bootbox.confirm('{{Etes-vous sûr de vouloir récréer toutes les commandes ? Cela va supprimer les commandes existantes}}', function (result) {
              if (result) {
                $.ajax({
                  type: "POST",
                  url: "plugins/beagle/core/ajax/beagle.ajax.php",
                  data: {
                    action: "autoDetectModule",
                    id: $('.eqLogicAttr[data-l1key=id]').value(),
                    createcommand: 1,
                  },
                  dataType: 'json',
                  global: false,
                  error: function (request, status, error) {
                    handleAjaxError(request, status, error);
                  },
                  success: function (data) {
                    if (data.state != 'ok') {
                      $('#div_alert').showAlert({message: data.result, level: 'danger'});
                      return;
                    }
                    $('#div_alert').showAlert({message: '{{Opération réalisée avec succès}}', level: 'success'});
                    $('.li_eqLogic[data-eqLogic_id=' + $('.eqLogicAttr[data-l1key=id]').value() + ']').click();
                  }
                });
              }
            });
          } else {
            $.ajax({
              type: "POST",
              url: "plugins/beagle/core/ajax/beagle.ajax.php",
              data: {
                action: "autoDetectModule",
                id: $('.eqLogicAttr[data-l1key=id]').value(),
                createcommand: 0,
              },
              dataType: 'json',
              global: false,
              error: function (request, status, error) {
                handleAjaxError(request, status, error);
              },
              success: function (data) {
                if (data.state != 'ok') {
                  $('#div_alert').showAlert({message: data.result, level: 'danger'});
                  return;
                }
                $('#div_alert').showAlert({message: '{{Opération réalisée avec succès}}', level: 'success'});
                $('.li_eqLogic[data-eqLogic_id=' + $('.eqLogicAttr[data-l1key=id]').value() + ']').click();
              }
            });
          }
        }
      },
    }
  });

});

$('#bt_askscenes').on('click', function () {
	var dialog_title = '{{Recharge configuration}}';
	var dialog_message = '<form class="form-horizontal onsubmit="return false;"> ';
	dialog_title = '{{Recharger la configuration}}';
	dialog_message += '<label class="control-label" > {{Sélectionner le type de scènes que vous voulez rafraichir !}} </label> ' +
	'<div> <div class="radio"> <label > ' +
	'<input type="radio" name="command" id="command-0" value="0" checked="checked"> {{Les scènes Schneider}} </label> ' +
	'</div><div class="radio"> <label > ' +
	'<input type="radio" name="command" id="command-1" value="1"> {{Les scènes Customers}}</label> ' +
	'</div> ' +
	'</div><br>';
	dialog_message += '</form>';
	bootbox.dialog({
		title: dialog_title,
		message: dialog_message,
		buttons: {
			"{{Annuler}}": {
				className: "btn-danger",
				callback: function () {
				}
			},
			success: {
				label: "{{Démarrer}}",
				className: "btn-success",
				callback: function () {
					if ($("input[name='command']:checked").val() == "0"){
						var name = 'Schneider';
						var type = 'schneiderScenes';
					} else {
						var name = 'Customers';
						var type = 'customerScenes';
					}
					bootbox.confirm('{{Etes-vous sûr de vouloir demander à tous les modules leurs scènes }}' + name + '{{ ? Cela peut durer un petit moment.}}', function (result) {
						if (result) {
							$('#div_alert').showAlert({message: '{{Demande de scènes }}' + name + '{{ en cours ...}}', level: 'warning'});
							$.ajax({
								type: "POST",
								url: "plugins/beagle/core/ajax/beagle.ajax.php",
								data: {
									action: "askscenes",
									type : type
								},
								dataType: 'json',
								global: false,
								error: function (request, status, error) {
									handleAjaxError(request, status, error);
								},
								success: function (data) {
									if (data.state != 'ok') {
										$('#div_alert').showAlert({message: data.result, level: 'danger'});
										return;
									}
									$('#div_alert').showAlert({message: '{{Opération réalisée avec succès}}', level: 'success'});
								}
							});
						}
					});
				}
			}
		}
	});
});

$('#bt_askgroups').on('click', function () {
    bootbox.confirm('{{Etes-vous sûr de vouloir demander à tous les modules leurs groupes ? Cela peut durer un petit moment.}}', function (result) {
        if (result) {
          $('#div_alert').showAlert({message: '{{Demande de groupes en cours ...}}', level: 'warning'});
          $.ajax({
            type: "POST",
            url: "plugins/beagle/core/ajax/beagle.ajax.php",
            data: {
              action: "askgroups"
            },
            dataType: 'json',
            global: false,
            error: function (request, status, error) {
              handleAjaxError(request, status, error);
            },
            success: function (data) {
              if (data.state != 'ok') {
                $('#div_alert').showAlert({message: data.result, level: 'danger'});
                return;
              }
              $('#div_alert').showAlert({message: '{{Opération réalisée avec succès}}', level: 'success'});
            }
          });
        }
    });
});

function getModelListParam(_conf) {
  $.ajax({
    type: "POST",
    url: "plugins/beagle/core/ajax/beagle.ajax.php",
    data: {
      action: "getModelListParam",
      conf: _conf,
    },
    dataType: 'json',
    global: false,
    error: function (request, status, error) {
      handleAjaxError(request, status, error);
    },
    success: function (data) {
      if (data.state != 'ok') {
        $('#div_alert').showAlert({message: data.result, level: 'danger'});
        return;
      }
      if (data.result[0] == true){
        $(".haspairing").show();
      } else {
        $(".haspairing").hide();
      }
	  if (data.result[1] == true){
        $(".hasFirmMac").show();
      } else {
        $(".hasFirmMac").hide();
      }
    }
  });
}

function changeIncludeState(_state,_mode,_type='') {
    $.ajax({// fonction permettant de faire de l'ajax
        type: "POST", // methode de transmission des données au fichier php
        url: "plugins/beagle/core/ajax/beagle.ajax.php", // url du fichier php
        data: {
            action: "changeIncludeState",
            state: _state,
            mode: _mode,
        },
        dataType: 'json',
        error: function (request, status, error) {
            handleAjaxError(request, status, error);
        },
        success: function (data) { // si l'appel a bien fonctionné
        if (data.state != 'ok') {
            $('#div_alert').showAlert({message: data.result, level: 'danger'});
            return;
        }
    }
});
}
