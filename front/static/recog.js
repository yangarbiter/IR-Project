
window.onload = function(){
	var recognizer = new webkitSpeechRecognition();
	var transcription = document.getElementById('transcription');
	var result_container = document.getElementById('result-container');
	var ws = new WebSocket("ws://localhost:8888/ws");
	
	ws.onopen = function() {
		//console.log("ws open");
	};
	ws.onmessage = function(event) {
		var msg = event.data;
		var entry = document.createElement('div');
		entry.innerHTML = msg;
		result_container.appendChild(entry);
	};

	// recognizer setting
	recognizer.interimResults = true;
	recognizer.continuous = true;
	recognizer.lang = 'en-US';
	recognizer.onresult = function(event) {
		transcription.textContent = '';
		for (var i = event.resultIndex; i < event.results.length; i++) {
			console.log("Result: " + event.results[i][0].transcript)
			if (event.results[i].isFinal) {
				transcription.textContent = event.results[i][0].transcript + ' (Confidence: ' + event.results[i][0].confidence + ')';
				ws.send(transcription.textContent);
			} else {
				transcription.textContent += event.results[i][0].transcript;
			}
		}
	};
	// log errors
	recognizer.onerror = function(event) {
		console.log('Recognition error: ' + event.message);
	};


	document.getElementById('btn-start-recog').addEventListener('click', function() {
		info = {title: $('#info-title').val(),
						speaker: $('#info-speaker').val(),
						description: $('#info-description').val(),
						biography: $('#info-biography').val()}
		$.post("info", info);
		$('#info-container').css("display", "none");
		$('#result-container').css("display", "block");
		try {
			recognizer.start();
			//console.log('Recognizer started');
		} catch(ex) {
			console.log('Recognizer error:' + ex.message);
		}
	});

	document.getElementById('btn-stop-recog').addEventListener('click', function() {
		$('#info-container').css("display", "block");
		$('#result-container').css("display", "none");
		recognizer.stop();
		//console.log('Recognition stopped')
	});

};
