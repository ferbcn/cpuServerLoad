let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
let wsUrl = ws_scheme + '://' + window.location.host + "/ws"
let socket = new WebSocket(wsUrl);
//let socket = new WebSocket("ws://0.0.0.0:8000/ws");

socket.onmessage = function(event) {

    try {
        let parsedData = JSON.parse(event.data);
        console.log(parsedData);
        let cpu_load = parsedData.cpu;
        let mem_load = parsedData.mem;
        document.getElementById("cpu-load").innerText = cpu_load + "%";
        document.getElementById("mem-load").innerText = mem_load + "%";
        cpuLoadGauge.refresh(parseFloat(cpu_load));
        memLoadGauge.refresh(parseFloat(mem_load));
    } catch (error) {
        console.error("Error encountered:", error);
    }
};

socket.onclose = function(event) {
    document.getElementById("cpu-load").innerText = 'Connection lost';
};

socket.onerror = function(error) {
    document.getElementById("cpu-load").innerText = `Error: ${error.message}`;
};

socket.onopen = function(event) {
    //socket.send("ping");
}

