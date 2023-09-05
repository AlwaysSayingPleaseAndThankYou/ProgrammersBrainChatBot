//async function askBot() {
//    const inputElement = document.getElementById("userInput");
//    const chatBox = document.getElementById("chatBox");
//
//    // Display user's question
//    chatBox.innerHTML += `<div>User: ${inputElement.value}</div>`;
//    const Question = {
//        question: inputElement.value
//    };
//    const q = JSON.stringify(Question);
//    console.log(q);
//    const response = await fetch('/ask', {
//        method: 'POST',
//        headers: {
//            'Content-Type': 'application/x-www-form-urlencoded',
//        },
//        body: JSON.stringify(Question)
//    });
//
//    const data = await response.json();
//
//    // Display bot's answer
//    chatBox.innerHTML += `<div>Bot: ${data.answer}</div>`;
//
//    // Clear input
//    inputElement.value = "";
//}
async function askBot() {
    const inputElement = document.getElementById("userInput");
    const chatBox = document.getElementById("chatBox");

    chatBox.innerHTML += `<div style="text-align: right; margin: 5px 0;">You: ${inputElement.value}</div>`;

    const response = await fetch(`/ask?question=${encodeURIComponent(inputElement.value)}`, {
        method: 'POST',
    });

    const data = await response.json();

    chatBox.innerHTML += `<div style="text-align: left; margin: 5px 0;">Bot: ${data.answer}</div>`;
    inputElement.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;
}
document.getElementById("userInput").addEventListener("keyup", function(event) {
    // Check if the key pressed is "Enter"
    if (event.key === "Enter") {
        askBot();
    }
});