var app = angular.module('chat',[]);

app.controller('ChatController',['$scope','$window','$http','$timeout',function($scope,$window,$http,$timeout) {
	$scope.myInit = function() {
		$scope.username = $window.sessionStorage.getItem('username');
		console.log('username = ' + $scope.username);
		$scope.isLoggedIn = $scope.username && $scope.username.length > 0;
		$scope.newMessage = null;
		$scope.messages = [];
		$scope.websocket = null;
		if ($scope.isLoggedIn) {
			$timeout($scope.startWS,100);
		}
	}
	$scope.login = function() {
		$window.sessionStorage.setItem('username',$scope.username);
		$scope.isLoggedIn = true;
		$timeout($scope.startWS,100);
		$scope.messages = [];
	}
	$scope.logout = function() {
		$window.sessionStorage.removeItem('username');
		$scope.username = null;
		$scope.isLoggedIn = false;
		if ($scope.websocket) {
			$scope.websocket.close();
		}
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
	$scope.formatMessage = function(msg) {
		if (msg.kind == "login") {
			return msg.username + ' joined'
		} else if (msg.kind == "logout") {
			return msg.username + " left"
		} else {
			return msg.username + ": " + msg.message;
		}
	}
	$scope.startWS = function() {
		console.log("starting web-service");
		var loc = $window.location;
		var host = loc.host;
		var wsurl = 'ws://' + host + '/api/chat-stream?username=' + $scope.username;
		console.log('wsurl = ' + wsurl);
	    var websocket = new WebSocket(wsurl)
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
	    $scope.websocket = websocket;
	}
	$scope.myInit();
}]);

