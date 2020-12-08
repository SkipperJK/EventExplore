"""EventExploreServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from EventExploreServer import view

urlpatterns = [
    # path('admin/', admin.site.urls),
    path(r'test', view.index, name='index'),
    path(r'echart', view.echart_test, name='echart'),
    # url(r'^query/(\w*)/', view.search_relative_articles),  # 位置参数
    # url(r'^query/(?P<topic>\S{1,})/$', view.search_relative_articles),  # 关键字参数
    url(r'^query/(?P<topic>\S{1,})/$', view.SearchView.as_view()),  # 关键字参数
    url(r'^extract/(?P<text>\S{1,})/$', view.OpenIEView.as_view()),
    url(r'^explore/(?P<topic>\S{1,})/$', view.EventExplore.as_view()),
]
'''
路由配置模块就是ulrpatterns列表，列表的每个元素都是一项path
    path()四个参数，route,view是必须的，kwargs和name是可选的
        route是一个匹配URL的准则（正则表达式），当Django响应一个请求时，会从urlpatterns按顺序依次匹配
        view指的是处理当前url请求的视图函数啊，当Django匹配到路由时，自动将封装的HttpRequest对象作为第一个参数
        name对URL进行命名，可以在Django的任意处，尤其是模版内显式引用它
        
URL参数传递：
    1 正则表达式分组匹配（圆括号）来捕获URL中的值并以 位置参数 形式传递给视图
    2 使用分组命名匹配的正则表达式来捕获URL中的值并以 关键字参数 形式传递给视图  语法：(?P<name>pattern)  NOTE:捕获的参数永远都是字符串
'''
