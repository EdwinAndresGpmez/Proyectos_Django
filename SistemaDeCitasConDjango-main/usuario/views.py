from django.shortcuts import render, redirect
from administrador import models as modelsAdministrador
from administrador import views as viewsAdministrador
from .forms import FormCitas
from entrarSistema import forms as formsEntrarSistema
from entrarSistema import models as modelsEntrarSistema
from .models import Citas
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

# Create your views here.


def inicio(request):
    # Si ya tiene sesión no le abre esta página
    user = request.user
    if not user.is_authenticated:
        return redirect('iniciarSesion')

    tipoRol = viewsAdministrador.TipoRol(request)

    if not tipoRol.es_usuario:
        return redirect('cerrar')
    else:

        if request.method == 'GET':

            formCitas = FormCitas()

            # lista_horas = Horas.objects.all()
            lista_horas = modelsAdministrador.Horas.objects.filter(
                horas_estado=True)
            lista_lugares = modelsAdministrador.Lugares.objects.filter(
                lugares_estado=True)
            lista_citas = Citas.objects.filter(
                id_usu=request.user.id, citas_estado=True).order_by('-id_cit')

            listaRoles = modelsEntrarSistema.UsuarioRoles.objects.filter(
                id_usu=request.user.id)

            return render(request, 'inicio.html', {
                'form': formCitas,

                'listaHoras': lista_horas,
                'listaLugares': lista_lugares,
                'listaCitas': lista_citas,
                'listaRoles': listaRoles
            })
        else:
            # formCitas = FormCitas()

            lista_horas = modelsAdministrador.Horas.objects.filter(
                horas_estado=True)
            lista_lugares = modelsAdministrador.Lugares.objects.filter(
                lugares_estado=True)
            lista_citas = Citas.objects.filter(
                id_usu=request.user.id, citas_estado=True)

            id_cita = Citas.objects.get(id_cit=request.POST['id_cit'])
            id_hora = modelsAdministrador.Horas.objects.get(
                id_hora=request.POST['id_hora'])
            id_lugar = modelsAdministrador.Lugares.objects.get(
                id_lugar=request.POST['id_lugar'])

            print(request.POST['id_pac'])

            if request.POST['id_pac'] == 'nada':
                pass
            else:
                id_pac = modelsAdministrador.Pacientes.objects.get(
                    id_pac=request.POST['id_pac'])
                id_cita.id_pac = id_pac
            id_cita.dia_cit = request.POST['dia_cit']
            id_cita.nota_cit = request.POST['nota_cit']
            id_cita.id_hora = id_hora
            id_cita.id_lugar = id_lugar

            id_cita.save()
            # Aqui ponemos el codigo del trigger -------

            Audi = modelsAdministrador.Auditoria(
                descripcion_aut=f"Se modificó una 'cita' en la tabla *Citas*, para el día {request.POST['dia_cit']}, modificado por el usuario: {request.user.id},")
            Audi.save()

            # fin de trigger ------
            return redirect('inicio')

        return render(request, 'inicio.html', {
            'form': formCitas,

            'listaHoras': lista_horas,
            'listaLugares': lista_lugares,
            'listaCitas': lista_citas,
        })


def deleteCita_historial(request, id_cit):
    user = request.user
    if not user.is_authenticated:
        return redirect('iniciarSesion')

    tipoRol = viewsAdministrador.TipoRol(request)

    if not tipoRol.es_usuario:
        return redirect('cerrar')
    else:
        idCita = Citas.objects.get(id_cit=id_cit)
        idCita.citas_estado = False
        idCita.save()

        # Aqui ponemos el codigo del trigger -------

        Audi = modelsAdministrador.Auditoria(
            descripcion_aut=f"Se eliminó una 'cita' en la tabla *Citas*, para el día {idCita.dia_cit} y con el id {id_cit}, eliminado por el usuario: {request.user.id},")
        Audi.save()

        # fin de trigger ------
        return redirect('inicio')

def cita(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('iniciarSesion')

    tipoRol = viewsAdministrador.TipoRol(request)
    if not tipoRol.es_usuario:
        return redirect('cerrar')

    fecha = request.GET.get("fecha")
    
    if request.method == 'GET':
        formCitas = FormCitas()

        # Obtener citas del día
        citas_dia = Citas.objects.filter(
            dia_cit=fecha,
            estado_cita__in=["Aceptada", "Sin confirmar", "Realizadas"],
            citas_estado=True
        )

        horas_ocupadas = citas_dia.values_list("id_hora_id", flat=True)
        lista_horas = modelsAdministrador.Horas.objects.filter(horas_estado=True).exclude(id_hora__in=horas_ocupadas)
        lista_lugares = modelsAdministrador.Lugares.objects.filter(lugares_estado=True)
        lista_pacientes = modelsAdministrador.Pacientes.objects.filter(
            pacientes_estado=True, tipo_usuario='Particular'
        )
        lista_profesionales = modelsAdministrador.Profesional.objects.filter(estado_prof=True)
        lista_servicios = modelsAdministrador.Servicio.objects.filter(servicio_estado=True)

        return render(request, 'citas.html', {
            'form': formCitas,
            'listaHoras': lista_horas,
            'listaLugares': lista_lugares,
            'listaPacientes': lista_pacientes,
            'listaServicios': lista_servicios,
            'listaProfesionales': lista_profesionales,
            'fecha': fecha
        })

    elif request.method == 'POST':
        formCitas = FormCitas(request.POST)
        
        print(request.POST)
        
        # Validar formulario
        if not formCitas.is_valid():
            return render(request, 'citas.html', {'form': formCitas})

        
        # Obtener el id_servicio, id_prof, y paciente_id desde el formulario
        id_servicio = formCitas.cleaned_data.get('id_servicio')
        id_prof = formCitas.cleaned_data.get('id_prof')
        paciente_id = formCitas.cleaned_data.get('id_pac')
        id_lugar = formCitas.cleaned_data.get('id_lugar') 
        id_usuario = formCitas.cleaned_data.get('id_usu') 
        print(f"request.user: {request.user}")
        print(f"request.user.id: {request.user.paciente_id}")

        # Validación de servicio y profesional
        if not id_servicio or not id_prof:
            error = "Servicio o profesional no seleccionados"
            return render(request, 'citas.html', {'error': error, 'form': formCitas})

        try:
            if isinstance(id_usuario, int):
                instance_User = modelsEntrarSistema.CrearCuenta.objects.get(id=id_usuario)
            else:  # Si ya tienes el objeto Servicio, solo asigna
                instance_User = id_usuario  # id_servicio ya es un objeto Servicio
            
            instance_Hora = modelsAdministrador.Horas.objects.get(id_hora=request.POST['id_hora'])

            if isinstance(id_servicio, int):  # Verifica que id_servicio sea un identificador numérico
                instance_Servicio = modelsAdministrador.Servicio.objects.get(id_servicio=id_servicio)
            else:  # Si ya tienes el objeto Servicio, solo asigna
                instance_Servicio = id_servicio  # id_servicio ya es un objeto Servicio

            if isinstance(id_prof, int):  # Verifica que id_prof sea un identificador numérico
                instance_Profesional = modelsAdministrador.Profesional.objects.get(id_prof=id_prof)
            else:  # Si ya tienes el objeto Profesional, solo asigna
                instance_Profesional = id_prof  # id_prof ya es un objeto Profesional

            if isinstance(id_lugar, int):  # Verifica que id_lugar sea un identificador numérico
                instance_Lugar = modelsAdministrador.Lugares.objects.get(id_lugar=id_lugar)
            else:  # Si ya tienes el objeto Lugar, solo asigna
                instance_Lugar = id_lugar  # id_lugar ya es un objeto Lugar
                
            if isinstance(paciente_id, int):
                instance_paciente = modelsEntrarSistema.CrearCuenta.objects.get(id=paciente_id)
            else: 
                 instance_paciente = paciente_id


            print(f"Usuario: {instance_User}")
            print(f"Hora: {instance_Hora}")
            print(f"Servicio: {instance_Servicio}")
            print(f"Profesional: {instance_Profesional}")
            print(f"Lugar: {instance_Lugar}")

        except ObjectDoesNotExist as e:
            error = f"Datos inválidos: {str(e)}"
            return render(request, 'citas.html', {'error': error, 'form': formCitas})

        # Crear cita sin paciente (si no se selecciona uno)
        if paciente_id:  # Solo se asigna paciente si se ha seleccionado
            try:
                id_cita = Citas(
                    id_usu=instance_User,
                    id_lugar=instance_Lugar,
                    id_hora=instance_Hora,
                    id_pac=instance_paciente,
                    id_servicio=instance_Servicio,
                    id_prof=instance_Profesional,
                    dia_cit=formCitas.cleaned_data['dia_cit'],
                    nota_cit=formCitas.cleaned_data['nota_cit'],
                    estado_cita='Sin confirmar'
                )
            except modelsAdministrador.Pacientes.DoesNotExist:
                error = "Paciente inválido"
                return render(request, 'citas.html', {'error': error, 'form': formCitas})
        else:
            id_cita = Citas(
                id_usu=instance_User,
                id_lugar=instance_Lugar,
                id_hora=instance_Hora,
                id_pac=instance_paciente,
                id_servicio=instance_Servicio,
                id_prof=instance_Profesional,
                dia_cit=formCitas.cleaned_data['dia_cit'],
                nota_cit=formCitas.cleaned_data['nota_cit'],
                estado_cita='Sin confirmar'
            )

        # Guardar la cita
        id_cita.save()

        # Mostrar un mensaje de éxito
        messages.success(request, "¡Cita solicitada exitosamente!")

        return redirect('cita')  # Redirigir a otra página o a la misma página
    
    
def get_lugares(request):
    id_servicio = request.GET.get('id_servicio')
    print(f"ID del servicio recibido: {id_servicio}")

    if id_servicio:
        try:
            # Filtrar lugares a través de los profesionales asociados al servicio
            lugares = modelsAdministrador.Lugares.objects.filter(
                profesionales__servicios__id_servicio=id_servicio,
                lugares_estado=True
            ).distinct()

            print(f"Lugares encontrados: {[lugar.nombre_lugar for lugar in lugares]}")
        except Exception as e:
            print(f"Error al realizar la consulta: {e}")
            lugares = []

        # Construir la respuesta en formato JSON
        data = [{'id_lugar': lugar.id_lugar, 'nombre_lugar': lugar.nombre_lugar} for lugar in lugares]
    else:
        print("No se proporcionó un ID de servicio")
        data = []

    return JsonResponse(data, safe=False)

def get_profesionales(request):
    id_servicio = request.GET.get('id_servicio')
    
    # Filtrar profesionales asociados al servicio con el estado activo
    profesionales = modelsAdministrador.Profesional.objects.filter(
        servicios__id_servicio=id_servicio,  # Usar la relación ManyToMany
        estado_prof=True  # Verificar que el profesional esté activo
    )
    
    # Construir la respuesta
    data = [{'id_prof': p.id_prof, 'nombre_prof': p.nombre_prof} for p in profesionales]
    
    return JsonResponse(data, safe=False)

def get_horas(request):
    id_prof = request.GET.get('id_prof')  # ID del profesional
    dia_cit = request.GET.get('dia_cit')  # Fecha seleccionada

    print(f"ID del profesional recibido: {id_prof}")  # Debug: Verificar ID del profesional
    print(f"Fecha seleccionada recibida: {dia_cit}")   # Debug: Verificar fecha seleccionada

    try:
        # Validar si el profesional está activo
        profesional = modelsAdministrador.Profesional.objects.get(id_prof=id_prof, estado_prof=True)
        print(f"Profesional encontrado: {profesional}")  # Debug: Profesional encontrado

        # Convertir la fecha de string a objeto de fecha
        fecha = parse_date(dia_cit)
        print(f"Fecha convertida: {fecha}")  # Debug: Fecha convertida

        if not fecha:
            print("Error: Fecha inválida")  # Debug: Fecha inválida
            return JsonResponse({'error': 'Fecha inválida'}, status=400)

        # Filtrar las horas ocupadas por citas existentes con las condiciones dadas
        horas_ocupadas = Citas.objects.filter(
            id_prof=profesional,
            dia_cit=fecha,
            citas_estado=True,
            estado_cita__in=["Aceptada", "Sin confirmar", "Realizadas"]
        ).values_list('id_hora', flat=True)

        print(f"Horas ocupadas: {horas_ocupadas}")  # Debug: Lista de horas ocupadas

        # Filtrar las horas disponibles
        horas_disponibles = modelsAdministrador.Horas.objects.filter(
            id_prof=profesional,
            horas_estado=True,          # Solo horas activas
            fecha_habilitada=fecha      # Solo para la fecha seleccionada
        ).exclude(id_hora__in=horas_ocupadas)

        print(f"Horas disponibles: {horas_disponibles}")  # Debug: Lista de horas disponibles

        # Construir la respuesta con el rango de horas
        data = [
            {
                'id_hora': h.id_hora,
                'rango_horas': f"{h.inicio_hora.strftime('%H:%M')} a {h.final_hora.strftime('%H:%M')}"
            }
            for h in horas_disponibles
        ]
        print(f"Respuesta construida: {data}")  # Debug: Respuesta final
    except modelsAdministrador.Profesional.DoesNotExist:
        # Si no existe el profesional o no está activo, devolver lista vacía
        print("Profesional no encontrado o no activo")  # Debug: Profesional no encontrado o inactivo
        data = []

    return JsonResponse(data, safe=False)



def historial(request):

    # Si ya tiene sesión no le abre esta página
    user = request.user
    if not user.is_authenticated:
        # HttpResponse('<script>alert("funcionó");</script>')
        return redirect('iniciarSesion')

    tipoRol = viewsAdministrador.TipoRol(request)

    if not tipoRol.es_usuario:
        return redirect('cerrar')
    else:

        if request.method == 'GET':

            lista_citas = modelsAdministrador.Consultorio.objects.filter(
                id_cit__id_usu=request.user.id, id_cit__citas_estado=True)

            return render(request, 'historial.html', {
                'listaCitas': lista_citas,
            })


def configuracion(request):

    # Si ya tiene sesión no le abre esta página
    user = request.user
    if not user.is_authenticated:
        # HttpResponse('<script>alert("funcionó");</script>')
        return redirect('iniciarSesion')

    tipoRol = viewsAdministrador.TipoRol(request)

    if not tipoRol.es_usuario:
        return redirect('cerrar')
    else:
        form = formsEntrarSistema.FormRegistrar()
        if request.method == 'GET':
            form = formsEntrarSistema.FormRegistrar()
            return render(request, 'configuracion.html', {
                'form': form
            })
        else:

            idUser = modelsEntrarSistema.CrearCuenta.objects.get(
                id=request.user.id)

            if 'btnUsuario' in request.POST:

                if modelsEntrarSistema.CrearCuenta.objects.filter(username=request.POST['username']).exists():
                    HttpResponse(
                        "<script>alert('Ya existe ese usuario')</script>")

                    return render(request, 'configuracion.html', {
                        'form': form
                    })
                else:
                    idUser.username = request.POST['username']
                    idUser.save()

                    # Aqui ponemos el codigo del trigger -------

                    Audi = modelsAdministrador.Auditoria(
                        descripcion_aut=f"Se modifico una 'cuenta' en la tabla *CrearCuenta*, se cambio el usuario por {request.POST['username']}.")
                    Audi.save()

                    # fin de trigger ------

                    return render(request, 'configuracion.html', {
                        'form': form
                    })

            elif 'btnCedula' in request.POST:
                if modelsEntrarSistema.CrearCuenta.objects.filter(cedula=request.POST['cedula']).exists():
                    HttpResponse(
                        "<script>alert('Ya se ha registrado esta cédula')</script>")

                    return render(request, 'configuracion.html', {
                        'form': form
                    })
                else:
                    idUser.cedula = request.POST['cedula']
                    idUser.save()
                    # Aqui ponemos el codigo del trigger -------

                    Audi = modelsAdministrador.Auditoria(
                        descripcion_aut=f"Se modifico una 'cuenta' en la tabla *CrearCuenta*, se cambio la cedula, del usuario {request.user.id} .")
                    Audi.save()

                    # fin de trigger ------

                    return render(request, 'configuracion.html', {
                        'form': form
                    })

            elif 'btnTelefono' in request.POST:

                if not request.POST['numero']:
                    HttpResponse(
                        "<script>alert('Tiene que escribir un número telefónico')</script>")

                    return render(request, 'configuracion.html', {
                        'form': form
                    })
                else:
                    idUser.numero = request.POST['numero']
                    idUser.save()

                    # Aqui ponemos el codigo del trigger -------

                    Audi = modelsAdministrador.Auditoria(
                        descripcion_aut=f"Se modifico una 'cuenta' en la tabla *CrearCuenta*, se cambio el numero de teléfono, del usuario {request.user.id} .")
                    Audi.save()

                    # fin de trigger ------

                    return render(request, 'configuracion.html', {
                        'form': form
                    })

            elif 'btnCorreo' in request.POST:

                if modelsEntrarSistema.CrearCuenta.objects.filter(correo=request.POST['correo']).exists():
                    HttpResponse(
                        "<script>alert('Ya existe este correo')</script>")

                    return render(request, 'configuracion.html', {
                        'form': form
                    })
                else:
                    idUser.correo = request.POST['correo']
                    idUser.save()
                    print(idUser.save())

                    # Aqui ponemos el codigo del trigger -------

                    Audi = modelsAdministrador.Auditoria(
                        descripcion_aut=f"Se modifico una 'cuenta' en la tabla *CrearCuenta*, se cambio el correo electrónico por {request.user.id}.")
                    Audi.save()

                    # fin de trigger ------

                    return render(request, 'configuracion.html', {
                        'form': form
                    })

            elif 'btnContrasenna' in request.POST:

                if not request.POST['password1'] == request.POST['password2']:
                    HttpResponse(
                        "<script>alert('Las contraseñas deben ser iguales')</script>")

                    return render(request, 'configuracion.html', {
                        'form': form
                    })
                else:
                    idUser.set_password(request.POST['password1'])
                    idUser.save()
                    # Aqui ponemos el codigo del trigger -------

                    Audi = modelsAdministrador.Auditoria(
                        descripcion_aut=f"Se modifico una 'cuenta' en la tabla *CrearCuenta*, se cambio la contraseña por {request.user.id}.")
                    Audi.save()

                    # fin de trigger ------

                    return render(request, 'configuracion.html', {
                        'form': form
                    })

            elif 'btnAll' in request.POST:
                if modelsEntrarSistema.CrearCuenta.objects.filter(correo=request.POST['correo']).exists() or modelsEntrarSistema.CrearCuenta.objects.filter(username=request.POST['username']).exists() or modelsEntrarSistema.CrearCuenta.objects.filter(cedula=request.POST['cedula']).exists():
                    HttpResponse(
                        "<script>alert('Los datos suministrados ya existen en el sistema, elija otros por favor.')</script>")
                    return render(request, 'configuracion.html', {
                        'form': form
                    })
                else:
                    if request.POST['password1'] == request.POST['password2']:

                        idUser.username = request.POST['username']
                        idUser.cedula = request.POST['cedula']
                        idUser.numero = request.POST['numero']
                        idUser.correo = request.POST['correo']
                        idUser.set_password(request.POST['password1'])
                        idUser.save()

                        # Aqui ponemos el codigo del trigger -------

                        Audi = modelsAdministrador.Auditoria(
                            descripcion_aut=f"Se modifico una 'cuenta' en la tabla *CrearCuenta*, se cambio todos los datos por {request.user.id}.")
                        Audi.save()

                        # fin de trigger ------

                        return render(request, 'configuracion.html', {
                            'form': form
                        })

                    else:
                        HttpResponse(
                            "<script>alert('Las contraseñas deben ser iguales')</script>")
                        return render(request, 'configuracion.html', {
                            'form': form
                        })

        return render(request, 'configuracion.html', {
            'form': form
        })


