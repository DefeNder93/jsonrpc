angular
    .module('reChat.alert', [])
    .directive('reAlert', ['$timeout', 'DialogService', function ($timeout, DialogService) {
        return {
            link: function ($scope, element, attrs) {
                angular.element(element).fadeIn(500, function() {
                    $timeout(function () {
                        angular.element(element).fadeOut(500,function() {
                            DialogService.closeAlert(attrs.reAlert);
                        });
                    }, 4000);
                });
            }
        }
    }]);
