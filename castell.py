import streamlit as st
from collections import Counter
import requests
import os
import platform
from datetime import datetime

# Importaciones para impresión térmica
try:
    from escpos.printer import Usb, Serial, Network, File
    from escpos.exceptions import USBNotFoundError, SerialException
    ESCPOS_AVAILABLE = True
except ImportError:
    ESCPOS_AVAILABLE = False

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Pedidos whatsapp",
    page_icon="🍕",
    layout="centered",
    initial_sidebar_state="collapsed",
)




# --- DATOS DEL MENÚ ---
MENU = {
    "Pizzas Tradicionales": {
        "Margherita (Personal 25cm)": 6.50,
        "Margherita (Mediana 33cm)": 10.00,
        "Margherita (Familiar 40cm)": 13.00,
        "Jamón (Personal 25cm)": 7.50,
        "Jamón (Mediana 33cm)": 11.50,
        "Jamón (Familiar 40cm)": 15.00,
        "Tocineta y Maíz (Personal 25cm)": 9.00,
        "Tocineta y Maíz (Mediana 33cm)": 13.50,
        "Tocineta y Maíz (Familiar 40cm)": 18.00,
        "4 Estaciones (Personal 25cm)": 11.50,
        "4 Estaciones (Mediana 33cm)": 17.00,
        "4 Estaciones (Familiar 40cm)": 23.00,
    },
    "Pizzas Especiales": {
        "Di Abruzzo (Personal 25cm)": 9.50,
        "Di Abruzzo (Mediana 33cm)": 13.00,
        "Di Abruzzo (Familiar 40cm)": 19.00,
        "Castell 1 (Personal 25cm)": 12.50,
        "Castell 1 (Mediana 33cm)": 18.50,
        "Castell 1 (Familiar 40cm)": 25.00,
        "Castell 2 (Personal 25cm)": 13.50,
        "Castell 2 (Mediana 33cm)": 19.50,
        "Castell 2 (Familiar 40cm)": 27.00,
    },
    "Otros Platos": {
        "Pizza Multicereal (Personal 25cm)": 13.50,
        "Pizza Multicereal (Mediana 33cm)": 19.50,
        "Pizza Multicereal (Familiar 40cm)": 27.00,
        "Pizza Dolce Nocciola (20cm)": 7.00,
        "Pizza Dolce Pistacchio (20cm)": 10.00,
        "Calzone (Comer aquí)": 6.00,
        "Calzone (Para llevar)": 6.50,
        "Pasticho Tradicional (Comer aquí)": 9.00,
        "Pasticho Tradicional (Para llevar)": 9.50,
        "Pasticho Berenjena/Platano/Zucchini (Comer aquí)": 9.00,
        "Pasticho Berenjena/Platano/Zucchini (Para llevar)": 9.50,
    },
    "Ingredientes Tradicionales (Pizza)": {
        "Jamón Adicional (Personal)": 1.00, "Jamón Adicional (Mediana)": 1.50, "Jamón Adicional (Familiar)": 2.00,
        "Queso Adicional (Personal)": 1.00, "Queso Adicional (Mediana)": 1.50, "Queso Adicional (Familiar)": 2.00,
        "Maíz Adicional (Personal)": 1.00, "Maíz Adicional (Mediana)": 1.50, "Maíz Adicional (Familiar)": 2.00,
        "Piña Adicional (Personal)": 1.00, "Piña Adicional (Mediana)": 1.50, "Piña Adicional (Familiar)": 2.00,
        "Cebolla Adicional (Personal)": 1.00, "Cebolla Adicional (Mediana)": 1.50, "Cebolla Adicional (Familiar)": 2.00,
        "Pimentón Adicional (Personal)": 1.00, "Pimentón Adicional (Mediana)": 1.50, "Pimentón Adicional (Familiar)": 2.00,
        "Tomate en Ruedas Adicional (Personal)": 1.00, "Tomate en Ruedas Adicional (Mediana)": 1.50, "Tomate en Ruedas Adicional (Familiar)": 2.00,
    },
    "Ingredientes Premium (Pizza)": {
        "Salami Adicional (Personal)": 1.50, "Salami Adicional (Mediana)": 2.00, "Salami Adicional (Familiar)": 3.00,
        "Aceitunas Negras Adicional (Personal)": 1.50, "Aceitunas Negras Adicional (Mediana)": 2.00, "Aceitunas Negras Adicional (Familiar)": 3.00,
        "Tocineta Adicional (Personal)": 1.50, "Tocineta Adicional (Mediana)": 2.00, "Tocineta Adicional (Familiar)": 3.00,
        "Pepperoni Adicional (Personal)": 1.50, "Pepperoni Adicional (Mediana)": 2.00, "Pepperoni Adicional (Familiar)": 3.00,
        "Champiñones Adicional (Personal)": 1.50, "Champiñones Adicional (Mediana)": 2.00, "Champiñones Adicional (Familiar)": 3.00,
        "Borde de Queso Adicional (Personal)": 1.50, "Borde de Queso Adicional (Mediana)": 2.00, "Borde de Queso Adicional (Familiar)": 3.00,
        "Tomate Seco Adicional (Personal)": 1.50, "Tomate Seco Adicional (Mediana)": 2.00, "Tomate Seco Adicional (Familiar)": 3.00,
        "Anchoas Adicional (Personal)": 1.50, "Anchoas Adicional (Mediana)": 2.00, "Anchoas Adicional (Familiar)": 3.00,
        "Pesto Genovés Adicional (Personal)": 1.50, "Pesto Genovés Adicional (Mediana)": 2.00, "Pesto Genovés Adicional (Familiar)": 3.00,
        "Pesto Rosso Adicional (Personal)": 1.50, "Pesto Rosso Adicional (Mediana)": 2.00, "Pesto Rosso Adicional (Familiar)": 3.00,
        "Rúcula Adicional (Personal)": 1.50, "Rúcula Adicional (Mediana)": 2.00, "Rúcula Adicional (Familiar)": 3.00,
        
    },
    "Adicionales Calzone y Empaques": {
        "Tocineta (Calzone)": 1.00, "Salami (Calzone)": 1.00, "Aceitunas Negras (Calzone)": 1.00,
        "Aceitunas Verdes (Calzone)": 1.00, "Champiñones (Calzone)": 1.00, "Maíz (Calzone)": 1.00,
        "Pepperoni (Calzone)": 1.00, "Anchoas (Calzone)": 1.00, "Cebolla (Calzone)": 1.00,
        "Pimentón (Calzone)": 1.00, "Piña (Calzone)": 1.00, "Caja para llevar (25cm)": 0.70,
        "Caja para llevar (33cm)": 0.90, "Caja para llevar (40cm)": 1.00,
    },
    "Bebidas": {
        "Refresco 1.5lts": 2.50,
        "Refresco 335ml": 1.50,
        "Refresco de Lata": 2.00,
        "Té Verde (tomar aquí)": 3.00,
        "Té Verde (Para llevar)": 3.80,
        "Té Negro (tomar aqui)": 3.00,
        "Té Negro (Para llevar)": 3.80,
        "Flor de Jamaica (Tomar aquí)": 3.00,
        "Flor de Jamaica (Para llevar)": 3.80,
        "Té Matcha (Tomar aquí)": 4.00,
        "Agua Pequeña (330ml)": 0.5,
        "Agua Mediana (600ml)": 1,
        "Té Matcha (Para llevar)": 4.80,
    }
}

# Categorías donde al tocar una pizza se abre el flujo rápido (extras mismo tamaño)
PIZZA_QUICK_ADD_CATEGORIES = ("Pizzas Tradicionales", "Pizzas Especiales")

# Pestañas del menú (móvil): agrupa categorías para menos scroll
MENU_TAB_GROUPS = [
    ("🍕 Pizzas", ["Pizzas Tradicionales", "Pizzas Especiales"]),
    ("🍝 Otros", ["Otros Platos"]),
    (
        "➕ Extras y bebidas",
        [
            "Ingredientes Tradicionales (Pizza)",
            "Ingredientes Premium (Pizza)",
            "Adicionales Calzone y Empaques",
            "Bebidas",
        ],
    ),
]

# --- INICIALIZACIÓN DEL ESTADO DE LA SESIÓN ---
if 'order' not in st.session_state:
    st.session_state.order = Counter()
if 'show_multicereal_modal' not in st.session_state:
    st.session_state.show_multicereal_modal = False
if 'selected_ingredients' not in st.session_state:
    st.session_state.selected_ingredients = []
if 'show_4estaciones_modal' not in st.session_state:
    st.session_state.show_4estaciones_modal = False
if 'selected_estaciones_ingredients' not in st.session_state:
    st.session_state.selected_estaciones_ingredients = []
if 'customer_name' not in st.session_state:
    st.session_state.customer_name = ""
if 'order_type' not in st.session_state:
    st.session_state.order_type = "Para comer aquí"
if 'pending_pizza' not in st.session_state:
    st.session_state.pending_pizza = None
if 'pending_extra_counts' not in st.session_state:
    st.session_state.pending_extra_counts = {}


# --- FUNCIONES PARA API DEL DÓLAR ---
@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_dollar_rate():
    """Obtiene la tasa oficial del dólar BCV de Venezuela usando múltiples APIs como respaldo."""
    apis = [
        {
            'name': 'VenezolanosEnElMundo',
            'url': 'https://api.venezuelanoselmundo.com/v1/exchange/bcv',
            'parser': lambda data: data.get('USD', {}).get('rate', 0)
        },
        {
            'name': 'ExchangeRate-API Venezuela',
            'url': 'https://api.exchangerate-api.com/v4/latest/USD',
            'parser': lambda data: data.get('rates', {}).get('VES', 0)
        },
        {
            'name': 'DolarToday',
            'url': 'https://s3.amazonaws.com/dolartoday/data.json',
            'parser': lambda data: data.get('USD', {}).get('bcv', 0)
        },
        {
            'name': 'Monitor Dolar Venezuela',
            'url': 'https://api.monitordolarvzla.com/api/v1/monitor',
            'parser': lambda data: data.get('bcv', 0)
        },
        {
            'name': 'LocalBitcoins VES',
            'url': 'https://localbitcoins.com/bitcoinaverage/ticker-all-currencies/',
            'parser': lambda data: data.get('VES', {}).get('avg_24h', 0) / 100000 if data.get('VES') else 0
        }
    ]
    
    for api in apis:
        try:
            response = requests.get(api['url'], timeout=10)
            response.raise_for_status()
            data = response.json()
            rate = api['parser'](data)
            if rate > 0:
                return rate, f"{api['name']} (BCV)"
        except Exception as e:
            continue  # Silencioso para no mostrar muchos errores
    
    # Si todas las APIs fallan, usar valor por defecto actualizado
    st.error("⚠️ No se pudo conectar con las APIs del BCV. Usando valor por defecto.")
    return 36.50, "Valor por defecto BCV"  # Valor aproximado actual

def get_bcv_rate_direct():
    """Intenta obtener la tasa directamente de fuentes oficiales del BCV."""
    try:
        # API más confiable para Venezuela
        response = requests.get('https://pydolarvenezuela.org/api/v1/dollar?page=bcv', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'price' in data:
                return float(data['price']), "PyDolarVenezuela (BCV Oficial)"
    except:
        pass
    
    try:
        # Otra fuente confiable
        response = requests.get('https://api.yadio.io/exrates/VES', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'USD' in data:
                return data['USD'], "Yadio (BCV)"
    except:
        pass
    
    return None, None

def format_currency(amount, show_usd=True):
    """Formatea el precio en bolívares venezolanos y opcionalmente en USD."""
    if 'dollar_rate' not in st.session_state:
        # Primero intentar fuentes directas del BCV
        rate, source = get_bcv_rate_direct()
        if rate:
            st.session_state.dollar_rate, st.session_state.api_source = rate, source
        else:
            st.session_state.dollar_rate, st.session_state.api_source = get_dollar_rate()
    
    bs_amount = amount * st.session_state.dollar_rate
    if show_usd:
        return f"${amount:.2f} USD (Bs. {bs_amount:,.2f})"
    else:
        return f"Bs. {bs_amount:,.2f}"

# --- FUNCIONES DE BÚSQUEDA ---
def filter_menu_items(menu, search_term):
    """Filtra los elementos del menú basándose en el término de búsqueda."""
    if not search_term:
        return menu
    
    search_term = search_term.lower().strip()
    filtered_menu = {}
    
    for category, items in menu.items():
        filtered_items = {}
        for item_name, price in items.items():
            item_lower = item_name.lower()
            
            # Buscar coincidencias más inteligentes
            search_words = search_term.split()
            matches = True
            
            for word in search_words:
                # Buscar cada palabra del término de búsqueda
                if word not in item_lower:
                    matches = False
                    break
            
            if matches:
                filtered_items[item_name] = price
        
        # Solo incluir la categoría si tiene items que coinciden
        if filtered_items:
            filtered_menu[category] = filtered_items
    
    return filtered_menu

def get_search_results_count(menu, search_term):
    """Cuenta cuántos resultados hay para el término de búsqueda."""
    if not search_term:
        return sum(len(items) for items in menu.values())
    
    filtered_menu = filter_menu_items(menu, search_term)
    return sum(len(items) for items in filtered_menu.values())

# --- INGREDIENTES PARA MULTICEREAL ---
MULTICEREAL_INGREDIENTS = [
    "Jamón", "Queso Extra", "Maíz", "Piña", "Cebolla", "Pimentón", 
    "Tomate en Ruedas", "Salami", "Aceitunas Negras", "Tocineta", 
    "Pepperoni", "Champiñones", "Tomate Seco", "Anchoas", "Pesto Genovés", 
    "Pesto Rosso", "Rúcula"
]

# --- INGREDIENTES PARA 4 ESTACIONES ---
ESTACIONES_INGREDIENTS = [
    "Jamón", "Queso Extra", "Maíz", "Piña", "Cebolla", "Pimentón", 
    "Tomate en Ruedas", "Salami", "Aceitunas Negras", "Tocineta", 
    "Pepperoni", "Champiñones", "Tomate Seco", "Anchoas", "Aceitunas Verdes",
    "Pesto Genovés", "Pesto Rosso", "Rúcula"
]

def show_multicereal_modal():
    """Muestra el modal para seleccionar ingredientes de la multicereal."""
    if not st.session_state.get('show_multicereal_modal', False):
        return
    
    # Crear el modal con estilo destacado
    st.markdown("""
    <div style="
        background-color: #f0f8ff;
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    ">
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.subheader(f"🌾 Selecciona 2 ingredientes para tu {st.session_state.multicereal_item}")
        st.info("💡 Los ingredientes están incluidos en el precio de la pizza multicereal")
        
        selected_count = len(st.session_state.get('selected_ingredients', []))
        
        # Mostrar progreso
        progress_text = f"Ingredientes seleccionados: {selected_count}/2"
        st.progress(min(selected_count / 2.0, 1.0))
        if selected_count == 0:
            st.warning(f"⚠️ {progress_text}")
        elif selected_count == 1:
            st.info(f"ℹ️ {progress_text}")
        else:
            st.success(f"✅ {progress_text}")
        
        # Dos columnas: mejor en pantallas pequeñas
        cols = st.columns(2)
        
        for i, ingredient in enumerate(MULTICEREAL_INGREDIENTS):
            with cols[i % 2]:
                is_selected = ingredient in st.session_state.get('selected_ingredients', [])
                
                # Deshabilitar si ya se seleccionaron 2 y este no está seleccionado
                disabled = selected_count >= 2 and not is_selected
                
                # Crear checkbox con emoji
                emoji_map = {
                    "Jamón": "🍖", "Queso Extra": "🧀", "Maíz": "🌽", "Piña": "🍍",
                    "Cebolla": "🧅", "Pimentón": "🫑", "Tomate en Ruedas": "🍅", "Salami": "🥩",
                    "Aceitunas Negras": "🫒", "Tocineta": "🥓", "Pepperoni": "🍕", "Champiñones": "🍄",
                    "Tomate Seco": "🍅", "Anchoas": "🐟", "Pesto Genovés": "🌿", "Pesto Rosso": "🌶️", "Rúcula": "🥬"
                }
                
                ingredient_display = f"{emoji_map.get(ingredient, '🔸')} {ingredient}"
                
                if st.checkbox(
                    ingredient_display, 
                    value=is_selected, 
                    key=f"ingredient_{ingredient}",
                    disabled=disabled
                ):
                    if ingredient not in st.session_state.selected_ingredients:
                        if len(st.session_state.selected_ingredients) < 2:
                            st.session_state.selected_ingredients.append(ingredient)
                else:
                    if ingredient in st.session_state.selected_ingredients:
                        st.session_state.selected_ingredients.remove(ingredient)
        
        # Mostrar ingredientes seleccionados
        if st.session_state.selected_ingredients:
            ingredients_with_emojis = []
            emoji_map = {
                "Jamón": "🍖", "Queso Extra": "🧀", "Maíz": "🌽", "Piña": "🍍",
                "Cebolla": "🧅", "Pimentón": "🫑", "Tomate en Ruedas": "🍅", "Salami": "🥩",
                "Aceitunas Negras": "🫒", "Tocineta": "🥓", "Pepperoni": "🍕", "Champiñones": "🍄",
                "Tomate Seco": "🍅", "Anchoas": "🐟", "Pesto Genovés": "🌿", "Pesto Rosso": "🌶️", "Rúcula": "🥬"
            }
            
            for ing in st.session_state.selected_ingredients:
                ingredients_with_emojis.append(f"{emoji_map.get(ing, '🔸')} {ing}")
            
            st.markdown(f"**Tus ingredientes:** {' + '.join(ingredients_with_emojis)}")
        
        st.markdown("---")
        
        # Botones de acción
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            confirm_disabled = len(st.session_state.selected_ingredients) != 2
            if st.button("✅ Confirmar Pizza", disabled=confirm_disabled, use_container_width=True):
                # Agregar la pizza con ingredientes al pedido
                pizza_name = st.session_state.multicereal_item
                ingredients_text = " + ".join(st.session_state.selected_ingredients)
                full_item_name = f"{pizza_name} (con {ingredients_text})"
                
                st.session_state.order[full_item_name] += 1
                
                # Limpiar el modal
                st.session_state.show_multicereal_modal = False
                st.session_state.selected_ingredients = []
                del st.session_state.multicereal_item
                st.success("🎉 ¡Pizza multicereal agregada al pedido!")
                
        with col2:
            if st.button("🗑️ Limpiar", use_container_width=True):
                st.session_state.selected_ingredients = []
                
        with col3:
            if st.button("❌ Cancelar", use_container_width=True):
                # Limpiar el modal sin agregar nada
                st.session_state.show_multicereal_modal = False
                st.session_state.selected_ingredients = []
                if 'multicereal_item' in st.session_state:
                    del st.session_state.multicereal_item

def show_4estaciones_modal():
    """Muestra el modal para seleccionar ingredientes de la pizza 4 Estaciones."""
    if not st.session_state.get('show_4estaciones_modal', False):
        return
    
    # Crear el modal con estilo destacado
    st.markdown("""
    <div style="
        background-color: #fff8dc;
        border: 2px solid #ff6b35;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    ">
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.subheader(f"🍕 Selecciona 4 ingredientes para tu {st.session_state.estaciones_item}")
        st.info("💡 Los ingredientes están incluidos en el precio de la pizza 4 Estaciones")
        
        selected_count = len(st.session_state.get('selected_estaciones_ingredients', []))
        
        # Mostrar progreso
        progress_text = f"Ingredientes seleccionados: {selected_count}/4"
        st.progress(min(selected_count / 4.0, 1.0))
        if selected_count == 0:
            st.warning(f"⚠️ {progress_text}")
        elif selected_count < 4:
            remaining = 4 - selected_count
            st.info(f"ℹ️ {progress_text} (faltan {remaining})")
        else:
            st.success(f"✅ {progress_text}")
        
        cols = st.columns(2)
        
        for i, ingredient in enumerate(ESTACIONES_INGREDIENTS):
            with cols[i % 2]:
                is_selected = ingredient in st.session_state.get('selected_estaciones_ingredients', [])
                
                # Deshabilitar si ya se seleccionaron 4 y este no está seleccionado
                disabled = selected_count >= 4 and not is_selected
                
                # Crear checkbox con emoji
                emoji_map = {
                    "Jamón": "🍖", "Queso Extra": "🧀", "Maíz": "🌽", "Piña": "🍍",
                    "Cebolla": "🧅", "Pimentón": "🫑", "Tomate en Ruedas": "🍅", "Salami": "🥩",
                    "Aceitunas Negras": "🫒", "Tocineta": "🥓", "Pepperoni": "🍕", "Champiñones": "🍄",
                    "Tomate Seco": "🍅", "Anchoas": "🐟", "Aceitunas Verdes": "🫒", "Pesto Genovés": "🌿", "Pesto Rosso": "🌶️", "Rúcula": "🥬"
                }
                
                ingredient_display = f"{emoji_map.get(ingredient, '🔸')} {ingredient}"
                
                if st.checkbox(
                    ingredient_display, 
                    value=is_selected, 
                    key=f"estaciones_ingredient_{ingredient}",
                    disabled=disabled
                ):
                    if ingredient not in st.session_state.selected_estaciones_ingredients:
                        if len(st.session_state.selected_estaciones_ingredients) < 4:
                            st.session_state.selected_estaciones_ingredients.append(ingredient)
                else:
                    if ingredient in st.session_state.selected_estaciones_ingredients:
                        st.session_state.selected_estaciones_ingredients.remove(ingredient)
        
        # Mostrar ingredientes seleccionados
        if st.session_state.selected_estaciones_ingredients:
            ingredients_with_emojis = []
            emoji_map = {
                "Jamón": "🍖", "Queso Extra": "🧀", "Maíz": "🌽", "Piña": "🍍",
                "Cebolla": "🧅", "Pimentón": "🫑", "Tomate en Ruedas": "🍅", "Salami": "🥩",
                "Aceitunas Negras": "🫒", "Tocineta": "🥓", "Pepperoni": "🍕", "Champiñones": "🍄",
                "Tomate Seco": "🍅", "Anchoas": "🐟", "Aceitunas Verdes": "🫒", "Pesto Genovés": "🌿", "Pesto Rosso": "🌶️", "Rúcula": "🥬"
            }
            
            for ing in st.session_state.selected_estaciones_ingredients:
                ingredients_with_emojis.append(f"{emoji_map.get(ing, '🔸')} {ing}")
            
            st.markdown(f"**Tus 4 estaciones:** {' + '.join(ingredients_with_emojis)}")
        
        st.markdown("---")
        
        # Botones de acción
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            confirm_disabled = len(st.session_state.selected_estaciones_ingredients) != 4
            if st.button("✅ Confirmar Pizza", disabled=confirm_disabled, use_container_width=True, key="confirm_4estaciones"):
                # Agregar la pizza con ingredientes al pedido
                pizza_name = st.session_state.estaciones_item
                ingredients_text = " + ".join(st.session_state.selected_estaciones_ingredients)
                full_item_name = f"{pizza_name} (con {ingredients_text})"
                
                st.session_state.order[full_item_name] += 1
                
                # Limpiar el modal
                st.session_state.show_4estaciones_modal = False
                st.session_state.selected_estaciones_ingredients = []
                del st.session_state.estaciones_item
                st.success("🎉 ¡Pizza 4 Estaciones agregada al pedido!")
                
        with col2:
            if st.button("🗑️ Limpiar", use_container_width=True, key="clear_4estaciones"):
                st.session_state.selected_estaciones_ingredients = []
                
        with col3:
            if st.button("❌ Cancelar", use_container_width=True, key="cancel_4estaciones"):
                # Limpiar el modal sin agregar nada
                st.session_state.show_4estaciones_modal = False
                st.session_state.selected_estaciones_ingredients = []
                if 'estaciones_item' in st.session_state:
                    del st.session_state.estaciones_item



# --- FUNCIONES AUXILIARES ---
def get_item_price(item_name):
    """Obtiene el precio de un item, incluso si es personalizado (como multicereal con ingredientes)."""
    all_items = {k: v for category in MENU.values() for k, v in category.items()}
    
    # Manejar delivery como caso especial
    if item_name == "🚚 Delivery":
        # El precio del delivery se almacena directamente en el pedido
        return st.session_state.order.get("🚚 Delivery", 0.0)
    
    # Primero intentar obtener el precio directamente
    if item_name in all_items:
        return all_items[item_name]
    
    # Si es un item personalizado (como multicereal con ingredientes)
    if "(con " in item_name:
        # Extraer el nombre base del item
        base_item = item_name.split(" (con ")[0]
        if base_item in all_items:
            return all_items[base_item]
        
        # Si no se encuentra exacto, buscar por coincidencia parcial
        for menu_item, price in all_items.items():
            # Comparar sin considerar el tamaño específico
            base_menu_item = menu_item.split(" (")[0] if " (" in menu_item else menu_item
            base_search_item = base_item.split(" (")[0] if " (" in base_item else base_item
            
            if base_menu_item.lower() == base_search_item.lower():
                # Verificar que el tamaño coincida
                if ("personal" in item_name.lower() and "personal" in menu_item.lower()) or \
                   ("mediana" in item_name.lower() and "mediana" in menu_item.lower()) or \
                   ("familiar" in item_name.lower() and "familiar" in menu_item.lower()):
                    return price
    
    # Buscar coincidencias parciales para cualquier item
    for menu_item, price in all_items.items():
        if item_name.lower().replace(" (con ", " ").split(")")[0] in menu_item.lower():
            return price
    
    return 0.0

def get_size_emoji(item_name):
    """Devuelve el emoji de color según el tamaño del producto."""
    name_lower = item_name.lower()
    if 'personal' in name_lower or '25cm' in name_lower or '20cm' in name_lower:
        return "🟢"  # Verde para Personal/25cm
    if 'familiar' in name_lower or '40cm' in name_lower:
        return "🔴"  # Rojo para Familiar/40cm
    if 'mediana' in name_lower or '33cm' in name_lower or '35cm' in name_lower:
        return "⚪"  # Blanco para Mediana/33cm
    return ""  # Sin emoji para items sin tamaño específico



def add_to_order(item_name):
    # Verificar si es una pizza multicereal Y no es un item ya personalizado
    if "multicereal" in item_name.lower() and "(con " not in item_name:
        st.session_state.pending_pizza = None
        st.session_state.pending_extra_counts = {}
        # Activar el modal para seleccionar ingredientes
        st.session_state.show_multicereal_modal = True
        st.session_state.multicereal_item = item_name
        st.session_state.selected_ingredients = []
    # Verificar si es una pizza 4 estaciones Y no es un item ya personalizado
    elif "4 estaciones" in item_name.lower() and "(con " not in item_name:
        st.session_state.pending_pizza = None
        st.session_state.pending_extra_counts = {}
        # Activar el modal para seleccionar ingredientes
        st.session_state.show_4estaciones_modal = True
        st.session_state.estaciones_item = item_name
        st.session_state.selected_estaciones_ingredients = []
    else:
        st.session_state.order[item_name] += 1


def start_pizza_order(item_name):
    """Pizzas tradicionales/especiales: abre panel de extras; multicereal y 4 estaciones siguen con modal."""
    if ("multicereal" in item_name.lower() or "4 estaciones" in item_name.lower()) and "(con " not in item_name.lower():
        add_to_order(item_name)
        return
    st.session_state.pending_pizza = item_name
    st.session_state.pending_extra_counts = {}


def pizza_order_size_label(item_name):
    """Personal / Mediana / Familiar para cruzar con precios de ingredientes adicionales."""
    n = item_name.lower()
    if "personal" in n or "25cm" in n:
        return "Personal"
    if "mediana" in n or "33cm" in n or "35cm" in n:
        return "Mediana"
    if "familiar" in n or "40cm" in n:
        return "Familiar"
    return None


def menu_items_for_size(category_key, size_label):
    if not size_label or category_key not in MENU:
        return []
    return [(k, v) for k, v in MENU[category_key].items() if k.endswith(f"({size_label})")]


def short_ingredient_menu_label(full_key):
    if " Adicional (" in full_key:
        return full_key.split(" Adicional (")[0]
    return full_key


def cancel_pending_pizza():
    st.session_state.pending_pizza = None
    st.session_state.pending_extra_counts = {}


def confirm_pending_pizza():
    p = st.session_state.pending_pizza
    if not p:
        return
    st.session_state.order[p] += 1
    for k, v in st.session_state.pending_extra_counts.items():
        if v and v > 0:
            st.session_state.order[k] += v
    cancel_pending_pizza()


def adjust_pending_extra(menu_key, delta):
    d = st.session_state.pending_extra_counts
    cur = d.get(menu_key, 0) + delta
    if cur <= 0:
        d.pop(menu_key, None)
    else:
        d[menu_key] = cur


def toggle_pending_extra(menu_key):
    """Toque rápido en móvil: activa/desactiva un extra para la pizza en edición."""
    cur = st.session_state.pending_extra_counts.get(menu_key, 0)
    if cur > 0:
        st.session_state.pending_extra_counts.pop(menu_key, None)
    else:
        st.session_state.pending_extra_counts[menu_key] = 1


def toggle_order_item(item_name):
    """Toque rápido para ingredientes sueltos: agrega si no existe, quita una unidad si ya existe."""
    if st.session_state.order.get(item_name, 0) > 0:
        remove_from_order(item_name)
    else:
        add_to_order(item_name)


def order_subtotal_usd():
    total = 0.0
    for item, qty in st.session_state.order.items():
        if item == "🚚 Delivery":
            total += qty
        else:
            total += get_item_price(item) * qty
    return total


def render_pizza_quick_panel():
    """Panel al elegir pizza: extras del mismo tamaño (sin precios en pantalla)."""
    pending = st.session_state.get("pending_pizza")
    if not pending:
        return
    size = pizza_order_size_label(pending)

    st.subheader("🍕 Completar esta pizza")
    st.markdown(f"**{compact_item_label(pending)}**")
    if not size:
        st.warning("No se detectó el tamaño; puedes añadir la pizza sola o cancelar.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Solo pizza", type="primary", use_container_width=True, key="pq_solo_nosize"):
                confirm_pending_pizza()
        with c2:
            if st.button("❌ Cancelar", use_container_width=True, key="pq_cancel_nosize"):
                cancel_pending_pizza()
        return

    st.caption("Extras opcionales (ya al tamaño de la pizza). Luego confirma para meter todo en el pedido.")

    trad = menu_items_for_size("Ingredientes Tradicionales (Pizza)", size)
    prem = menu_items_for_size("Ingredientes Premium (Pizza)", size)

    def render_extra_grid(items_list, key_prefix):
        if not items_list:
            return
        cols = st.columns(3)
        for i, (fk, pr) in enumerate(items_list):
            with cols[i % 3]:
                label = short_ingredient_menu_label(fk)
                is_on = st.session_state.pending_extra_counts.get(fk, 0) > 0
                btn_label = f"✅ {label}" if is_on else label
                st.button(
                    btn_label,
                    key=f"{key_prefix}_t_{i}",
                    use_container_width=True,
                    on_click=toggle_pending_extra,
                    args=(fk,),
                )

    st.markdown("**Tradicionales**")
    render_extra_grid(trad, "pqt")
    st.markdown("**Premium**")
    render_extra_grid(prem, "pqp")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Añadir pizza al pedido", type="primary", use_container_width=True, key="pq_confirm"):
            confirm_pending_pizza()
    with c2:
        if st.button("❌ Cancelar", use_container_width=True, key="pq_cancel"):
            cancel_pending_pizza()

def remove_from_order(item_name):
    if st.session_state.order[item_name] > 0:
        st.session_state.order[item_name] -= 1
        if st.session_state.order[item_name] == 0:
            del st.session_state.order[item_name]


def compact_item_label(item_name):
    """Etiqueta corta: nombre + talla breve."""
    if "(" in item_name and ")" in item_name:
        base_name = item_name.split(" (")[0]
        size_raw = item_name.split("(")[1].split(")")[0]
        size_clean = size_raw.replace("25cm", "").replace("33cm", "").replace("35cm", "").replace("40cm", "").replace("20cm", "").strip()
        if size_clean:
            size_map = {
                "Personal": "P",
                "Mediana": "M",
                "Familiar": "F",
                "Comer aquí": "Aquí",
                "Para llevar": "Llevar",
            }
            short_size = size_map.get(size_clean, size_clean)
            return f"{base_name} ({short_size})"
    return item_name


def render_menu_item_row(category, item_name, price, *, show_usd):
    """Una fila del menú en formato compacto para móvil."""
    use_small_buttons = "Ingredientes" in category or "Adicionales Calzone" in category
    use_pizza_flow = category in PIZZA_QUICK_ADD_CATEGORIES
    size_emoji = get_size_emoji(item_name)

    if use_small_buttons:
        if " Adicional (" in item_name:
            base_name = item_name.split(" Adicional (")[0]
            size_part = item_name.split("(")[1].split(")")[0]
            size_letter = size_part[0].upper()
            display_name = f"{base_name} ({size_letter})"
        else:
            parts = item_name.split(" Adicional ")
            display_name = parts[0]
            if len(parts) > 1:
                size_letter = parts[1][0].lower()
                display_name += f" ({size_letter})"
            else:
                display_name = item_name
        count = st.session_state.order.get(item_name, 0)
        btn_label = f"✅ {display_name}" if count > 0 else display_name
        st.button(
            btn_label,
            key=f"toggle_{item_name}",
            on_click=toggle_order_item,
            args=(item_name,),
            use_container_width=True,
        )
    else:
        short_name = compact_item_label(item_name)
        button_label = f"{size_emoji} {short_name}" if size_emoji else short_name
        if use_pizza_flow:
            st.button(button_label, key=item_name, on_click=start_pizza_order, args=(item_name,), use_container_width=True)
        else:
            st.button(button_label, key=item_name, on_click=add_to_order, args=(item_name,), use_container_width=True)


def render_category_grid(category, items, *, show_usd, columns_count=2):
    """Renderiza una categoría en grid compacto para reducir scroll."""
    cols = st.columns(columns_count)
    for idx, (item_name, price) in enumerate(items.items()):
        with cols[idx % columns_count]:
            render_menu_item_row(category, item_name, price, show_usd=show_usd)


def format_order_text():
    if not st.session_state.order:
        return "Pedido vacío", 0.0
    order_lines = []
    subtotal_usd = 0.0
    all_items = {k: v for category in MENU.values() for k, v in category.items()}
    sorted_order = sorted(st.session_state.order.items())
    
    # Agregar información del cliente al inicio
    order_lines.append("=" * 50)
    order_lines.append("CASTELL PIZZAS")
    order_lines.append("=" * 50)
    order_lines.append("")
    order_lines.append(f"CLIENTE: {st.session_state.customer_name or 'Sin nombre'}")
    order_lines.append(f"TIPO: {st.session_state.order_type}")
    order_lines.append("")
    order_lines.append("-" * 50)
    order_lines.append("PEDIDO:")
    order_lines.append("-" * 50)
    
    # Obtener tasa del dólar
    if 'dollar_rate' not in st.session_state:
        st.session_state.dollar_rate, st.session_state.api_source = get_dollar_rate()
    
    for item, quantity in sorted_order:
        # Manejar delivery de forma especial
        if item == "🚚 Delivery":
            price_usd = quantity  # Para delivery, quantity es el precio
            total_item_price_usd = price_usd
            total_item_price_bs = total_item_price_usd * st.session_state.dollar_rate
            subtotal_usd += total_item_price_usd
            
            line = f"🚚 Delivery"
            price_str = f"${total_item_price_usd:.2f} (Bs. {total_item_price_bs:,.2f})"
            formatted_line = f"{line.ljust(45, '.')} {price_str.rjust(20)}"
            order_lines.append(formatted_line)
        else:
            price_usd = get_item_price(item)  # Usar la nueva función
            total_item_price_usd = price_usd * quantity
            total_item_price_bs = total_item_price_usd * st.session_state.dollar_rate
            subtotal_usd += total_item_price_usd
            
            # Agregar emoji al texto del pedido
            size_emoji = get_size_emoji(item)
            item_with_emoji = f"{size_emoji} {item}" if size_emoji else item
            line = f"{quantity}x {item_with_emoji}"
            price_str = f"${total_item_price_usd:.2f} (Bs. {total_item_price_bs:,.2f})"
            formatted_line = f"{line.ljust(45, '.')} {price_str.rjust(20)}"
            order_lines.append(formatted_line)
    
    subtotal_bs = subtotal_usd * st.session_state.dollar_rate
    order_lines.append("")
    order_lines.append("-" * 50)
    subtotal_line = f"{'SUBTOTAL'.ljust(25)} ${subtotal_usd:.2f} (Bs. {subtotal_bs:,.2f})"
    order_lines.append(subtotal_line)
    order_lines.append("")
    order_lines.append(f"Tasa BCV: Bs. {st.session_state.dollar_rate:,.2f} por USD")
    order_lines.append("")
    order_lines.append("=" * 50)
    order_lines.append("¡GRACIAS POR SU PEDIDO!")
    order_lines.append("=" * 50)
    
    return "\n".join(order_lines), subtotal_usd

# --- FUNCIONES DE IMPRESIÓN 58MM ---

def format_bar_ticket_58mm():
    """Formatea el ticket para la barra (con precios) en formato 80mm."""
    if not st.session_state.order:
        return "PEDIDO VACÍO"
    
    # Configuración para 80mm (aproximadamente 48 caracteres por línea)
    line_width = 48
    
    # Obtener tasa del dólar
    if 'dollar_rate' not in st.session_state:
        st.session_state.dollar_rate, st.session_state.api_source = get_dollar_rate()
    
    lines = []
    lines.append("=" * line_width)
    lines.append("CASTELL PIZZAS".center(line_width))
    lines.append("TICKET BARRA".center(line_width))
    lines.append("=" * line_width)
    lines.append("")
    
    # Información del cliente
    lines.append(f"CLIENTE: {st.session_state.customer_name or 'Sin nombre'}")
    lines.append(f"TIPO: {st.session_state.order_type}")
    lines.append("")
    lines.append("-" * line_width)
    lines.append("PEDIDO")
    lines.append("-" * line_width)
    
    # Items del pedido con precios
    subtotal_usd = 0.0
    sorted_order = sorted(st.session_state.order.items())
    
    for item, quantity in sorted_order:
        # Manejar delivery de forma especial
        if item == "🚚 Delivery":
            price_usd = quantity
            total_item_price_usd = price_usd
            total_item_price_bs = total_item_price_usd * st.session_state.dollar_rate
            subtotal_usd += total_item_price_usd
            
            lines.append("Delivery")
            lines.append(f"${total_item_price_usd:.2f}".rjust(line_width))
            lines.append(f"Bs.{total_item_price_bs:,.0f}".rjust(line_width))
            lines.append("")
        else:
            price_usd = get_item_price(item)
            total_item_price_usd = price_usd * quantity
            total_item_price_bs = total_item_price_usd * st.session_state.dollar_rate
            subtotal_usd += total_item_price_usd
            
            # Formatear nombre del item (sin emoji para impresión)
            item_clean = item.replace("🟢", "").replace("⚪", "").replace("🔴", "").strip()
            
            # Línea de cantidad y nombre
            qty_line = f"{quantity}x {item_clean}"
            lines.append(qty_line)
            
            # Líneas de precio
            lines.append(f"${total_item_price_usd:.2f}".rjust(line_width))
            lines.append(f"Bs.{total_item_price_bs:,.0f}".rjust(line_width))
            lines.append("")
    
    # Subtotal
    lines.append("-" * line_width)
    subtotal_bs = subtotal_usd * st.session_state.dollar_rate
    lines.append("SUBTOTAL:")
    lines.append(f"${subtotal_usd:.2f}".rjust(line_width))
    lines.append(f"Bs.{subtotal_bs:,.0f}".rjust(line_width))
    lines.append("")
    
    # Información del dólar
    lines.append("-" * line_width)
    lines.append(f"Tasa BCV: Bs.{st.session_state.dollar_rate:,.2f}")
    lines.append("")
    
    # Pie de página
    lines.append("=" * line_width)
    lines.append("GRACIAS POR SU COMPRA")
    lines.append("=" * line_width)
    
    return "\n".join(lines)

def format_kitchen_ticket_58mm():
    """Formatea el ticket para la cocina (sin precios) en formato 80mm."""
    if not st.session_state.order:
        return "PEDIDO VACÍO"
    
    # Configuración para 80mm (aproximadamente 48 caracteres por línea)
    line_width = 48
    
    lines = []
    lines.append("=" * line_width)
    lines.append("".center(line_width))
    lines.append("TICKET COCINA".center(line_width))
    lines.append("=" * line_width)
    lines.append("")
    
    # Información del cliente
    lines.append(f"CLIENTE: {st.session_state.customer_name or 'Sin nombre'}")
    lines.append(f"TIPO: {st.session_state.order_type}")
    lines.append("")
    lines.append("-" * line_width)
    lines.append("PEDIDO")
    lines.append("-" * line_width)
    
    # Items del pedido sin precios
    sorted_order = sorted(st.session_state.order.items())
    
    for item, quantity in sorted_order:
        # Saltar delivery en ticket de cocina
        if item == "🚚 Delivery":
            continue
            
        # Formatear nombre del item (sin emoji para impresión)
        item_clean = item.replace("🟢", "").replace("⚪", "").replace("🔴", "").strip()
        
        # Solo cantidad y nombre del producto
        qty_line = f"{quantity}x {item_clean}"
        lines.append(qty_line)
        lines.append("")  # Espacio entre items
    
    # Pie de página
    lines.append("=" * line_width)
    lines.append("BUEN PROVECHO!")
    lines.append("=" * line_width)
    
    return "\n".join(lines)

def generate_print_html(content, title="Ticket"):
    """Genera HTML optimizado para impresión térmica 58mm."""
    # Escapar el contenido para HTML
    import html
    escaped_content = html.escape(content)
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title} -</title>
    <style>
        @media print {{
            @page {{
                size: 58mm auto;
                margin: 1mm;
            }}
            body {{
                margin: 0;
                padding: 0;
                font-size: 10px;
            }}
            .no-print {{
                display: none !important;
            }}
        }}
        
        body {{
            font-family: 'Courier New', 'Lucida Console', monospace;
            font-size: 11px;
            line-height: 1.1;
            margin: 0;
            padding: 8px;
            width: 58mm;
            max-width: 58mm;
            background: white;
            color: black;
        }}
        
        .print-content {{
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            line-height: 1.1;
        }}
        
        .no-print {{
            text-align: center;
            margin: 15px 0;
            padding: 10px;
            background: #f5f5f5;
            border-radius: 8px;
        }}
        
        .print-btn {{
            padding: 12px 24px;
            font-size: 14px;
            font-weight: bold;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            margin: 5px;
            transition: background-color 0.3s;
        }}
        
        .print-btn.primary {{
            background: #4CAF50;
            color: white;
        }}
        
        .print-btn.primary:hover {{
            background: #45a049;
        }}
        
        .print-btn.secondary {{
            background: #f44336;
            color: white;
        }}
        
        .print-btn.secondary:hover {{
            background: #da190b;
        }}
        
        @media screen {{
            body {{
                background: #f0f0f0;
                padding: 20px;
                max-width: none;
                width: auto;
            }}
            .print-content {{
                background: white;
                padding: 15px;
                border: 2px solid #ddd;
                border-radius: 8px;
                max-width: 58mm;
                margin: 0 auto;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
        }}
        
        .instructions {{
            background: #e3f2fd;
            border: 1px solid #2196f3;
            border-radius: 6px;
            padding: 10px;
            margin: 10px 0;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="no-print">
        <h3>🖨️ Impresión de Ticket Térmico 58mm</h3>
        <div class="instructions">
            <strong>📋 Instrucciones:</strong><br>
            1. Asegúrate de que tu impresora térmica esté encendida<br>
            2. Haz clic en "Imprimir" y selecciona tu impresora térmica<br>
            3. En configuración de impresión, selecciona tamaño personalizado: 58mm de ancho<br>
            4. Desactiva márgenes o ponlos al mínimo
        </div>
        <button onclick="printTicket()" class="print-btn primary">
            🖨️ Imprimir {title}
        </button>
        <button onclick="window.close()" class="print-btn secondary">
            ❌ Cerrar Ventana
        </button>
    </div>
    <div class="print-content">{escaped_content}</div>
    <script>
        // Auto-abrir diálogo de impresión inmediatamente
        window.addEventListener('load', function() {{
            // Abrir diálogo de impresión automáticamente
            setTimeout(function() {{
                window.print();
            }}, 300);
        }});
        
        // Función para imprimir manualmente
        function printTicket() {{
            window.print();
        }}
        
        // Cerrar ventana después de imprimir
        window.addEventListener('afterprint', function() {{
            setTimeout(function() {{
                if (confirm('¿Deseas cerrar esta ventana?')) {{
                    window.close();
                }}
            }}, 1000);
        }});
    </script>
</body>
</html>"""
    
    return html_content

# --- FUNCIONES DE IMPRESIÓN TÉRMICA ---

def detect_thermal_printers():
    """Detecta impresoras térmicas disponibles en el sistema."""
    printers = []
    
    if not ESCPOS_AVAILABLE:
        return printers
    
    # Detectar impresoras USB (más común para impresoras térmicas)
    try:
        # Intentar detectar impresoras USB comunes
        common_usb_ids = [
            (0x04b8, 0x0202),  # Epson TM-T20
            (0x04b8, 0x0203),  # Epson TM-T70
            (0x04b8, 0x0205),  # Epson TM-T88
            (0x0519, 0x0001),  # Star TSP100
            (0x0519, 0x0003),  # Star TSP650
            (0x154f, 0x154f),  # Generic thermal printer
        ]
        
        for vendor_id, product_id in common_usb_ids:
            try:
                printer = Usb(vendor_id, product_id)
                printers.append({
                    'type': 'USB',
                    'name': f'USB Printer ({hex(vendor_id)}:{hex(product_id)})',
                    'connection': (vendor_id, product_id)
                })
            except:
                continue
                
    except Exception:
        pass
    
    # Detectar puertos serie (COM en Windows)
    if platform.system() == "Windows":
        for i in range(1, 10):  # COM1 a COM9
            try:
                port = f"COM{i}"
                # No intentar conectar aquí, solo listar puertos potenciales
                printers.append({
                    'type': 'Serial',
                    'name': f'Puerto Serie {port}',
                    'connection': port
                })
            except:
                continue
    else:
        # Linux/Mac
        import glob
        serial_ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
        for port in serial_ports:
            printers.append({
                'type': 'Serial',
                'name': f'Puerto Serie {port}',
                'connection': port
            })
    
    return printers

def print_thermal_ticket(content, printer_config=None):
    """Imprime un ticket en impresora térmica."""
    if not ESCPOS_AVAILABLE:
        return False, "La librería python-escpos no está instalada"
    
    try:
        # Configuración por defecto (archivo para pruebas)
        if not printer_config:
            # Crear archivo temporal para pruebas
            temp_file = f"ticket_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            printer = File(temp_file)
        else:
            # Usar configuración específica
            if printer_config['type'] == 'USB':
                vendor_id, product_id = printer_config['connection']
                printer = Usb(vendor_id, product_id)
            elif printer_config['type'] == 'Serial':
                port = printer_config['connection']
                printer = Serial(port, baudrate=9600)
            elif printer_config['type'] == 'Network':
                ip = printer_config['connection']
                printer = Network(ip)
            else:
                return False, "Tipo de impresora no soportado"
        
        # Configurar impresora para 58mm
        printer.set(align='left', font='a', bold=False, underline=False, width=1, height=1)
        
        # Imprimir contenido línea por línea
        lines = content.split('\n')
        for line in lines:
            if line.strip() == "":
                printer.ln()
            elif line.startswith("="):
                printer.set(bold=True)
                printer.text(line + '\n')
                printer.set(bold=False)
            elif "CASTELL" in line or "TICKET" in line:
                printer.set(align='center', bold=True)
                printer.text(line + '\n')
                printer.set(align='left', bold=False)
            elif line.startswith("-"):
                printer.text(line + '\n')
            elif "SUBTOTAL" in line or "TOTAL" in line:
                printer.set(bold=True)
                printer.text(line + '\n')
                printer.set(bold=False)
            else:
                printer.text(line + '\n')
        
        # Cortar papel
        printer.cut()
        printer.close()
        
        return True, "Ticket impreso correctamente"
        
    except USBNotFoundError:
        return False, "Impresora USB no encontrada. Verifica que esté conectada y encendida."
    except SerialException:
        return False, "Error en puerto serie. Verifica la conexión y configuración."
    except Exception as e:
        return False, f"Error de impresión: {str(e)}"

def print_to_system_printer(content, printer_name=None):
    """Imprime usando las impresoras del sistema (Windows/Linux/Mac)."""
    try:
        # Crear archivo temporal
        temp_file = f"ticket_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Comando de impresión según el sistema operativo
        if platform.system() == "Windows":
            if printer_name:
                os.system(f'print /D:"{printer_name}" "{temp_file}"')
            else:
                os.system(f'print "{temp_file}"')
        elif platform.system() == "Darwin":  # macOS
            if printer_name:
                os.system(f'lpr -P "{printer_name}" "{temp_file}"')
            else:
                os.system(f'lpr "{temp_file}"')
        else:  # Linux
            if printer_name:
                os.system(f'lpr -P "{printer_name}" "{temp_file}"')
            else:
                os.system(f'lpr "{temp_file}"')
        
        # Limpiar archivo temporal
        try:
            os.remove(temp_file)
        except:
            pass
            
        return True, "Ticket enviado a impresora del sistema"
        
    except Exception as e:
        return False, f"Error al imprimir: {str(e)}"


def _nav_pedido():
    st.session_state.castell_nav = "Pedido"


def render_print_ticket_buttons(key_suffix=""):
    """Botones de impresión térmica / navegador (mismo bloque que antes)."""
    ks = key_suffix
    if st.button("💰 Ticket barra", use_container_width=True, key=f"print_barra{ks}", help="Ticket con precios para la barra"):
        bar_content = format_bar_ticket_58mm()
        st.components.v1.html(f"""
            <div id="printContent" style="
                font-family: 'Courier New', 'Lucida Console', 'Monaco', monospace;
                font-size: 11px;
                font-weight: normal;
                line-height: 1.2;
                white-space: pre-wrap;
                color: #333333;
                padding: 10px;
                border: 1px solid #ccc;
                background: white;
                margin: 10px 0;
            ">
{bar_content}
            </div>
            <style>
                @media print {{
                    body * {{ visibility: hidden !important; }}
                    #printContent, #printContent * {{ visibility: visible !important; display: block !important; }}
                    #printContent {{
                        position: absolute !important; left: 0 !important; top: 0 !important;
                        width: 80mm !important; font-size: 16px !important; font-weight: 900 !important;
                        color: #000000 !important;
                        font-family: 'Courier New', 'Lucida Console', 'Monaco', monospace !important;
                        white-space: pre-wrap !important;
                        -webkit-print-color-adjust: exact !important;
                        print-color-adjust: exact !important;
                        background: white !important; padding: 2mm !important; margin: 0 !important;
                        border: none !important; line-height: 1.3 !important; letter-spacing: 0.5px !important;
                    }}
                    @page {{ size: 80mm auto; margin: 2mm; }}
                }}
            </style>
            <script>
                setTimeout(function() {{ window.print(); }}, 300);
            </script>
            """, height=200)

    if st.button("👨‍🍳 Ticket cocina", use_container_width=True, key=f"print_cocina{ks}", help="Ticket sin precios para la cocina"):
        kitchen_content = format_kitchen_ticket_58mm()
        st.components.v1.html(f"""
            <div id="printContentKitchen" style="
                font-family: 'Courier New', 'Lucida Console', 'Monaco', monospace;
                font-size: 11px;
                font-weight: normal;
                line-height: 1.2;
                white-space: pre-wrap;
                color: #333333;
                padding: 10px;
                border: 1px solid #ccc;
                background: white;
                margin: 10px 0;
            ">
{kitchen_content}
            </div>
            <style>
                @media print {{
                    body * {{ visibility: hidden !important; }}
                    #printContentKitchen, #printContentKitchen * {{ visibility: visible !important; display: block !important; }}
                    #printContentKitchen {{
                        position: absolute !important; left: 0 !important; top: 0 !important;
                        width: 80mm !important; font-size: 16px !important; font-weight: 900 !important;
                        color: #000000 !important;
                        font-family: 'Courier New', 'Lucida Console', 'Monaco', monospace !important;
                        white-space: pre-wrap !important;
                        -webkit-print-color-adjust: exact !important;
                        print-color-adjust: exact !important;
                        background: white !important; padding: 2mm !important; margin: 0 !important;
                        border: none !important; line-height: 1.3 !important; letter-spacing: 0.5px !important;
                    }}
                    @page {{ size: 80mm auto; margin: 2mm; }}
                }}
            </style>
            <script>
                setTimeout(function() {{ window.print(); }}, 300);
            </script>
            """, height=200)


# --- INTERFAZ DE USUARIO ---
CASTELL_CSS = """
<style>
    :root {
        --castell-red: #b22222;
        --castell-red-dark: #8b0000;
        --castell-gold: #c9a227;
        --castell-bg: #f8f8f8;
        --castell-card: #ffffff;
    }
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 4.5rem !important;
        max-width: 28rem !important;
        background: var(--castell-bg) !important;
    }
    h1, h2, h3 { letter-spacing: -0.02em; }
    div[data-testid="stRadio"] > div { flex-wrap: wrap !important; gap: 0.35rem !important; }
    div[data-testid="stRadio"] label {
        border-radius: 999px !important;
        padding: 0.35rem 0.75rem !important;
        border: 1px solid #e0e0e0 !important;
        background: #fff !important;
    }
    button[kind="secondary"], button[kind="primary"] {
        min-height: 2rem !important;
        font-size: 0.85rem !important;
        border-radius: 12px !important;
    }
    .castell-header {
        display: flex; align-items: center; justify-content: space-between;
        padding: 0.25rem 0 0.5rem 0; margin-bottom: 0.25rem;
        border-bottom: 1px solid #eee;
    }
    .castell-brand { font-size: 1.15rem; font-weight: 700; color: var(--castell-red); margin: 0; }
    .castell-sub { font-size: 0.75rem; color: #666; margin-top: 0.15rem; }
    div[data-testid="stSidebarNav"] { font-size: 0.9rem; }
</style>
"""
st.markdown(CASTELL_CSS, unsafe_allow_html=True)

if "dollar_rate" not in st.session_state:
    rate, source = get_bcv_rate_direct()
    if rate:
        st.session_state.dollar_rate, st.session_state.api_source = rate, source
    else:
        st.session_state.dollar_rate, st.session_state.api_source = get_dollar_rate()

if "castell_nav" not in st.session_state:
    st.session_state.castell_nav = "Menú"

# Cabecera estilo app
hc1, hc2, hc3 = st.columns([1, 4, 2])
with hc1:
    st.caption("☰")
with hc2:
    st.markdown('<p class="castell-brand">Castell Pizzas</p><p class="castell-sub">Pedidos rápidos</p>', unsafe_allow_html=True)
with hc3:
    show_usd = st.checkbox("USD/Bs", value=True, help="Mostrar montos en USD además de Bs donde aplique")

st.radio(
    "Vista",
    ["Menú", "Pedido", "Resumen"],
    horizontal=True,
    label_visibility="collapsed",
    key="castell_nav",
)

nav = st.session_state.castell_nav

st.markdown("---")

# Modales primero (multicereal / 4 estaciones)
show_multicereal_modal()
show_4estaciones_modal()

# --- Contenido por vista ---
if nav == "Menú":
    with st.expander("💱 Tasa BCV", expanded=False):
        st.metric("Bolívares por USD", f"Bs. {st.session_state.dollar_rate:,.2f}")
        if st.button("🔄 Actualizar tasa", key="bcv_refresh_main"):
            st.cache_data.clear()
            rate, source = get_bcv_rate_direct()
            if rate:
                st.session_state.dollar_rate, st.session_state.api_source = rate, source
            else:
                st.session_state.dollar_rate, st.session_state.api_source = get_dollar_rate()
            st.success("Tasa actualizada")

    bs1, bs2 = st.columns([5, 1])
    with bs1:
        search_term = st.text_input(
            "Buscar",
            placeholder="Buscar en el menú…",
            key="menu_search_key",
            label_visibility="collapsed",
        )
    with bs2:
        if st.button("✕", key="menu_search_clear", help="Limpiar búsqueda"):
            st.session_state.menu_search_key = ""
            st.rerun()

    filtered_menu = filter_menu_items(MENU, search_term)
    results_count = get_search_results_count(MENU, search_term)

    if search_term:
        if results_count == 0:
            st.warning("Sin resultados.")
            st.stop()

    render_pizza_quick_panel()

    st.markdown("##### Catálogo")
    st.caption("🟢 P · ⚪ M · 🔴 F")

    section_labels = ["🍕 Pizzas", "🍝 Otros", "➕ Extras"]
    section_pick = st.radio(
        "Categoría",
        section_labels,
        horizontal=True,
        label_visibility="collapsed",
        key="castell_menu_section",
    )
    tab_idx = section_labels.index(section_pick)
    _, group_cats = MENU_TAB_GROUPS[tab_idx]

    if not search_term:
        visible_cats = [cat for cat in group_cats if cat in filtered_menu]
        if not visible_cats:
            st.caption("Sin productos.")
        else:
            selected_cat = st.selectbox(
                "Sección",
                options=visible_cats,
                key="mobile_cat_selector_0",
                label_visibility="collapsed",
            )
            grid_cols = 3 if ("Ingredientes" in selected_cat or "Adicionales Calzone" in selected_cat) else 2
            render_category_grid(selected_cat, filtered_menu[selected_cat], show_usd=show_usd, columns_count=grid_cols)
    else:
        for category, items in filtered_menu.items():
            st.markdown(f"**{category}**")
            grid_cols = 3 if ("Ingredientes" in category or "Adicionales Calzone" in category) else 2
            render_category_grid(category, items, show_usd=show_usd, columns_count=grid_cols)

    # Barra tipo checkout (mockup): artículos + subtotal + ir a pedido
    _n = sum(st.session_state.order.values()) if st.session_state.order else 0
    _sub = order_subtotal_usd()
    _bs = _sub * st.session_state.dollar_rate
    st.markdown("---")
    f1, f2, f3 = st.columns([2, 2, 2])
    with f1:
        st.caption(f"{_n} artículos")
    with f2:
        if show_usd:
            st.markdown(f"**${_sub:.2f}**")
        else:
            st.markdown(f"**Bs. {_bs:,.2f}**")
    with f3:
        st.button("Pedido →", use_container_width=True, key="dock_pedido", on_click=_nav_pedido)

elif nav == "Pedido":
    st.markdown("##### Tu pedido")
    customer_name = st.text_input("Nombre del cliente", value=st.session_state.customer_name, placeholder="Nombre", key="cust_field")
    if customer_name != st.session_state.customer_name:
        st.session_state.customer_name = customer_name

    t1, t2, t3 = st.columns(3)
    with t1:
        if st.button("Comer aquí", use_container_width=True, type="primary" if st.session_state.order_type == "Para comer aquí" else "secondary"):
            st.session_state.order_type = "Para comer aquí"
    with t2:
        if st.button("Pickup", use_container_width=True, type="primary" if st.session_state.order_type == "Para llevar (PICKUP)" else "secondary"):
            st.session_state.order_type = "Para llevar (PICKUP)"
    with t3:
        if st.button("Delivery", use_container_width=True, type="primary" if st.session_state.order_type == "Para llevar (DELIVERY)" else "secondary"):
            st.session_state.order_type = "Para llevar (DELIVERY)"

    if st.session_state.order_type == "Para llevar (DELIVERY)":
        st.caption("Zona de envío")
        d1, d2 = st.columns(2)
        with d1:
            if st.button("0–3 km", use_container_width=True, key="dz1"):
                st.session_state.order["🚚 Delivery"] = 1.50
        with d2:
            if st.button("3–6 km", use_container_width=True, key="dz2"):
                st.session_state.order["🚚 Delivery"] = 2.50
        d3, d4 = st.columns(2)
        with d3:
            if st.button("6–8.5 km", use_container_width=True, key="dz3"):
                st.session_state.order["🚚 Delivery"] = 3.50
        with d4:
            if st.button("8.6–10 km", use_container_width=True, key="dz4"):
                st.session_state.order["🚚 Delivery"] = 4.50
        if "🚚 Delivery" in st.session_state.order:
            if st.button("Quitar delivery", key="dz_clear"):
                del st.session_state.order["🚚 Delivery"]

    if not st.session_state.order:
        st.info("Aún no hay productos. Ve a **Menú** para agregar.")
    else:
        st.caption("Ítems")
        sorted_order_items = sorted(st.session_state.order.items())
        for item, quantity in sorted_order_items:
            if item == "🚚 Delivery":
                st.markdown("**Delivery** — tarifa en subtotal")
                continue
            size_emoji = get_size_emoji(item)
            item_with_emoji = f"{size_emoji} {item}" if size_emoji else item
            r1, r2, r3, r4 = st.columns([4, 1, 1, 1])
            with r1:
                st.markdown(f"{item_with_emoji}")
            with r2:
                st.markdown(f"**×{quantity}**")
            with r3:
                st.button("−", key=f"rm_{item}", on_click=remove_from_order, args=(item,))
            with r4:
                st.button("+", key=f"ad_{item}", on_click=add_to_order, args=(item,))

        st.markdown("##### Empaques")
        e1, e2, e3 = st.columns(3)
        with e1:
            if st.button("Caja P", use_container_width=True, key="bx_p"):
                st.session_state.order["Caja para llevar (25cm)"] += 1
        with e2:
            if st.button("Caja M", use_container_width=True, key="bx_m"):
                st.session_state.order["Caja para llevar (33cm)"] += 1
        with e3:
            if st.button("Caja G", use_container_width=True, key="bx_g"):
                st.session_state.order["Caja para llevar (40cm)"] += 1
        empaque_items = [it for it in st.session_state.order.keys() if "Caja para llevar" in it]
        if empaque_items:
            if st.button("Quitar cajas", key="bx_all"):
                for it in empaque_items:
                    del st.session_state.order[it]

    sub_u = order_subtotal_usd()
    sub_bs = sub_u * st.session_state.dollar_rate
    st.markdown("---")
    if show_usd:
        st.metric("Subtotal", f"${sub_u:.2f} USD", delta=f"Bs. {sub_bs:,.2f}")
    else:
        st.metric("Subtotal", f"Bs. {sub_bs:,.2f}")

    order_text, _ = format_order_text()
    st.markdown("##### Copiar para WhatsApp")
    st.text_area("Pedido", value=order_text, height=220, key="wa_text_pedido", label_visibility="collapsed")

    st.markdown("##### Impresión")
    render_print_ticket_buttons("_pedido")

    if st.button("🗑️ Reiniciar pedido", use_container_width=True, key="reset_pedido"):
        st.session_state.order.clear()
        st.session_state.customer_name = ""
        st.session_state.order_type = "Para comer aquí"
        cancel_pending_pizza()

else:
    # Resumen (solo totales y acciones; sin precios por línea)
    st.markdown("##### Resumen del pedido")
    st.caption("Revisa y copia o imprime")
    if not st.session_state.order:
        st.warning("El pedido está vacío.")
    else:
        for item, qty in sorted(st.session_state.order.items()):
            if item == "🚚 Delivery":
                st.markdown("- **Delivery** (tarifa según zona)")
            else:
                em = get_size_emoji(item)
                lab = f"{em} {item}" if em else item
                st.markdown(f"- **{qty}×** {lab}")
        su = order_subtotal_usd()
        sbs = su * st.session_state.dollar_rate
        st.markdown("---")
        if show_usd:
            st.metric("Total a pagar", f"${su:.2f} USD")
            st.caption(f"Equivalente: Bs. {sbs:,.2f} · Tasa BCV Bs. {st.session_state.dollar_rate:,.2f}")
        else:
            st.metric("Total a pagar", f"Bs. {sbs:,.2f}")

    ot, _ = format_order_text()
    st.text_area("Texto WhatsApp", value=ot, height=180, key="wa_text_resumen", label_visibility="collapsed")

    st.markdown("##### Acciones")
    render_print_ticket_buttons("_resumen")

    if st.button("🗑️ Reiniciar pedido", use_container_width=True, key="reset_resumen"):
        st.session_state.order.clear()
        st.session_state.customer_name = ""
        st.session_state.order_type = "Para comer aquí"
        cancel_pending_pizza()

