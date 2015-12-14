(function() {
  'use strict';

  angular
    .module('horizon.dashboard.project.hzrequestspanel', ['ngMaterial'])
    .config(config);

  config.$inject = [
    '$provide',
    '$windowProvider'
  ];

  function config($provide, $windowProvider) {
    var path = $windowProvider.$get().STATIC_URL + 'dashboard/project/hzrequestspanel/';
    $provide.constant('horizon.dashboard.project.hzrequestspanel.basePath', path);
  }

})();
