(function(){
  'use strict';

  angular.module('horizon.app.hzrequestspanel', ['ngMaterial'])
    .controller('Hzrequestspanelcontroller', function($scope, $mdDialog, $mdMedia) {
      $scope.status = '  ';
      $scope.customFullscreen = $mdMedia('sm');

      $scope.showAdvanced = function(ev) {
        $mdDialog.show({
          controller: DialogController,
          templateUrl: 'view',
          parent: angular.element(document.body),
          targetEvent: ev,
          clickOutsideToClose:true,
          fullscreen: $mdMedia('sm') && $scope.customFullscreen
        })
        .then(function(answer) {
          $scope.status = 'You said the information was "' + answer + '".';
        }, function() {
          $scope.status = 'You cancelled the dialog.';
        });
        $scope.$watch(function() {
          return $mdMedia('sm');
        }, function(sm) {
          $scope.customFullscreen = (sm === true);
        });
      };

    });
    function DialogController($scope, $mdDialog, $http, $sce) {
      $scope.reset = function() {
        var compute_hidden_fields = ['instances', 'cores', 'ram'];
        var volume_hidden_fields = ['standard', 'wig-cp1', 'wig-cp01', 'io1', 'cp1', 'cp2', 'cp02'];
        for (var i in compute_hidden_fields){
            var start_value = document.getElementById(compute_hidden_fields[i] + '_number_actual').value;
            document.getElementById(compute_hidden_fields[i] + '_number').value = start_value;
            changeBackgroundInputs(compute_hidden_fields[i], 'number');
        }
        for (var i in volume_hidden_fields){
            var start_value = document.getElementById(volume_hidden_fields[i] + '_number_actual').value;
            document.getElementById(volume_hidden_fields[i] + '_number').value = start_value;
            changeBackgroundInputs(volume_hidden_fields[i], 'number');

            start_value = document.getElementById(volume_hidden_fields[i] + '_size_actual').value;
            document.getElementById(volume_hidden_fields[i] + '_size').value = start_value;
            changeBackgroundInputs(volume_hidden_fields[i], 'size');
        }
        document.getElementById('textarea-comments').value = '';
      };
      $scope.cancel = function() {
        $mdDialog.cancel();
      };
      $scope.answer = function(answer) {
        $mdDialog.hide(answer);
      };

      $scope.volumes = {'volumes': [
        {
            "name": "Standard",
          "usage": "default",
          "hypervisor": "Linux",
          "max_iops": 100,
          "max_throughput": "80 MB/s"
        },
        {
            "name": "WIG-CP1",
            "usage": "critical power in Wigner",
            "hypervisor": "Linux",
            "max_iops": 100,
            "max_throughput": "80 MB/s"
        },
        {
            "name": "WIG-CPO1",
            "usage": "critical power IO intensive in Wigner",
            "hypervisor": "Linux",
            "max_iops": 500,
            "max_throughput": "120 MB/s"
        },
        {
            "name": "IO1",
            "usage": "  IO intensive",
            "hypervisor": "Linux",
            "max_iops": 500,
            "max_throughput": "120 MB/s"
        },
        {
            "name": "CP1",
            "usage": "critical power",
            "hypervisor": "Linux",
            "max_iops": 100,
            "max_throughput": "80 MB/s"
        },
        {
            "name": "CP2",
            "usage": "critical power",
            "hypervisor": "Windows",
            "max_iops": 100,
            "max_throughput": "80 MB/s"
        },
        {
            "name": "CPIO2",
            "usage": "critical power",
            "hypervisor": "Linux",
            "max_iops": 100,
            "max_throughput": "80 MB/s"
        }
      ]};

      $scope.show_form = showForm;
      $scope.form_display = false;
      $scope.resquest_sent = false;

      $scope.messageNewProject = showMessageNewProject;
      $scope.send_request = sendRequest;
      $scope.name = 'Standard';
      $scope.usage = 'default';
      $scope.hyper = 'Linux';
      $scope.max_iops = '100';
      $scope.max_throughput = '80 MB/s';

      $scope.show_volume = showVolume;
      $scope.volume_descrip = false;

      $scope.create_ticket_msg = "gola";

      function showVolume(i, id){
        $scope.volume_descrip = true;
        $scope.name = $scope.volumes['volumes'][i]['name'];
        $scope.usage = $scope.volumes['volumes'][i]['usage'];
        $scope.hyper = $scope.volumes['volumes'][i]['hypervisor'];
        $scope.max_iops = $scope.volumes['volumes'][i]['max_iops'];
        $scope.max_throughput = $scope.volumes['volumes'][i]['max_throughput'];

      }

      function showMessageNewProject(){
        alert('Do we really want this form?')
      }

      function sendRequest(){
        $mdDialog.cancel();
      }

      function showForm(b){
        $scope.form_display = b;
      }
    }
})();
