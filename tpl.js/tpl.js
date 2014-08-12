/**
 * =====================================================================================
 *
 * tpl(简单模板引擎)
 *     @author chishaxie (Q: 404264294, Email: flashsl@qq.com)
 *     @feature 无任何依赖(可用于浏览器和NodeJS),高效短小,压缩后仅800+字节
 *
 * API:
 *     @param {String}  模板
 *     @param {Object}  数据源json对象
 *     @return {String}  渲染结果
 *
 * Grammar:
 *     使用 <% code %> 包裹Javascript代码
 *     <% = var %> 用于渲染变量(有无空白字符均可)
 *     Javascript代码的语句块请确保使用 { } 包裹(if,for,...)
 *     <% code %>若独立一行(前后可有空白字符),渲染时自动抽空(方便排版)
 *
 * Demo:
 *     模板:
 *         <h1><% = title %></h1>
 *         <ul>
 *             <% for (var i=0; i<list.length; i++) { %>
 *             <li><% = list[i].key %><% if (list[i].val) { %> -- <% = list[i].val %><% } %></li>
 *             <% } %>
 *         </ul>
 *     数据源:
 *         {
 *             title : "标题",
 *             list : [{
 *                     key : "Key1"
 *                 }, {
 *                     key : "Key2",
 *                     val : "Val2"
 *                 }]
 *         }
 *     渲染结果:
 *         <h1>标题</h1>
 *         <ul>
 *             <li>Key1</li>
 *             <li>Key2 -- Val2</li>
 *         </ul>
 *
 * =====================================================================================
 */
(function () {
	var grammar = /<%([\s\S]+?)%>/g,
	format = function (text) {
		return text.replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/\t/g, '\\t').replace(/\r/g, '\\r').replace(/\n/g, '\\n');
	},
	tpl = function (text, data) {
		var statement,
		cursor = 0,
		code = 'var _=[];',
		parm = [],
		argv = [];
		while (statement = grammar.exec(text)) {
			var prefix = text.slice(cursor, statement.index),
			rendering,
			ptrash,
			strash = null;
			code += (!(rendering = statement[1].match(/^[\s]*=/)) &&
				(ptrash = (cursor === 0) ? prefix.match(/^([\s\S]*\r?\n)?[ \t]*$/) : prefix.match(/^([\s\S]*\r?\n)[ \t]*$/)) &&
				(strash = text.slice(statement.index + statement[0].length).match(/^[ \t]*(?:\r?\n|$)/))) ?
			(ptrash[1] ? ('_.push("' + format(ptrash[1]) + '");') : '') :
			((prefix.length !== 0) ? ('_.push("' + format(prefix) + '");') : '');
			rendering ? (code += '_.push(' + statement[1].slice(rendering[0].length) + ');') : (code += statement[1] + '\n');
			cursor = statement.index + statement[0].length + (strash ? strash[0].length : 0);
		}
		code += (cursor !== text.length) ? ('_.push("' + format(text.slice(cursor)) + '");return _.join("");') : 'return _.join("");';
		for (var p in data) {
			parm.push(p);
			argv.push(data[p]);
		}
		return new Function(parm, code).apply(null, argv);
	};
	typeof(exports) !== "undefined" ? exports.tpl = tpl : this.tpl = tpl;
})();
