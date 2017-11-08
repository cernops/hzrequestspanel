(function(){
  'use strict';

  angular.module('horizon.dashboard.project.hzrequestspanel')
    .controller('Hzrequestspanelcontroller', Hzrequestspanelcontroller);

  Hzrequestspanelcontroller.$inject = [
      '$scope',
      '$mdDialog',
      '$mdMedia',
      'horizon.app.core.openstack-service-api.keystone'
  ];

  function Hzrequestspanelcontroller($scope, $mdDialog, $mdMedia, keystoneAPI) {
      var ctrl = this;

      ctrl.openRequestFormQuotaChange = openRequestFormQuotaChange;
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

      function openRequestFormQuotaChange(ev){
        $mdDialog.show({
          controller: DialogControllerQuotaChange,
          templateUrl: STATIC_URL + 'dashboard/project/hzrequestspanel/quotaChange/viewQuotaChange.html',
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
          templateUrl: STATIC_URL + 'dashboard/project/hzrequestspanel/newProject/viewNewProject.html',
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
          templateUrl: STATIC_URL + 'dashboard/project/hzrequestspanel/deleteProject/viewDeleteProject.html',
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

})();
