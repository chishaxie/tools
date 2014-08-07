var conf = {
	port : 8080, //HTTP服务的端口
	cwd : '.', //shell运行的当前目录
	shell : "ps -ef | grep '#0#' | grep -v 'grep'", //用 #数字# 表示可变部分
	params : [{
			name : 'opt', //参数的名字
			optional : 'bash', //存在该属性表示参数可选(值为其默认值)
			pattern : /^[a-zA-Z0-9_]+$/, //参数必须匹配的模式(防止shell注入)
		}, //多个参数分别对应 #0# #1# #2# ...
	],
	contentType : 'text/plain', //HTTP返回的Content-Type
	encoding : 'utf8', //shell的标准输出的编码
	timeout : 5 * 1000, //shell运行的超时时间(毫秒)
	maxBuffer : 1024 * 1024, //shell的标准输出的Buffer大小
	logEachRequest : true, //将每个请求记录到stdout上?
};

/**
 * =====================================================================================
 *
 * shell2http
 *         Powered by chishaxie (Q: 404264294, Email: flashsl@qq.com)
 *         Version: 2014.05.08
 *
 * Tips:
 *     参数通过HTTP的GET方法传递
 *     Shell的输出采用Buffer的方式接收(一次性接收全部),配置中的maxBuffer很重要
 *     Shell的运行时间限制由配置中的timeout决定
 * =====================================================================================
 */

var url = require('url');
var util = require('util');
var http = require('http');
var child_process = require('child_process');

http.createServer(function (req, rsp) {
	rsp.setHeader('Server', 'shell2http.js');

	if (conf.logEachRequest)
		console.log(new Date().toLocaleString() + ' ' + req.url);

	var obj = url.parse(req.url, true).query;
	var argv = [];
	for (var i = 0; i < conf.params.length; i++) {
		var param = conf.params[i];
		if (typeof(obj[param.name]) !== 'string') {
			if (typeof(param.optional) !== 'string') {
				rsp.writeHeader(403, {
					'Content-Type' : 'text/plain'
				});
				rsp.end('Missing required argument "' + param.name + '"\n');
				return;
			}
			argv.push(param.optional);
		} else {
			if (util.isRegExp(param.pattern) && !obj[param.name].match(param.pattern)) {
				rsp.writeHeader(403, {
					'Content-Type' : 'text/plain'
				});
				rsp.end('Illegal argument "' + param.name + '"\n');
				return;
			}
			argv.push(obj[param.name]);
		}
	}

	var cmd = conf.shell;
	for (var i = 0; i < argv.length; i++)
		cmd = cmd.replace(new RegExp('#' + i + '#', 'g'), argv[i]);

	child_process.exec(cmd, {
		cwd : conf.cwd,
		encoding : conf.encoding,
		timeout : conf.timeout,
		maxBuffer : conf.maxBuffer

	}, function (error, stdout, stderr) {
		if (error) {
			rsp.writeHeader(500, {
				'Content-Type' : 'text/plain'
			});
			rsp.end('Runtime exception "' + error.message + '"\n');
			return;
		}
		rsp.writeHeader(200, {
			'Content-Type' : conf.contentType,
			'Content-Length' : stdout.length
		});
		rsp.end(stdout);
	});
}).listen(conf.port);
