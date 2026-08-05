# MANUAL DE USUARIO - INSCRIB SYSTEM

## Sistema de Gestion de Inscripciones y Administracion Escolar

**U.E. Dr. Jose Manuel Cova Maza**
**Puerto Ordaz, Estado Bolivar, Venezuela**

---

## Tabla de Contenidos

1. [Descripcion General](#1-descripcion-general)
2. [Como Acceder](#2-como-acceder)
3. [Credenciales por Defecto](#3-credenciales-por-defecto)
4. [Panel Administrativo](#4-panel-administrativo)
5. [Sitio Web Publico](#5-sitio-web-publico)
6. [Portal del Representante](#6-portal-del-representante)
7. [Preguntas Frecuentes (FAQ)](#7-preguntas-frecuentes-faq)
8. [Solucion de Problemas](#8-solucion-de-problemas)
9. [Soporte y Contacto](#9-soporte-y-contacto)

---

## 1. Descripcion General

**INSCRIB SYSTEM** es un sistema web de gestion de inscripciones y administracion escolar desarrollado para la U.E. Dr. Jose Manuel Cova Maza. El sistema permite:

- **Gestionar inscripciones y matriculas escolares** de forma digital
- **Administrar estudiantes y representantes** con trazabilidad total
- **Publicar informacion institucional** en un sitio web publico
- **Generar documentos** (constancias, certificados) con plantillas
- **Registrar actividades** en un log de auditoria para garantizar integridad

El sistema reemplaza el metodo manual de hojas de calculo, permitiendo un control en tiempo real con seguridad reforzada (hash de contrasenas, proteccion HTTP, limitacion de peticiones).

### Componentes del Sistema

| Componente | Descripcion |
|------------|-------------|
| **Panel Administrativo** | Gestion de estudiantes, representantes, matriculas, usuarios, ano escolar y sitio web |
| **Sitio Web Publico** | Portal institucional con noticias, programas, galeria, contacto y requisitos de inscripcion |
| **Portal del Representante** | Registro y consulta de representantes y sus estudiantes asociados |

---

## 2. Como Acceder

### 2.1 Acceso Online (Produccion)

| Servicio | URL |
|----------|-----|
| **Sistema completo** | https://web-production-d4f80.up.railway.app |

Desde esta URL podras acceder tanto al panel administrativo como al sitio web publico.

### 2.2 Acceso Local (Desarrollo)

Si ejecutas el sistema en tu computadora:

| Servicio | URL |
|----------|-----|
| **Panel Administrativo** | http://localhost:5001 |
| **Sitio Web Publico** | http://localhost:5002 |

Para iniciar localmente, ejecuta en la terminal:

`ash
# Panel administrativo
python app_admin_prod.py

# Sitio web publico (en otra terminal)
python app_public.py
`

### 2.3 Requisitos del Navegador

- Google Chrome, Mozilla Firefox, Microsoft Edge o Safari (versiones recientes)
- Conexion a internet (para acceso online)
- Resolucion de pantalla recomendada: 1024x768 o superior
- El sitio es **responsivo** y funciona en dispositivos moviles

---

## 3. Credenciales por Defecto

| Campo | Usuario | Contrasena |
|-------|---------|------------|
| **Administrador** | dmin | dmin123 |
| **Secretario** | secretario | secretario123 |

> **IMPORTANTE**: Cambiar estas credenciales despues del primer inicio de sesion para garantizar la seguridad del sistema.

---

## 4. Panel Administrativo

El panel administrativo es la seccion principal para el personal autorizado. Se accede desde la URL /login.

### 4.1 Iniciar Sesion

1. Navega a la URL del panel administrativo
2. Ingresa tu **usuario** y **contrasena**
3. Haz clic en **"Iniciar Sesion"**
4. Seras redirigido al **Dashboard** principal

### 4.2 Dashboard (Panel Principal)

El Dashboard muestra un resumen general del sistema:
- Total de estudiantes registrados
- Total de representantes
- Inscripciones activas por ano escolar
- Accesos rapidos a los modulos principales

### 4.3 Modulo: Gestion de Usuarios

Administra las cuentas de acceso al sistema.

**Funcionalidades:**
- **Listar usuarios**: Ve todos los usuarios registrados
- **Crear usuario**: Registra un nuevo usuario con rol (admin o secretario)
- **Editar usuario**: Modifica datos de un usuario existente
- **Cambiar contrasena**: Actualiza la contrasena de un usuario
- **Eliminar/Desactivar usuario**: Elimina o desactiva una cuenta

**Pasos para crear un usuario:**
1. Ve a **Usuarios** - **Nuevo Usuario**
2. Completa los campos: nombre, usuario, contrasena, rol
3. Selecciona el rol: **Administrador** o **Secretario**
4. Haz clic en **"Guardar"**

### 4.4 Modulo: Ano Escolar

Gestiona los periodos escolares del sistema.

**Funcionalidades:**
- **Listar anos escolares**: Ve todos los periodos registrados
- **Crear ano escolar**: Registra un nuevo periodo (ej: 2026-2027)
- **Activar ano escolar**: Marca un periodo como activo (solo uno puede estar activo)
- **Editar ano escolar**: Modifica los datos de un periodo

**Nota**: El sistema viene precargado con el Ano Escolar **2025-2026** como ACTIVO.

### 4.5 Modulo: Estudiantes

Registra y administra la informacion de los estudiantes.

**Funcionalidades:**
- **Listar estudiantes**: Ve todos los estudiantes con filtros por ano escolar y grado
- **Crear estudiante**: Registra un nuevo estudiante con sus datos personales
- **Ver detalle**: Consulta el expediente completo de un estudiante
- **Editar estudiante**: Modifica los datos de un estudiante
- **Eliminar estudiante**: Elimina un registro de estudiante

**Datos requeridos para un estudiante:**
- Nombres y apellidos
- Cedula de identidad (si aplica)
- Fecha de nacimiento
- Sexo
- Ano escolar y grado
- Representante asociado

### 4.6 Modulo: Representantes

Registra y administra los representantes legales de los estudiantes.

**Funcionalidades:**
- **Listar representantes**: Ve todos los representantes registrados
- **Crear representante**: Registra un nuevo representante
- **Ver detalle**: Consulta los estudiantes asociados a un representante
- **Editar representante**: Modifica los datos de un representante
- **Eliminar representante**: Elimina un registro de representante

**Asociacion Representante-Estudiante:**
Un representante puede tener multiples estudiantes asociados a traves de la tabla "Familiar". Esta relacion se establece al registrar o editar un estudiante.

### 4.7 Modulo: Matricula / Inscripcion

Gestiona la inscripcion de estudiantes a grados en un ano escolar.

**Funcionalidades:**
- **Listar inscripciones**: Ve todas las inscripciones por ano escolar
- **Crear inscripcion**: Registra una nueva matricula
- **Ver detalle**: Consulta el detalle de una inscripcion
- **Editar inscripcion**: Modifica el estado o datos de una inscripcion

**Campos de control de inscripcion:**
- **Estado**: Activa, Retirada, Pendiente
- **Fecha de retiro**: Fecha en que el estudiante se retiro (si aplica)
- **Lapso de registro**: Periodo en que se realizo la inscripcion
- **Motivo de retiro**: Razon del retiro (si aplica)

### 4.8 Modulo: Plantillas de Documentos

Genera documentos institucionales oficiales.

**Funcionalidades:**
- **Generar documento**: Selecciona una plantilla y genera un documento Word (.docx)
- **Tipos de documentos**: Constancias, certificados, cartas, etc.

**Pasos para generar un documento:**
1. Ve a **Documentos** - **Generar Documento**
2. Selecciona el tipo de plantilla
3. Completa los campos requeridos
4. Haz clic en **"Generar"**
5. Se descargara el documento en formato Word

### 4.9 Modulo: Administracion del Sitio Web

Gestiona el contenido del sitio web publico institucional.

**Submodulos:**

#### 4.9.1 Noticias
- **Crear noticia**: Publica una nueva noticia institucional
- **Editar noticia**: Modifica el contenido de una noticia existente
- **Eliminar noticia**: Elimina una noticia

#### 4.9.2 Programas Academicos
- **Crear programa**: Registra un programa educativo (Inicial, Primaria, Media, etc.)
- **Editar programa**: Modifica la informacion de un programa
- **Eliminar programa**: Elimina un programa

#### 4.9.3 Galeria de Imagenes
- **Subir imagen**: Agrega nuevas imagenes a la galeria institucional
- **Eliminar imagen**: Remueve una imagen de la galeria

#### 4.9.4 Configuracion del Sitio
- **Editar configuracion**: Modifica datos generales del sitio (nombre, direccion, telefono, etc.)
- **SiteConfig**: Configuracion global del sitio web publico

### 4.10 Modulo: Seguridad y Auditoria

Control de acceso y registro de actividades.

**Funcionalidades:**
- **Log de Auditoria (REGISTRO_AUDITORIA)**: Ve el registro cronologico de actividades criticas del sistema
- **Filtros**: Busca por usuario, fecha, tipo de actividad
- **Trazabilidad**: Cada accion importante queda registrada con fecha, hora y usuario

### 4.11 Cerrar Sesion

Haz clic en **"Cerrar Sesion"** o **"Logout"** en el menu superior para salir del panel administrativo.

---

## 5. Sitio Web Publico

El sitio web publico es la presencia institucional en internet, accesible para cualquier visitante.

### 5.1 Paginas del Sitio

| Pagina | URL | Descripcion |
|--------|-----|-------------|
| **Inicio** | / | Pagina principal con informacion destacada |
| **Nosotros** | /nosotros/ | Resena historica y mision/vision de la institucion |
| **Programas** | /programas/ | Programas academicos ofrecidos (Inicial, Primaria, Media, Especial, Docente) |
| **Noticias** | /noticias/ | Ultimas noticias y publicaciones institucionales |
| **Galeria** | /galeria/ | Galeria de imagenes de la institucion |
| **Contacto** | /contacto/ | Formulario de contacto y datos de ubicacion |
| **Requisitos de Inscripcion** | /requisitos/ | Documentos y requisitos para inscribir a un estudiante |
| **Portal del Representante** | /portal/ | Acceso al portal para representantes |

### 5.2 Navegacion

- Usa el **menu superior** para navegar entre las paginas
- En dispositivos moviles, el menu se convierte en un icono de **hamburguesa**
- El sitio es **completamente responsivo** y se adapta a cualquier tamano de pantalla

### 5.3 Formulario de Contacto

1. Ve a la pagina de **Contacto**
2. Completa: nombre, correo electronico, asunto y mensaje
3. Haz clic en **"Enviar"**
4. Recibiras una confirmacion de envio

---

## 6. Portal del Representante

El Portal del Representante permite a los padres y representantes legales registrarse y consultar informacion de sus hijos.

### 6.1 Acceso al Portal

1. Navega a la pagina principal del sitio web publico
2. Haz clic en **"Portal del Representante"** o accede directamente a /portal/
3. Si es tu primera vez, haz clic en **"Registrarse"**
4. Si ya tienes cuenta, inicia sesion con tu correo y contrasena

### 6.2 Registro de Representante

**Campos requeridos:**
- Nombres y apellidos
- Cedula de identidad
- Correo electronico (sera tu usuario)
- Contrasena
- Telefono de contacto
- Direccion

**Pasos:**
1. Completa todos los campos del formulario
2. Haz clic en **"Registrarse"**
3. Tu cuenta sera creada y podras iniciar sesion

### 6.3 Iniciar Sesion en el Portal

1. Ingresa tu **correo electronico** y **contrasena**
2. Haz clic en **"Iniciar Sesion"**
3. Seras redirigido a tu **perfil** con la informacion de tus hijos

### 6.4 Funcionalidades del Portal

#### 6.4.1 Ver Perfil
- Consulta tus datos personales registrados
- Verifica la informacion de contacto

#### 6.4.2 Consultar Estudiantes Asociados
- Ve la lista de tus hijos/hijas registrados en el sistema
- Consulta el grado, ano escolar y estado de inscripcion de cada uno

#### 6.4.3 Cambiar Contrasena
1. Ve a **Perfil** - **Cambiar Contrasena**
2. Ingresa la contrasena actual
3. Ingresa la nueva contrasena (minimo 6 caracteres)
4. Confirma la nueva contrasena
5. Haz clic en **"Guardar"**

### 6.5 Cerrar Sesion del Portal

Haz clic en **"Cerrar Sesion"** para salir del portal.

---

## 7. Preguntas Frecuentes (FAQ)

### P: Cual es la URL del sistema?
**R:** El sistema esta disponible en linea en: https://web-production-d4f80.up.railway.app

### P: Como accedo al panel administrativo?
**R:** Navega a la URL del sistema y haz clic en "Iniciar Sesion" o accede a /login.

### P: Cuales son las credenciales por defecto?
**R:**
- Administrador: dmin / dmin123
- Secretario: secretario / secretario123

> **IMPORTANTE**: Cambia estas credenciales despues del primer inicio de sesion.

### P: Puedo crear mas usuarios?
**R:** Si, desde el panel administrativo en **Usuarios** - **Nuevo Usuario**. Solo los administradores pueden crear nuevos usuarios.

### P: Como registro un nuevo estudiante?
**R:** Ve a **Estudiantes** - **Nuevo Estudiante**, completa los datos y asocia un representante.

### P: Como inscribo a un estudiante en un grado?
**R:** Ve a **Inscripciones** - **Nueva Inscripcion**, selecciona el estudiante, ano escolar y grado.

### P: Como publico una noticia en el sitio web?
**R:** Desde el panel administrativo, ve a **Sitio Web** - **Noticias** - **Nueva Noticia**.

### P: Puedo acceder desde el celular?
**R:** Si, el sitio web es completamente responsivo y funciona en dispositivos moviles. Tambien es una PWA instalable.

### P: Como genero documentos (constancias, certificados)?
**R:** Ve a **Documentos** - **Generar Documento**, selecciona la plantilla y completa los campos.

### P: Que es el registro de auditoria?
**R:** Es un log que registra todas las actividades criticas del sistema (creaciones, ediciones, eliminaciones) con fecha, hora y usuario. Se encuentra en **Auditoria**.

### P: Como cambio el ano escolar activo?
**R:** Ve a **Ano Escolar**, selecciona el periodo deseado y haz clic en **"Activar"**.

### P: Olvide mi contrasena, que hago?
**R:** Contacta al administrador del sistema para que restablezca tu contrasena desde **Usuarios** - **Cambiar Contrasena**.

### P: El sistema esta seguro?
**R:** Si. El sistema utiliza: hash de contrasenas (bcrypt), cabeceras de seguridad (Flask-Talisman), proteccion contra fuerza bruta (Flask-Limiter) y registro de auditoria.

### P: Puedo instalar el sistema en mi telefono?
**R:** Si. El sitio web es una PWA (Aplicacion Web Progresiva). En tu navegador movil, busca la opcion "Agregar a pantalla de inicio" para instalarlo como una app.

---

## 8. Solucion de Problemas

### No puedo iniciar sesion
- Verifica que este usando las credenciales correctas
- Si olvidaste tu contrasena, contacta al administrador
- Si el sistema esta en linea, verifica tu conexion a internet

### El sitio se carga lento
- Verifica tu conexion a internet
- Intenta recargar la pagina (F5 o Ctrl+R)
- Limpia la cache del navegador

### No puedo subir imagenes en la galeria
- Verifica que el formato sea JPG, PNG o GIF
- El tamano maximo recomendado es 5 MB
- Si el problema persiste, contacta al administrador

### Los datos no se guardan
- Verifica que todos los campos obligatorios esten completos
- Si el sistema esta en linea, verifica tu conexion
- Intenta recargar la pagina y volver a intentar

### Error al generar documentos
- Verifica que el navegador permita descargas
- Desactiva temporalmente el bloqueador de pop-ups
- Intenta con otro navegador

### El panel administrativo no carga
- Verifica la URL: https://web-production-d4f80.up.railway.app
- Si es local, verifica que los servidores esten corriendo (puertos 5001 y 5002)
- Revisa los logs de errores en la carpeta del proyecto

---

## 9. Soporte y Contacto

### Informacion del Proyecto

| Campo | Valor |
|-------|-------|
| **Nombre del Sistema** | INSCRIB SYSTEM |
| **Institucion** | U.E. Dr. Jose Manuel Cova Maza |
| **Ubicacion** | Puerto Ordaz, Estado Bolivar, Venezuela |
| **URL Produccion** | https://web-production-d4f80.up.railway.app |
| **Desarrollador** | Marcelo Fernando Campos Anacona |
| **Tutor Industrial** | Sol Liliana Romero Gil |
| **Tutor Academico** | Ing. Yalitza Guevara |
| **Periodo** | Junio - Agosto 2026 |

### Credenciales por Defecto

| Usuario | Contrasena |
|---------|------------|
| admin | admin123 |
| secretario | secretario123 |

### Tecnologias

- Backend: Flask 3.1.1 (Python 3.13)
- Base de Datos: SQLite / SQLAlchemy 2.0
- Seguridad: Flask-Talisman, Flask-Limiter, bcrypt
- Frontend: HTML5, CSS3, JavaScript, Font Awesome
- PWA: manifest.json, sw.js
- Despliegue: Railway

---

*Manual de usuario generado para el sistema INSCRIB SYSTEM - U.E. Dr. Jose Manuel Cova Maza*
*Ultima actualizacion: Agosto 2026*