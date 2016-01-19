(function() {
  'use strict';

  var deps = [];
  if (window.location.href.indexOf('dashboard/project/hzrequestspanel/') > -1){
    deps = ['ngMaterial'];
  }

  angular
    .module('horizon.dashboard.project.hzrequestspanel', deps)
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
