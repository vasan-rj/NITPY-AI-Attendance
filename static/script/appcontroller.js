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

app.controller('FacultypageController', function($scope) {
    $scope.attendance = {};
    $scope.students = [
        { rollNo: 'CS21B10XX', status: 'Absent', change: false },
        { rollNo: 'CS21B10YY', status: 'Absent', change: false },
        { rollNo: 'CS21B10ZZ', status: 'Absent', change: false }
    ];

    $scope.takeAttendance = function() {
        alert('Attendance taken for ' + $scope.attendance.classRoom);
    };

    $scope.commitChange = function() {
        $scope.students.forEach(function(student) {
            if (student.change) {
                student.status = student.status === 'Absent' ? 'Present' : 'Absent';
            }
        });
        alert('Changes committed');
    };
});