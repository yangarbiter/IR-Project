
window.onload = function(){
	var transcription = document.getElementById('transcription');
	var result_container = document.getElementById('result-container');
	var ws = new WebSocket("ws://"+location.host+"/ws");
	var count = 1;
	
	ws.onopen = function() {
		console.log("ws open");
	};
	ws.onmessage = function(event) {
		var msg = JSON.parse(event.data);
		$('#result-container').html('');
		for(i=0; i<msg.length; i++){
			var entry = document.createElement('div');
			var title = document.createElement('a');
			var content = document.createElement('div');
			var btn_del = document.createElement('button');
			var btn_acc = document.createElement('button');

			entry.id = 'entry'.concat(msg[i].vocab);
			entry.className = 'entry';

			btn_del.nodeType = "button";
			btn_del.id = 'btn-del'.concat(msg[i].vocab);
			btn_del.className = "btn btn-default btn-sm btn-del";
			btn_del.appendChild(document.createElement('span'));
			btn_del.firstChild.className = "glyphicon glyphicon-remove";
			btn_del.addEventListener('click', function(){
				var voc = this.id.substr(7, this.id.length-7);
				$.post("fb", { type: 'remove', vocab: voc});
				$(this).parent().hide('slow', function(){$(this).remove()});
			});

			btn_acc.nodeType = "button";
			btn_acc.id = 'btn-acc'.concat(msg[i].vocab);
			btn_acc.className = "btn btn-default btn-sm btn-acc";
			btn_acc.appendChild(document.createElement('span'));
			btn_acc.firstChild.className = "glyphicon glyphicon-ok";
			btn_acc.addEventListener('click', function(){
				$.post("fb", { type: 'accept', vocab: this.id.substr(7, this.id.length-7)});
				$(this).parent().effect('shake');
			});

			title.innerHTML = msg[i].title;
			title.className = 'entry-title';
			title.href = msg[i].url;

			content.innerHTML = msg[i].content;
			content.className = 'entry-content';

			entry.appendChild(btn_acc);
			entry.appendChild(btn_del);
			entry.appendChild(title);
			entry.appendChild(content);

			//entry.style.display="none";

			result_container.appendChild(entry);

			//$("#"+entry.id).fadeIn('slow');
		}
	};



	document.getElementById('btn-start-recog').addEventListener('click', function() {
		info = {title: $('#info-title').val(),
						speaker: $('#info-speaker').val(),
						description: $('#info-description').val(),
						biography: $('#info-biography').val()}
		$.post("info", info);
		$('#info-container').css("display", "none");
		$('#result-container').css("display", "block");
		ws.send(" ");
	});

	document.getElementById('btn-stop-recog').addEventListener('click', function() {
		$('#info-container').css("display", "block");
		$('#result-container').css("display", "none");
	});

	document.getElementById('btn-send').addEventListener('click', function() {
		ws.send($('#transcript').val())
	});

};
