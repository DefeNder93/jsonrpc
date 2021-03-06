/**
 * A controller to manage login page
 * @class
 */
angular.module('reChat.loginCtrl', [])
    .controller('LoginCtrl', ['$scope','JsonRpsService','ipCookie','$location','$timeout','$route',
        function($scope, JsonRpsService, ipCookie, $location, $timeout, $route) {
            $scope.userName = "";
            $scope.userPassword = "";
            var USERNAME_COOKIE = "username";
            var SESSION_ID_COOKIE = "session_uid";
            $scope.login = function() {
                console.log("L/P: " + $scope.userName + " " + $scope.userPassword);
                JsonRpsService.sendJSONRPC(JSONRPC_URL, "login", {username: $scope.userName, password: $scope.userPassword }, function(response) {
                    console.log("Success login - " + response.message);
                    ipCookie(USERNAME_COOKIE, $scope.userName.toString(), {path: '/'});
                    ipCookie(SESSION_ID_COOKIE, response.result.session_id, {path: '/'});
                    console.log("set sid sid - " + response.result.session_id);
                    $location.path("/feed");
                    $route.reload();
                }, function(response) {
                    $scope.loginError = response.message;
                    angular.element("#login-error").text("Attention please! " + response.message);  // TODO переделать!
                    $timeout(function(){
                        $scope.loginError = "";
                        angular.element("#login-error").text("");
                    },5000);
                    console.log("Error - " + response.message);
                });
            }
        }]);
