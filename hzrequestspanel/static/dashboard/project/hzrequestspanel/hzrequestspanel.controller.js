(function(){
  'use strict';

  angular.module('horizon.dashboard.project.hzrequestspanel')
    .controller('Hzrequestspanelcontroller', Hzrequestspanelcontroller);

  Hzrequestspanelcontroller.$inject = [
      '$scope',
      '$mdDialog',
      '$mdMedia',
      'horizon.app.core.openstack-service-api.keystone'];

  DialogController.$inject = [
      '$scope',
      '$mdDialog',
      '$http',
      'horizon.app.core.openstack-service-api.nova',
      'horizon.app.core.openstack-service-api.keystone',
      'horizon.app.core.openstack-service-api.cinder',
      'horizon.framework.util.http.service',
      'horizon.framework.widgets.toast.service'
  ];

  function Hzrequestspanelcontroller($scope, $mdDialog, $mdMedia, keystoneAPI) {
      var ctrl = this;
      ctrl.project_name = '';

      ctrl.openRequestForm = openRequestForm;
      ctrl.customFullscreen = $mdMedia('sm');

      init();

      function init(){
           keystoneAPI.getCurrentUserSession().success(onGetCurrentUserSession);
      }

      function onGetCurrentUserSession(dict){
          ctrl.project_name = dict['project_name'];
      }

      function openRequestForm(ev){
        $mdDialog.show({
          controller: DialogController,
          templateUrl: STATIC_URL + 'dashboard/project/hzrequestspanel/view.html',
          parent: angular.element(document.body),
          targetEvent: ev,
          clickOutsideToClose:true,
          fullscreen: $mdMedia('sm') && $scope.customFullscreen
        });
        $scope.$watch(function() {
          return $mdMedia('sm');
        }, function(sm) {
          $scope.customFullscreen = (sm === true);
        });
      }
  }

  function DialogController($scope, $mdDialog, $http, novaAPI, keystoneAPI, cinderAPI, apiService, toastService) {

      $scope.nova_limits = {};
      $scope.username = '';
      $scope.project_id = '';
      $scope.project_name = '';
      $scope.volume_types = {'volumes': []};
      $scope.tenant_absolute_limits = {};
      $scope.volume_type_list_limits = [];
      $scope.volume_type_names = [];

      $scope.loading_img_show_storage = false;

      init();

      function init(){
          toastService.clearAll();
          novaAPI.getLimits().success(onGetNovaLimits);
          keystoneAPI.getCurrentUserSession().success(onGetCurrentUserSession);
          cinderAPI.volumeTypeList().success(onVolumeTypeList);
          $scope.loading_img_show_storage = true;
          cinderAPI.tenantAbsoluteLimits().success(onTenantAbsoluteLimits);
      }

      function onGetNovaLimits(dict){
          $scope.nova_limits = dict;
          $scope.nova_limits.totalRAMUsed = ($scope.nova_limits.totalRAMUsed / 1024);
          $scope.nova_limits.maxTotalRAMSize = ($scope.nova_limits.maxTotalRAMSize / 1024);
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
          for (var k in $scope.volume_types['volumes']){
              var id = $scope.volume_types['volumes'][k]['id'];
              var name = $scope.volume_types['volumes'][k]['name'];

              var total_volumes_key_string = 'total_volumes_' + name;
              var total_gigabytes_key_string = 'total_gigabytes_' + name;
              var used_volumes_key_string = 'used_volumes_' + name;
              var used_gigabytes_key_string = 'used_gigabytes_' + name;

              var total_volumes = $scope.tenant_absolute_limits['items'][total_volumes_key_string];
              var total_gigabytes = $scope.tenant_absolute_limits['items'][total_gigabytes_key_string];
              var used_volumes = $scope.tenant_absolute_limits['items'][used_volumes_key_string];
              var used_gigabytes = $scope.tenant_absolute_limits['items'][used_gigabytes_key_string];

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
              $scope.volume_type_names[i] = name;
              $scope.volume_type_list_limits[i] = d; i++;
          }
          $scope.loading_img_show_storage = false;

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
          }
          $scope.volume_types = {'volumes': vt};
      }

      $scope.reset = reset;

      $scope.cancel = function() {
        $mdDialog.cancel();
      };
      $scope.answer = function(answer) {
        $mdDialog.hide(answer);
      };

      $scope.changeNumber = changeFormValue;

      $scope.show_form = showForm;
      $scope.form_display = false;
      $scope.resquest_sent = false;

      $scope.send_request = sendRequest;
      $scope.name = 'Standard';
      $scope.usage = 'default';
      $scope.hyper = 'Linux';
      $scope.max_iops = '100';
      $scope.max_throughput = '80 MB/s';

      $scope.show_volume = showVolume;
      $scope.volume_descrip = false;

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
        var r = apiService.post('/project/hzrequestspanel/hzrequests/requests/', data)
          .error(function () {
            toastService.add('error', gettext('Unable to create the ticket.'));
        }).success(function(response){
            toastService.add('success', gettext('Ticket created ' + response.ticket_number));
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
              'instances': document.getElementById('instances_number').value,
              'cores': document.getElementById('cores_number').value,
              'ram': document.getElementById('ram_number').value,
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
        var compute_hidden_fields = ['instances', 'cores', 'ram'];
        for (var i in compute_hidden_fields){
            var start_value = document.getElementById(compute_hidden_fields[i] + '_number_actual').value;
            document.getElementById(compute_hidden_fields[i] + '_number').value = start_value;
            changeBackgroundInputs(compute_hidden_fields[i], 'number');
        }
        for (var i in $scope.volume_type_names){
            var start_value = document.getElementById($scope.volume_type_names[i] + '_number_actual').value;
            document.getElementById($scope.volume_type_names[i] + '_number').value = start_value;
            changeBackgroundInputs($scope.volume_type_names[i], 'number');

            start_value = document.getElementById($scope.volume_type_names[i] + '_size_actual').value;
            document.getElementById($scope.volume_type_names[i] + '_size').value = start_value;
            changeBackgroundInputs($scope.volume_type_names[i], 'size');
        }
        document.getElementById('textarea-comments').value = '';
      }

      function changeFormValue(prefix_id, field){
        changeBackgroundInputs(prefix_id, field)

        if(field == 'number'){
          var input = document.getElementById(prefix_id + '_' + field);
          var volume_size = document.getElementById(prefix_id + '_size');
          if(volume_size){
            if(parseInt(input.value) > parseInt(volume_size.value)){
              volume_size.value = input.value;
            }
            changeBackgroundInputs(prefix_id, 'size');
          }
        }
      }

      function changeBackgroundInputs(prefix_id, field){
        var input_actual = document.getElementById(prefix_id + '_' + field + '_actual');
        var input = document.getElementById(prefix_id + '_' + field);

        if(parseInt(input.value) > parseInt(input_actual.value)){
          input.style.background = '#2CB04B';
          input.style.color = '#FFFFFF';
        }else if (parseInt(input.value) < parseInt(input_actual.value)) {
          input.style.background = '#7DA6B8'; //#006CCF//darkblue
          input.style.color = '#FFFFFF';
        }else{
          input.style.background = '';
          input.style.color = '#000000';
        }
      }

    }

})();
