/**
 * A controller to manage header
 * @class
 */
angular.module('reChat.headerCtrl', [])
    .controller('HeaderCtrl', ['$scope','ipCookie','UserService','$location','$route',
        function($scope, ipCookie, UserService, $location, $route) {

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


