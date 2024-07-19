var app = angular.module('attendenceApp', []);

app.controller('HomeController', ['$scope', '$location' , function($scope, $location){
    document.getElementById('loginSignupButton').addEventListener('click', function(){
        window.location.href= '/login';
    })
}]);