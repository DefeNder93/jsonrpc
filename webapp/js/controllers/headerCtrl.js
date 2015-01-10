/**
 * A controller to manage header
 * @class
 */
angular.module('reChat.headerCtrl', [])
    .controller('HeaderCtrl', ['$scope','ipCookie','UserService','$timeout','$rootScope',
        function($scope, ipCookie, UserService, $timeout, $rootScope) {

            //console.log("Is logged in - " + UserService.isLoggedIn());
            $scope.isLoggedIn = function() {
                return UserService.isLoggedIn();
            };

            $scope.logout = function() {
                ipCookie.remove("username");
            };

            $scope.getUsername = function() {
                return UserService.getUsername();
            };

            $rootScope.alerts = [];

            /*$rootScope.$watch(function() {
                return $rootScope.alerts;
            }, function (alerts) {
                $timeout(function() {
                    if (alerts.length > 0) {
                        $scope.alerts.splice(alerts.length-1,1);
                    }
                },3000);
            }, true);*/

            $scope.addAlert = function() {
                $rootScope.alerts.push({msg: 'Another alert!'});
            };

            $scope.closeAlert = function(index) {
                $scope.alerts.splice(index, 1);
            };

            /*$scope.radioModel = 'Feed';
            $scope.changeRoute = function(type) {
                switch (type) {
                    case "feed":
                        $location.path("/feed");
                    break;
                    case "chat":
                        $location.path("/chat");
                    break;
                }
            };*/
    }]);


