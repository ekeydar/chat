var app = angular.module('chat',[]);

app.controller('ChatController',['$scope','$window','$http','$timeout',function($scope,$window,$http,$timeout) {
	$scope.username = $window.sessionStorage.getItem('username');
	console.log('username = ' + $scope.username);
	$scope.isLoggedIn = $scope.username && $scope.username.length > 0;
	$scope.newMessage = null;
	$scope.messages = [];
	$scope.login = function() {
		$window.sessionStorage.setItem('username',$scope.username);
		$scope.isLoggedIn = true;
	}
	$scope.logout = function() {
		$window.sessionStorage.removeItem('username');
		$scope.username = null;
		$scope.isLoggedIn = false;
	}
	$scope.say = function() {
		console.log($scope.username + ": " + $scope.newMessage);
		$http.post('/api/addMessage',{
			message : $scope.newMessage,
			username : $scope.username
		}).success(function() {
			$scope.newMessage = null;
		}).error(function(data,status,headers,config) {
			console.log('failed in ' + config.url + '\n' + status + '\n' + JSON.stringify(data));
		});
		$scope.newMessage = null;
	}
	$scope.startWS = function() {
		console.log("starting web-service");
		var host = 'ws://localhost:8000/api/chat-stream';
	    var websocket = new WebSocket(host)
	    websocket.onopen = function (evt) { 
	    	console.log("websocket open")
	    };
	    websocket.onmessage = function(evt) {
	        console.log("websocket message");
	        console.log(JSON.parse(evt.data));
	        var msg = JSON.parse(evt.data);
	        $scope.$apply(function() {
	        	$scope.messages.push(msg);
	        });
	        
	    };
	    websocket.onerror = function (evt) { 
	    	console.log("websocket close");
	    };
	}
	
	$timeout($scope.startWS,100);
}]);

