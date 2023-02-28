/**
 * Returns the current datetime for the message creation.
 */
function getCurrentTimestamp() {
	return new Date();
}

/**
 * Renders a message on the chat screen based on the given arguments.
 * This is called from the `showUserMessage` and `showBotMessage`.
 */
function renderMessageToScreen(args) {
	// local variables
	let displayDate = (args.time || getCurrentTimestamp()).toLocaleString('en-IN', {
		month: 'short',
		day: 'numeric',
		hour: 'numeric',
		minute: 'numeric',
	});
	let messagesContainer = $('.messages');

	// init element
	let message = $(`
	<li class="message ${args.message_side}">
		<div class="avatar"></div>
		<div class="text_wrapper">
			<div class="text">${args.text}</div>
			<div class="timestamp">${displayDate}</div>
		</div>
	</li>
	`);

	// add to parent
	messagesContainer.append(message);

	// animations
	setTimeout(function () {
		message.addClass('appeared');
	}, 0);
	messagesContainer.animate({ scrollTop: messagesContainer.prop('scrollHeight') }, 300);
}

/**
 * Displays the user message on the chat screen. This is the right side message.
 */
function showUserMessage(message, datetime) {
	message = message.replace(/(?:\r\n|\r|\n)/g, '<br>');
	renderMessageToScreen({
		text: message,
		time: datetime,
		message_side: 'right',
	});
}

/**
 * Displays the chatbot message on the chat screen. This is the left side message.
 */
async function showBotMessage(message, datetime) {
	renderMessageToScreen({
		text: message,
		time: datetime,
		message_side: 'left',
	});
}

/**
 * Get input from user and show it on screen on button click.
 */
$('#send_button').on('click', function (e) {
	// USER: obtain & show message and reset input
	user_question = $('#msg_input').val()
	showUserMessage(user_question);
	$('#msg_input').val('');

	// BOT: show bot message
	setTimeout(function () {
		queryDB(user_question);
	}, 300);
});


async function queryDB(question) {
	const data = {
		data: question
	};

  	// QUERY: pass in user text to backend endpoint as query
	fetch("http://localhost:8080/query", {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify(data),
	})
	.then(next => {
		// RESPONSE: obtain english response
		fetch("http://localhost:8080/response")
		.then(response => response.text())
		.then(txt => {
			// simply dumps query response but will clean output @ backend endpoint
			renderMessageToScreen({
				text: txt,
				time: getCurrentTimestamp(),
				message_side: 'left',
			});
			return txt;
		})
		.catch(function (error) {
			console.log("Response Error: " + error);
		});
	})
	.catch(function (error) {
		console.log("Query Error: " + error);
	});
}

/**
 * Set initial bot message to the screen for the user.
 */
$(window).on('load', function () {
	showBotMessage('Hello there! Type in a message.');
});
