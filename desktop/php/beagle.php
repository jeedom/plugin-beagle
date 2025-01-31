<?php
if (!isConnect('admin')) {
  throw new Exception('Error 401 Unauthorized');
}
$plugin = plugin::byId('beagle');
sendVarToJS('eqType', $plugin->getId());
$eqLogics = eqLogic::byType($plugin->getId());

if (config::byKey('include_mode', 'beagle', 0) == 1) {
  echo '<div class="alert jqAlert alert-warning" id="div_inclusionAlert" style="margin : 0px 5px 15px 15px; padding : 7px 35px 7px 15px;">{{Vous êtes en mode scan. Recliquez sur le bouton scan pour sortir de ce mode (sinon le mode restera actif une minute)}}</div>';
} else {
  echo '<div id="div_inclusionAlert"></div>';
}
?>

<div class="row row-overflow">
  <div class="col-xs-12 eqLogicThumbnailDisplay">
    <legend><i class="fas fa-cog"></i> {{Gestion}}</legend>
    <div class="eqLogicThumbnailContainer">
      <?php
      if (config::byKey('include_mode', 'beagle', 0) == 1) {
        echo '<div class="cursor changeIncludeState include card logoPrimary" data-mode="1" data-state="0" >';
        echo '<i class="fa fa-spinner fa-pulse"></i>';
        echo '<br/>';
        echo '<span>{{Arrêter scan}}</span>';
        echo '</div>';
      } else {
        echo '<div class="cursor changeIncludeState include card logoPrimary " data-mode="1" data-state="1">';
        echo '<i class="fa fa-bullseye"></i>';
        echo '<br/>';
        echo '<span>{{Lancer scan}}</span>';
        echo '</div>';
      }
      ?>
      <div class="cursor eqLogicAction logoSecondary" data-action="gotoPluginConf">
        <i class="fas fa-wrench"></i>
        <br />
        <span>{{Configuration}}</span>
      </div>
      <div class="cursor logoSecondary" id="bt_healthbeagle">
        <i class="fas fa-medkit"></i>
        <br />
        <span>{{Santé}}</span>
      </div>
      <div class="cursor logoSecondary" id="bt_askscenes">
        <i class="fas fa-image"></i>
        <br />
        <span>{{Scènes}}</span>
      </div>
      <div class="cursor logoSecondary" id="bt_askgroups">
        <i class="fas fa-list-alt"></i>
        <br />
        <span>{{Groupes}}</span>
      </div>
    </div>
    <?php
    if (count($eqLogics) == 0) {
      echo '<br><div class="text-center" style="font-size:1.2em;font-weight:bold;">{{Aucun équipement trouvé, cliquer sur "Lancer le scan" pour commencer}}</div>';
    } else {
      // Champ de recherche
      echo '<div class="input-group" style="margin:5px;">';
      echo '<input class="form-control roundedLeft" placeholder="{{Rechercher}}" id="in_searchEqlogic">';
      echo '<div class="input-group-btn">';
      echo '<a id="bt_resetSearch" class="btn" style="width:30px"><i class="fas fa-times"></i></a>';
      echo '<a class="btn roundedRight hidden" id="bt_pluginDisplayAsTable" data-coreSupport="1" data-state="0"><i class="fas fa-grip-lines"></i></a>';
      echo '</div>';
      echo '</div>';
    ?>
      <legend><i class="fas fa-table"></i> {{Mes devices Odace SFSP}}</legend>
      <div class="eqLogicThumbnailContainer">
        <?php
        foreach ($eqLogics as $eqLogic) {
          if (!in_array(substr($eqLogic->getConfiguration('device', ''), 0, 5), array('scene', 'group'))) {
            $opacity = ($eqLogic->getIsEnable()) ? '' : 'disableCard';
            echo '<div class="eqLogicDisplayCard cursor ' . $opacity . '" data-eqLogic_id="' . $eqLogic->getId() . '">';
            if (file_exists(__DIR__ . '/../../core/config/devices/' . $eqLogic->getConfiguration('device') . '/' . $eqLogic->getConfiguration('device') . '.png')) {
              echo '<img class="lazy" src="plugins/beagle/core/config/devices/' . $eqLogic->getConfiguration('device') . '/' . $eqLogic->getConfiguration('device') . '.png"/>';
            } else {
              echo '<img src="' . $plugin->getPathImgIcon() . '"/>';
            }
            echo '<br/>';
            echo '<span class="name">' . $eqLogic->getHumanName(true, true) . '</span>';
            echo '</div>';
          }
        }
        ?>
      </div>
      <legend><i class="fas fa-image"></i> {{Mes scènes Odace SFSP}}</legend>
      <div class="eqLogicThumbnailContainer">
        <?php
        foreach ($eqLogics as $eqLogic) {
          if (in_array($eqLogic->getConfiguration('device', ''), array('scene'))) {
            $opacity = ($eqLogic->getIsEnable()) ? '' : 'disableCard';
            echo '<div class="eqLogicDisplayCard cursor ' . $opacity . '" data-eqLogic_id="' . $eqLogic->getId() . '">';
            if (file_exists(__DIR__ . '/../../core/config/devices/' . $eqLogic->getConfiguration('device') . '/' . $eqLogic->getConfiguration('device') . '.png')) {
              echo '<img class="lazy" src="plugins/beagle/core/config/devices/' . $eqLogic->getConfiguration('device') . '/' . $eqLogic->getConfiguration('device') . '.png"/>';
            } else {
              echo '<img src="' . $plugin->getPathImgIcon() . '"/>';
            }
            echo '<br/>';
            echo '<span class="name">' . $eqLogic->getHumanName(true, true) . '</span>';
            echo '</div>';
          }
        }
        ?>
      </div>
      <legend><i class="fas fa-list-alt"></i> {{Mes groupes Odace SFSP}}</legend>
      <div class="eqLogicThumbnailContainer">
        <?php
        foreach ($eqLogics as $eqLogic) {
          if (in_array(substr($eqLogic->getConfiguration('device', ''), 0, 5), array('group'))) {
            $opacity = ($eqLogic->getIsEnable()) ? '' : 'disableCard';
            echo '<div class="eqLogicDisplayCard cursor ' . $opacity . '" data-eqLogic_id="' . $eqLogic->getId() . '">';
            if (file_exists(__DIR__ . '/../../core/config/devices/' . $eqLogic->getConfiguration('device') . '/' . $eqLogic->getConfiguration('device') . '.png')) {
              echo '<img class="lazy" src="plugins/beagle/core/config/devices/' . $eqLogic->getConfiguration('device') . '/' . $eqLogic->getConfiguration('device') . '.png"/>';
            } else {
              echo '<img src="' . $plugin->getPathImgIcon() . '"/>';
            }
            echo '<br/>';
            echo '<span class="name">' . $eqLogic->getHumanName(true, true) . '</span>';
            echo '</div>';
          }
        }
        ?>
      </div>
    <?php
    }
    ?>
  </div>

  <div class="col-xs-12 eqLogic" style="display: none;">
    <div class="input-group pull-right" style="display:inline-flex">
      <span class="input-group-btn">
        <a class="btn btn-danger btn-sm roundedLeft" id="bt_autoDetectModule"><i class="fas fa-search" title="{{Recréer les commandes}}"></i> {{Recréer les commandes}}
        </a><a class="btn btn-warning btn-sm haspairing" id="bt_pairing"><i class="fas fa-barcode" title="{{Trame pairing}}"></i> {{Trame pairing}}
        </a><a class="btn btn-default btn-sm eqLogicAction" data-action="configure"><i class="fas fa-cogs"></i><span class="hidden-xs"> {{Configuration avancée}}</span>
        </a><a class="btn btn-sm btn-success eqLogicAction" data-action="save"><i class="fas fa-check-circle"></i> {{Sauvegarder}}
        </a><a class="btn btn-danger btn-sm eqLogicAction roundedRight" data-action="remove"><i class="fas fa-minus-circle"></i> {{Supprimer}}
        </a>
      </span>
    </div>
    <ul class="nav nav-tabs" role="tablist">
      <li role="presentation"><a href="#" class="eqLogicAction" aria-controls="home" role="tab" data-toggle="tab" data-action="returnToThumbnailDisplay"><i class="fas fa-arrow-circle-left"></i></a></li>
      <li role="presentation" class="active"><a href="#eqlogictab" aria-controls="home" role="tab" data-toggle="tab"><i class="fas fa-tachometer-alt"></i> {{Equipement}}</a></li>
      <li role="presentation"><a href="#commandtab" aria-controls="profile" role="tab" data-toggle="tab"><i class="fas fa-list-alt"></i> {{Commandes}}</a></li>
    </ul>
    <div class="tab-content">
      <div role="tabpanel" class="tab-pane active" id="eqlogictab">
        <form class="form-horizontal">
          <fieldset>
            <div class="col-lg-7">
              <div class="form-group">
                <label class="col-sm-3 control-label">{{Nom du device}}</label>
                <div class="col-sm-7">
                  <input type="text" class="eqLogicAttr form-control" data-l1key="id" style="display : none;" />
                  <input type="text" class="eqLogicAttr form-control" data-l1key="name" placeholder="Nom de l'équipement beagle" />
                </div>
              </div>
              <div class="form-group">
                <label class="col-sm-3 control-label"></label>
                <div class="col-sm-7">
                  <label class="checkbox-inline"><input type="checkbox" class="eqLogicAttr" data-l1key="isEnable" checked />{{Activer}}</label>
                  <label class="checkbox-inline"><input type="checkbox" class="eqLogicAttr" data-l1key="isVisible" checked />{{Visible}}</label>
                </div>
              </div>
              <div class="form-group">
                <label class="col-sm-3 control-label">{{Objet parent}}</label>
                <div class="col-sm-7">
                  <select class="eqLogicAttr form-control" data-l1key="object_id">
                    <option value="">Aucun</option>
                    <?php
                    $options = '';
                    foreach ((jeeObject::buildTree(null, false)) as $object) {
                      $options .= '<option value="' . $object->getId() . '">' . str_repeat('&nbsp;&nbsp;', $object->getConfiguration('parentNumber')) . $object->getName() . '</option>';
                    }
                    echo $options;
                    ?>
                  </select>
                </div>
              </div>
              <div class="form-group">
                <label class="col-sm-3 control-label">{{Catégorie}}</label>
                <div class="col-sm-9">
                  <?php
                  foreach (jeedom::getConfiguration('eqLogic:category') as $key => $value) {
                    echo '<label class="checkbox-inline">';
                    echo '<input type="checkbox" class="eqLogicAttr" data-l1key="category" data-l2key="' . $key . '" />' . $value['name'];
                    echo '</label>';
                  }
                  ?>

                </div>
              </div>
            </div>
            <div class="col-lg-5">
              <div class="form-group">
                <center>
                  <img src="core/img/no_image.gif" data-original=".jpg" id="img_device" class="img-responsive" style="max-height : 250px;" />
                </center>
              </div>
              <div class="form-group">
                <label class="col-sm-3 control-label">{{Modèle}}</label>
                <div class="col-sm-3">
                  <span class="eqLogicAttr label label-info" style="font-size:1em;cursor: default;" data-l1key="configuration" data-l2key="device"></span>
                </div>
                <label class="col-sm-2 control-label">{{Uuid}}</label>
                <div class="col-sm-3">
                  <span class="eqLogicAttr label label-info" style="font-size:1em;cursor: default;" data-l1key="logicalId"></span>
                </div>
              </div>
              <div class="form-group hasFirmMac">
                <label class="col-sm-3 control-label">{{Firmware}}</label>
                <div class="col-sm-3">
                  <span class="eqLogicAttr label label-info" style="font-size:1em;cursor: default;" data-l1key="configuration" data-l2key="firmware"></span>
                </div>
                <label class="col-sm-2 control-label">{{Mac}}</label>
                <div class="col-sm-3">
                  <span class="eqLogicAttr label label-info" style="font-size:1em;cursor: default;" data-l1key="configuration" data-l2key="mac"></span>
                </div>
              </div>
              <div class="form-group haspairing">
                <label class="col-sm-3 control-label">{{Pairé}}</label>
                <div class="col-sm-3">
                  <span class="eqLogicAttr label label-info" style="font-size:1em;cursor: default;" data-l1key="configuration" data-l2key="paired"></span>
                </div>
              </div>
            </div>
          </fieldset>
        </form>
      </div>

      <div role="tabpanel" class="tab-pane" id="commandtab">
        <a class="btn btn-success btn-sm cmdAction pull-right" data-action="add" style="margin-top:5px;"><i class="fa fa-plus-circle"></i> {{Ajouter une commande}}</a><br /><br />
        <table id="table_cmd" class="table table-bordered table-condensed">
          <thead>
            <tr>
              <th style="min-width:200px;width:350px;">{{Nom}}</th>
              <th>{{Type}}</th>
              <th style="min-width:260px;">{{Options}}</th>
              <th>{{Etat}}</th>
              <th style="min-width:80px;width:200px;">{{Actions}}</th>
            </tr>
          </thead>
          <tbody>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<?php include_file('desktop', 'beagle', 'js', 'beagle'); ?>
<?php include_file('core', 'plugin.template', 'js'); ?>