angular.module('reChat',
    [
        'reChat.feedCtrl',
        'reChat.chatCtrl',
        'reChat.headerCtrl',
        'reChat.dialogService',
        'ngRoute',
        'infinite-scroll',
        'ui.bootstrap',
        'reChat.modalCtrl',
        'reChat.modalInstanceCtrl',
        'reChat.registerCtrl',
        'reChat.loginCtrl'
    ]).config(['$routeProvider',
        function($routeProvider) {
            $routeProvider.
                when('/chat', {
                    templateUrl: 'templates/chat.html',
                    controller: 'ChatCtrl'
                }).
                when('/feed', {
                    templateUrl: 'templates/feed.html',
                    controller: 'FeedCtrl'
                }).
                when('/login', {
                    templateUrl: 'templates/login.html',
                    controller: 'LoginCtrl'
                }).
                when('/register', {
                    templateUrl: 'templates/register.html',
                    controller: 'RegisterCtrl'
                }).
                otherwise({
                    redirectTo: '/feed'
                });
        }]);