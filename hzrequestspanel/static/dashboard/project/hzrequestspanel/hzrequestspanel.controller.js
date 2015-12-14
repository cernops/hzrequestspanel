(function(){
  'use strict';

  angular.module('horizon.app')
    .controller('Hzrequestspanelcontroller', Hzrequestspanelcontroller);

  Hzrequestspanelcontroller.$inject = ['horizon.dashboard.project.workflow.launch-instance.modal.service'];

  function Hzrequestspanelcontroller(modalService) {
      var ctrl = this;

      ctrl.openRequestForm = openRequestForm;

      function openRequestForm(context){
          modalService.open(context);
      }
  }

})();
