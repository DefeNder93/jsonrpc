angular
    .module('reChat.userService', [])
    .factory('UserService', ['$rootScope','ipCookie', function ($rootScope, ipCookie) {
        var USERNAME_COOKIE = "username";
        return {
            isLoggedIn: function () {
                return angular.isDefined(ipCookie(USERNAME_COOKIE));
            },
            getUsername: function() {
                return ipCookie(USERNAME_COOKIE) ? ipCookie(USERNAME_COOKIE) : null;
            }
        }
    }]);
