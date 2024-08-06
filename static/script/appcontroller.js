var app = angular.module('attendanceApp', []);

app.controller('HomeController', ['$scope', '$location', function($scope, $location){
    $scope.goToLogin = function() {
        window.location.href = '/login';
    };
}]);


app.controller('LoginController', ['$scope', '$location', function($scope, $location){
    $scope.goToStudentPage = function() {
        window.location.href = '/studentpage';
    };

    $scope.goToFacultyPage = function() {
        window.location.href = '/facultypage';
    };
}]);
