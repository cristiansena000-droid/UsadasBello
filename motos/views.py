
from django.shortcuts import render
from .models import Moto, Solicitud, Favorito, Notificacion
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import *
from django.contrib.admin.views.decorators import staff_member_required
from .models import CodigoReset
import random
from django.core.mail import send_mail
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from django.template.loader import get_template
import time
from .models import Configuracion
from django.views.generic import RedirectView


import platform
import psutil
from django.contrib.auth.models import User
from xhtml2pdf import pisa


import matplotlib.pyplot as plt

from io import BytesIO

import base64

from django.contrib.auth.models import User

from .forms import RegistroForm
# Create your views here.


def index(request):

    if request.user.is_authenticated and request.user.is_staff and not request.GET.get("logout"):
        return redirect("/panel/")

    mensaje = None

    if request.method == 'POST':

        # LOGIN
        if 'password' in request.POST and not 'password1' in request.POST:

            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:

                login(request, user)

                # 🔥 REDIRECCIÓN AQUÍ
                if user.is_staff:
                    return redirect("/panel/")
                else:
                    return redirect("/index/")

            else:
                mensaje = "Usuario o contraseña incorrectos"

        # REGISTRO
        elif 'password1' in request.POST:

            username = request.POST.get('username')
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')


            acepta_terminos = request.POST.get(
                "acepta_terminos"
            )

            if not username or not email or not password1 or not password2:

                mensaje = "Todos los campos son obligatorios"
                mostrar_registro = True

            elif len(password1) < 8:

                mensaje = "La contraseña debe tener mínimo 8 caracteres"
                mostrar_registro = True

            elif password1 != password2:

                mensaje = "Las contraseñas no coinciden"
                mostrar_registro = True

            elif not acepta_terminos:

                mensaje = (
                    "Debes aceptar los términos y condiciones"
                )

                mostrar_registro = True

            elif User.objects.filter(username=username).exists():

                mensaje = "El usuario ya existe"
                mostrar_registro = True
            elif User.objects.filter(email=email).exists():

                mensaje = "Ya existe una cuenta con ese correo"
                mostrar_registro = True

            else:

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1
                )

                login(request, user)

                # 🔥 TAMBIÉN AQUÍ (opcional pero pro)
                return redirect("/index/")

    # 🔔 NOTIFICACIONES
    notificaciones_no_leidas = 0

    if request.user.is_authenticated:

        notificaciones_no_leidas = Notificacion.objects.filter(
            usuario=request.user,
            leida=False
        ).count()

    return render(request, "motos/index.html", {
        'mensaje': mensaje,
        'mostrar_registro': locals().get('mostrar_registro', False),
        'notificaciones_no_leidas': notificaciones_no_leidas,
        'datos_registro': request.POST
        })

def nosotros(request):
    return render(request, "motos/nosotros.html")


def vender(request):

    if not request.user.is_authenticated:

        return render(
            request,
            "motos/vender.html",
            {
                "mensaje": "Debes registrarte o iniciar sesión"
            }
        )

    if request.method == "POST":

        marca = request.POST.get("marca")

        modelo = request.POST.get("modelo")

        año = request.POST.get("año")

        nombre = request.POST.get("nombre")

        whatsapp = request.POST.get("whatsapp")

        kilometraje = request.POST.get("kilometraje")

        imagen = request.FILES.get("imagen")

        if not marca or not modelo or not año or not nombre or not whatsapp or not kilometraje:

            return render(
                request,
                "motos/vender.html",
                {
                    "mensaje": "Todos los campos son obligatorios"
                }
            )

        if imagen and not imagen.content_type.startswith("image/"):

            return render(
                request,
                "motos/vender.html",
                {
                    "mensaje": "Solo se permiten imágenes"
                }
            )

        Solicitud.objects.create(

            usuario=request.user,

            marca=marca,

            modelo=modelo,

            año=año,

            nombre=nombre,

            whatsapp=whatsapp,

            kilometraje=kilometraje,

            imagen=imagen
        )

        return render(
            request,
            "motos/vender.html",
            {
                "mensaje": "Solicitud enviada exitosamente"
            }
        )

    return render(request, "motos/vender.html")
def servicios(request):
    return render(request, "motos/servicios.html")

def comprar(request):

    # 🔥 BASE

    motos = Moto.objects.filter(
        estado="Publicada"
    )

    # ⚙ CONFIGURACIÓN

    config, creado = Configuracion.objects.get_or_create(
        id=1
    )

    # 🔍 FILTROS

    marca = request.GET.get('marca')

    precio = request.GET.get('precio')

    cilindraje = request.GET.get('cilindraje')

    if marca:

        motos = motos.filter(
            marca=marca
        )

    if precio:

        motos = motos.filter(
            precio__lte=precio
        )

    if cilindraje:

        motos = motos.filter(
            cilindraje=cilindraje
        )

    # 🏷 MARCAS

    marcas = Moto.objects.values_list(

        'marca',

        flat=True

    ).distinct()

    # 📄 PAGINACIÓN

    paginator = Paginator(
        motos,
        16
    )

    pagina = request.GET.get(
        'page'
    )

    motos_paginadas = paginator.get_page(
        pagina
    )

    # ❤️ FAVORITOS

    favoritos_ids = []

    if request.user.is_authenticated:

        favoritos_ids = Favorito.objects.filter(

            usuario=request.user

        ).values_list(

            'moto_id',

            flat=True

        )

    # 🔔 NOTIFICACIONES

    notificaciones_no_leidas = 0

    if request.user.is_authenticated:

        notificaciones_no_leidas = Notificacion.objects.filter(

            usuario=request.user,

            leida=False

        ).count()

    # 🚀 RENDER

    return render(

        request,

        'motos/comprar.html',

        {

            'motos': motos_paginadas,

            'marcas': marcas,

            'favoritos_ids': favoritos_ids,

            'notificaciones_no_leidas': notificaciones_no_leidas,

           'interes_credito': float(config.interes_credito)
        }

)

def gps(request):
    return render(request, 'motos/gps.html')


def traspasos(request):
    return render(request, 'motos/traspasos.html')

def recibimos(request):
    return render(request, 'motos/recibimos.html')

def soat(request):
    return render(request, 'motos/soat.html')

@staff_member_required
def panel(request):

    motos = Moto.objects.all()

    solicitudes = Solicitud.objects.all()

    total_motos = Moto.objects.count()

    total_usuarios = User.objects.count()

    total_solicitudes = Solicitud.objects.count()

    total_vistas = 0

    for moto in motos:

        total_vistas += moto.vistas

    moto_top = Moto.objects.order_by(
        "-vistas"
    ).first()

    # SOLICITUDES

    pendientes = Solicitud.objects.filter(
        estado="pendiente"
    ).count()

    aceptadas = Solicitud.objects.filter(
        estado="aceptada"
    ).count()

    rechazadas = Solicitud.objects.filter(
        estado="rechazada"
    ).count()

    # ULTIMAS SOLICITUDES

    ultimas_solicitudes = Solicitud.objects.order_by(
        "-fecha"
    )[:5]

    # MOTO MAS CARA

    moto_cara = Moto.objects.order_by(
        "-precio"
    ).first()

    # PROMEDIO PRECIO

    promedio_precio = 0

    if motos.exists():

        total = 0

        for moto in motos:

            total += moto.precio

        promedio_precio = total // motos.count()

    contexto = {

    "motos": motos,

    "solicitudes": solicitudes,

    "total_motos": total_motos,

    "total_usuarios": total_usuarios,

    "total_solicitudes": total_solicitudes,

    "total_vistas": total_vistas,

    "moto_top": moto_top,

    "pendientes": pendientes,

    "aceptadas": aceptadas,

    "rechazadas": rechazadas,

    "ultimas_solicitudes": ultimas_solicitudes,

    "moto_cara": moto_cara,

    "promedio_precio": promedio_precio,

    # GRAFICAS

    "labels": [
        moto.linea for moto in motos[:5]
    ],

    "data_vistas": [
        moto.vistas for moto in motos[:5]
    ]
    }

    return render(
        request,
        "motos/panel.html",
        contexto
    )


def eliminar_moto(request, id):

    moto = Moto.objects.get(id=id)

    moto.delete()

    return redirect("/panel/")

def login_registro(request):

    registro_form = RegistroForm()

    # REGISTRO

    if request.method == "POST":

        # REGISTRO

        if "registro" in request.POST:

            registro_form = RegistroForm(request.POST)

            if registro_form.is_valid():

                user = registro_form.save()

                PerfilUsuario.objects.create(
                usuario=user
                )

                login(request, user)

                return redirect('/index/')

        # LOGIN

        if "login" in request.POST:

            username = request.POST.get("username")

            password = request.POST.get("password")

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:

                login(request, user)

                # ADMIN

                if user.is_staff:

                    return redirect('/panel/')

                # USUARIO NORMAL

                return redirect('/index/')

    return render(request, 'motos/login.html', {

        'registro_form': registro_form

    })

def editar_moto(request, id):

    moto = get_object_or_404(Moto, id=id)

    if request.method == "POST":

        moto.marca = request.POST.get("marca")

        moto.linea = request.POST.get("linea")

        moto.modelo = request.POST.get("modelo")

        moto.precio = request.POST.get("precio")

        moto.cilindraje = request.POST.get("cilindraje")

        moto.kilometraje = request.POST.get("kilometraje")

        moto.descripcion = request.POST.get("descripcion")

        moto.estado = request.POST.get("estado")

        moto.soat = request.POST.get("soat")

        moto.tecnomecanica = request.POST.get("tecnomecanica")

        moto.transito = request.POST.get("transito")

        moto.placa = request.POST.get("placa")

        if request.FILES.get("imagen"):
            moto.imagen = request.FILES.get("imagen")

        moto.save()

        return redirect("/panel/")

    return render(request, "motos/editar.html", {
        "moto": moto
    })


def agregar_moto(request):

    if request.method == "POST":

        marca = request.POST.get("marca")

        linea = request.POST.get("linea")

        modelo = request.POST.get("modelo")

        precio = request.POST.get("precio")

        cilindraje = request.POST.get("cilindraje")

        kilometraje = request.POST.get("kilometraje")

        descripcion = request.POST.get("descripcion")

        imagenes = request.FILES.getlist("imagenes")

        estado = request.POST.get("estado")

        soat = request.POST.get("soat")

        tecnomecanica = request.POST.get("tecnomecanica")

        transito = request.POST.get("transito")

        placa = request.POST.get("placa")

        # CREAR MOTO
        moto = Moto.objects.create(

            marca=marca,

            linea=linea,

            modelo=modelo,

            precio=precio,

            cilindraje=cilindraje,

            kilometraje=kilometraje,

            descripcion=descripcion,

            imagen=imagenes[0],

            estado=estado,

            soat=soat,

            tecnomecanica=tecnomecanica,

            transito=transito,

            placa=placa,
        )

        # GUARDAR GALERIA
        for img in imagenes:

            ImagenMoto.objects.create(
                moto=moto,
                imagen=img
            )

        return redirect("/panel/")

    return render(request, "motos/agregar.html")


def solicitudes(request):

    solicitudes = Solicitud.objects.all().order_by("-id")

    paginator = Paginator(
        solicitudes,
        10
    )

    page = request.GET.get("page")

    solicitudes = paginator.get_page(page)

    contexto = {

        "solicitudes": solicitudes

    }

    return render(
        request,
        "motos/solicitudes.html",
        contexto
    )


def detalle_moto(request, id):

    moto = get_object_or_404(Moto, id=id)

    moto.vistas += 1

    moto.save()

    return render(request, 'motos/detalle_moto.html', {
        'moto': moto
    })

def aceptar_solicitud(request, id):

    solicitud = Solicitud.objects.get(id=id)

    solicitud.estado = "aceptada"

    solicitud.save()

    # 🔔 NOTIFICACIÓN

    if solicitud.usuario:

        Notificacion.objects.create(

            usuario=solicitud.usuario,

            mensaje=(

                f'Tu solicitud de la moto '

                f'{solicitud.marca} {solicitud.modelo} '

                f'fue aceptada ✅'

            )

        )

    return redirect("/solicitudes/")


def rechazar_solicitud(request, id):

    solicitud = Solicitud.objects.get(id=id)

    solicitud.estado = "rechazada"

    solicitud.save()

    # 🔔 NOTIFICACIÓN

    if solicitud.usuario:

        Notificacion.objects.create(

            usuario=solicitud.usuario,

            mensaje=(

                f'Tu solicitud de la moto '

                f'{solicitud.marca} {solicitud.modelo} '

                f'fue rechazada ❌'

            )

        )

    return redirect("/solicitudes/")


def cerrar_sesion(request):

    logout(request)

    return redirect('/index/')


@login_required
@login_required
def agregar_favorito(request, id):

    moto = Moto.objects.get(id=id)

    favorito = Favorito.objects.filter(
        usuario=request.user,
        moto=moto
    )

    if favorito.exists():

        favorito.delete()

    else:

        Favorito.objects.create(
            usuario=request.user,
            moto=moto
        )

    return redirect('/comprar/')

    moto = Moto.objects.get(id=id)

    existe = Favorito.objects.filter(
        usuario=request.user,
        moto=moto
    ).first()

    if not existe:

        Favorito.objects.create(
            usuario=request.user,
            moto=moto
        )

    return redirect('/comprar/')


@login_required
def favoritos(request):

    favoritos = Favorito.objects.filter(
        usuario=request.user
    )

    motos = [f.moto for f in favoritos]

    # 🔥 CLAVE PARA EL CORAZÓN
    favoritos_ids = [m.id for m in motos]

    return render(
        request,
        "motos/comprar.html",
        {
            'motos': motos,
            'favoritos_ids': favoritos_ids
        }
    )
@login_required
def mis_solicitudes(request):

    solicitudes = Solicitud.objects.filter(
        usuario=request.user
    ).order_by('-id')

    return render(
        request,
        "motos/mis_solicitudes.html",
        {
            'solicitudes': solicitudes
        }
    )



@login_required
def notificaciones(request):

    notificaciones = Notificacion.objects.filter(
        usuario=request.user
    ).order_by('-fecha')

    # 🔥 MARCAR COMO LEÍDAS
    notificaciones.update(leida=True)

    return render(
        request,
        "motos/notificaciones.html",
        {
            'notificaciones': notificaciones
        }
    )

@login_required
def toggle_favorito(request, id):

    moto = Moto.objects.get(id=id)

    favorito = Favorito.objects.filter(
        usuario=request.user,
        moto=moto
    ).first()

    if favorito:

        favorito.delete()

        return JsonResponse({
            'agregado': False
        })

    else:

        Favorito.objects.create(
            usuario=request.user,
            moto=moto
        )

        return JsonResponse({
            'agregado': True
        })
    
@login_required
def eliminar_favorito(request, id):

    favorito = Favorito.objects.filter(
        usuario=request.user,
        moto_id=id
    ).first()

    if favorito:
        favorito.delete()

    return redirect('/favoritos/')



def logout_view(request):

    logout(request)

    return redirect("/login/")  



def recuperar_password(request):

    if request.method == "POST":

        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "motos/recuperar.html", {
                "error": "Correo no registrado"
            })

        codigo = str(random.randint(100000, 999999))

        CodigoReset.objects.create(
            usuario=user,
            codigo=codigo
        )

        send_mail(

    "Recuperación de contraseña - UsadasBello",

    f"""
Hola {user.username},

Recibimos una solicitud para recuperar la contraseña de tu cuenta en UsadasBello.

Tu código de verificación es:

{codigo}

Ingresa este código en la aplicación para continuar con el proceso de recuperación.

Si no realizaste esta solicitud, puedes ignorar este correo de forma segura.

Atentamente,

Equipo de UsadasBello
Compra y Venta de Motocicletas
""",

    "usadasbello@gmail.com",

    [email],

)

        request.session["user_reset"] = user.id

        return render(request, "motos/index.html", {
        "mostrar_paso2": True,
        
        })

    return render(request, "motos/recuperar.html")


def verificar_codigo(request):

    if request.method == "POST":

        codigo = request.POST.get("codigo")
        user_id = request.session.get("user_reset")

        try:
            registro = CodigoReset.objects.filter(
                usuario_id=user_id,
                codigo=codigo
            ).latest('creado')
        except:
            return render(request, "motos/index.html", {
                "mostrar_paso2": True,
                "error_codigo": "Código incorrecto"
            })

        request.session["codigo_valido"] = True

        return render(request, "motos/index.html", {
            "mostrar_paso3": True
        })

    return redirect("/index/")


def nueva_password(request):

    if not request.session.get("codigo_valido"):
        return redirect("/index/")

    if request.method == "POST":

        password = request.POST.get("password")
    confirmar = request.POST.get("confirmar_password")

    if password != confirmar:

        return render(request, "motos/index.html", {
        "mostrar_paso3": True,
        "error_password": "Las contraseñas no coinciden"
    })
        user_id = request.session.get("user_reset")

        user = User.objects.get(id=user_id)
        user.set_password(password)
        user.save()

        request.session.flush()

        return render(request, "motos/index.html", {
            "mensaje": "Contraseña actualizada correctamente"
        })

    return redirect("/index/")



@login_required
def perfil(request):

    perfil, creado = PerfilUsuario.objects.get_or_create(
        usuario=request.user
    )

    if request.method == "POST":

        # DATOS USUARIO

        username = request.POST.get("username")

        email = request.POST.get("email")

        request.user.username = username

        request.user.email = email

        request.user.save()

        # PERFIL

        telefono = request.POST.get("telefono")

        perfil.telefono = telefono

        foto = request.FILES.get("foto")

        if foto:

            perfil.foto = foto

        perfil.save()

        # CONTRASEÑA

        password_actual = request.POST.get(
            "password_actual"
        )

        nueva_password = request.POST.get(
            "password_nueva"
        )

        error_password = None

        if password_actual and nueva_password:

            # VALIDAR PASSWORD ACTUAL

            if not request.user.check_password(
                password_actual
            ):

                error_password = (
                    "La contraseña actual es incorrecta"
                )

                return render(
                    request,
                    "motos/perfil.html",
                    {
                        "perfil": perfil,
                        "error_password": error_password
                    }
                )

            # VALIDAR MINIMO 8

            if len(nueva_password) < 8:

                error_password = (
                    "La nueva contraseña debe tener mínimo 8 caracteres"
                )

                return render(
                    request,
                    "motos/perfil.html",
                    {
                        "perfil": perfil,
                        "error_password": error_password
                    }
                )

            # CAMBIAR PASSWORD

            request.user.set_password(
                nueva_password
            )

            request.user.save()

            update_session_auth_hash(
                request,
                request.user
            )

        return redirect("/perfil/")

    return render(request, "motos/perfil.html", {

        "perfil": perfil

    })


@staff_member_required


def panel_motos(request):

    motos = Moto.objects.all().order_by("-id")

    paginator = Paginator(
        motos,
        10
    )

    page = request.GET.get("page")

    motos = paginator.get_page(page)

    return render(
        request,
        "motos/panel_motos.html",
        {
            "motos": motos
        }
    )



@staff_member_required
def exportar_dashboard_pdf(request):

    template = get_template(
        "motos/dashboard_pdf.html"
    )

    motos = Moto.objects.all()

    total_motos = Moto.objects.count()

    total_usuarios = User.objects.count()

    total_solicitudes = Solicitud.objects.count()

    total_vistas = sum(
        moto.vistas
        for moto in motos
    )

    ultimas_solicitudes = Solicitud.objects.order_by(
        "-fecha"
    )[:5]

        # GRAFICA TOP MOTOS

    top_motos = Moto.objects.order_by(
        "-vistas"
    )[:5]

    nombres = [
        moto.linea or moto.modelo
        for moto in top_motos
    ]

    vistas = [
        moto.vistas
        for moto in top_motos
    ]

    plt.figure(figsize=(6,3))

    plt.bar(
        nombres,
        vistas
    )

    plt.title(
        "Top motos"
    )

    buffer = BytesIO()

    plt.savefig(
        buffer,
        format='png',
        bbox_inches='tight'
    )

    buffer.seek(0)

    imagen_base64 = base64.b64encode(
        buffer.read()
    ).decode('utf-8')

    buffer.close()

    contexto = {

        "motos": motos,

        "total_motos": total_motos,

        "total_usuarios": total_usuarios,

        "total_solicitudes": total_solicitudes,

        "total_vistas": total_vistas,

        "grafica_top": imagen_base64,

        "ultimas_solicitudes":
        ultimas_solicitudes

    }

    html = template.render(contexto)

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = (
        'attachment; '
        'filename="dashboard.pdf"'
    )

    pisa.CreatePDF(

        html,

        dest=response

    )

    return response

@staff_member_required


def usuarios_admin(request):

    usuarios = User.objects.all().order_by("-id")

    paginator = Paginator(
        usuarios,
        10
    )

    page = request.GET.get("page")

    usuarios = paginator.get_page(page)

    return render(

        request,

        "motos/usuarios.html",

        {

            "usuarios": usuarios

        }

    )

def usuarios_admin(request):

    usuarios = User.objects.all().order_by("-id")

    paginator = Paginator(
        usuarios,
        10
    )

    page = request.GET.get("page")

    usuarios = paginator.get_page(page)

    return render(

        request,

        "motos/usuarios.html",

        {

            "usuarios": usuarios

        }

    )

@staff_member_required
def rendimiento(request):

    sistema = platform.system()

    version = platform.release()

    cpu_nombre = platform.processor()

    contexto = {

        "sistema": sistema,

        "version": version,

        "cpu_nombre": cpu_nombre

    }

    return render(

        request,

        "motos/rendimiento.html",

        contexto

    )

def api_rendimiento(request):

    cpu = psutil.cpu_percent()

    ram = psutil.virtual_memory()

    disco = psutil.disk_usage('/')

    return JsonResponse({

        "cpu": cpu,

        "ram": ram.percent,

        "ram_usada": round(
            ram.used / (1024**3),
            1
        ),

        "ram_total": round(
            ram.total / (1024**3),
            1
        ),

        "disco": disco.percent,

        "disco_usado": round(
            disco.used / (1024**3),
            1
        ),

        "disco_total": round(
            disco.total / (1024**3),
            1
        )

    })


@staff_member_required
def eliminar_usuario(request, id):

    usuario = User.objects.get(
        id=id
    )

    usuario.delete()

    return redirect(
        "/usuarios/"
    )

@staff_member_required
def editar_usuario(request, id):

    usuario = User.objects.get(id=id)

    perfil, creado = PerfilUsuario.objects.get_or_create(
    usuario=usuario
    )

  

    if request.method == "POST":

        usuario.username = request.POST.get(
            "username"
        )

        usuario.email = request.POST.get(
            "email"
        )

        perfil.telefono = request.POST.get(
            "telefono"
        )

        if "foto" in request.FILES:

            perfil.foto = request.FILES[
                "foto"
            ]

        usuario.save()

        perfil.save()

        return redirect(
            "/usuarios/"
        )

    return render(

        request,

        "motos/editar_usuario.html",

        {

            "usuario_obj": usuario,

            "perfil": perfil

        }

    )


@staff_member_required
def editar_interes(request):

    config, creado = Configuracion.objects.get_or_create(
        id=1
    )

    if request.method == "POST":

        config.interes_credito = request.POST.get(
            "interes"
        )

        config.save()

        return redirect(
            "/panel-motos/"
        )

    return render(

        request,

        "motos/editar_interes.html",

        {

            "config": config

        }

    )


def terminos(request):

    return render(
        request,
        "motos/terminos.html"
    )



def obtener_motos(request):

    motos = Moto.objects.all()

    datos = []

    for moto in motos:

        datos.append({

            "marca": moto.marca,
            "linea": moto.linea,
            "placa": moto.placa

        })

    return JsonResponse(datos, safe=False)