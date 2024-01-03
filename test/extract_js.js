var xpathExpression = "//*[@id='left']/ul/li/p[1]/strong[1]"; // 修改你的xpath表达式
var hrefResults = [];

// 执行XPath查询
var result = document.evaluate(xpathExpression, document, null, XPathResult.ORDERED_NODE_ITERATOR_TYPE, null);

// 遍历所有匹配的节点
var node;
while (node = result.iterateNext()) {
    // 获取节点的href属性值
    var href = node.getAttribute('href');
    if (href) {
        const match = href.match(/\d+/);
        const extractedNumber = match ? match[0] : null;
        hrefResults.push(extractedNumber); // 将href添加到结果数组中
    }
}

hrefResults