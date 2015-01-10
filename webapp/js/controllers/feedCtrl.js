/**
 * A controller to manage news feed
 * @class
 */
angular.module('reChat.feedCtrl', [])
    .controller('FeedCtrl', ['$scope','DialogService','UserService',
        function($scope, DialogService, UserService) {

            //console.log("init feed ctrl " + DialogService.showSuccessAlert('Тестовый заголовок','Тело сообщения'));
            //DialogService.showModalDialog(1,2,3);

            $scope.isLoggedIn = function() {
                return UserService.isLoggedIn();
            };

            $scope.message = "";

            $scope.sendMessage = function() {
                i++;
                $scope.comments.unshift({
                    author: "Петр" + i,
                    text: $scope.message,
                    theme: $scope.theme,
                    time: moment(new Date()).format('HH:mm'),
                    date: moment(new Date()).format('DD.MM.YY')
                });
                $scope.message = "";
                $scope.theme = "";
            };

            $scope.comments = [  // TODO get from server
                {
                    author: "Сергей",
                    text: "Хакатон (англ. hackathon, от hack (см. хакер) и marathon — марафон) — мероприятие, во " +
                    "время которого специалисты из разных областей разработки программного обеспечения (программисты, " +
                    "дизайнеры, менеджеры) сообща работают над решением какой-либо проблемы. Сегодня хакатоны уже не " +
                    "относятся к хакерству, это просто марафоны программирования. Обычно хакатоны длятся от одного дня до недели.",
                    theme: "Хакатон",
                    time: "17:26",
                    date: "25.12.14"
                },
                {
                    author: "Иван2",
                    text: "Текст письма2"
                },
                {
                    author: "Иван3",
                    text: "Текст письма3"
                },
                {
                    author: "Иван4",
                    text: "Текст письма4"
                },
                {
                    author: "Иван5",
                    text: "Текст письма5"
                },
                {
                    author: "Иван6",
                    text: "Текст письма6"
                },
                {
                    author: "Иван7",
                    text: "Текст письма7"
                },
                {
                    author: "Иван8",
                    text: "Текст письма8"
                },
                {
                    author: "Иван9",
                    text: "Текст письма9"
                },
                {
                    author: "Иван10",
                    text: "Текст письма10"
                },
                {
                    author: "Иван11",
                    text: "Текст письма11"
                },
                {
                    author: "Иван12",
                    text: "Текст письма12"
                },
                {
                    author: "Иван13",
                    text: "Текст письма13"
                },
                {
                    author: "Иван14",
                    text: "Текст письма14"
                },
                {
                    author: "Иван15",
                    text: "Текст письма15"
                },
                {
                    author: "Иван16",
                    text: "Текст письма16"
                },
                {
                    author: "Иван17",
                    text: "Текст письма17"
                },
                {
                    author: "Иван18",
                    text: "Текст письма18"
                },
                {
                    author: "Иван19",
                    text: "Текст письма19"
                },
                {
                    author: "Иван20",
                    text: "Текст письма20"
                }
            ];

            var i = 21;
            $scope.nextScroll = function() {
                for (j=0;j<=30;j++) {
                    $scope.comments.push({
                        author: "Иван" + i,
                        text: "Текст письма" + i
                    });
                    i++;
                }
            };

        }]);