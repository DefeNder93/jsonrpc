angular
    .module('reChat.reAffix', [])
    .directive('reAffix', function () {
        return function ($scope, element, attrs) {
            angular.element(element).affix({
                offset: {
                    top: 100
                }
            });
        }
    });