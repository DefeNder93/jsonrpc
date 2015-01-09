angular
    .module('reChat.reUsersPanel', [])
    .directive('reUsersPanel', function () {
        return function ($scope, element, attrs) {
                //var panel = $('#users');
                var panel = angular.element(element);
                if (panel.length) {
                    var sticker = panel.children('#users-sticker');
                    var showPanel = function() {
                        panel.animate({
                            left: '+=300'
                        }, 200, function() {
                            angular.element(this).addClass('visible');
                        });
                    };
                    var hidePanel = function() {
                        panel.animate({
                            left: '-=300'
                        }, 200, function() {
                            angular.element(this).removeClass('visible');
                        });
                    };
                    sticker.click(function() {
                            if (panel.hasClass('visible')) {
                                hidePanel();
                            }
                            else {
                                showPanel();
                            }
                        });
                }
        }
    });