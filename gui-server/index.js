var app = require('express')();
var http = require('http').createServer(app);
var io = require('socket.io')(http);
var mqtt = require('mqtt')
var client  = mqtt.connect('mqtt://localhost')

client.on('connect', function () {
    client.subscribe('/data')
})

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/public/index.html');
});

io.on('connection', (socket) => {
    console.log('a user connected');

    client.on('message', function (topic, message) {
        if(topic === "/data") {
            io.emit('data', message.toString())
        }
    })

    socket.on('message', (msg)=> {
        console.log('message', msg);

    })
    socket.on('disconnect', () => {
        console.log('user disconnected');
    });
});

http.listen(3000, () => {
    console.log('listening on *:3000');
});
