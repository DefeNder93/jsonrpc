/**
 * A controller to manage register page
 * @class
 */
angular.module('reChat.registerCtrl', [])
    .controller('RegisterCtrl', ['$scope','JsonRpsService','ipCookie','$location','$timeout','$route',
        function($scope, JsonRpsService, ipCookie, $location, $timeout, $route) {
            var JSONRPC_URL = '/ajax';
            var USERNAME_COOKIE = 'username';
            var SESSION_ID_COOKIE = "session_uid";
            $scope.register = function() {
                console.log("Try register");
                JsonRpsService.sendJSONRPC(JSONRPC_URL, "register",{username: $scope.userName, password: $scope.userPassword }, function(response) {
                    console.log("success register");
                    JsonRpsService.sendJSONRPC(JSONRPC_URL, "login", {username: $scope.userName, password: $scope.userPassword }, function(response) {
                        console.log("Success - " + response.message);
                        ipCookie(USERNAME_COOKIE, $scope.userName.toString(), {path: '/'});
                        ipCookie(SESSION_ID_COOKIE, response.session_id, {path: '/'});
                        $location.path("/feed");
                        $route.reload();
                    }, function(responce) {
                        console.log("error login when register");
                    });
                }, function(response) {
                    $scope.registerError = response.message;
                    angular.element("#register-error").text("Attention please! " + response.message);  // TODO переделать!
                    $timeout(function(){
                        $scope.registerError = "";
                        angular.element("#register-error").text("");
                    },5000);
                    console.log("Error - " + response.message);
                });
            }
        }]);
