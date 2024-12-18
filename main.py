# -*- coding: utf-8 -*-
import xmlrpc.client
import ssl
import sys
import yaml

# ------------------------------------------------------
# Configuración y utilidades básicas
# ------------------------------------------------------

def read_app_props(env: str) -> dict:
    """Lee las propiedades de conexión desde el archivo config.yml"""
    configFile = sys.path[0] + "/config.yml"
    with open(configFile, 'r', encoding='utf-8') as f:
        configData = yaml.full_load(f).get(env)
    return configData

# ------------------------------------------------------
# Funciones para manejar la API de Odoo
# ------------------------------------------------------

def get_xmlrpc_url(url: str, port: int) -> str:
    """Construye la URL base para XML-RPC"""
    return f"{url}:{port}/xmlrpc/"

def get_xmlrpc_urlByProps(props: dict) -> str:
    """Obtiene la URL base desde las propiedades"""
    cnProps = props.get('connection')
    return get_xmlrpc_url(cnProps.get('url'), cnProps.get('port'))

def get_ws_cmclient(props: dict) -> object:
    """Obtiene el cliente 'common' de Odoo"""
    rootUrl = get_xmlrpc_urlByProps(props)
    return xmlrpc.client.ServerProxy(
        rootUrl + 'common',
        allow_none=True,
        verbose=False,
        use_datetime=True,
        context=ssl._create_unverified_context()
    )

def get_ws_rpcclient(props: dict) -> object:
    """Obtiene el cliente 'object' de Odoo"""
    rootUrl = get_xmlrpc_urlByProps(props)
    return xmlrpc.client.ServerProxy(
        rootUrl + 'object',
        allow_none=True,
        verbose=False,
        use_datetime=True,
        context=ssl._create_unverified_context()
    )

def getuid(props: dict) -> int:
    """Obtiene el UID del usuario"""
    connProps = props.get('connection')
    db = connProps.get('db')
    user = connProps.get('user')
    pwd = connProps.get('password')
    wsClient = get_ws_cmclient(props)
    return wsClient.login(db, user, pwd)

def getversion(props: dict) -> object:
    """Obtiene la versión del servidor de Odoo"""
    wsClient = get_ws_cmclient(props)
    return wsClient.version()

def request_props(props: dict, tablename: str, operation: str, conditionsArr: list = [], params: dict = {}):
    """Realiza una solicitud genérica a la API de Odoo"""
    connProps = props.get('connection')
    db = connProps.get('db')
    uid = getuid(props)
    pwd = connProps.get('password')
    wsClient = get_ws_rpcclient(props)
    return wsClient.execute_kw(db, uid, pwd, tablename, operation, conditionsArr, params)

# ------------------------------------------------------
# Test para verificar funcionalidad
# ------------------------------------------------------

def main_test():
    """Ejecuta pruebas para verificar la conexión y operaciones básicas"""
    env = "production"  # Cambiar a 'development' para entornos locales
    props = read_app_props(env)

    print("UID:", getuid(props))
    print("Versión de Odoo:", getversion(props))
    print("Permisos:",
          request_props(props, 'res.partner', 'check_access_rights', ['read'], {'raise_exception': False}))

    print("Buscar registros:",
          request_props(props, 'res.partner', 'search_read', [[['name', 'like', '%Escr%']]],
                        {'fields': ['name'], 'limit': 5}))

if __name__ == "__main__":
    print("Ejecutando pruebas de conexión con Odoo...")
    main_test()
