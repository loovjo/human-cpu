let ws = new WebSocket("wss://localhost/ws/");

console.log("Started connection");

ws.onopen = function(e) {
    console.log("Connection opened");
    ws.send("JavaScript Client");
};

ws.onmessage = function(e) {
    console.log(`[Received] ${e}`);
}
