import io from 'socket.io-client';
import store from './Livedata';

var socket = io('http://raspberrypi.local:3000');

class Socketz {

  checkpi() {
    //Check if pi connected 
    //look for picheck callback
    socket.emit('picheck', '{ping}')
  }

  changemode(mode) {
    socket.emit('mode', mode)
    console.log('mode changed to: ' + mode)
  }


  changetemp() {
    socket.emit('changetemp', '{' + parseFloat(store.targetTemp) + '}')
  }

  contoserver() {

    socket.on('connect', function() {
      console.log('Connected to server')

      socket.emit('join', 'React App Connected')
      console.log('Sending to get temp')
      socket.emit('gettemptarget', '{givemetemp}')
      store.isConnected = true

      socket.on('tempdata', function(data) {
        var jsondata = JSON.parse(data);
        store.tempinside = parseFloat(jsondata.tempinside);
        store.temphousing = parseFloat(jsondata.temphousing);
        store.tempoutside = parseFloat(jsondata.tempoutside);
        store.radiatorFan = jsondata.radiatorFan;
        store.peltier = jsondata.peltier;
        store.pump = jsondata.pump;
        store.insideFan = jsondata.insideFan
        console.log('inside: ' + store.tempinside + ' pump: ' + store.temphousing + ' outside: ' + store.tempoutside + ' radiatorFan: ' + jsondata.radiatorFan);
        store.insidegrid.push(parseFloat(jsondata.tempinside))
        store.outsidegrid.push(parseFloat(jsondata.tempoutside))
        store.housinggrid.push(parseFloat(jsondata.temphousing))
        store.timegrid.push(jsondata.time)

        if (store.timegrid.length >= 15) {
          // shift() removes first row of array
          store.timegrid.shift()
          store.insidegrid.shift()
          store.outsidegrid.shift()
          store.housinggrid.shift()

        }

      });

      socket.on('disconnect', function(data) {
        store.isConnected = false
      });

      socket.on('targettemp', function(data) {
        store.targetTemp = parseFloat(data)
      });

      socket.on('reconnect', function(data) {
        store.isConnected = true
      });

      socket.on('join', function(data) {
        console.log('Recieved: ' + data)
      });

      socket.on('picheck', function(data) {
        console.log('picheck(rec) : ' + data)
        if (data == 'pong') {
          store.PiOnline = true
        }
      });
    });
  }


}

var socketz = new Socketz();

export default socketz
