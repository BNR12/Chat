var timeoutID;

//timeout = 1 second
var timeout = 1000;

function setup(){

	//on button click, send message
	document.getElementById("submit").addEventListener("click", createMsg, true);

	//set poller to execute every 1 second
	timeoutID = window.setTimeout(poller, timeout);
}

function createMsg() {

	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}

	var msg = document.getElementById("msg").value;
	var user = document.getElementById("user").innerHTML;
	var room = document.getElementById("room").innerHTML;

	httpRequest.onreadystatechange = function() { sendMsg(httpRequest, msg, user) };

	httpRequest.open("POST", "/send_message");
	httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

	var data;
	data = "msg=" + msg + "&user=" + user + "&room=" + room;
	
	httpRequest.send(data);
}

//check if request was successful
function sendMsg(httpRequest, msg, user) {
	if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status === 200) {
			addMsg(msg, user, httpRequest.responseText);
			clearInput();
		} else {
			alert("There was a problem with the post request.");
		}
	}
}

//clear text area
function clearInput() {
	document.getElementById("msg").value = "";
}

//add message to the chat room display
function addMsg(msg, user, id) {
	//add row to table
	var table = document.getElementById("msgs");
	var row = document.createElement('tr');
	table.appendChild(row);

	//add sender to row
	var sender = document.createElement('td');
	sender.innerHTML = user + ": ";
	row.appendChild(sender);

	//add message to row
	var text = document.createElement('td');
	text.innerHTML = msg;
	row.appendChild(text);

	//add id to row
	var num = document.createElement('td');
	num.innerHTML = id;
	num.style.visibility = "hidden";
	row.appendChild(num);
}

//polling function
function poller() {
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}


	httpRequest.onreadystatechange = function() { handlePoll(httpRequest) };
	httpRequest.open("POST", "/messages");
	httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

	//get last row in the table
	var last_row = document.getElementById("msgs").lastChild;
	var room = document.getElementById("room").innerHTML;

	//get last ID 
	var last_col = last_row.lastChild;
	var data;
	if (last_col == null){
		data = "id=0&room=" + room;
	} else{
		var last_id = last_row.lastChild.innerHTML;
		data = "id=" + last_id + "&room=" + room;
	}

	//send last message id in table
	httpRequest.send(data);
}

function handlePoll(httpRequest) {
	if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status === 200) {

			var messages = JSON.parse(httpRequest.responseText);
			for (var i = 0; i < messages.length; i++) {
				var user = messages[i].user;
				var text = messages[i].text;
				var id = messages[i].id;
				addMsg(text, user, id);

			}
			
			timeoutID = window.setTimeout(poller, timeout);
			
		} else {
			alert("There was a problem with the poll request.  you'll need to refresh the page to recieve updates again!");
		}
	}
}

window.addEventListener("load", setup, true);