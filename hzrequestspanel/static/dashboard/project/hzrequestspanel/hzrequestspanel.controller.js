(function(){
  'use strict';

  angular.module('horizon.dashboard.project.hzrequestspanel')
    .controller('Hzrequestspanelcontroller', Hzrequestspanelcontroller);

  Hzrequestspanelcontroller.$inject = ['$scope', '$mdDialog', '$mdMedia'];
  DialogController.$inject = ['$mdDialog', '$http'];

  function Hzrequestspanelcontroller($scope, $mdDialog, $mdMedia) {
      var ctrl = this;

      ctrl.openRequestForm = openRequestForm;

      ctrl.customFullscreen = $mdMedia('sm');

      function openRequestForm(ev){
        $mdDialog.show({
          controller: DialogController,
          templateUrl: '/static/dashboard/project/hzrequestspanel/view.html',
          parent: angular.element(document.body),
          targetEvent: ev,
          clickOutsideToClose:true,
          fullscreen: $mdMedia('sm') && ctrl.customFullscreen
        });
        $scope.$watch(function() {
          return $mdMedia('sm');
        }, function(sm) {
          ctrl.customFullscreen = (sm === true);
        });
      }
  }

  function DialogController($mdDialog, $http) {
      var ctrl = this;

      ctrl.reset = function() {
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
      ctrl.cancel = function() {
        $mdDialog.cancel();
      };
      ctrl.answer = function(answer) {
        $mdDialog.hide(answer);
      };

      ctrl.volumes = {'volumes': [
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

      ctrl.show_form = showForm;
      ctrl.form_display = false;
      ctrl.resquest_sent = false;

      ctrl.messageNewProject = showMessageNewProject;
      ctrl.send_request = sendRequest;
      ctrl.name = 'Standard';
      ctrl.usage = 'default';
      ctrl.hyper = 'Linux';
      ctrl.max_iops = '100';
      ctrl.max_throughput = '80 MB/s';

      ctrl.show_volume = showVolume;
      ctrl.volume_descrip = false;

      ctrl.create_ticket_msg = "gola";

      function showVolume(i, id){
        ctrl.volume_descrip = true;
        ctrl.name = ctrl.volumes['volumes'][i]['name'];
        ctrl.usage = ctrl.volumes['volumes'][i]['usage'];
        ctrl.hyper = ctrl.volumes['volumes'][i]['hypervisor'];
        ctrl.max_iops = ctrl.volumes['volumes'][i]['max_iops'];
        ctrl.max_throughput = ctrl.volumes['volumes'][i]['max_throughput'];

      }

      function showMessageNewProject(){
        alert('Do we really want this form?')
      }

      function sendRequest(){
        $mdDialog.cancel();
        showGreenMessage();
      }

      function showForm(b){
        ctrl.form_display = b;
      }
    }


})();
