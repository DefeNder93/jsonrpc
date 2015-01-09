/**
 * A controller to manage register page
 * @class
 */
angular.module('reChat.registerCtrl', [])
    .controller('RegisterCtrl', ['$scope','JsonRpsService','ipCookie','JsonRpsService','$location',
        function($scope, JsonRpsServce, ipCookie, JsonRpsService, $location) {
            var JSONRPC_URL = '/ajax';
            var USERNAME_COOKIE = 'username';
            /*sendJSONRPC(JSONRPC_URL, "register", {username: $('#register-login').val(), password: $('#register-password').val() }, function (response) { //$('#register-secret').val()
                if (response.status == "error") {
                    $("#register-error").text(response.message);
                }
                else {
                    $("#register-error").text("successfully registered")
                    var isRegistered = 1;
                    sendJSONRPC(JSONRPC_URL, "login", {username: $('#register-login').val(), password: $('#register-password').val() }, function (response) {
                        if (response.status == "error") {
                            $("#register-error").text(response.message);
                        }
                        else {
                            var next = getURLParameter('next');
                            if (!next) {
                                next = "/"
                            }
                            window.location = next
                        }
                    });
                    return false
                }
            });*/

            $scope.register = function() {
                console.log("Try register");
                JsonRpsServce.sendJSONRPC(JSONRPC_URL, "register",{username: $scope.userName, password: $scope.userPassword }, function(response) {
                    console.log("success register");
                    JsonRpsService.sendJSONRPC(JSONRPC_URL, "login", {username: $scope.userName, password: $scope.userPassword }, function(response) {
                        console.log("Success - " + response.message);
                        ipCookie(USERNAME_COOKIE, $scope.userName.toString(), {path: '/'});
                        $location.path("/feed");
                    }, function(responce) {
                        console.log("error login when register");
                    });
                }, function(response) {
                    console.log("error register");
                })
            }
        }]);
