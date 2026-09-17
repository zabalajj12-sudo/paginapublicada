"""
Modelo de Chatbot.
Responde preguntas del usuario sobre el destino que se le acaba de
recomendar ("¿qué puedo hacer aquí?", "¿cómo llego?", "¿dónde compro
tiquetes?", etc.) usando reglas de coincidencia de palabras clave —
no depende de ningún servicio de IA externo ni de una clave de API paga.
"""

import random
import re
import urllib.parse

# Palabras/frases clave -> intención. Se buscan como palabra completa
# (no como substring), para evitar falsos positivos (p. ej. que "ir"
# no dispare con cualquier palabra que lo contenga).
PATRONES = {
    "saludo": ["hola", "buenas", "buenos dias", "buenos días", "buenas tardes", "buenas noches", "que tal", "qué tal"],
    "despedida": ["gracias", "chao", "adios", "adiós", "hasta luego", "nos vemos"],
    "transporte": [
        "tiquete", "tiquetes", "boleto", "boletos", "vuelo", "vuelos", "avion", "avión",
        "pasaje", "pasajes", "comprar", "llegar", "llego", "ir", "viajar", "transporte",
        "transportarme", "movilizarme", "carretera", "bus", "buseta", "carro",
    ],
    "clima": ["clima", "tiempo", "temperatura", "llueve", "lluvia", "calor", "frio", "frío", "epoca", "época", "mes", "meses"],
    "hospedaje": ["hotel", "hoteles", "hospedaje", "alojamiento", "dormir", "quedarme", "quedarse", "quedo", "alojarme", "airbnb", "posada"],
    "comida": ["comida", "comer", "gastronomia", "gastronomía", "plato", "platos", "restaurante", "restaurantes", "tipico", "típico"],
    "presupuesto": ["precio", "costo", "cuesta", "presupuesto", "barato", "caro", "dinero", "plata", "gastar"],
    "actividades": ["hacer", "actividad", "actividades", "planes", "plan", "visitar", "conocer", "recorrer", "lugares", "sitios", "pasear"],
}

# Sugerencias de actividades según el tipo de gusto que tiene el destino.
# Así la respuesta de "actividades" no repite siempre el mismo texto de
# "detalle" del destino, sino que arma algo más rico combinando sus gustos.
ACTIVIDADES_POR_GUSTO = {
    "playa": ["nadar y tomar el sol en la playa", "hacer snorkel si hay arrecifes cerca", "caminar por la orilla al atardecer"],
    "aventura": ["hacer caminatas o senderismo", "practicar deportes al aire libre", "explorar zonas naturales cercanas"],
    "cultura": ["visitar museos y sitios históricos", "recorrer el centro o casco histórico", "conocer las tradiciones locales"],
    "gastronomia": ["probar la comida típica de la región", "visitar mercados locales", "hacer un tour gastronómico"],
    "lujo": ["hospedarte en un resort o spa de alta gama", "reservar experiencias exclusivas con anticipación"],
    "naturaleza": ["observar la flora y fauna del lugar", "hacer ecoturismo", "visitar parques naturales cercanos"],
}

RESPUESTAS_NO_ENTENDIDO = [
    "No estoy seguro de haber entendido eso. Puedo ayudarte con: actividades, cómo llegar, clima, hospedaje, comida o presupuesto — ¿sobre cuál quieres saber?",
    "Esa no la manejo todavía 🙂 Prueba preguntando por actividades, transporte, clima, hospedaje o comida en este destino.",
    "Reformula un poco tu pregunta — te puedo hablar de qué hacer, cómo llegar, el clima, dónde quedarte, o cuánto cuesta viajar aquí.",
]


def _texto_normalizado(pregunta):
    texto = pregunta.lower().strip()
    return re.sub(r"[¿?¡!.,]", "", texto)


def _detectar_intencion(texto):
    for intencion, palabras in PATRONES.items():
        for p in palabras:
            if re.search(r"\b" + re.escape(p) + r"\b", texto):
                return intencion
    return None


def _sugerencias_actividades(gustos):
    sugerencias = []
    for g in gustos or []:
        sugerencias.extend(ACTIVIDADES_POR_GUSTO.get(g, []))
    return sugerencias[:4]


def responder_pregunta(pregunta, destino):
    """
    destino: el diccionario del destino recomendado (nombre, pais, detalle,
    tags, gustos, tipo). Genera una respuesta contextual según la intención
    detectada en la pregunta.
    """
    texto = _texto_normalizado(pregunta)
    intencion = _detectar_intencion(texto)

    nombre = destino.get("nombre", "este destino")
    pais = destino.get("pais", "")
    detalle = destino.get("detalle", "")
    tipo = destino.get("tipo", "internacional")
    gustos = destino.get("gustos", [])
    lugar_busqueda = urllib.parse.quote(f"{nombre} {pais}")

    if intencion == "saludo":
        return f"¡Hola! Soy tu asistente para {nombre}. Puedo ayudarte con actividades, cómo llegar, clima, hospedaje, comida o presupuesto. ¿Qué quieres saber?"

    if intencion == "despedida":
        return f"¡Que disfrutes {nombre}! Cualquier otra duda, aquí estoy 👋"

    if intencion == "actividades":
        sugerencias = _sugerencias_actividades(gustos)
        if sugerencias:
            lista = "; ".join(sugerencias)
            return f"En {nombre} puedes: {lista}. Además: {detalle}"
        return f"En {nombre} puedes: {detalle}"

    if intencion == "transporte":
        link_vuelos = f"https://www.google.com/travel/flights?q=Vuelos%20a%20{lugar_busqueda}"
        if tipo == "local":
            return (f"{nombre} queda dentro de Colombia, así que puedes llegar en vuelo doméstico, "
                    f"por carretera (bus intermunicipal o carro particular), dependiendo de qué tan lejos esté de tu ciudad. "
                    f"Si prefieres avión, aquí tienes un buscador ya armado: {link_vuelos}")
        return (f"Para llegar a {nombre}, lo más común es un vuelo internacional. "
                f"Te dejo un buscador de vuelos ya armado para comparar precios: {link_vuelos}")

    if intencion == "clima":
        link_clima = f"https://www.google.com/search?q=clima+en+{lugar_busqueda}"
        return f"El clima en {nombre} varía según la época del año, así que revisa antes de viajar. Búsqueda actualizada aquí: {link_clima}"

    if intencion == "hospedaje":
        link_hoteles = f"https://www.google.com/travel/hotels/{lugar_busqueda}"
        return f"Para hospedaje en {nombre}, puedes comparar hoteles y precios aquí: {link_hoteles}"

    if intencion == "comida":
        return f"{nombre} tiene una oferta gastronómica que vale la pena explorar. {detalle}"

    if intencion == "presupuesto":
        return (f"El presupuesto para {nombre} depende de la temporada y el tipo de viaje (mochilero, cómodo, lujo). "
                f"Compara vuelos y alojamiento con anticipación — normalmente bajan de precio entre más rápido reserves.")

    # No se detectó ninguna intención conocida: variar la respuesta para
    # que no se sienta repetitivo, y guiar hacia lo que sí puede responder.
    return random.choice(RESPUESTAS_NO_ENTENDIDO)
