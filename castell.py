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
    layout="wide"
)




# --- DATOS DEL MENÚ ---
MENU = {
    "Pizzas Tradicionales": {
        "Margherita (Personal 25cm)": 5.00,
        "Margherita (Mediana 33cm)": 7.50,
        "Margherita (Familiar 40cm)": 10.00,
        "Jamón (Personal 25cm)": 6.00,
        "Jamón (Mediana 33cm)": 9.00,
        "Jamón (Familiar 40cm)": 12.00,
        "Tocineta y Maíz (Personal 25cm)": 7.50,
        "Tocineta y Maíz (Mediana 33cm)": 11.00,
        "Tocineta y Maíz (Familiar 40cm)": 15.00,
        "4 Estaciones (Personal 25cm)": 10.00,
        "4 Estaciones (Mediana 33cm)": 14.50,
        "4 Estaciones (Familiar 40cm)": 20.00,
    },
    "Pizzas Especiales": {
        "Di Abruzzo (Personal 25cm)": 8.00,
        "Di Abruzzo (Mediana 33cm)": 10.50,
        "Di Abruzzo (Familiar 40cm)": 16.00,
        "Castell 1 (Personal 25cm)": 11.00,
        "Castell 1 (Mediana 33cm)": 16.00,
        "Castell 1 (Familiar 40cm)": 22.00,
        "Castell 2 (Personal 25cm)": 12.00,
        "Castell 2 (Mediana 33cm)": 17.00,
        "Castell 2 (Familiar 40cm)": 24.00,
    },
    "Otros Platos": {
        "Pizza Multicereal (Personal 25cm)": 12.00,
        "Pizza Multicereal (Mediana 35cm)": 17.00,
        "Pizza Multicereal (Familiar 40cm)": 24.00,
        "Pizza Dolce (Personal 20cm)": 5.50,
        "Calzone (Comer aquí)": 4.50,
        "Calzone (Para llevar)": 5.00,
        "Pasticho Tradicional (Comer aquí)": 7.00,
        "Pasticho Tradicional (Para llevar)": 7.50,
        "Pasticho Berenjena/Platano/Zucchini (Comer aquí)": 7.00,
        "Pasticho Berenjena/Platano/Zucchini (Para llevar)": 7.50,
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
        "Pimentón (Calzone)": 1.00, "Piña (Calzone)": 1.00, "Caja para llevar (25cm)": 0.50,
        "Caja para llevar (33cm)": 0.70, "Caja para llevar (40cm)": 0.90,
    },
    "Bebidas": {
        "Refresco 1.5lts": 2.50,
        "Refresco 335ml": 1.50,
        "Refresco de Lata": 2.00,
        "Té Verde (tomar aquí)": 2.00,
        "Té Verde (Para llevar)": 2.80,
        "Té Negro (tomar aqui aquí)": 2.00,
        "Té Negro (Para llevar)": 2.80,
        "Flor de Jamaica (Tomar aquí)": 2.00,
        "Flor de Jamaica (Para llevar)": 2.80,
        "Té Matcha (Tomar aquí)": 3.00,
        "Agua Pequeña (330ml)": 0.5,
        "Agua Mediana (600ml)": 1,
        "Té Matcha (Para llevar)": 3.80,
    }
}

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
        if selected_count == 0:
            st.warning(f"⚠️ {progress_text} - Selecciona 2 ingredientes")
        elif selected_count == 1:
            st.info(f"ℹ️ {progress_text} - Selecciona 1 ingrediente más")
        else:
            st.success(f"✅ {progress_text} - ¡Listo para confirmar!")
        
        # Crear columnas para los ingredientes
        cols = st.columns(4)
        
        for i, ingredient in enumerate(MULTICEREAL_INGREDIENTS):
            with cols[i % 4]:
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
        if selected_count == 0:
            st.warning(f"⚠️ {progress_text} - Selecciona 4 ingredientes")
        elif selected_count < 4:
            remaining = 4 - selected_count
            st.info(f"ℹ️ {progress_text} - Selecciona {remaining} ingrediente{'s' if remaining > 1 else ''} más")
        else:
            st.success(f"✅ {progress_text} - ¡Listo para confirmar!")
        
        # Crear columnas para los ingredientes
        cols = st.columns(4)
        
        for i, ingredient in enumerate(ESTACIONES_INGREDIENTS):
            with cols[i % 4]:
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
        # Activar el modal para seleccionar ingredientes
        st.session_state.show_multicereal_modal = True
        st.session_state.multicereal_item = item_name
        st.session_state.selected_ingredients = []
    # Verificar si es una pizza 4 estaciones Y no es un item ya personalizado
    elif "4 estaciones" in item_name.lower() and "(con " not in item_name:
        # Activar el modal para seleccionar ingredientes
        st.session_state.show_4estaciones_modal = True
        st.session_state.estaciones_item = item_name
        st.session_state.selected_estaciones_ingredients = []
    else:
        st.session_state.order[item_name] += 1

def remove_from_order(item_name):
    if st.session_state.order[item_name] > 0:
        st.session_state.order[item_name] -= 1
        if st.session_state.order[item_name] == 0:
            del st.session_state.order[item_name]

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
    """Formatea el ticket para la barra (con precios) en formato 58mm."""
    if not st.session_state.order:
        return "PEDIDO VACÍO"
    
    # Configuración para 58mm (aproximadamente 32 caracteres por línea)
    line_width = 32
    
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
    """Formatea el ticket para la cocina (sin precios) en formato 58mm."""
    if not st.session_state.order:
        return "PEDIDO VACÍO"
    
    # Configuración para 58mm (aproximadamente 32 caracteres por línea)
    line_width = 32
    
    lines = []
    lines.append("=" * line_width)
    lines.append("CASTELL PIZZERIA".center(line_width))
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
    <title>{title} - Castell Pizzeria</title>
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

# --- INTERFAZ DE USUARIO ---
st.title("🍕 Pedidos whatsapp")
st.write("Selecciona los productos del menú para agregarlos al pedido.")

# Mostrar modales si están activos
show_multicereal_modal()
show_4estaciones_modal()

# --- INFORMACIÓN DEL DÓLAR ---
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    if 'dollar_rate' not in st.session_state:
        # Primero intentar fuentes directas del BCV
        rate, source = get_bcv_rate_direct()
        if rate:
            st.session_state.dollar_rate, st.session_state.api_source = rate, source
        else:
            st.session_state.dollar_rate, st.session_state.api_source = get_dollar_rate()
    st.info(f"💱 Dólar BCV: Bs. {st.session_state.dollar_rate:,.2f}")
with col2:
    if st.button("🔄 Actualizar BCV"):
        st.cache_data.clear()
        # Primero intentar fuentes directas del BCV
        rate, source = get_bcv_rate_direct()
        if rate:
            st.session_state.dollar_rate, st.session_state.api_source = rate, source
        else:
            st.session_state.dollar_rate, st.session_state.api_source = get_dollar_rate()
        st.success(f"Tasa actualizada: Bs. {st.session_state.dollar_rate:,.2f}")
with col3:
    show_usd = st.checkbox("Mostrar USD", value=True)

# --- INFORMACIÓN DE IMPRESIÓN ---
with st.expander("ℹ️ Información sobre Impresión Térmica", expanded=False):
    st.markdown("""
    ### 🖨️ Cómo imprimir en tu impresora térmica de 58mm:
    
    **Pasos para imprimir:**
    1. Haz clic en el botón "🖨️ Imprimir Ticket"
    2. Se abrirá una ventana optimizada para impresión
    3. En el diálogo de impresión, selecciona tu impresora térmica
    4. **Importante:** Configura el tamaño de papel como "Personalizado" o "58mm"
    5. Ajusta los márgenes al mínimo (0mm si es posible)
    
    **Impresoras térmicas compatibles:**
    - Epson TM-T20, TM-T70, TM-T88
    - Star TSP100, TSP650
    - Bixolon SRP-350
    - Cualquier impresora térmica de 58mm
    
    **Consejos:**
    - Asegúrate de que la impresora esté encendida y con papel
    - Si no tienes impresora térmica, puedes usar cualquier impresora normal
    - Los tickets están optimizados para 32 caracteres por línea
    """)

st.markdown("---")

# --- BUSCADOR ---
col_search, col_clear = st.columns([4, 1])
with col_search:
    search_term = st.text_input("🔍 Buscar pizzas o ingredientes:", placeholder="Ej: margherita, jamón, tocineta, personal, familiar...")
with col_clear:
    st.write("")  # Espaciado
    if st.button("🗑️ Limpiar"):
        st.rerun()

# --- BÚSQUEDAS RÁPIDAS ---
if not search_term:
    st.markdown("**Búsquedas rápidas:**")
    quick_col1, quick_col2, quick_col3, quick_col4, quick_col5 = st.columns(5)
    
    with quick_col1:
        if st.button("🍕 Pizzas"):
            st.session_state.quick_search = "pizza"
    with quick_col2:
        if st.button("🟢 Personal"):
            st.session_state.quick_search = "personal"
    with quick_col3:
        if st.button("⚪ Mediana"):
            st.session_state.quick_search = "mediana"
    with quick_col4:
        if st.button("🔴 Familiar"):
            st.session_state.quick_search = "familiar"
    with quick_col5:
        if st.button("🧀 Ingredientes"):
            st.session_state.quick_search = "adicional"
    
    # Aplicar búsqueda rápida si se seleccionó
    if 'quick_search' in st.session_state:
        search_term = st.session_state.quick_search
        del st.session_state.quick_search

# --- LEYENDA DE TAMAÑOS ---
st.markdown("**Leyenda de tamaños:** 🟢 Personal (25cm) | ⚪ Mediana (33cm) | 🔴 Familiar (40cm)")

with st.sidebar:
    # --- INFORMACIÓN DEL CLIENTE ---
    st.header("👤 Información del Cliente")
    
    # Campo para el nombre del cliente
    customer_name = st.text_input("Nombre del cliente:", value=st.session_state.customer_name, placeholder="Ej: Juan Pérez")
    if customer_name != st.session_state.customer_name:
        st.session_state.customer_name = customer_name
    
    # Botones para tipo de pedido
    st.subheader("📍 Tipo de Pedido")
    
    if st.button("🍽️ Comer aquí", use_container_width=True, 
                 type="primary" if st.session_state.order_type == "Para comer aquí" else "secondary"):
        st.session_state.order_type = "Para comer aquí"
    
    if st.button("🥡 Pickup", use_container_width=True,
                 type="primary" if st.session_state.order_type == "Para llevar (PICKUP)" else "secondary"):
        st.session_state.order_type = "Para llevar (PICKUP)"
    
    if st.button("🚚 Delivery", use_container_width=True,
                 type="primary" if st.session_state.order_type == "Para llevar (DELIVERY)" else "secondary"):
        st.session_state.order_type = "Para llevar (DELIVERY)"
    
    # Mostrar selección actual
    st.info(f"**Cliente:** {st.session_state.customer_name or 'Sin nombre'}")
    st.info(f"**Tipo:** {st.session_state.order_type}")
    
    st.markdown("---")
    
    st.header("🛒 Pedido Actual")
    if not st.session_state.order:
        st.info("El pedido está vacío.")
    else:
        sorted_order_items = sorted(st.session_state.order.items())
        for item, quantity in sorted_order_items:
            # Agregar emoji al pedido en el sidebar
            size_emoji = get_size_emoji(item)
            item_with_emoji = f"{size_emoji} {item}" if size_emoji else item
            st.write(f"{quantity}x {item_with_emoji}")
            
            # Botones de agregar y quitar en líneas separadas
            if st.button(f"➕ Agregar {item}", key=f"add_{item}", use_container_width=True):
                add_to_order(item)
            if st.button(f"➖ Quitar {item}", key=f"rem_{item}", use_container_width=True):
                remove_from_order(item)
            st.markdown("---")
        st.markdown("---")
        order_text, subtotal = format_order_text()
        st.subheader("📝 Texto para Copiar")
        st.text_area("Pedido para WhatsApp", value=order_text, height=300)
        

        
        # Botones de Delivery
        st.subheader("🚚 Delivery")
        
        st.markdown("<small>0km - 3km</small>", unsafe_allow_html=True)
        if st.button("$1.50", key="delivery_1_5", use_container_width=True):
            st.session_state.order["🚚 Delivery"] = 1.50
        
        st.markdown("<small>3.1km - 6km</small>", unsafe_allow_html=True)
        if st.button("$2.50", key="delivery_2_5", use_container_width=True):
            st.session_state.order["🚚 Delivery"] = 2.50
        
        st.markdown("<small>6.1km - 8.5km</small>", unsafe_allow_html=True)
        if st.button("$3.50", key="delivery_3_5", use_container_width=True):
            st.session_state.order["🚚 Delivery"] = 3.50
        
        st.markdown("<small>8.6km - 10km</small>", unsafe_allow_html=True)
        if st.button("$4.50", key="delivery_4_5", use_container_width=True):
            st.session_state.order["🚚 Delivery"] = 4.50
        
        # Botón para quitar delivery
        if "🚚 Delivery" in st.session_state.order:
            if st.button("❌ Quitar Delivery", use_container_width=True):
                del st.session_state.order["🚚 Delivery"]
        
        # Botones de impresión
        st.subheader("🖨️ Impresión 58mm")
        
        if st.button("💰 Imprimir Ticket Barra", use_container_width=True, help="Ticket con precios para la barra"):
            # Generar contenido del ticket de barra
            bar_content = format_bar_ticket_58mm()
            
            # Crear archivo HTML temporal
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            html_file = f"ticket_barra_{timestamp}.html"
            
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Ticket Barra - Castell Pizzeria</title>
    <style>
        @page {{ size: 58mm auto; margin: 1mm; }}
        body {{ font-family: 'Courier New', monospace; font-size: 10px; line-height: 1.1; margin: 0; padding: 2mm; }}
        .ticket {{ white-space: pre-wrap; }}
    </style>
</head>
<body>
    <div class="ticket">{bar_content}</div>
    <script>
        window.onload = function() {{
            window.print();
            setTimeout(function() {{ window.close(); }}, 2000);
        }};
    </script>
</body>
</html>"""
            
            # Guardar archivo HTML
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Abrir archivo automáticamente
            import webbrowser
            import os
            file_path = os.path.abspath(html_file)
            webbrowser.open(f'file://{file_path}')
            
            st.success("✅ Abriendo ventana de impresión...")
            st.info("💡 Se abrió una ventana para imprimir. Si no aparece, revisa si tu navegador bloquea ventanas emergentes.")
        
        if st.button("👨‍🍳 Imprimir Ticket Cocina", use_container_width=True, help="Ticket sin precios para la cocina"):
            # Generar contenido del ticket de cocina
            kitchen_content = format_kitchen_ticket_58mm()
            
            # Crear archivo HTML temporal
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            html_file = f"ticket_cocina_{timestamp}.html"
            
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Ticket Cocina - Castell Pizzeria</title>
    <style>
        @page {{ size: 58mm auto; margin: 1mm; }}
        body {{ font-family: 'Courier New', monospace; font-size: 10px; line-height: 1.1; margin: 0; padding: 2mm; }}
        .ticket {{ white-space: pre-wrap; }}
    </style>
</head>
<body>
    <div class="ticket">{kitchen_content}</div>
    <script>
        window.onload = function() {{
            window.print();
            setTimeout(function() {{ window.close(); }}, 2000);
        }};
    </script>
</body>
</html>"""
            
            # Guardar archivo HTML
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Abrir archivo automáticamente
            import webbrowser
            import os
            file_path = os.path.abspath(html_file)
            webbrowser.open(f'file://{file_path}')
            
            st.success("✅ Abriendo ventana de impresión...")
            st.info("💡 Se abrió una ventana para imprimir. Si no aparece, revisa si tu navegador bloquea ventanas emergentes.")

    
    if st.button("🗑️ Reiniciar Pedido", use_container_width=True):
        st.session_state.order.clear()
        st.session_state.customer_name = ""
        st.session_state.order_type = "Para comer aquí"

# --- MENÚ PRINCIPAL ---
# Aplicar filtro de búsqueda
filtered_menu = filter_menu_items(MENU, search_term)
results_count = get_search_results_count(MENU, search_term)

# Mostrar información de búsqueda
if search_term:
    if results_count > 0:
        st.success(f"🔍 Se encontraron {results_count} resultados para '{search_term}'")
    else:
        st.warning(f"🔍 No se encontraron resultados para '{search_term}'. Intenta con otros términos.")
        st.stop()

menu_categories = list(filtered_menu.items())
all_cols = st.columns(3)
col_index = 0

for category, items in menu_categories:
    with all_cols[col_index % 3]:
        st.subheader(category)
        use_small_buttons = "Ingredientes" in category or "Adicionales Calzone" in category
        
        for item_name, price in items.items():
            # Obtener emoji de tamaño
            size_emoji = get_size_emoji(item_name)
            
            if use_small_buttons:
                # Procesar ingredientes para mostrar formato corto
                if " Adicional (" in item_name:
                    # Para ingredientes como "Maíz Adicional (Personal)"
                    base_name = item_name.split(" Adicional (")[0]
                    size_part = item_name.split("(")[1].split(")")[0]
                    size_letter = size_part[0].upper()  # Usar mayúscula para mejor legibilidad
                    display_name = f"{base_name} ({size_letter})"
                else:
                    # Para otros items como "Tocineta (Calzone)"
                    parts = item_name.split(" Adicional ")
                    display_name = parts[0]
                    if len(parts) > 1:
                        size_letter = parts[1][0].lower()
                        display_name += f" ({size_letter})"
                    else:
                        display_name = item_name
                
                # Agregar emoji al inicio del nombre
                if size_emoji:
                    display_name = f"{size_emoji} {display_name}"
                
                b_col1, b_col2 = st.columns([0.7, 0.3])
                with b_col1:
                    st.button(display_name, key=item_name, on_click=add_to_order, args=(item_name,), use_container_width=True)
                with b_col2:
                    price_text = format_currency(price, show_usd) if 'show_usd' in locals() else f"${price:.2f}"
                    st.markdown(f"**{price_text}**", help=f"Precio: {format_currency(price, True)}")
            else:
                price_text = format_currency(price, show_usd) if 'show_usd' in locals() else f"${price:.2f}"
                # Agregar emoji al inicio del nombre del botón
                button_text = f"{size_emoji} {item_name}" if size_emoji else item_name
                button_label = f"{button_text} - {price_text}"
                st.button(button_label, key=item_name, on_click=add_to_order, args=(item_name,), use_container_width=True)
            

            
    col_index += 1
    if col_index % 3 == 0:
        st.markdown("---") # Separador visual entre filas
        all_cols = st.columns(3)
