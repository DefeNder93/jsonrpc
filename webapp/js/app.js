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
                otherwise({
                    redirectTo: '/feed'
                });
        }]);
