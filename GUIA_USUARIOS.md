# Guía de Usuarios — Sistema INSCRIB

**Escuela José Manuel Cova Maza**  
Plataforma web: https://inscrib-admin.onrender.com

Esta guía explica, paso a paso, cómo usar el panel administrativo de INSCRIB.
También está disponible **dentro del panel**: menú **Guía de Uso** (en la barra izquierda).

---

## 1. Acceso al sistema

1. Abra el navegador y entre a: **https://inscrib-admin.onrender.com**
2. Inicie sesión con su **usuario** y **contraseña**.
3. Si olvidó la contraseña del panel, use **“¿Olvidó su contraseña?”** en el login (solo administradores; requiere SMTP configurado).
4. Al entrar, verá el **Inicio** (panel con estadísticas).

> Consejo: si la pantalla se ve vieja o desactualizada, presione **Ctrl + F5** (o Ctrl + Shift + R) para recargar sin caché.

---

## 2. Menú principal (barra izquierda)

| Opción | Para qué sirve |
|--------|----------------|
| **Inicio** | Panel de control: totales, gráficas y últimos accesos. |
| **Estudiantes** | Registrar y listar estudiantes. |
| **Representante** | Registrar y listar representantes (padres/tutores). |
| **Plantilla Inscripción** | Crear y ver planillas de inscripción. |
| **Matrícula** | Matrícula activa, nuevos ingresos y **retiros**. |
| **Gestión de Año** | Abrir/cerrar el año escolar. |
| **Usuario** | Crear y editar usuarios del sistema. |
| **Configurar Sitio Web** | Noticias, galería, mensajes del sitio público. |
| **Reportes PDF** | Descargar listados en PDF. |
| **Guía de Uso** | Esta misma guía, dentro del panel. |
| **Salir del Sistema** | Cerrar sesión. |

---

## 3. Estudiantes

### 3.1 Registrar Estudiante (1.° opción del menú)

1. Menú **Estudiantes → Registrar Estudiante**.
2. Complete los datos obligatorios:
   - **Nº Cédula Escolar (C.E.)**
   - Nombres y apellidos
   - Fecha de nacimiento, lugar, etc.
3. Pulse **Guardar** y confirme.

> **Nota:** los campos de **teléfono/SMS** y **correo electrónico** están ocultos a propósito en este formulario (no se usan en el registro del estudiante).

### 3.2 Listado General (2.° opción del menú)

1. Menú **Estudiantes → Listado General**.
2. Aquí puede **buscar** estudiantes y ver el listado completo.

> La opción **“Consulta Individual”** fue **eliminada** del menú. Use el listado para localizar al estudiante.

---

## 4. Representantes

1. Menú **Representante → Registrar Representante** para dar de alta al padre/madre/tutor.
2. Menú **Representante → Listado General** para verlos o buscarlos.

Igual que en estudiantes, **Consulta Individual** ya no aparece en el menú.

---

## 5. Plantillas de inscripción

### 5.1 Nueva Plantilla

1. Menú **Plantilla Inscripción → Nueva Plantilla**.
2. Busque al estudiante por **cédula**.
3. Seleccione el **grado**.
4. Indique la cédula del **representante**.
5. Pulse **Guardar**.

**Si el estudiante ya tiene una planilla en el año escolar activo:**

- El sistema lo **avisa** en pantalla.
- Puede abrir la **planilla existente** con un enlace.
- Si intenta guardar de nuevo, recibirá un mensaje y se abrirá la planilla que ya existe (no se duplica).

### 5.2 Plantillas Guardadas

1. Menú **Plantilla Inscripción → Plantillas Guardadas**.
2. Cada ficha muestra grado, fecha y lapso.
3. Botón **VER PLANILLA**: descarga/abre el **PDF** de esa inscripción.

---

## 6. Matrícula y retiros

1. Menú **Matrícula**.
2. Pestañas:
   - **Matrícula Total**: todos los inscritos del año escolar activo (por grado). Puede **Modificar** o **Retirar**.
   - **Nuevos Ingresos**: solo inscritos nuevos.
   - **Retiros**: historial de retiros (fecha, lapso, motivo).

### Procesar un retiro

1. En **Matrícula Total**, localice al estudiante.
2. Pulse **Retirar**.
3. Complete **fecha**, **lapso** y **motivo**.
4. Confirme. El estudiante pasará a la pestaña **Retiros**.

> Los retiros **solo** se gestionan en **Matrícula → Retiros** (y desde el botón Retirar de la matrícula). En el **Inicio** ya no se muestra el contador de retiros.

---

## 7. Inicio (panel)

Tarjetas de resumen:

- Estudiantes registrados  
- Representantes registrados  
- Matrícula activa  
- Usuarios del sistema  

Gráficas: matrícula por grado, inscripciones por mes, usuarios por rol.  
Tabla: últimos accesos al sistema.

> **Mensajes sin leer** y **Retiros** ya **no** aparecen en el Inicio (simplificado a petición).

---

## 8. Reportes PDF

1. Menú **Reportes PDF**.
2. Elija el reporte:
   - Listado general de estudiantes  
   - Matrícula activa  
   - Representantes  
   - Usuarios  
   - Estadístico general  
3. Se descarga un **PDF** con:

   - **Encabezado verde institucional** (Escuela José Manuel Cova Maza)  
   - Título del reporte y fecha/hora de generación  
   - **Línea de resumen** (totales del reporte)  
   - Tablas con bandas alternas, acentos correctos y columnas legibles  
   - Texto largo recortado con “…” para que no se desborde  
   - Tablas que **continúan en varias hojas** si hace falta  
   - **Pie de página** en cada hoja: *INSCRIB · Página X de Y*  

También puede descargar la **planilla** individual desde **Plantillas Guardadas → VER PLANILLA** (formato ficha con datos del estudiante, representante y grado).

> El PDF se genera en el servidor sin dependencias externas (evita errores 502 en Render).

---

## 9. Usuarios del sistema

1. Menú **Usuario**.
2. **Nuevo usuario**: nombre, usuario, contraseña, rol (admin, director, secretario, coordinador, docente).
3. **Editar**: puede cambiar nombre completo y rol; la contraseña es opcional al editar.

---

## 10. Configurar sitio web (público)

Menú **Configurar Sitio Web**:

- **Configuración** general del sitio  
- **Noticias** (con imagen)  
- **Programas**  
- **Galería**  
- **Mensajes** recibidos del formulario de contacto  

Las imágenes subidas se guardan de forma que **sobreviven al reinicio** del servidor (van en la base de datos).

---

## 11. Gestión de año escolar

Menú **Gestión de Año**:

1. Cree un año (ej. `2025-2026`) y márquelo **ACTIVO**.
2. Solo puede haber **un** año activo a la vez.
3. Las inscripciones y matrículas se asocian al año escolar activo; los estudiantes se listan y reportan por grado.

> **Nota:** el sistema **no envía correos a representantes ni padres** (ni de bienvenida, ni de inscripción, ni de retiros). La opción **Enviar Correo** fue retirada del menú.

---

## 12. Preguntas frecuentes

**¿No descarga el PDF?**  
Verifique que inició sesión y que no haya error 502; recargue con Ctrl+F5. Si persiste, contacte al administrador del servidor.

**¿No se ve una imagen nueva?**  
Recargue con Ctrl+F5. Las imágenes nuevas se guardan en la base de datos.

**¿Se cerró la sesión sola?**  
Vuelva a entrar; por seguridad la sesión expira.

**¿Aparece “año escolar activo”?**  
Vaya a **Gestión de Año** y active el año en curso.

**¿Puedo duplicar una planilla?**  
No. Si el estudiante ya tiene planilla en el año escolar activo, el sistema lo avisa y muestra la existente.

---

## 13. Cierre de sesión

Menú **Salir del Sistema → Confirmar**.  
Si usa una computadora compartida, **siempre** cierre la sesión.

---

## 14. Qué se guarda en el sistema

Casi todo lo que usted **escribe y registra** se guarda en la base de datos del servidor:

| Lo que registra | ¿Se guarda? |
|-----------------|-------------|
| Estudiantes, representantes, planillas | **Sí** |
| Matrícula y retiros (fecha, lapso, motivo) | **Sí** |
| Usuarios y roles | **Sí** |
| Noticias, galería, imágenes, mensajes de contacto | **Sí** (imágenes en la BD) |
| Año escolar, grados y configuración del sitio | **Sí** |
| Búsquedas/filtros en pantalla | No (solo visual) |
| SMS/correo al registrar estudiante | No (campo oculto) |

Si pulsa **Guardar**, el dato queda en la BD y se ve en listados, reportes PDF y el sitio público. El sistema **no envía correos** a representantes ni padres.

Esta misma guía está **dentro del panel**: menú **Guía de Uso**.

---

*Guía del Sistema INSCRIB — versión de presentación. Actualizada para el rediseño de menús, PDFs y simplificación del panel.*
