angular.module('horizon.dashboard.project.hzrequestspanel')
  .controller('DialogControllerDeleteProject', DialogControllerDeleteProject);

DialogControllerDeleteProject.$inject = [
    '$scope',
    '$mdDialog',
    '$mdSidenav',
    'horizon.app.core.openstack-service-api.keystone',
    'horizon.framework.util.http.service',
    'horizon.framework.widgets.toast.service'
];

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
              'project_name': $scope.project_name,
              'comment': document.getElementById('textarea-comments').value
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
