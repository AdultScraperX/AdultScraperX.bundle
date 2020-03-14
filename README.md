### TG群：https://t.me/AdultScraperX
# AdultScraperX 
### AdultScraperX是一个可以匹配成人影片信息的插件(不提供任何影片下载与观看连接)，仅提供简介、演员、标题、类型、系列、导演、工作室的信息匹配。
## AdultScraperX 需要搭配 AdultScraperX-server 一起使用
- 服务端项目地址：
[https://github.com/chunsiyang/AdultScraperX-server](https://github.com/chunsiyang/AdultScraperX-server)

# 使用帮助
### 本地字幕挂载：
- 需要在代理中勾选：Local Media Assets (Movies)

### plex目录标记设置（无特殊需求不用改动）：
- 欧美与日本(骑兵、步兵、动漫)的目录标记可以在插件中自定义配置:
- 配置主目录标记，必须含有(前、后)特殊字符如：-M- 、*M*、=M=以此类推
- 目录标记只可出现一次，并且与主目录文件夹名的标记一致才可识别

#### 本地主目录配置标记举例：
- 修改你的本地文件夹为如下：
- volume1/有码=M=/（无数个子目录）/（无数个文件）.mp4
- volume1/无码=NM=/（无数个子目录）/（无数个文件）.mp4
- volume1/动漫=A=/（无数个子目录）/（无数个文件）.mp4
- volume1/欧美=E=/（无数个子目录）/（无数个文件）.mp4

#### 合集标记 =C=
- volume1/有码=M=/（无数个子目录）/=C=(xxx合集)/（无数个文件）.mp4
- volume1/无码=NM=/（无数个子目录）/=C=(xxx合集)/（无数个文件）.mp4
- volume1/动漫=A=/（无数个子目录）/=C=(xxx合集)/（无数个文件）.mp4
- volume1/欧美=E=/（无数个子目录）/=C=(xxx合集)/（无数个文件）.mp4


### 命名规范：

#### 日本骑兵：

- 项目列表标准番号.mp4  (优选)

- 项目列表任意字符与标准番号.mp4 

#### 日本步兵：

- 标准番号.mp4  (优选)
- 任意字符与标准番号.mp4  

#### 日本动漫
- 标准番号.mp4  (优选)
- 任意字符与标准番号.mp4 

#### 欧美：
- 工作室 - 片名 - 明星（可以包含多个）.mp4 

#### 同片多版本或多CD的命名方法：
- 命名-vol1.mp4
- 命名-vol2.mp4


### 插件配置说明
- Plex Plugin 服务端参数配置
```
- API服务URL ：服务端地址（填写时需包含 http://或https://头）
- API服务Port ： 服务端端口
```
- 使用缓存或开启用户权限时才需要填写下列配置，群晖Docker用户群体无需填写。
```
个人DDNS ：plex所使用的公网域名或固定IP地址
Plex端口 ：plex所使用的端口
令牌 ： 访问服务端的令牌
```

### 检测服务端状态及命令说明
在搜刮器为AdultScraperX的库中打开任意一个文件的手动匹配并输入以下代码
```
--checkState
```
【此功能需服务端开启mongo缓存库】
查询与服务端当前状态，推荐安装插件并设置完成后运行
```
--checkSpider
```
查询服务端搜刮器连接状态，用于排查网络问题，推荐安装插件并设置完成后运行
```
要匹配的名  --noCache
```
搜刮器默认启用缓存机制，手动匹配可跳过缓存进行匹配，需要在匹配名称结尾加入代码 --noCache 
```
要匹配的名 --nore
```
手动匹配时不使用正则过滤关键字，根据所输入的片名直接查询匹配


# 本地备份媒体信息说明
- 测试功能不一定好用
- 1.2.0 初次测试备份代码
- 1.3.0开始支持混合搜索 local or online （仍然是测试）
- 若存在nfo，优先匹配nfo不会在线匹配，除非出抛异常或者没有nfo才会进行在线匹配。想要强制在线匹配需要删除nfo文件
- 这弄能目前不稳定
- 1.3.2 基本稳定工作

# 常见服务器异常log输出
## 服务端问题
### HTTPError: HTTP Error 500: INTERNAL SERVER ERROR
- 查看服务端日志
## 权限问题
### \[Errno 13\] Permission denied:
- 没有权限操作目录
## 以下请找自身网络问题：
### error : ConnectionError(ProtocolError('Connection aborted.', OSError(0, 'Error')))
- 网络连接断开或无法连接
### URLError: <urlopen error \[Errno 111\] Connection refused>
- 检查你的服务端是否启动
### HTTP Error 403: Forbidden
- 拒绝连接
### 海报、背景、头像出现黑板无图
- 网络异常或中断导致图像没有返回，需要在网络稳定时候重新刷新元数据

## 程序抛异常、数据错乱怎么办？
### Issues上报或者tg上报
- Issues 上报问题 阐述问题并使用  \`\`\` 你的最新日志文本 \`\`\` 发表Issues （不要上传任何文件）
- tg上报问题 阐述问题并上传你最新日志文本 .log单文件 不要压缩包
### 以下是程序报错例子
- 通常程序错误会出现类似于下面的内容
```
Traceback (most recent call last):
  File "/usr/local/lib/python3.7/site-packages/flask/app.py", line 2446, in wsgi_app
    response = self.full_dispatch_request()
  File "/usr/local/lib/python3.7/site-packages/flask/app.py", line 1951, in full_dispatch_request
    rv = self.handle_user_exception(e)
  File "/usr/local/lib/python3.7/site-packages/flask/app.py", line 1820, in handle_user_exception
    reraise(exc_type, exc_value, tb)
  File "/usr/local/lib/python3.7/site-packages/flask/_compat.py", line 39, in reraise
    raise value
  File "/usr/local/lib/python3.7/site-packages/flask/app.py", line 1949, in full_dispatch_request
    rv = self.dispatch_request()
  File "/usr/local/lib/python3.7/site-packages/flask/app.py", line 1935, in dispatch_request
    return self.view_functions[rule.endpoint](**req.view_args)
  File "AdultScraperX-server/main.py", line 200, in getMediaInfos
    cacheFlag)
  File "AdultScraperX-server/main.py", line 227, in search
    items = webSite.search(q)
  File "/home/adultScraperX/AdultScraperX-server/app/spider/arzon.py", line 63, in search
    html_item['html'], q)
  File "/home/adultScraperX/AdultScraperX-server/app/spider/arzon.py", line 93, in analysisMediaHtmlByxpath
    title = html.xpath(xpath_title)
AttributeError: 'NoneType' object has no attribute 'xpath'
```





