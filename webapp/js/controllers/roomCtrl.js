/**
 * A controller to manage chat
 * @class
 */
angular.module('reChat.roomCtrl', [])
    .controller('RoomCtrl', ['$scope', 'UserService', 'JsonRpsService',
        function ($scope, UserService, JsonRpsService) {

            $scope.isShowUserPanel = true;

            $scope.isCreateRoomCollapsed = true;
            $scope.isInviteCollapsed = true;
            $scope.addedUserName = "";
            //$scope.message = "Write message";

            $scope.isLoggedIn = function () {
                return UserService.isLoggedIn();
            };

            $scope.typeOfComment = function (type) {
                if (type === 'my') {
                    return 'right';
                }
                return 'left';
            };

            $scope.toggleUserPanel = function () {
                $scope.isShowUserPanel = !$scope.isShowUserPanel;
            };

            $scope.sendMessage = function () {
                if (!UserService.isLoggedIn()) {
                    console.log("Please logged in to write messages!");
                    return;
                }

                /*JsonRpsService.sendJSONRPC(JSONRPC_URL, "sendMessage", {text: $scope.message}, function (response) {
                 if ($scope.message.length > 0) {
                 $scope.comments.unshift({
                 author: UserService.getUsername(),
                 text: $scope.message
                 });
                 }
                 }, function (response) {
                 // TODO alert и сообщение сервера в нем
                 });*/

                if ($scope.message.length > 0) {  // TODO выпилить
                    $scope.comments.unshift({
                        author: UserService.getUsername(),
                        text: $scope.message,
                        type: "my",
                        time: moment(new Date()).format('HH:mm')
                    });
                }
                $scope.message = "";
            };

            $scope.toggleUserCollapse = function () {
                $scope.isInviteCollapsed = !$scope.isInviteCollapsed;
                $scope.isCreateRoomCollapsed = true;
            };

            $scope.addUser = function () {
                if ($scope.addedUserName.length > 0) {
                     JsonRpsService.sendJSONRPC(JSONRPC_URL, "addUser", {name: $scope.addedUserName}, function (response) {

                        }, function (response) {
                            // TODO alert и сообщение сервера в нем
                        });

                    $scope.users.push({ // TODO выпилить
                        name: $scope.addedUserName
                    });
                    $scope.addedUserName = "";
                    $scope.isInviteCollapsed = true;
                }
                $scope.invitedName = "";
            };

            $scope.toggleRoomCollapse = function () {
                $scope.isCreateRoomCollapsed = !$scope.isCreateRoomCollapsed;
                $scope.isInviteCollapsed = true;
            };

            $scope.createRoom = function () {
                if ($scope.roomName.length > 0) {
                    /*JsonRpsService.sendJSONRPC(JSONRPC_URL, "createRoom", {name: $scope.roomName}, function (response) {
                     $scope.rooms.push(
                     {name: $scope.roomName}
                     );
                     }, function (response) {
                     // TODO alert и сообщение сервера в нем
                     });*/
                    $scope.isCreateRoomCollapsed = true;
                }
                $scope.roomName = "";
            };

            $scope.deleteUser = function (index, userName) {
                /*JsonRpsService.sendJSONRPC(JSONRPC_URL, "deleteUser", {name: userName}, function (response) {
                 $scope.users.splice(index, 1);
                 }, function (response) {
                 // TODO alert и сообщение сервера в нем
                 });*/
                $scope.users.splice(index, 1);
            };

            $scope.inviteUser = function (index, userName) {
                console.log("Invite user " + userName);
            };

            $scope.openUserDialog = function (index, userName) {
                console.log("Open dialog " + userName);
            };

            $scope.isSettingsCollapsed = true;

            $scope.rooms = [
                {name: "room 10"},
                {name: "925"},
                {name: "a lot of fun here"},
                {name: "Комната отдыха"}
            ];

            $scope.comments = [ // TODO get from server
                {
                    author: "Иван1",
                    text: "Текст комментария1",
                    type: "my",
                    time: "12:06"
                },
                {
                    author: "Иван2",
                    text: "Текст комментария2",
                    time: "12:05"
                },
                {
                    author: "Иван3",
                    text: "Текст комментария3",
                    time: "12:05"
                },
                {
                    author: "Иван4",
                    text: "Текст комментария4",
                    time: "12:04"
                },
                {
                    author: "Иван5",
                    text: "Текст комментария5"
                },
                {
                    author: "Иван6",
                    text: "Текст комментария6",
                    type: "my"
                },
                {
                    author: "Иван7",
                    text: "Текст комментария7"
                },
                {
                    author: "Иван8",
                    text: "Текст комментария8"
                },
                {
                    author: "Иван9",
                    text: "Текст комментария9"
                },
                {
                    author: "Иван10",
                    text: "Текст комментария10"
                },
                {
                    author: "Иван11",
                    text: "Текст комментария11"
                },
                {
                    author: "Иван12",
                    text: "Текст комментария12"
                },
                {
                    author: "Иван13",
                    text: "Текст комментария13"
                },
                {
                    author: "Иван14",
                    text: "Текст комментария14"
                },
                {
                    author: "Иван15",
                    text: "Текст комментария15"
                },
                {
                    author: "Иван16",
                    text: "Текст комментария16"
                },
                {
                    author: "Иван17",
                    text: "Текст комментария17"
                },
                {
                    author: "Иван18",
                    text: "Текст комментария18"
                },
                {
                    author: "Иван19",
                    text: "Текст комментария19"
                },
                {
                    author: "Иван20",
                    text: "Текст комментария20"
                }
            ];

            $scope.users = [
                {name: "Иван"},
                {name: "Петр"},
                {name: "Ирина"},
                {name: "Андрей"},
                {name: "Санек"}
            ];

            $scope.toggleSettingsCollapse = function () {
                $scope.isSettingsCollapsed = !$scope.isSettingsCollapsed;
            };

            var i = 21;
            $scope.nextScroll = function () {
                console.log("myPagingFunction");
                for (j = 0; j <= 30; j++) {
                    $scope.comments.push({
                        author: "Иван" + i,
                        text: "Текст комментария" + i
                    });
                    i++;
                }
            };

        }]);

