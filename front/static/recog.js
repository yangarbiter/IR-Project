
window.onload = function(){
	var recognizer = new webkitSpeechRecognition();
	var transcription = document.getElementById('transcription');
	var result_container = document.getElementById('result-container');
	var ws = new WebSocket("ws://localhost:8888/ws");
	
	ws.onopen = function() {
		//console.log("ws open");
	};
	ws.onmessage = function(event) {
		var msg = JSON.parse(event.data);
		for(i=0; i<msg.length; i++){
			var entry = document.createElement('div');
			var title = document.createElement('div');
			var content = document.createElement('div');
			var btn_del = document.createElement('button');
			var btn_acc = document.createElement('button');

			entry.className = 'entry';

			btn_del.nodeType = "button";
			btn_del.id = 'btn-del'.concat(msg[i].vocab);
			btn_del.className = "btn btn-default btn-sm btn-del";
			btn_del.appendChild(document.createElement('span'));
			btn_del.firstChild.className = "glyphicon glyphicon-remove";
			btn_del.addEventListener('click', function(){
				$.post("fb", { type: 'remove', vocab: this.id.substr(7, this.id.length-7)});
			});

			btn_acc.nodeType = "button";
			btn_acc.id = 'btn-acc'.concat(msg[i].vocab);
			btn_acc.className = "btn btn-default btn-sm btn-acc";
			btn_acc.appendChild(document.createElement('span'));
			btn_acc.firstChild.className = "glyphicon glyphicon-ok";
			btn_acc.addEventListener('click', function(){
				$.post("fb", { type: 'accept', vocab: this.id.substr(7, this.id.length-7)});
			});

			title.innerHTML = msg[i].title;
			title.className = 'entry-title';

			content.innerHTML = msg[i].content;
			content.className = 'entry-content';

			entry.appendChild(title);
			entry.appendChild(btn_acc);
			entry.appendChild(btn_del);
			entry.appendChild(content);

			result_container.appendChild(entry);
		}
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
