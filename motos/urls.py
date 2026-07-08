from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

from django.views.generic import RedirectView

urlpatterns = [
    path('index/', views.index),
    path('comprar/', views.comprar),
    path('vender/', views.vender),
    path('servicios/', views.servicios),
    path('nosotros/', views.nosotros),
    path('servicios/gps/', views.gps, name='gps'),
    path('servicios/traspasos/', views.traspasos, name='traspasos'),
    path('servicios/recibimos/', views.recibimos, name='recibimos'),
    path('servicios/soat', views.soat, name='soat'),
    path("panel/", views.panel, name="panel"),
    path("eliminar-moto/<int:id>/", views.eliminar_moto, name="eliminar_moto"),
    path("editar-moto/<int:id>/",views.editar_moto,name="editar_moto"),
    path("agregar-moto/",views.agregar_moto,name="agregar_moto"),
    path("solicitudes/",views.solicitudes,name="solicitudes"),
    path('moto/<int:id>/', views.detalle_moto),
    path('aceptar-solicitud/<int:id>/',views.aceptar_solicitud),
    path('rechazar-solicitud/<int:id>/',views.rechazar_solicitud),
    path('login/',views.login_registro,name='login'),
    path('logout/',views.cerrar_sesion,name='logout'),
    path('password-reset/',auth_views.PasswordResetView.as_view(template_name='motos/password_reset.html'),name='password_reset'),
    path('password-reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='motos/password_reset_done.html'),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='motos/password_reset_confirm.html'),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(template_name='motos/password_reset_complete'),name='password_reset_complete'),
    path('favorito/<int:id>/',views.agregar_favorito,name='favorito'),
    path('favoritos/',views.favoritos,name='favoritos'),
    path('mis_solicitudes/',views.mis_solicitudes,name='mis_solicitudes'),
    path('notificaciones/',views.notificaciones,name='notificaciones'),
    path('toggle-favorito/<int:id>/',views.toggle_favorito,name='toggle_favorito'),
    path('eliminar-favorito/<int:id>/', views.eliminar_favorito, name='eliminar_favorito'),
    path('logout/', views.logout_view, name='logout'),
    path('recuperar/', views.recuperar_password),
    path('verificar-codigo/', views.verificar_codigo),
    path('nueva-password/', views.nueva_password),
    path('perfil/', views.perfil, name='perfil'),
    path("panel-motos/",views.panel_motos,name="panel_motos"),
    path('exportar-dashboard/',views.exportar_dashboard_pdf,name='exportar_dashboard_pdf'),
    path(
    "usuarios/",
    views.usuarios_admin,
    name="usuarios_admin"
),

path(
    "editar-usuario/<int:id>/",
    views.editar_usuario,
    name="editar_usuario"
),

path(
    "eliminar-usuario/<int:id>/",
    views.eliminar_usuario,
    name="eliminar_usuario"
),

path(
    "rendimiento/",
    views.rendimiento,
    name="rendimiento"
),

path(
    "api-rendimiento/",
    views.api_rendimiento,
    name="api_rendimiento"
),

path(
    "editar-interes/",
    views.editar_interes,
    name="editar_interes"
),
path(
    'terminos/',
    views.terminos,
    name='terminos'
),

path(
    "manual/",
    RedirectView.as_view(
        url="/media/manuales/manual_usuario.pdf"
    ),
    name="manual"
),

path("obtener-motos/",views.obtener_motos,name="obtener_motos"),

path('', lambda request: redirect('/index/')),
   ]


urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)