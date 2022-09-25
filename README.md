# 百度指数自动化下载

## 一、原理

selenium控制浏览器自动输入+点击查询；charles捕获HTTP查询请求；ptbk+uniqid解密请求结果；

## 一、技术栈

- selenium
- charles

## 二、前置条件

- chrome浏览器
- [chrome browser drivers](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/)
- charles

## 三、操作步骤

1. 打开charles，启动代理，只捕获`index.baidu.com`域名;
2. 运行`auto_search.py`: 启动浏览器，打开百度指数页面，自动查询;
3. 查询结束后，导出charles结果（json session file）;
4. 运行`parse_charles_session.py`: 解析charles结果

## 四、注意

- 百度指数限制了每个账号每天的访问次数