(function(){
  'use strict';

  angular.module('horizon.dashboard.project.hzrequestspanel')
    .controller('Hzrequestspanelcontroller', Hzrequestspanelcontroller);

  Hzrequestspanelcontroller.$inject = ['$scope', '$mdDialog', '$mdMedia'];

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

})();
