var httpNgin = require('./httpNgin');

httpNgin.createServer(80, function (req, res, httppath) {
	console.log("dynamic page: " + httppath);
	switch (httppath.slice(1)) { //remove \ or /
	case 'time.njs':
		res.writeHeader(200, {
			'Content-Type' : 'text/html'
		});
		res.end('<h3>' + new Date().toLocaleString() + '</h3>');
		break;
	default:
		res.writeHeader(404, {
			'Content-Type' : 'text/html'
		});
		res.end('<h3>404: Not Found</h3>');
		break;
	}
});
