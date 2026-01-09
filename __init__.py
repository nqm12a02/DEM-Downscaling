"""
QGIS Plugin initialization
"""

def classFactory(iface):
    """
    Load plugin class from file my_qgis_plugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .my_qgis_plugin import MyQGISPlugin
    return MyQGISPlugin(iface)

