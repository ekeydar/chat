var app = angular.module('chat', []);

app.controller('ChatController',['$scope',function($scope) {
	$scope.isLoggedIn = false;
	$scope.username = null;
	$scope.login = function() {
		$scope.isLoggedIn = true;
	}
}]);

