(function(){
  'use strict';

  angular.module('horizon.dashboard.project.hzrequestspanel')
    .controller('Hzrequestspanelcontroller', Hzrequestspanelcontroller)
    .controller('DialogController', DialogController)
    .controller('DialogControllerNewProject', DialogControllerNewProject)
    .controller('DialogControllerDeleteProject', DialogControllerDeleteProject);

  Hzrequestspanelcontroller.$inject = [
      '$scope',
      '$mdDialog',
      '$mdMedia',
      'horizon.app.core.openstack-service-api.keystone'
  ];

  DialogController.$inject = [
      '$scope',
      '$mdDialog',
      '$mdSidenav',
      'horizon.app.core.openstack-service-api.nova',
      'horizon.app.core.openstack-service-api.keystone',
      'horizon.app.core.openstack-service-api.cinder',
      'horizon.app.core.openstack-service-api.settings',
      'horizon.framework.util.http.service',
      'horizon.framework.widgets.toast.service'
  ];

  DialogControllerNewProject.$inject = [
      '$scope',
      '$mdDialog',
      '$mdSidenav',
      'horizon.app.core.openstack-service-api.keystone',
      'horizon.framework.util.http.service',
      'horizon.framework.widgets.toast.service'
  ];

  DialogControllerDeleteProject.$inject = [
      '$scope',
      '$mdDialog',
      '$mdSidenav',
      'horizon.app.core.openstack-service-api.keystone',
      'horizon.framework.util.http.service',
      'horizon.framework.widgets.toast.service'
  ];

  function Hzrequestspanelcontroller($scope, $mdDialog, $mdMedia, keystoneAPI) {
      var ctrl = this;

      ctrl.openRequestForm = openRequestForm;
      ctrl.openRequestFormNewProject = openRequestFormNewProject;
      ctrl.openRequestFormDeleteProject = openRequestFormDeleteProject;
      ctrl.customFullscreen = $mdMedia('sm');

      ctrl.is_personal_project = true;

      init();

      function init(){
           keystoneAPI.getCurrentUserSession().success(onGetCurrentUserSession);
      }

      function onGetCurrentUserSession(dict){
          ctrl.project_name = dict['project_name'];
          ctrl.is_personal_project = (ctrl.project_name.indexOf("Personal") > -1);
      }

      function openRequestForm(ev){
        $mdDialog.show({
          controller: DialogController,
          templateUrl: STATIC_URL + 'dashboard/project/hzrequestspanel/view.html',
          parent: angular.element(document.body),
          targetEvent: ev,
          clickOutsideToClose: false,
          fullscreen: $mdMedia('sm') && $scope.customFullscreen
        });
        $scope.$watch(function() {
          return $mdMedia('sm');
        }, function(sm) {
          $scope.customFullscreen = (sm === true);
        });
      }

      function openRequestFormNewProject(ev){
        $mdDialog.show({
          controller: DialogControllerNewProject,
          templateUrl: STATIC_URL + 'dashboard/project/hzrequestspanel/viewNewProject.html',
          parent: angular.element(document.body),
          targetEvent: ev,
          clickOutsideToClose: false,
          fullscreen: $mdMedia('sm') && $scope.customFullscreen
        });
        $scope.$watch(function() {
          return $mdMedia('sm');
        }, function(sm) {
          $scope.customFullscreen = (sm === true);
        });
      }

      function openRequestFormDeleteProject(ev){
        $mdDialog.show({
          controller: DialogControllerDeleteProject,
          templateUrl: STATIC_URL + 'dashboard/project/hzrequestspanel/viewDeleteProject.html',
          parent: angular.element(document.body),
          targetEvent: ev,
          clickOutsideToClose: false,
          fullscreen: $mdMedia('sm') && $scope.customFullscreen
        });
        $scope.$watch(function() {
          return $mdMedia('sm');
        }, function(sm) {
          $scope.customFullscreen = (sm === true);
        });
      }
  }

  function DialogController($scope, $mdDialog, $mdSidenav, novaAPI, keystoneAPI, cinderAPI, settingsAPI, apiService, toastService) {

      $scope.nova_limits = {};
      $scope.username = '';
      $scope.project_id = '';
      $scope.project_name = '';
      $scope.volume_types = {'volumes': []};
      $scope.tenant_absolute_limits = {};
      $scope.volume_type_list_limits = [];
      $scope.volume_type_ids = [];

      $scope.loading_img_show_storage = false;
      $scope.static_url = STATIC_URL;
      $scope.request_sent = false;

      /* COMPUTE MODEL FIELDS */
      $scope.instances = 0;
      $scope.cores = 0;
      $scope.ram = 0;

      /* STORAGE MODEL FIELDS */
      $scope.volume_fields = [];

      $scope.changeNumber = changeInputVolumes;

      $scope.show_form = showForm;
      $scope.form_display = false;
      $scope.resquest_sent = false;

      /* VARS FOR VOLUME TYPE DESCRIPTION */
      $scope.name = '';
      $scope.usage = '';
      $scope.hyper = '';
      $scope.max_iops = '';
      $scope.max_throughput = '';
      $scope.description = '';

      /* VARS TO CHANGE VOLUME TYPE DESCRIPTION */
      $scope.show_volume = showVolume;
      $scope.volume_descrip = false;

      /* VAR TO SAVE THE PERCENTAJE OF QUOTA CHANGE */
      $scope.volume_type_change = [];

      /* TO EXECUTE ON COMPUTE INFO CHANGE*/
      $scope.compute_change = {'instances': '', 'cores': '', 'ram': ''};
      $scope.change_instances = change_instances;
      $scope.change_cores = change_cores;
      $scope.change_ram = change_ram;

      /* FORM BUTTONS */
      $scope.cancel = cancel;
      $scope.reset = reset;
      $scope.send_request = sendRequest;

      /* HELP BUTTON */
      $scope.openHelp = openHelp;
      $scope.closeHelp = closeHelp;

      init();

      function init(){
          toastService.clearAll();
          novaAPI.getLimits().success(onGetNovaLimits);
          keystoneAPI.getCurrentUserSession().success(onGetCurrentUserSession);
          cinderAPI.getVolumeTypes().success(onVolumeTypeList);
          $scope.loading_img_show_storage = true;
          cinderAPI.getAbsoluteLimits().success(onTenantAbsoluteLimits);
      }

      function onGetNovaLimits(dict){
          $scope.nova_limits = dict;
          $scope.instances = dict.maxTotalInstances;
          $scope.cores = dict.maxTotalCores;
          $scope.nova_limits.totalRAMUsed = Math.round($scope.nova_limits.totalRAMUsed / 1024);
          $scope.nova_limits.maxTotalRAMSize = Math.round($scope.nova_limits.maxTotalRAMSize / 1024);
          $scope.ram = $scope.nova_limits.maxTotalRAMSize;
      }

      function onGetCurrentUserSession(dict){
          $scope.username = dict['username'];
          $scope.project_id = dict['project_id'];
          $scope.project_name = dict['project_name'];
      }

      function onGetSetting(dict){
          $scope.volume_type_meta = dict;
          dict['standard']['name'] = 'standard';
          set_default_volume_type_description(dict['standard']);
          for (var key in $scope.volume_types['volumes']){
              var name = $scope.volume_types['volumes'][key]['name'];
              $scope.volume_types['volumes'][key]['usage'] = dict[name]['usage'];
              $scope.volume_types['volumes'][key]['hypervisor'] = dict[name]['hypervisor'];
              $scope.volume_types['volumes'][key]['max_iops'] = dict[name]['iops'];
              $scope.volume_types['volumes'][key]['max_throughput'] = dict[name]['throughput'];
          }
      }

      function onTenantAbsoluteLimits(dict){
          $scope.tenant_absolute_limits = dict
          var i = 0;
          for (var k in $scope.volume_types['volumes']){
              var id = $scope.volume_types['volumes'][k]['id'];
              var name = $scope.volume_types['volumes'][k]['name'];

              var total_volumes_key_string = 'total_volumes_' + name;
              var total_gigabytes_key_string = 'total_gigabytes_' + name;
              var used_volumes_key_string = 'used_volumes_' + name;
              var used_gigabytes_key_string = 'used_gigabytes_' + name;

              var total_volumes = $scope.tenant_absolute_limits[total_volumes_key_string];
              var total_gigabytes = $scope.tenant_absolute_limits[total_gigabytes_key_string];
              var used_volumes = $scope.tenant_absolute_limits[used_volumes_key_string];
              var used_gigabytes = $scope.tenant_absolute_limits[used_gigabytes_key_string];

              var d = {'id': id,
                       'name': name,
                       'volumes': {
                           'used': used_volumes,
                           'total': total_volumes
                       },
                       'gigabytes': {
                           'used': used_gigabytes,
                           'total': total_gigabytes
                       }
              };
              $scope.volume_fields[id + '_number'] = total_volumes;
              $scope.volume_fields[id + '_size'] = total_gigabytes;

              $scope.volume_type_change[id] = {'number': '', 'size': ''};

              $scope.volume_type_ids[i] = id;
              $scope.volume_type_list_limits[i] = d;
              i++;
          }
          $scope.loading_img_show_storage = false;

          // Hack to put STANDAR in first place
          $scope.volume_type_list_limits = sort_volume_type_list_limits();
      }

      function sort_volume_type_list_limits(){
          $scope.volume_type_list_limits.sort( function(a, b){
                  return a['name'] > b['name'] ? 1 : a['name'] < b['name'] ? -1 : 0;
              }
          );
          var l = $scope.volume_type_list_limits.length;
          var custom_sorted_list = [];
          var k = 1;
          for (var i = 0; i < l; i++) {
              if ($scope.volume_type_list_limits[i]['name'] == 'standard') {
                  custom_sorted_list[0] = $scope.volume_type_list_limits[i];
              }else{
                  custom_sorted_list[k] = $scope.volume_type_list_limits[i];
                  k++;
              }
          }
          return custom_sorted_list;
      }

      function onVolumeTypeList(list){
          var len = list['items'].length;
          var vt = [];
          for (var i=0; i < len; i++){
              var d = {'id': list['items'][i]['id'],
                       'name': list['items'][i]['name'],
                       'description': list['items'][i]['description']
              };
              for (var k in list['items'][i]['extra_specs']){
                  d[k] = list['items'][i]['extra_specs'][k];
              }
              vt[d['id']] = d;
              $scope.volume_fields[d['id'] + '_number'] = 0;
              $scope.volume_fields[d['id'] + '_size'] = 0;
          }
          $scope.volume_types = {'volumes': vt};
          settingsAPI.getSetting('VOLUME_TYPE_META').then(onGetSetting);
      }

      function set_default_volume_type_description(data){
          $scope.volume_descrip = true;
          $scope.name = data['name'];
          $scope.usage = data['usage'];
          $scope.hyper = data['hypervisor'];
          $scope.max_iops = data['iops'];
          $scope.max_throughput = data['throughput'];
          $scope.description = data['description'];
      }

      function showVolume(i){
        $scope.volume_descrip = true;
        $scope.name = $scope.volume_types['volumes'][i]['name'];
        $scope.usage = $scope.volume_types['volumes'][i]['usage'];
        $scope.hyper = $scope.volume_types['volumes'][i]['hypervisor'];
        $scope.max_iops = $scope.volume_types['volumes'][i]['max_iops'];
        $scope.max_throughput = $scope.volume_types['volumes'][i]['max_throughput'];
        $scope.description = $scope.volume_types['volumes'][i]['description'];
      }

      /**
       * Create a new Service now ticket calling a REST API
       * 
       */
      function sendRequest(){
        var data = getFormData();
        $scope.request_sent = true;
        var r = apiService.post('/project/hzrequestspanel/hzrequests/requests/', data)
          .error(function (response) {
            var mode = 'error';
            if (response.includes("Ticket created")){ mode = 'warning'; }
            toastService.add(mode, gettext(response));
            //Close request quota change model dialog
            $mdDialog.cancel();
        }).success(function(response){
            toastService.add('success', gettext('Ticket created ' + response.ticket_number));
            //Close request quota change model dialog
            $mdDialog.cancel();
        });
      }

      /**
       * Get the form information about quota change to be sent to API call
       */
      function getFormData() {
          var data = {
              'ticket_type': 'quota_change',
              'username': $scope.username,
              'projectname': $scope.project_name,
              'comments': document.getElementById('textarea-comments').value,
              'instances': $scope.instances,
              'cores': $scope.cores,
              'ram': $scope.ram,
              'volumes': {},
              'current_quota': {
                  'nova_quota': {
                      'instances': document.getElementById('instances_number_actual').value,
                      'cores': document.getElementById('cores_number_actual').value,
                      'ram': document.getElementById('ram_number_actual').value
                  },
                  'cinder_quota': {}
              }
          };
          for (var key in $scope.volume_types['volumes']){
              var vol_type_name = $scope.volume_types['volumes'][key]['name'];
              var dict_volume_data = {
                  'gigabytes': document.getElementById(vol_type_name + '_size').value,
                  'volumes': document.getElementById(vol_type_name + '_number').value
              };
              data['volumes'][vol_type_name] = dict_volume_data;

              var gigabytes_key = 'gigabytes_' + vol_type_name;
              var volumes_key = 'volumes_' + vol_type_name;
              data['current_quota']['cinder_quota'][gigabytes_key] = document.getElementById(key + '_size_actual').value;
              data['current_quota']['cinder_quota'][volumes_key] = document.getElementById(key + '_number_actual').value;
          }
          return data;
      }

      function showForm(b){
        $scope.form_display = b;
      }

      function cancel() {
        $mdDialog.cancel();
      };

      function reset(){
        $scope.instances = parseInt(document.getElementById('instances_number_actual').value);
        $scope.cores = parseInt(document.getElementById('cores_number_actual').value);
        $scope.ram = parseInt(document.getElementById('ram_number_actual').value);
        change_compute('instances', $scope.instances, $scope.instances);
        change_compute('cores', $scope.cores, $scope.cores);
        change_compute('ram', $scope.ram, $scope.ram);
        for (var i in $scope.volume_type_ids){
            var start_value = parseInt(document.getElementById($scope.volume_type_ids[i] + '_number_actual').value);
            $scope.volume_fields[$scope.volume_type_ids[i] + '_number'] = start_value;

            start_value = parseInt(document.getElementById($scope.volume_type_ids[i] + '_size_actual').value);
            $scope.volume_fields[$scope.volume_type_ids[i] + '_size'] = start_value;

            change_volume_type_percentaje($scope.volume_type_ids[i]);
        }
        document.getElementById('textarea-comments').value = '';
      }

      function changeInputVolumes(prefix_id, field){
        if ($scope.volume_fields[prefix_id + '_number'] == 0) {
            $scope.volume_fields[prefix_id + '_size'] = 0;
        }else if ($scope.volume_fields[prefix_id + '_number'] > 0 && $scope.volume_fields[prefix_id + '_number'] > $scope.volume_fields[prefix_id + '_size']) {
            $scope.volume_fields[prefix_id + '_size'] = $scope.volume_fields[prefix_id + '_number'];
        }

        change_volume_type_percentaje(prefix_id);
      }

      function change_volume_type_percentaje(vol_id){
          var number_new = $scope.volume_fields[vol_id + '_number'];
          var size_new = $scope.volume_fields[vol_id + '_size'];
          var number_actual =  parseInt(document.getElementById(vol_id + '_number_actual').value);
          var size_actual = parseInt(document.getElementById(vol_id + '_size_actual').value);

          var number = parseInt(number_new - number_actual);
          var size = parseInt(size_new - size_actual);
          if (isNaN(number)){ number = 0; }
          if (isNaN(size)){ size = 0; }

          var percent_number = 0;
          var percent_size = 0;
          if ( number_new != number_actual && number_actual > 0) {
              percent_number = parseInt(((100 * number_new) / number_actual) - 100);
          }
          if (size_new != size_actual && size_actual > 0) {
              percent_size = parseInt(((100 * size_new) / size_actual) - 100);
          }
          if (number_actual == 0){ percent_number = 100; }
          if (size_actual == 0){ percent_size = 100; }
          if (number_new == 0){ percent_number = 0; }
          if (size_new == 0){ percent_size = 0; }

          var sign_number = '';
          var sign_size = '';
          if (percent_number > 0) { sign_number = '+'; }
          if (percent_size > 0) { sign_size = '+'; }

          if (number == 0 && percent_number == 0) {
               $scope.volume_type_change[vol_id]['number'] = '';
          }else{
               $scope.volume_type_change[vol_id]['number'] = sign_number + number + ' (' + sign_number + '' +  percent_number + '%)';
          }
          if (size == 0 && percent_size == 0) {
               $scope.volume_type_change[vol_id]['size'] = '';
          }else{
               $scope.volume_type_change[vol_id]['size'] = sign_size + size + ' (' + sign_size + '' +percent_size + '%)';
          }
      }

      function change_instances(){
          change_compute('instances', $scope.instances, $scope.nova_limits.maxTotalInstances);
      }

      function change_cores(){
          change_compute('cores', $scope.cores, $scope.nova_limits.maxTotalCores);
      }

      function change_ram(){
          change_compute('ram', $scope.ram, $scope.nova_limits.maxTotalRAMSize);
      }

      function change_compute(field, number_new, number_actual){
          var percentaje = parseInt(((100 * number_new) / number_actual) - 100);
          var number = (number_new - number_actual);
          if (isNaN(number)){ number = 0; }
          if (isNaN(percentaje)){ percentaje = 0; }
          var sign = '';
          if (number > 0) { sign = '+'; }

          // Only display info if it is != 0
          if (number == 0 && percentaje == 0) {
              $scope.compute_change[field] = '';
          }else{
              $scope.compute_change[field] = sign + number + ' (' + sign + '' + percentaje + '%)';
          }
      }

      function openHelp() {
          $mdSidenav('right').toggle();
      }

      function closeHelp(){
          $mdSidenav('right').close()
      }

    }

  function DialogControllerNewProject($scope, $mdDialog, $mdSidenav, keystoneAPI, apiService, toastService) {

      $scope.nova_limits = {};
      $scope.username = '';
      $scope.project_id = '';
      $scope.project_name = '';

      $scope.loading_img_show_storage = false;
      $scope.static_url = STATIC_URL;
      $scope.request_sent = false;

      /* REQUEST FIELDS */
      $scope.exp_or_dept = '';
      $scope.new_project_name = '';
      $scope.new_project_description = '';
      $scope.new_project_owner = '';
      $scope.new_project_egroup = '';

      $scope.instances = 25;
      $scope.cores = 25;
      $scope.ram = 50;

      $scope.volumes_size = 500;
      $scope.volumes_number = 5;

      $scope.show_form = showForm;
      $scope.form_display = false;
      $scope.resquest_sent = false;

      /* FORM BUTTONS */
      $scope.cancel = cancel;
      $scope.send_request = sendRequest;

      /* HELP BUTTON */
      $scope.openHelp = openHelp;
      $scope.closeHelp = closeHelp;

      init();

      function init(){
          toastService.clearAll();
          keystoneAPI.getCurrentUserSession().success(onGetCurrentUserSession);
      }

      function onGetCurrentUserSession(dict){
          $scope.username = dict['username'];
          $scope.project_id = dict['project_id'];
          $scope.project_name = dict['project_name'];
      }

      /**
       * Create a new Service now ticket calling a REST API
       *
       */
      function sendRequest(){
        var data = getFormData();
        $scope.request_sent = true;
        var r = apiService.post('/project/hzrequestspanel/hzrequests/requests/', data)
          .error(function (response) {
            var mode = 'error';
            if (response.includes("Ticket created")){ mode = 'warning'; }
            toastService.add(mode, gettext(response));
            //Close request quota change model dialog
            $mdDialog.cancel();
        }).success(function(response){
            toastService.add('success', gettext('Ticket created ' + response.ticket_number));
            //Close request quota change model dialog
            $mdDialog.cancel();
        });
      }

      /**
       * Get the form information about quota change to be sent to API call
       */
      function getFormData() {
          var data = {
              'ticket_type': 'new_project',
              'username': $scope.username,
              'comments': document.getElementById('textarea-comments').value,
              'exp_or_dept': $scope.exp_or_dept,
              'new_project_name': $scope.new_project_name,
              'new_project_description': $scope.new_project_description,
              'new_project_owner': $scope.new_project_owner,
              'new_project_egroup': $scope.new_project_egroup,
              'instances': $scope.instances,
              'cores': $scope.cores,
              'ram': $scope.ram,
              'volumes_size': $scope.volumes_size,
              'volumes_number': $scope.volumes_number
          };

          return data;
      }

      function showForm(b){
        $scope.form_display = b;
      }

      function cancel() {
        $mdDialog.cancel();
      }

      function openHelp() {
          $mdSidenav('right').toggle();
      }

      function closeHelp(){
          $mdSidenav('right').close()
      }

    }

  function DialogControllerDeleteProject($scope, $mdDialog, $mdSidenav, keystoneAPI, apiService, toastService) {

      $scope.nova_limits = {};
      $scope.username = '';
      $scope.project_id = '';
      $scope.project_name = '';
      $scope.user_entered_project_name = '';

      $scope.loading_img_show_storage = false;
      $scope.static_url = STATIC_URL;
      $scope.request_sent = false;

      $scope.show_form = showForm;
      $scope.form_display = false;
      $scope.resquest_sent = false;

      /* FORM BUTTONS */
      $scope.cancel = cancel;
      $scope.send_request = sendRequest;

      /* HELP BUTTON */
      $scope.openHelp = openHelp;
      $scope.closeHelp = closeHelp;

      init();

      function init(){
          toastService.clearAll();
          keystoneAPI.getCurrentUserSession().success(onGetCurrentUserSession);
      }

      function onGetCurrentUserSession(dict){
          $scope.username = dict['username'];
          $scope.project_id = dict['project_id'];
          $scope.project_name = dict['project_name'];
      }

      /**
       * Create a new Service now ticket calling a REST API
       *
       */
      function sendRequest(){
        var data = getFormData();
        $scope.request_sent = true;
        var r = apiService.post('/project/hzrequestspanel/hzrequests/requests/', data)
          .error(function (response) {
            var mode = 'error';
            if (response.includes("Ticket created")){ mode = 'warning'; }
            toastService.add(mode, gettext(response));
            //Close request quota change model dialog
            $mdDialog.cancel();
        }).success(function(response){
            toastService.add('success', gettext('Ticket created ' + response.ticket_number));
            //Close request quota change model dialog
            $mdDialog.cancel();
        });
      }

      /**
       * Get the form information about quota change to be sent to API call
       */
      function getFormData() {
          var data = {
              'ticket_type': 'delete_project',
              'username': $scope.username,
              'projectname': $scope.project_name,
              'comments': document.getElementById('textarea-comments').value
          };

          return data;
      }

      function showForm(b){
        $scope.form_display = b;
      }

      function cancel() {
        $mdDialog.cancel();
      }

      function openHelp() {
          $mdSidenav('right').toggle();
      }

      function closeHelp(){
          $mdSidenav('right').close()
      }

}

})();
