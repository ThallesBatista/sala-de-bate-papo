<script>
	import { onMount } from "svelte";

  	let messageInput;
	let messages = [];
	let inputText = "";

	onMount(() => {
    	messageInput.focus();
  	});

	const ws = new WebSocket("ws://localhost:6789");

	ws.onmessage = function (e) {
		let data = JSON.parse(e.data);
		messages = [...messages, [data.type, data.message]];
	};

	function handleClick() {
		let output;
		let message;
		if (inputText.charAt(0) == "\\") {
			let receiver = inputText.split(" ")[0].substring(1);
			let msg = inputText.substr(inputText.indexOf(" ") + 1);
			output = {"action": "private_message", "message": msg, "receiver": receiver};
			message = "Você (" + receiver +") >> " + msg; 
		} else {
			output = {"action": "public_message", "message": inputText};
			message = "Você >> " + inputText;
		}
		ws.send(JSON.stringify(output));
		messages = [...messages, ["OWN", message]];
		inputText = "";
	};

</script>

<main>
	<h1>Web Chat</h1>
	<p>
		Para enviar uma mensagem privada, uma barra invertida seguida do nome do destinatário no início da mensagem.
		Por exemplo: "\Fulano Ei, Fulano!"
	</p> 
	<div class="chatbox">
		{#each messages as message}
    		<p>{message[1]}</p>
		{/each}
	</div>
	<form class="inputbox">
		<input type="text" bind:this={messageInput} bind:value={inputText} />
    	<button type="submit" on:click|preventDefault={handleClick}>Send</button>	
	</form>
</main>

<style>
  	* {
    	box-sizing: border-box;
  	}
	main {
		width: calc(100% - 30px);
		text-align: center;
		padding: 1em;
		max-width: 1240px;
		margin: 0 auto;
	}
	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}
	.chatbox {
		width: 100%;
		height: 50vh;
		padding: 0 1em;
		text-align: left;
		background-color: #eee;
		overflow-y: scroll;
		overscroll-behavior-y: contain;
		scroll-snap-type: y proximity;
	}
	.chatbox p {
		margin-top: 0.5em;
		margin-bottom: 0;
		padding-bottom: 0.5em;
	}
	.chatbox > p:last-child {
		scroll-snap-align: end;
	}
	.inputbox {
		display: flex;
		margin-top: 0.5em;
	}
	.inputbox input {
		flex-grow: 1;
	}
</style>