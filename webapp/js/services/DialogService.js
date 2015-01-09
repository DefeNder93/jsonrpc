/**
 *
 */
angular
    .module('reChat.dialogService', [])
    .factory('DialogService', ['$rootScope','$modal', function ($rootScope,$modal) {
        //$rootScope.alerts = [];
        return {
            /**
             * Shows alert
             */
            showSuccessAlert: function (header, message) {
                console.log("Show warning alert " + header + " " + message);
                /*$rootScope.alerts.push({
                    type: type,
                    text: message,
                    header: header ? header : "Heads up!"
                });*/
            },

            showModalDialog: function(header, template, size) {
                /*var modalInstance = $modal.open({
                    templateUrl: '/templates/getInvite.html',
                    controller: 'ModalInstanceCtrl',
                    size: size,
                    resolve: {
                        *//*items: function () {
                            return $scope.items;
                        }*//*
                    }
                });*/
            }
        }
    }]);
