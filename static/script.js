function scrollToBottom() {
    const chatBox = document.getElementById("chatBox");
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function askBot() {
    const inputElement = document.getElementById("userInput");
    const chatBox = document.getElementById("chatBox");
    const loadingElement = document.getElementById("loading");

    chatBox.innerHTML += `<div style="text-align: right; margin: 5px 0;">You: ${inputElement.value}</div>`;
    loadingElement.style.display = "block";

    try {
        const response = await fetch(`/ask?question=${encodeURIComponent(inputElement.value)}`, {
            method: 'POST',
        });

        if (response.ok) {
            const data = await response.json();
            chatBox.innerHTML += `<div style="text-align: left; margin: 5px 0;">Bot: ${data.answer}</div>`;
        } else {
            console.error("Error:", response.statusText);
            chatBox.innerHTML += `<div style="text-align: left; margin: 5px 0;">Bot: Sorry, I couldn't process that request.</div>`;
        }
    } catch (error) {
        console.error("Error:", error);
        chatBox.innerHTML += `<div style="text-align: left; margin: 5px 0;">Bot: Oops, something went wrong.</div>`;
    }

    inputElement.value = "";
    loadingElement.style.display = "none";
    scrollToBottom();
}

document.getElementById("userInput").addEventListener("keyup", function(event) {
    if (event.key === "Enter") {
        askBot();
    }
});
