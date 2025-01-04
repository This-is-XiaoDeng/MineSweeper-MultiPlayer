const HOST = "10.21.0.101:8080"

export async function getServerStatus() {
    const response = await fetch(`http://${HOST}/`)
    return response.json()
}

let ws = null
let listeners = []

function handleMessage(origin_message) {
    let message = JSON.parse(origin_message.data)
    console.log("Received message: ", message)
    let message_type = message["subject"]
    if (message["code"] !== undefined) {
        message_type = "callback"
    }
    listeners.forEach(listener_data => {
        if (listener_data["type"] === message_type) {
            listener_data["callback"](message)
        }
    })
}

function getListenerID() {
    let id = 0
    while (listeners.some(listener_data => listener_data.id === id)) {
        id++
    }
    return id
}

export function bindListener(type, callback) {
    let id = getListenerID()
    listeners.push({type: type, callback: callback, id: id})
}

let selfName = null

function waitForMessage(type) {
    return new Promise((resolve) => {
        const tempListener = (message) => {
            resolve(message);
            listeners = listeners.filter(listener_data => listener_data.callback !== tempListener);
        };
        bindListener(type, tempListener);
    });
}


export function createWebSocketConnection() {
    ws = new WebSocket(`ws://${HOST}/ws`)
    ws.onmessage = handleMessage
    return new Promise((resolve) => {
        ws.onopen = () => {
            resolve()
        }
    });
}

export function removeListener(listener_id) {
    listeners = listeners.filter(listener_data => listener_data.id !== listener_id)
}

function sendWebSocketMessage(message) {
    ws.send(JSON.stringify(message))
}

export async function startMatching() {
    return await wsCallFunction("start_matching", {})
}

async function wsCallFunction(func, args) {
    let message = args
    message["func"] = func
    sendWebSocketMessage(message)
    return await waitForMessage("callback")
}

export function getName() {
    return selfName
}

export async function setName(name) {
    selfName = name
    return await wsCallFunction("set_name", {name: name})
}

export async function getReady(ready) {
    return await wsCallFunction("get_ready", {ready: ready})
}


export async function getGameMap() {
    return await wsCallFunction("get_game_map", {})
}

export async function mineBlock(pos) {
    return await wsCallFunction("mine_block", {pos: pos})
}