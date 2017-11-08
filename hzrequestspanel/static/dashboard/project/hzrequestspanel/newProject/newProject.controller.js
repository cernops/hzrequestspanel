angular.module('horizon.dashboard.project.hzrequestspanel')
    .controller('DialogControllerNewProject', DialogControllerNewProject);

DialogControllerNewProject.$inject = [
    '$scope',
    '$mdDialog',
    '$mdSidenav',
    'horizon.app.core.openstack-service-api.keystone',
    'horizon.app.core.openstack-service-api.cinder',
    'horizon.framework.util.http.service',
    'horizon.framework.widgets.toast.service'
];

function DialogControllerNewProject($scope, $mdDialog, $mdSidenav, keystoneAPI, cinderAPI, apiService, toastService) {

      $scope.nova_limits = {};
      $scope.username = '';
      $scope.project_id = '';
      $scope.project_name = '';
      $scope.volume_types = {'volumes': []};
      $scope.volume_type_list_limits = [];
      $scope.static_url = STATIC_URL;
      $scope.request_sent = false;

      /* REQUEST FIELDS */
      $scope.exp_or_dept = '';
      $scope.available_experiments = [ 'ALICE', 'ALPHA', 'AMS', 'ATLAS', 'ATLAS-Tokyo', 'ATLAS-Wisconsin', 'CLOUD', 'CMS', 'COMPASS', 'FCC', 'ILC', 'ISOLDE', 'LHCb', 'MA', 'NA48', 'NA61', 'NA62', 'TOTEM',
        'BE', 'CLUB', 'DGU', 'DO', 'EN', 'EP', 'FAP', 'HR', 'HSE', 'IPT', 'IR', 'IT', 'IT-Batch', 'PRJ', 'SIS', 'SMB', 'TE', 'TH'
      ];
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
          cinderAPI.getVolumeTypes().success(onVolumeTypeList);
      }

      function onGetCurrentUserSession(dict){
          $scope.username = dict['username'];
          $scope.project_id = dict['project_id'];
          $scope.project_name = dict['project_name'];
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

          var i = 0;
          for (var k in $scope.volume_types['volumes']){
              var id = $scope.volume_types['volumes'][k]['id'];
              var name = $scope.volume_types['volumes'][k]['name'];

              var d = {'id': id,
                       'name': name
              };

              $scope.volume_type_list_limits[i] = d;
              i++;
          }

          // Hack to put STANDARD in first place
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
              'comment': document.getElementById('textarea-comments').value,
              'accounting_group': $scope.exp_or_dept,
              'project_name': $scope.new_project_name,
              'description': $scope.new_project_description,
              'owner': $scope.new_project_owner,
              'egroup': $scope.new_project_egroup,
              'instances': $scope.instances,
              'cores': $scope.cores,
              'ram': $scope.ram,
              'gigabytes': $scope.volumes_size,
              'volumes': $scope.volumes_number
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
