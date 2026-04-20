# Documentacion funcional - Castell Pizzas

## 1) Que hace esta aplicacion

Aplicacion en `Streamlit` para tomar pedidos de Castell Pizzas de forma rapida (principalmente en telefono), con:

- Catalogo de productos por categorias.
- Agregado de items al pedido.
- Flujos especiales para pizzas personalizables.
- Calculo de subtotal en USD y Bs segun tasa BCV.
- Generacion de texto para copiar a WhatsApp.
- Impresion de ticket de barra (con precios) y cocina (sin precios).

Archivo principal: `castell.py`.

---

## 2) Estructura general de la interfaz

La app esta dividida en dos grandes zonas:

- **Vista principal (centro):** busqueda, resumen rapido, flujo de seleccion y menu compacto.
- **Sidebar (menu lateral):** datos del cliente, tipo de pedido, detalle completo del pedido, empaques, delivery, impresion y reinicio.

Configuracion de pagina:

- `layout="centered"` para mejor uso en movil.
- `initial_sidebar_state="collapsed"` para iniciar limpio en pantalla pequena.

---

## 3) Datos del menu y categorias

El menu esta en el diccionario `MENU` y contiene:

- `Pizzas Tradicionales`
- `Pizzas Especiales`
- `Otros Platos`
- `Ingredientes Tradicionales (Pizza)`
- `Ingredientes Premium (Pizza)`
- `Adicionales Calzone y Empaques`
- `Bebidas`

Para navegacion movil, se agrupa en pestañas (`MENU_TAB_GROUPS`):

- `🍕 Pizzas`
- `🍝 Otros`
- `➕ Extras y bebidas`

---

## 4) Estado de sesion (memoria de la app)

Variables clave en `st.session_state`:

- `order`: pedido actual (`Counter` de item -> cantidad).
- `customer_name`: nombre del cliente.
- `order_type`: tipo de pedido.
- `dollar_rate`, `api_source`: tasa BCV y origen.
- `pending_pizza`: pizza en proceso de configuracion rapida.
- `pending_extra_counts`: extras seleccionados para esa pizza.
- `show_multicereal_modal`, `selected_ingredients`: modal y seleccion de multicereal.
- `show_4estaciones_modal`, `selected_estaciones_ingredients`: modal y seleccion 4 estaciones.

---

## 5) Flujo principal de uso (operativo)

1. Buscar producto (opcional).
2. Elegir pestaña y seccion del menu.
3. Tocar productos para agregarlos.
4. Si es pizza tradicional/especial, completar extras del mismo tamano en panel rapido.
5. Revisar resumen y subtotal.
6. Abrir sidebar para:
   - confirmar cliente/tipo,
   - copiar texto de pedido,
   - agregar empaques/delivery,
   - imprimir ticket barra/cocina.

---

## 6) Vista principal: componentes, botones y funcion

## 6.1 Encabezado

- **Titulo:** `🍕 Pedidos whatsapp`
- **Descripcion corta:** orienta al uso movil y menu lateral.

## 6.2 Tasa BCV

- **Info BCV:** muestra tasa activa.
- **Boton `🔄 Actualizar BCV`:** limpia cache y vuelve a consultar APIs.
- **Checkbox `Mostrar USD`:** controla visualizacion de formato monetario donde aplique.

## 6.3 Buscador

- **Input `🔍 Buscar en el menú`:** filtra items por texto (palabras parciales).
- **Boton `Limpiar`:** borra busqueda y recarga vista.

## 6.4 Resumen rapido (expander)

- **Titulo:** `🛒 Resumen del pedido (N lineas)`.
- Muestra items con cantidad.
- Muestra subtotal aproximado en USD y Bs.

## 6.5 Leyenda de tamanos

- `🟢 Personal`
- `⚪ Mediana`
- `🔴 Familiar`

## 6.6 Panel "Completar esta pizza" (flujo rapido)

Aparece cuando se toca una pizza tradicional o especial.

Elementos:

- Nombre de pizza seleccionada + precio base.
- Grilla de extras `Tradicionales` y `Premium` (al mismo tamano de la pizza).
- Cada extra es boton toggle:
  - estado apagado: `Nombre`
  - estado activo: `✅ Nombre`
- Botones:
  - `✅ Añadir pizza al pedido`: agrega pizza + extras seleccionados.
  - `❌ Cancelar`: descarta configuracion actual.

## 6.7 Menu principal compacto

- Pestañas: `🍕 Pizzas`, `🍝 Otros`, `➕ Extras y bebidas`.
- Dentro de cada pestaña:
  - selector de `Seccion` (solo una categoria visible a la vez para reducir scroll),
  - grilla de productos:
    - 2 columnas para pizzas/platos.
    - 3 columnas para ingredientes/adicionales.

Comportamiento de botones:

- **Pizzas tradicionales/especiales:** abren flujo rapido de extras.
- **Multicereal / 4 estaciones:** abren modales especiales.
- **Ingredientes/adicionales sueltos:** toggle rapido
  - si no esta: agrega 1,
  - si ya esta: quita 1.

---

## 7) Modales especiales (personalizacion)

## 7.1 Pizza Multicereal

- Seleccion exacta de **2 ingredientes**.
- Indicador de progreso (0/2, 1/2, 2/2).
- Botones:
  - `✅ Confirmar Pizza`
  - `🗑️ Limpiar`
  - `❌ Cancelar`
- Al confirmar, guarda item como:
  - `Pizza Multicereal (...) (con ing1 + ing2)`

## 7.2 Pizza 4 Estaciones

- Seleccion exacta de **4 ingredientes**.
- Indicador de progreso (0/4 ... 4/4).
- Botones:
  - `✅ Confirmar Pizza`
  - `🗑️ Limpiar`
  - `❌ Cancelar`
- Al confirmar, guarda item como:
  - `4 Estaciones (...) (con ing1 + ing2 + ing3 + ing4)`

---

## 8) Sidebar: componentes, botones y funcion

## 8.1 Informacion del cliente

- Campo `Nombre del cliente`.

## 8.2 Tipo de pedido

Botones:

- `🍽️ Comer aquí`
- `🥡 Pickup`
- `🚚 Delivery`

Muestran estado seleccionado con estilo `primary`.

## 8.3 Pedido actual (detalle completo)

- Lista de items con cantidad.
- Para cada linea:
  - `➕ Agregar <item>`
  - `➖ Quitar <item>`

## 8.4 Texto para copiar

- `text_area` con formato de pedido para WhatsApp:
  - cliente,
  - tipo,
  - items,
  - subtotal,
  - tasa BCV.

## 8.5 Empaques

Botones:

- `Caja Personal (25cm)`
- `Caja Mediana (33cm)`
- `Caja Familiar (40cm)`
- `❌ Quitar Empaques` (si hay empaques en el pedido)

## 8.6 Delivery

Botones por rango:

- `0km - 3km`
- `3.1km - 6km`
- `6.1km - 8.5km`
- `8.6km - 10km`
- `❌ Quitar Delivery` (si existe)

## 8.7 Impresion

- `💰 Imprimir Ticket Barra`: ticket con precios.
- `👨‍🍳 Imprimir Ticket Cocina`: ticket sin precios.

Ambos generan bloque HTML y disparan `window.print()`.

## 8.8 Reinicio

- `🗑️ Reiniciar Pedido`: limpia pedido, cliente, tipo y flujo pendiente.

---

## 9) Precios, subtotal y moneda

Logica de moneda:

- Intenta BCV directo (`pydolarvenezuela`, `yadio`).
- Si falla, usa fuentes alternas.
- Si todo falla, usa valor por defecto.

Subtotal:

- Se calcula con `order_subtotal_usd()` y `get_item_price()`.
- Delivery se trata como item especial.
- Items personalizados (por ejemplo pizzas con `con ...`) toman el precio base del item original.

---

## 10) Tickets y salida de impresion

Funciones principales:

- `format_bar_ticket_58mm()`: ticket para barra con montos.
- `format_kitchen_ticket_58mm()`: ticket para cocina sin montos.
- `generate_print_html()`: plantilla HTML imprimible.
- `print_thermal_ticket()`: impresion directa via `python-escpos`.
- `print_to_system_printer()`: impresion por comando del sistema operativo.

---

## 11) Funciones clave del codigo (mapa rapido)

- **Busqueda y conteo:** `filter_menu_items`, `get_search_results_count`
- **Moneda:** `get_dollar_rate`, `get_bcv_rate_direct`, `format_currency`
- **Pedido:** `add_to_order`, `remove_from_order`, `toggle_order_item`
- **Flujo pizza rapida:** `start_pizza_order`, `render_pizza_quick_panel`, `confirm_pending_pizza`
- **Extras rapidos:** `toggle_pending_extra`, `menu_items_for_size`
- **Visual compacta:** `compact_item_label`, `render_menu_item_row`, `render_category_grid`
- **Salida de pedido:** `format_order_text`
- **Impresion:** `format_bar_ticket_58mm`, `format_kitchen_ticket_58mm`, `print_thermal_ticket`

---

## 12) Observaciones operativas

- La app prioriza rapidez de toma de ordenes en movil.
- Los precios no se muestran en botones compactos del menu principal; se concentran en subtotal/tickets/texto final.
- El flujo de personalizacion evita ir categoria por categoria para extras de pizzas principales.

