(function(){
  'use strict';

  angular.module('horizon.dashboard.project.hzrequestspanel')
    .controller('Hzrequestspanelcontroller', Hzrequestspanelcontroller)
    .controller('DialogController', DialogController);

  Hzrequestspanelcontroller.$inject = [
      '$scope',
      '$mdDialog',
      '$mdMedia'
  ];

  DialogController.$inject = [
      '$scope',
      '$mdDialog',
      '$mdSidenav',
      'horizon.app.core.openstack-service-api.nova',
      'horizon.app.core.openstack-service-api.keystone',
      'horizon.app.core.openstack-service-api.cinder',
      'horizon.framework.util.http.service',
      'horizon.framework.widgets.toast.service'
  ];

  function Hzrequestspanelcontroller($scope, $mdDialog, $mdMedia) {
      var ctrl = this;

      ctrl.openRequestForm = openRequestForm;
      ctrl.customFullscreen = $mdMedia('sm');

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
  }

  function DialogController($scope, $mdDialog, $mdSidenav, novaAPI, keystoneAPI, cinderAPI, apiService, toastService) {

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

      $scope.send_request = sendRequest;

      /* VARS FOR VOLUME TYPE DESCRIPTION */
      $scope.name = '';
      $scope.usage = '';
      $scope.hyper = '';
      $scope.max_iops = '';
      $scope.max_throughput = '';

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

      $scope.reset = reset;

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

      function onTenantAbsoluteLimits(dict){
          $scope.tenant_absolute_limits = dict
          var l = [];
          var i = 0;
          var index_standard = 0;
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
              if (name == 'standard'){
                  index_standard = i;
              }
              i++;
          }
          $scope.loading_img_show_storage = false;

          // Hack to put STANDAR in first place
          var temp = $scope.volume_type_list_limits[0];
          $scope.volume_type_list_limits[0] = $scope.volume_type_list_limits[index_standard];
          $scope.volume_type_list_limits[index_standard] = temp;
      }

      function onVolumeTypeList(list){
          var len = list['items'].length;
          var vt = [];
          var default_volume_type_name = 'standard'
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

              if (d['name'] == default_volume_type_name){
                  set_default_volume_type_description(d);
              }
          }
          $scope.volume_types = {'volumes': vt};
      }

      function set_default_volume_type_description(data){
          $scope.volume_descrip = true;
          $scope.name = data['name'];
          $scope.usage = data['usage'];
          $scope.hyper = data['hypervisor'];
          $scope.max_iops = data['max_iops'];
          $scope.max_throughput = data['max_throughput'];
      }

      function showVolume(i){
        $scope.volume_descrip = true;
        $scope.name = $scope.volume_types['volumes'][i]['name'];
        $scope.usage = $scope.volume_types['volumes'][i]['usage'];
        $scope.hyper = $scope.volume_types['volumes'][i]['hypervisor'];
        $scope.max_iops = $scope.volume_types['volumes'][i]['max_iops'];
        $scope.max_throughput = $scope.volume_types['volumes'][i]['max_throughput'];
      }

      /**
       * Create a new Service now ticket calling a REST API
       * 
       */
      function sendRequest(){
        var data = getFormData();
        $scope.request_sent = true;
        var r = apiService.post('/project/hzrequestspanel/hzrequests/requests/', data)
          .error(function () {
            toastService.add('error', gettext('Unable to create the ticket.'));
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
              'username': $scope.username,
              'projectname': $scope.project_name,
              'comments': document.getElementById('textarea-comments').value,
              'instances': $scope.instances,
              'cores': $scope.cores,
              'ram': $scope.ram,
              'volumes': {}
          };
          for (var key in $scope.volume_types['volumes']){
              var vol_type_name = $scope.volume_types['volumes'][key]['name'];
              var dict_volume_data = {
                  'gigabytes': document.getElementById(vol_type_name + '_size').value,
                  'volumes': document.getElementById(vol_type_name + '_number').value
              };
              data['volumes'][vol_type_name] = dict_volume_data;
          }
          return data;
      }

      function showForm(b){
        $scope.form_display = b;
      }

      function reset(){
        $scope.instances = parseInt(document.getElementById('instances_number_actual').value);
        $scope.cores = parseInt(document.getElementById('cores_number_actual').value);
        $scope.ram = parseInt(document.getElementById('ram_number_actual').value);
        for (var i in $scope.volume_type_ids){
            var start_value = parseInt(document.getElementById($scope.volume_type_ids[i] + '_number_actual').value);
            $scope.volume_fields[$scope.volume_type_ids[i] + '_number'] = start_value;

            start_value = parseInt(document.getElementById($scope.volume_type_ids[i] + '_size_actual').value);
            $scope.volume_fields[$scope.volume_type_ids[i] + '_size'] = start_value;
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

          var number = (number_new - number_actual);
          var size = (size_new - size_actual);
          if (isNaN(number)){ number = 0; }
          if (isNaN(size)){ size = 0; }

          var percent_number = parseInt(((100 * number_new) / number_actual) - 100);
          var percent_size = parseInt(((100 * size_new) / size_actual) - 100);
          if (isNaN(percent_number)){ percent_number = 0; }
          if (isNaN(percent_size)){ percent_size = 0; }

          var sign_number = '';
          var sign_size = '';
          if (percent_number > 0) { sign_number = '+'; }
          if (percent_size > 0) { sign_size = '+'; }
          $scope.volume_type_change[vol_id]['number'] = sign_number + number + ' (' + sign_number + '' +  percent_number + '%)';
          $scope.volume_type_change[vol_id]['size'] = sign_size + size + ' (' + sign_size + '' +percent_size + '%)';
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
          if (number_new > 0) { sign = '+'; }
          $scope.compute_change[field] = sign + (number_new - number_actual) + ' (' + sign + '' + percentaje + '%)';
      }

      function openHelp() {
          $mdSidenav('right').toggle();
      }

      function closeHelp(){
          $mdSidenav('right').close()
      }

    }

})();
