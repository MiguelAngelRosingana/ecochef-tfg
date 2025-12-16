from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
from deep_translator import GoogleTranslator
import socket

# --- PARCHE PARA ARREGLAR CONEXIÓN EN WINDOWS ---
# Guarda la función original para evitar recursión infinita
_original_getaddrinfo = socket.getaddrinfo

def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    # Fuerza el uso de IPv4 usando la función original
    return _original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

socket.getaddrinfo = getaddrinfo_ipv4
# ------------------------------------------------

app = Flask(__name__)

print("--- 🚀 INICIANDO ECOCHEF (VERSIÓN FINAL TFG) ---")

# --- 1. CONFIGURACIÓN ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nevera.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- 2. MODELOS (TABLAS DE LA BASE DE DATOS) ---

# Tabla 1: Ingredientes de la Nevera
class Ingrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

# Tabla 2: Lista de la Compra
class ItemCompra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    comprado = db.Column(db.Boolean, default=False)

# Crear las tablas automáticamente
with app.app_context():
    db.create_all()
    print("--- ✅ BASE DE DATOS ACTUALIZADA ---")

# --- 3. RUTAS Y CONTROLADORES ---

# PORTADA (Con datos para el gráfico)
@app.route('/')
def home():
    # Contamos datos para el gráfico de estadísticas
    total_nevera = Ingrediente.query.count()
    total_lista = ItemCompra.query.count()
    return render_template('index.html', n_nevera=total_nevera, n_lista=total_lista)

# --- SECCIÓN NEVERA ---
@app.route('/nevera', methods=['GET', 'POST'])
def nevera():
    if request.method == 'POST':
        nuevo_ingrediente = request.form.get('nombre_ingrediente')
        if nuevo_ingrediente:
            nuevo_item = Ingrediente(nombre=nuevo_ingrediente)
            db.session.add(nuevo_item)
            db.session.commit()
        return redirect(url_for('nevera'))
    
    todos_los_ingredientes = Ingrediente.query.all()
    return render_template('nevera.html', ingredientes=todos_los_ingredientes)

@app.route('/nevera/borrar/<int:id>')
def borrar_nevera(id):
    item = Ingrediente.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('nevera'))

# --- SECCIÓN RECETAS (EL CEREBRO DE LA APP) ---
@app.route('/recetas')
def recetas():
    print("--- 🔍 BUSCANDO RECETAS (SPOONACULAR + TRADUCCIÓN) ---")
    
    # ⚠️ ¡IMPORTANTE! Pega aquí tu clave de Spoonacular
    API_KEY = "bd7c4b4baf7b4dfe8bd8c3fe6bc8632e"
    
    # 1. Recuperamos TODOS los ingredientes
    todos_ingredientes = Ingrediente.query.all()
    
    if not todos_ingredientes:
        return render_template('recetas.html', platos=[], ingrediente="Nada (Nevera Vacía)")

    # Creamos lista: ["Tomate", "Huevos"] -> "Tomate, Huevos"
    lista_nombres_es = [item.nombre for item in todos_ingredientes]
    texto_ingredientes_es = ", ".join(lista_nombres_es)
    texto_ingredientes_en = texto_ingredientes_es 
    
    # 2. TRADUCCIÓN DE ENTRADA (Español -> Inglés)
    try:
        traductor_en = GoogleTranslator(source='auto', target='en')
        texto_ingredientes_en = traductor_en.translate(texto_ingredientes_es)
        print(f"   ✅ Ingredientes traducidos: {texto_ingredientes_en}")
    except:
        print("   ⚠️ Fallo traducción entrada, usando original")

    lista_platos = []
    
    # 3. LLAMADA A LA API (Spoonacular)
    url = f"https://api.spoonacular.com/recipes/findByIngredients"
    parametros = {
        'ingredients': texto_ingredientes_en,
        'number': 6,            # Traemos 6 recetas
        'ranking': 1,           # Priorizar usar más ingredientes
        'ignorePantry': 'true', # Ignorar sal, agua, aceite...
        'apiKey': API_KEY
    }
    
    try:
        respuesta = requests.get(url, params=parametros, timeout=5)
        
        if respuesta.status_code == 200:
            lista_platos = respuesta.json()
            
            # --- 4. TRADUCCIÓN DE SALIDA (Inglés -> Español) ---
            print("   🔄 Procesando recetas...")
            traductor_es = GoogleTranslator(source='en', target='es')
            
            for plato in lista_platos:
                # A) Traducir Título
                try:
                    titulo_en = plato.get('title')
                    plato['title'] = traductor_es.translate(titulo_en)
                except:
                    pass
                
                # B) Traducir Ingredientes Faltantes
                faltan_texto = ""
                if plato.get('missedIngredientCount', 0) > 0:
                    try:
                        lista_faltantes = [ing['name'] for ing in plato['missedIngredients']]
                        faltantes_en = ", ".join(lista_faltantes)
                        faltan_texto = traductor_es.translate(faltantes_en)
                    except:
                        faltan_texto = "Ingredientes varios"
                
                plato['texto_faltantes'] = faltan_texto

            print("   ✅ Recetas listas.")

        elif respuesta.status_code == 402:
            print("⚠️ Error: Cuota API agotada.")
        else:
            print(f"⚠️ Error API: {respuesta.status_code}")
            
    except Exception as e:
        print(f"⚠️ ERROR DE CONEXIÓN: {e}")
    
    # 5. MODO OFFLINE (PLAN B)
    if not lista_platos:
        print("   ❌ Usando modo OFFLINE (Fotos locales).")
        lista_platos = [
            {
                "title": "Tortilla de Patatas (Offline)",
                "image": "/static/img/tortilla.jpg",
                "texto_faltantes": "", # Tienes todo
                "id": "1"
            },
            {
                "title": "Pollo Asado (Offline)",
                "image": "/static/img/pollo.jpg",
                "texto_faltantes": "Limón, Ajo",
                "id": "2"
            },
             {
                "title": "Ensalada César (Offline)",
                "image": "/static/img/ensalada.jpg",
                "texto_faltantes": "Salsa César, Picatostes",
                "id": "3"
            }
        ]

    # Pasamos "Tu Nevera" como texto fijo para el título
    return render_template('recetas.html', platos=lista_platos, ingrediente="Tu Nevera")

# --- SECCIÓN LISTA DE COMPRA ---
@app.route('/lista')
def lista_compra():
    items = ItemCompra.query.all()
    return render_template('lista.html', items=items)

@app.route('/lista/agregar', methods=['POST'])
def agregar_lista():
    producto = request.form.get('producto')
    if producto:
        nuevo_item = ItemCompra(nombre=producto)
        db.session.add(nuevo_item)
        db.session.commit()
    return redirect(url_for('lista_compra'))

@app.route('/lista/borrar/<int:id>')
def borrar_lista(id):
    item = ItemCompra.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('lista_compra'))

# --- 4. ARRANQUE DEL SERVIDOR ---
if __name__ == '__main__':
    print("--- 🌍 SERVIDOR LISTO EN: http://127.0.0.1:5001 ---")
    app.run(debug=True, port=5001)