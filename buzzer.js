var gpio = require("rpi-gpio");
var sleeper = require("sleep");
var async = require('async');

var isOn = true;
var count = 0;
gpio.setup(16, gpio.DIR_OUT, on);

function on() {
	if (count > 100) {
		gpio.destroy(function() {
			console.log('All pins unexported');
		})
		return;
	}
	writeValue(true);
	count += 1;
	setTimeout(off, 10);
}

function off() {
	writeValue(false);
	count += 1;
	setTimeout(on, 10);
}

function writeValue(value) {
	gpio.write(16, value, function(err) {
		if (err) throw err;
		console.log("write value: " + value);
        });
}

function delayWriteValue(value) {
	setTimeout(function() {
		writeValue(value);
	}, 100);
}

//async.parallel([
//	function(cb) {
//		gpio.setup(16, gpio.DIR_OUT, cb);
//	}
//], function(err, results) {
//	console.log('Pins set up');
//	async.series([
//		function(cb) { delayWriteValue(true); },
//		function(cb) { delayWriteValue(false); },
//		function(cb) { delayWriteValue(true); },
//		function(cb) { delayWriteValue(false); }
//	], function(err, results) {
//		console.log('Write done');
//		setTimeout(function() {
//	       	     gpio.destroy(function() {
//		                    console.log('Closed pins, now exit');
//			            });
//	        }, 500);	    
//	});
//});
