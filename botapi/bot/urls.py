from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter

from bot.views import views


def deploy_static_url():
    # 静态资源加载
    from django.views import static
    url_pattern = url(r'^bot_api/static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT},
                      name='static')
    return url_pattern


# 创建路由器并注册我们的视图。
router = DefaultRouter()
router.register(r'bot_login', views.BotLoginViewSet)
router.register(r'pub_verify', views.PublicVerifyViewSet)

urlpatterns = [
    url(r'', include(router.urls)),
]

# url路由器
urlpatterns += [
    url(r'^bot_api/', include(router.urls)),
    deploy_static_url(),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
