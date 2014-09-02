var ajax = { //ajax for NodeJS
	get : function (url, cb) {
		var req = ajax._http.get(url, function (rsp) {
				if (rsp.statusCode !== 200) {
					cb(new Error('statusCode = ' + rsp.statusCode));
					return;
				}
				rsp.setEncoding('utf8');
				var content = '';
				rsp.on('data', function (chunk) {
					content += chunk;
				}).on('end', function () {
					cb(content);
				}).on('error', function (err) {
					cb(err);
				});
			});
		req.on('error', function (err) {
			cb(err);
		});
	},
	post : function (url, data, cb) { //data is optional
		if (typeof(data) === 'object') {
			var _data = '';
			for (var k in data)
				_data += k + '=' + data[k] + '&';
			if (_data.length > 0)
				_data = _data.slice(0, -1);
			data = _data;
		} else if (typeof(data) === 'function' && typeof(cb) !== 'function') {
			cb = data;
			data = '';
		}
		var options = ajax._url.parse(url);
		options.method = 'POST';
		var req = ajax._http.request(options, function (rsp) {
				if (rsp.statusCode !== 200) {
					cb(new Error('statusCode = ' + rsp.statusCode));
					return;
				}
				rsp.setEncoding('utf8');
				var content = '';
				rsp.on('data', function (chunk) {
					content += chunk;
				}).on('end', function () {
					cb(content);
				}).on('error', function (err) {
					cb(err);
				});
			});
		req.on('error', function (err) {
			cb(err);
		});
		req.end(data);
	},
	_http : require('http'),
	_url : require('url')
};

typeof(exports) !== "undefined" ? (exports.get = ajax.get) && (exports.post = ajax.post) : 0;
