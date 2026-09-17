"""
Modelo de Destino.
Contiene el catálogo de destinos turísticos y la lógica que decide
cuál recomendar según los gustos y el entorno elegidos por el usuario.
"""

import random
import requests

# Imagen de respaldo si Wikipedia no responde o no tiene foto para ese lugar.
IMAGEN_RESPALDO = "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&q=80"

# Caché en memoria: evita volver a pedirle la imagen a Wikipedia por cada
# búsqueda repetida del mismo destino mientras el servidor sigue corriendo.
_cache_imagenes = {}


def _buscar_titulo_real(termino_busqueda):
    """
    Le pregunta a Wikipedia cuál es el título EXACTO del artículo más
    parecido a este término (por si el nombre que tenemos no coincide
    letra por letra con el título real del artículo). Devuelve None si
    no encuentra nada razonable.
    """
    url = "https://es.wikipedia.org/w/api.php"
    params = {
        "action": "query", "list": "search", "srsearch": termino_busqueda,
        "format": "json", "srlimit": 1,
    }
    resp = requests.get(url, params=params, timeout=4, headers={"User-Agent": "Wanderlust-App/1.0"})
    resp.raise_for_status()
    resultados = resp.json().get("query", {}).get("search", [])
    return resultados[0]["title"] if resultados else None


def obtener_imagen_real(termino_busqueda):
    """
    Trae la foto principal de un lugar directamente desde Wikipedia,
    para garantizar que la imagen SIEMPRE corresponda al destino real
    (en vez de depender de una URL fija que puede estar mal o caída).

    Primero busca el título exacto del artículo (por si el nombre que
    tenemos no es idéntico al título real), y luego pide su foto.
    """
    if termino_busqueda in _cache_imagenes:
        return _cache_imagenes[termino_busqueda]

    try:
        titulo_real = _buscar_titulo_real(termino_busqueda) or termino_busqueda

        url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(titulo_real)}"
        resp = requests.get(url, timeout=4, headers={"User-Agent": "Wanderlust-App/1.0"})
        if resp.status_code == 200:
            data = resp.json()
            img = (data.get("originalimage") or {}).get("source") or (data.get("thumbnail") or {}).get("source")
            if img:
                _cache_imagenes[termino_busqueda] = img
                return img
    except (requests.RequestException, ValueError, KeyError):
        # ValueError/KeyError cubren respuestas inesperadas (JSON raro, etc.)
        pass

    _cache_imagenes[termino_busqueda] = IMAGEN_RESPALDO
    return IMAGEN_RESPALDO


DESTINOS = [
    {"nombre": "Maldivas", "wiki": "Maldivas", "pais": "Maldivas", "gustos": ["playa", "lujo"], "tipo": "internacional",
     "detalle": "Bungalows sobre el agua turquesa, arrecifes de coral y silencio absoluto.",
     "img": "https://images.unsplash.com/photo-1573843981267-be1999ff37cd?w=800&q=80",
     "tags": ["🏖️ Playa", "💎 Lujo"]},

    {"nombre": "Cancún & Riviera Maya", "wiki": "Cancún", "pais": "México", "gustos": ["playa", "cultura"], "tipo": "internacional",
     "detalle": "Playas de arena blanca con el Caribe al frente y ruinas mayas a un paso.",
     "img": "https://images.unsplash.com/photo-1552074284-5e88ef1aef18?w=800&q=80",
     "tags": ["🏖️ Playa", "🏛️ Cultura"]},

    {"nombre": "Bali", "wiki": "Bali", "pais": "Indonesia", "gustos": ["playa", "aventura", "cultura", "naturaleza"], "tipo": "internacional",
     "detalle": "Templos entre arrozales, olas perfectas en Uluwatu y mercados de incienso.",
     "img": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&q=80",
     "tags": ["🌿 Naturaleza", "🏖️ Playa", "🏛️ Cultura"]},

    {"nombre": "Santorini", "wiki": "Santorini", "pais": "Grecia", "gustos": ["playa", "gastronomia", "lujo"], "tipo": "internacional",
     "detalle": "Cúpulas azules sobre el Egeo, vino local al atardecer y marisco fresco.",
     "img": "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800&q=80",
     "tags": ["🏖️ Playa", "🍕 Gastronomía"]},

    {"nombre": "Ibiza", "wiki": "Ibiza", "pais": "España", "gustos": ["playa", "gastronomia"], "tipo": "internacional",
     "detalle": "El Mediterráneo más festivo: calas escondidas de día y vida nocturna legendaria.",
     "img": "https://images.unsplash.com/photo-1530565883715-61083a6a5b7c?w=800&q=80",
     "tags": ["🏖️ Playa", "🎶 Ocio"]},

    {"nombre": "Costa Rica", "wiki": "Costa Rica", "pais": "Costa Rica", "gustos": ["aventura", "naturaleza"], "tipo": "internacional",
     "detalle": "Volcanes activos, tirolinas sobre selva tropical y surfeo en el Pacífico.",
     "img": "https://images.unsplash.com/photo-1518509562904-e7ef99cdcc86?w=800&q=80",
     "tags": ["⛰️ Aventura", "🌿 Naturaleza"]},

    {"nombre": "Patagonia", "wiki": "Patagonia", "pais": "Chile / Argentina", "gustos": ["aventura", "naturaleza"], "tipo": "internacional",
     "detalle": "Torres del Paine, glaciares infinitos y cóndores en el viento.",
     "img": "https://images.unsplash.com/photo-1531794477966-964877ac2ffd?w=800&q=80",
     "tags": ["⛰️ Aventura", "🌿 Naturaleza"]},

    {"nombre": "Nueva Zelanda", "wiki": "Nueva Zelanda", "pais": "Nueva Zelanda", "gustos": ["aventura", "naturaleza"], "tipo": "internacional",
     "detalle": "Fiordos, volcanes y una escena de deporte extremo sin igual en el mundo.",
     "img": "https://images.unsplash.com/photo-1507699622108-4be3abd695ad?w=800&q=80",
     "tags": ["⛰️ Aventura", "🌿 Naturaleza"]},

    {"nombre": "Islandia", "wiki": "Islandia", "pais": "Islandia", "gustos": ["aventura", "naturaleza"], "tipo": "internacional",
     "detalle": "Auroras boreales, géiseres humeantes y cascadas épicas.",
     "img": "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=800&q=80",
     "tags": ["⛰️ Aventura", "🌿 Naturaleza"]},

    {"nombre": "Perú: Machu Picchu", "wiki": "Machu Picchu", "pais": "Perú", "gustos": ["aventura", "cultura", "naturaleza"], "tipo": "internacional",
     "detalle": "El camino inca entre nubes y la ciudadela perdida de los Andes.",
     "img": "https://images.unsplash.com/photo-1587595431973-160d0d94add1?w=800&q=80",
     "tags": ["⛰️ Aventura", "🏛️ Cultura"]},

    {"nombre": "Roma", "wiki": "Roma", "pais": "Italia", "gustos": ["cultura", "gastronomia"], "tipo": "internacional",
     "detalle": "El Coliseo, el Vaticano y la mejor pasta carbonara del universo conocido.",
     "img": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=800&q=80",
     "tags": ["🏛️ Cultura", "🍕 Gastronomía"]},

    {"nombre": "Kioto", "wiki": "Kioto", "pais": "Japón", "gustos": ["cultura", "gastronomia"], "tipo": "internacional",
     "detalle": "Templos zen entre bambúes, geishas en Gion y matcha en cada esquina.",
     "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80",
     "tags": ["🏛️ Cultura", "🌸 Tradición"]},

    {"nombre": "Atenas", "wiki": "Atenas", "pais": "Grecia", "gustos": ["cultura", "gastronomia"], "tipo": "internacional",
     "detalle": "Cuna de la democracia, el arte y la filosofía.",
     "img": "https://images.unsplash.com/photo-1555993539-1732b0258235?w=800&q=80",
     "tags": ["🏛️ Cultura", "🏛️ Historia"]},

    {"nombre": "Marrakech", "wiki": "Marrakech", "pais": "Marruecos", "gustos": ["cultura", "gastronomia"], "tipo": "internacional",
     "detalle": "Zocos laberínticos, tajines aromáticos y riads con fuentes.",
     "img": "https://images.unsplash.com/photo-1489749798305-4fea3ae63d43?w=800&q=80",
     "tags": ["🏛️ Cultura", "🍕 Gastronomía"]},

    {"nombre": "Estambul", "wiki": "Estambul", "pais": "Turquía", "gustos": ["cultura", "gastronomia"], "tipo": "internacional",
     "detalle": "Una ciudad que vive entre dos continentes: mezquitas y bazar de las especias.",
     "img": "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=800&q=80",
     "tags": ["🏛️ Cultura", "🌉 Histórico"]},

    {"nombre": "París", "wiki": "Torre Eiffel", "pais": "Francia", "gustos": ["gastronomia", "cultura", "lujo"], "tipo": "internacional",
     "detalle": "Croissants a las 7am, bistrós con vino natural y mercados bajo los puentes.",
     "img": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&q=80",
     "tags": ["🍕 Gastronomía", "💎 Lujo"]},

    {"nombre": "Tokio", "wiki": "Tokio", "pais": "Japón", "gustos": ["gastronomia", "cultura"], "tipo": "internacional",
     "detalle": "Más estrellas Michelin que ninguna otra ciudad e izakayas hasta el amanecer.",
     "img": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&q=80",
     "tags": ["🍕 Gastronomía", "🌃 Ciudad"]},

    {"nombre": "Ciudad de México", "wiki": "Ciudad de México", "pais": "México", "gustos": ["gastronomia", "cultura"], "tipo": "internacional",
     "detalle": "Tacos al pastor, mercados de Coyoacán y museos de clase mundial.",
     "img": "https://images.unsplash.com/photo-1518659526054-190340e6a4b0?w=800&q=80",
     "tags": ["🍕 Gastronomía", "🏛️ Cultura"]},

    {"nombre": "Barcelona", "wiki": "Barcelona", "pais": "España", "gustos": ["gastronomia", "cultura", "playa"], "tipo": "internacional",
     "detalle": "Arquitectura de Gaudí, la Boquería, pintxos en el Born y playa a 10 minutos.",
     "img": "https://images.unsplash.com/photo-1539037116277-4db20889f2d4?w=800&q=80",
     "tags": ["🍕 Gastronomía", "🏛️ Cultura", "🏖️ Playa"]},

    {"nombre": "Dubái", "wiki": "Dubái", "pais": "Emiratos Árabes", "gustos": ["lujo"], "tipo": "internacional",
     "detalle": "Rascacielos imposibles, desierto en 4x4 al atardecer y playas privadas.",
     "img": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800&q=80",
     "tags": ["💎 Lujo", "🌃 Ciudad"]},

    {"nombre": "Mónaco & Riviera Francesa", "wiki": "Mónaco", "pais": "Francia / Mónaco", "gustos": ["lujo", "gastronomia", "playa"], "tipo": "internacional",
     "detalle": "Casino de Montecarlo, yates en el puerto de Cannes y alta cocina.",
     "img": "https://images.unsplash.com/photo-1592635196078-9fbeb245ae2a?w=800&q=80",
     "tags": ["💎 Lujo", "🏖️ Playa"]},

    {"nombre": "Amazonas Colombiano", "wiki": "Amazonía", "pais": "Colombia", "gustos": ["naturaleza", "aventura"], "tipo": "internacional",
     "detalle": "La selva más biodiversa del planeta: delfines rosados y comunidades indígenas.",
     "img": "https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=800&q=80",
     "tags": ["🌿 Naturaleza", "⛰️ Aventura"]},

    {"nombre": "Galápagos", "wiki": "Islas Galápagos", "pais": "Ecuador", "gustos": ["naturaleza", "aventura"], "tipo": "internacional",
     "detalle": "Iguanas marinas, tortugas gigantes y leones marinos sin miedo al hombre.",
     "img": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&q=80",
     "tags": ["🌿 Naturaleza", "🐢 Fauna"]},

    {"nombre": "Cartagena de Indias", "wiki": "Cartagena de Indias", "pais": "Colombia", "gustos": ["cultura", "playa", "gastronomia"], "tipo": "local",
     "detalle": "Ciudad amurallada de colores, pesca fresca y atardeceres dorados en el Caribe.",
     "img": "https://images.unsplash.com/photo-1583531352515-8884af319dc1?w=800&q=80",
     "tags": ["🏛️ Cultura", "🏖️ Playa"]},

    {"nombre": "El Eje Cafetero", "wiki": "Eje Cafetero", "pais": "Colombia", "gustos": ["naturaleza", "aventura", "gastronomia"], "tipo": "local",
     "detalle": "Fincas cafeteras entre brumas, jeeps willys y el mejor café del planeta.",
     "img": "https://images.unsplash.com/photo-1608686207856-001b95cf60ca?w=800&q=80",
     "tags": ["🌿 Naturaleza", "☕ Café"]},

    {"nombre": "San Andrés & Providencia", "wiki": "San Andrés (isla)", "pais": "Colombia", "gustos": ["playa", "naturaleza"], "tipo": "local",
     "detalle": "El mar de los siete colores y snorkeling en arrecifes vírgenes.",
     "img": "https://images.unsplash.com/photo-1544644181-1484b3fdfc62?w=800&q=80",
     "tags": ["🏖️ Playa", "🌿 Naturaleza"]},

    {"nombre": "Parque Tayrona", "wiki": "Parque nacional natural Tayrona", "pais": "Colombia", "gustos": ["naturaleza", "playa", "aventura"], "tipo": "local",
     "detalle": "Selva tropical que llega hasta el mar Caribe, playas de piedras redondas.",
     "img": "https://images.unsplash.com/photo-1617999764988-3fb8fce5e38b?w=800&q=80",
     "tags": ["🌿 Naturaleza", "🏖️ Playa"]},

    {"nombre": "Villa de Leyva", "wiki": "Villa de Leyva", "pais": "Colombia", "gustos": ["cultura", "naturaleza"], "tipo": "local",
     "detalle": "La plaza más grande de Colombia, fósiles de dinosaurio y arquitectura colonial.",
     "img": "https://images.unsplash.com/photo-1568402102990-bc541580b59f?w=800&q=80",
     "tags": ["🏛️ Cultura", "🌿 Naturaleza"]},

    {"nombre": "Desierto de la Tatacoa", "wiki": "Desierto de la Tatacoa", "pais": "Colombia", "gustos": ["aventura", "naturaleza"], "tipo": "local",
     "detalle": "Cañones rojizos y cielos estrellados extraordinarios en pleno trópico.",
     "img": "https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=800&q=80",
     "tags": ["⛰️ Aventura", "🌿 Naturaleza"]},

    {"nombre": "Nuquí & Bahía Solano", "wiki": "Nuquí", "pais": "Colombia", "gustos": ["naturaleza", "aventura", "playa"], "tipo": "local",
     "detalle": "Selva del Chocó, ballenas jorobadas de julio a octubre y surfing salvaje.",
     "img": "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=800&q=80",
     "tags": ["🌿 Naturaleza", "🐋 Ballenas"]},

    {"nombre": "Guatapé & El Peñol", "wiki": "Guatapé", "pais": "Colombia", "gustos": ["aventura", "naturaleza", "gastronomia"], "tipo": "local",
     "detalle": "740 escalones a la cima del Peñol para la mejor vista de Antioquia.",
     "img": "https://images.unsplash.com/photo-1591721512434-7f7e8ec5e3f4?w=800&q=80",
     "tags": ["⛰️ Aventura", "🌄 Paisaje"]},
]


def calcular_destino(gustos_usuario, entorno):
    """Elige el destino que más coincide con los gustos e entorno del usuario."""
    candidatos = []
    for d in DESTINOS:
        score = len(set(gustos_usuario) & set(d["gustos"]))
        if score > 0:
            candidatos.append({**d, "score": score})

    if entorno != "indiferente":
        filtrados = [d for d in candidatos if d["tipo"] == entorno]
        if filtrados:
            candidatos = filtrados

    if not candidatos:
        elegido = dict(random.choice(DESTINOS))
    else:
        max_score = max(d["score"] for d in candidatos)
        mejores = [d for d in candidatos if d["score"] == max_score]
        elegido = dict(random.choice(mejores))

    # Reemplaza la imagen fija por una real, buscada en vivo.
    elegido["img"] = obtener_imagen_real(elegido.get("wiki", elegido["nombre"]))
    return elegido
