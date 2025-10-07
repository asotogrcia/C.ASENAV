## 🚢 Sistema de Mantención ASENAV

Proyecto desarrollado como parte del **Proyecto Integrado** del Técnico Analista Programador.  
El sistema permite gestionar mantenciones, agendar trabajos, registrar uso de repuestos y mantener control de stock dentro de la empresa **ASENAV**.

---

## 🧠 Tecnologías utilizadas

- **Python 3.12**
- **Django 5.2.7**
- **PostgreSQL**
- **HTML, CSS, JavaScript**
- **Bootstrap**
- **Virtualenv**

---

## 🚀 Instrucciones de levantamiento (modo desarrollo)

### 1️⃣ Clonar el repositorio
---
- git clone https://github.com/asotogrcia/C.ASENAV.git
- cd C.ASENAV/ASENAV
---

### 2️⃣ Crear entorno virtual
python -m venv ../ASENAV-venv

### 3️⃣ Activar entorno virtual
../ASENAV-venv/Scripts/activate


### 4️⃣ Instalar dependencias
pip install -r requirements.txt


### 5️⃣ Configurar variables de entorno
Crea un archivo .env dentro de la carpeta ASENAV/ con el siguiente contenido (ajustando tus credenciales):

SECRET_KEY= **TU CLAVE SECRETA DJANGO**
DEBUG=True
DB_NAME= **TU BASE DE DATOS**
DB_USER= **TU USUARIO**
DB_PASSWORD= **TU CONTRASEÑA**
DB_HOST=localhost **HOST POR DEFECTO**
DB_PORT=5432 **PUERTO POR DEFECTO**

### 6️⃣ Aplicar migraciones
python manage.py makemigrations
python manage.py migrate


### 7️⃣ Crear superusuario
python manage.py createsuperuser


### 8️⃣ Ejecutar servidor local
python manage.py runserver
**Luego abre "http://localhost:8000"**


## 🌿 Flujo de trabajo en ramas

### ✅ Main Branch
main → rama principal (versión estable)

### 💻 Develop Branch
develop → rama de desarrollo (donde se integran nuevas funciones)

### 🛠️ Features Branch
feature/ → ramas individuales para nuevas funcionalidades
    - Ejemplo: feature/registro-mantenciones

### 🔩 Fix Branch
fix/ → ramas para corregir errores específicos
    - Ejemplo: fix/reporte-pdf


### 🧩 Colaboradores

|       Nombres         |          Rol           |Usuario GitHub|
|-----------------------|------------------------|--------------|
|      Augusto Soto     | Analista / Fullstack   | @asotogrcia  |
|   Gustavo Huequemán   | Analista / Fullstack   |  @gahg0301   |
|     Felipe Badilla    | Analista / Fullstack   | @pendiente   |