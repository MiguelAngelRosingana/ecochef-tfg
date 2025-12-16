# 🥬 EcoChef - Smart Zero Waste Kitchen

**EcoChef** es una aplicación web inteligente desarrollada como Trabajo de Fin de Grado (TFG) para reducir el desperdicio alimentario doméstico. 

La aplicación permite gestionar el inventario de la nevera y utiliza algoritmos de **Inteligencia Artificial** (vía API Spoonacular) para sugerir recetas basadas exclusivamente en los ingredientes disponibles.

## 🚀 Funcionalidades Clave

* **Gestión de Inventario (CRUD):** Base de datos SQLite para añadir y eliminar ingredientes.
* **Smart Chef Engine:**
    * Conexión a la API **Spoonacular** para búsqueda avanzada.
    * **Doble Traducción Automática:** Motor de traducción integrado (Español $\leftrightarrow$ Inglés) para permitir consultas en lenguaje natural.
    * **Detección de Faltantes:** Algoritmo que identifica y alerta sobre ingredientes necesarios para completar una receta.
* **Modo Offline (Resiliencia):** Sistema de respaldo local que asegura la funcionalidad incluso sin conexión a internet.
* **Dashboard Visual:** Gráficos interactivos (Chart.js) para el control de stock.
* **Lista de la Compra:** Gestión integrada para reposición de alimentos.

## 🛠️ Stack Tecnológico

* **Backend:** Python 3, Flask.
* **Base de Datos:** SQLAlchemy (SQLite).
* **Frontend:** HTML5, Jinja2, Bootstrap 5, CSS3 (Custom Properties).
* **APIs & Librerías:** Spoonacular API, Deep-Translator, Chart.js.

## 🔧 Instalación y Despliegue

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/ecochef.git](https://github.com/tu-usuario/ecochef.git)