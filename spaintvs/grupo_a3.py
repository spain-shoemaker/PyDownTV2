#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of spaintvs.
#
#    spaintvs is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    spaintvs is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with spaintvs.  If not, see <http://www.gnu.org/licenses/>.

# Se establece la Clase del objeto a3: que maneja los métodos para descargar
# los vídeos de la página de Antena 3 Televisón:

__author__="aabilio"
__date__ ="$12-oct-2012 11:03:38$"

import re

import Canal
import Descargar
import Utiles
import Error

url_validas = ["antena3.com", "lasexta.com", "lasextadeportes.com", "lasextanoticias.com"]

class GrupoA3(Canal.Canal):
    '''
        Clase para manejar los vídeo del grupo Antena3
    '''
    
    URL_DE_ANTENA3  = "http://www.antena3.com/"
    URL_DE_LASEXTA = "http://www.lasexta.com/"
    URL_DE_DESCARGA = "http://desprogresiva.antena3.com/"
    URL_DE_DESCARGA_LA_SEXTA = "http://deslasexta.antena3.com/"
    URL_DE_F1 = "http://www.antena3.com/gestorf1/xml_visor/"
    URL_VISOR_F1 = "http://www.antena3.com/gestorf1/static_visor/"

    '''
        Clase para manejar los vídeos de la RTVE (todos).
    '''
    
    def __init__(self, url="", opcs=None):
        Canal.Canal.__init__(self, url, opcs, url_validas, __name__)
        
    # Métodos propios del canal, start the party!
    # Attributos disponibles:
    #    - self.url (url recibida)
    #    - self.opcs (diccionario de opciones) Ver Módulo Canal "_default_opcs" para opciones
    # Métodos disponibles de clase Canal:
    #    - self.log() para mostrar por pantalla (está disponible si self.opcs["log"] es True)
    #    - self.debug() mostrar información de debug (está disponible si self.opcs["debug"] es True)
    # Comunicación de errores con nivel de aplicación:
    #    - lanzar la excepción: raise Error.GeneralPyspainTVsError("mensaje")
    
    def __getUrlDescarga(self, xml):
        try:
            urlDeDescarga = Utiles.recortar(xml, "<urlHttpVideo><![CDATA[", "]]></urlHttpVideo>")
        except:
            urlDeDescarga = self.URL_DE_DESCARGA
        return urlDeDescarga

    def __modoSalonNuevo(self, streamXML):
        '''Nuevos vídeos con extensión .m4v'''
        self.log(u"[INFO] Modo Salón")
        self.log(u"[INFO] Nuevos vídeos en formato f4v")

        self.URL_DE_DESCARGA = self.__getUrlDescarga(streamXML)

        # Soporte para una parte OFF (desde hace tiempo no se detecta un 000.mp4)
        #if streamXML.find("000.f4v"):
        #    url2down1 = self.URL_DE_DESCARGA + streamXML.split("<archivo><![CDATA[")[1].split("]")[0]
        #else:
        #    url2down1 = self.URL_DE_DESCARGA + \
        #        streamXML.split("<archivo><![CDATA[")[1].split("001.f4v]]></archivo>")[0] + "000.f4v"
        
        #if Descargar.isReachable(url2down1): # Vídeo en una parte
        #    url2down = url2down1
        #    name = streamXML.split("<nombre><![CDATA[")[1].split("]]>")[0] + ".f4v"
        #else: # Vídeo en varias partes
        #self.info(u"[!!!]  No se puede encuentra el vídeo en un archivo (000.m4v)")
        self.info(u"[INFO] El vídeo consta de varias partes")
        parts = re.findall("\<archivo\>\<\!\[CDATA\[.*\.f4v\]\]\>\<\/archivo\>", streamXML)
        if parts:
            name1 = streamXML.split("<nombre><![CDATA[")[1].split("]]>")[0]
            url2down = []
            name = []
            for i in parts:
                url2down.append(self.URL_DE_DESCARGA + i.split("<archivo><![CDATA[")[1].split("]]></archivo>")[0])
                name.append(name1 + "_" + i.split("]")[0].split("/")[-1])
        else:
            raise Error.GeneralPyspainTVsError("Grupo Antena 3. No se encuentra ninguna parte de contenido.")
        return [url2down,  name]
    
    def __modoSalon(self, streamHTML):
        #TODO: Poner cada Canal su URL, no solo a todos la de antena 3 ;)
        self.log(u"[INFO] Modo Salón")
        if streamHTML.find("so.addVariable(\"xml\"") != -1:
            streamXML = \
            Descargar.getHtml(self.URL_DE_ANTENA3 + streamHTML.split("so.addVariable(\"xml\",\"")[1].split("\"")[0])
        elif streamHTML.find("player_capitulo.xml='") != -1:
            streamXML = \
            Descargar.getHtml(self.URL_DE_ANTENA3 + streamHTML.split("player_capitulo.xml='")[1].split("'")[0])
        else:
            if streamHTML.find("<div class=\"premium\">") != -1: 
                raise Error.GeneralPyspainTVsError(u"PyDownTV no acepta la descarga de contenidos premium de las cadenas.")
            raise Error.GeneralPyspainTVsError(u"Grupo Antena 3. No se encuentra XML.")
        
        self.URL_DE_DESCARGA = self.__getUrlDescarga(streamXML)
        # Comprobar aquí si se puede descargar 000.mp4:
        if streamXML.find(".mp4") != -1:
            tipo = ".mp4"
            #url2down1 = self.URL_DE_DESCARGA + \
            #    streamXML.split("<archivo><![CDATA[")[1].split("001.mp4]]></archivo>")[0] + "000.mp4"
        elif streamXML.find(".flv") != -1:
            tipo = ".flv"
            #url2down1 = self.URL_DE_DESCARGA + \
            #    streamXML.split("<archivo><![CDATA[")[1].split("001.flv]]></archivo>")[0] + "000.flv"
        elif streamXML.find(".f4v") != -1:
            [url2down, name] = self.__modoSalonNuevo(streamXML)
            return [url2down, name]
        else:
            raise Error.GeneralPyspainTVsError("Grupo Antena 3. No se encuentra mp4, f4v ni flv")
        
        #if Descargar.isReachable(url2down1): # Vídeo completo en una parte
        #    url2down = url2down1
        #    name = streamXML.split("<nombre><![CDATA[")[1].split("]]>")[0] + tipo
        #else: # Vídeo en varias partes
        #self.info(u"[!!!]  No se puede encuentra el vídeo en un archivo (000.mp4)")
        self.info(u"[INFO] El vídeo consta de varias partes")
        parts = re.findall("\<archivo\>\<\!\[CDATA\[.*"+tipo+"\]\]\>\<\/archivo\>", streamXML)
        if parts:
            name1 = streamXML.split("<nombre><![CDATA[")[1].split("]]>")[0]
            url2down = []
            name = []
            for i in parts:
                url2down.append(self.URL_DE_DESCARGA + i.split("<archivo><![CDATA[")[1].split("]]></archivo>")[0])
                name.append(name1 + "_" + i.split("]")[0].split("/")[-1])
        else:
            raise Error.GeneralPyspainTVsError(u"Grupo Antena 3. No se encuentra niguna parte de contenido.")
        return [url2down,  name]
    
    def __modoNormalConURL(self,  streamHTML):
        url2down = streamHTML.split(".seoURL='")[1].split("'")[0]
        if not Descargar.isReachable(url2down): # A veces el vídeo de .seoURL da NOT FOUND!
            xmlURL = Utiles.recortar(streamHTML, ".xml=\'", "\'")
            streamXML = Descargar.getHtml(self.URL_DE_ANTENA3 + xmlURL)
            self.URL_DE_DESCARGA = self.__getUrlDescarga(streamXML)
            url2down =  self.URL_DE_DESCARGA + \
            streamXML.split("<archivo><![CDATA[")[1].split("]]></archivo>")[0]
            name = streamXML.split("<nombre><![CDATA[")[1].split("]]>")[0] + ".mp4"
            return [url2down, name]
        url2down = url2down.replace("deslasexta", "desprogresiva")
        try: # Parece que a veces aunque en el código aparezca el html, este no existe..
            name = Descargar.getHtml(self.URL_DE_ANTENA3 + streamHTML.split(".xml='")[1].split("'")[0]).split("<nombre><![CDATA[")[1].split("]]>")[0] + ".mp4"
        except:
            name = Utiles.recortar(streamHTML, "<title>", "</title>").replace("ANTENA 3 TV", "").replace("-", "").strip() + ".mp4" 
        return [url2down,  name]
    
    def __modoNormalUnaParte(self, streamHTML):
        xmlURL = streamHTML.split("A3Player.swf?xml=")[1].split("\"")[0]
        streamXML = Descargar.getHtml(xmlURL)
        self.URL_DE_DESCARGA = self.__getUrlDescarga(streamXML)
        url2down =  self.URL_DE_DESCARGA + \
        streamXML.split("<archivo><![CDATA[")[1].split("]]></archivo>")[0]
        name = streamXML.split("<nombre><![CDATA[")[1].split("]]>")[0] + ".mp4"
        return [url2down, name]
    
    def __modoNormalVariasPartes(self, streamHTML):
        url2down = []
        name = []
        # Delimitamos la parte del carrusel (funcionará para todos??)
        streamHTML = streamHTML.split("<a title=\"Video Anterior\"")[1].split("<a title=\"Video Siguiente\"")[0]
        partes = len(streamHTML.split("<img title="))-1
        streamPARTES = streamHTML.split("<img title=")[1:]
        self.log(u"[INFO] Número de partes:", str(partes))
        
        ret =   {
                "exito" : True,
                "num_videos" : 0,
                "mensaje"   : u"URLs obtenido correctamente",
                "videos":[],
                "titulos": [],
                "descs": []
                }
        video = {
                "url_video" : [],
                "url_img"   : None,
                "filename"  : [],
                "tipo"      : "http",
                "partes"    : 0,
                "rtmpd_cmd" : None,
                "menco_cmd" : None,
                "url_publi" : None,
                "otros"     : None,
                "mensaje"   : None
                }
        
        for i in streamPARTES:
            video = {
                "url_video" : [],
                "url_img"   : None,
                "filename"  : [],
                "tipo"      : "http",
                "partes"    : 0,
                "rtmpd_cmd" : None,
                "menco_cmd" : None,
                "url_publi" : None,
                "otros"     : None,
                "mensaje"   : None
                }
            ret["num_videos"] += 1
            ret["titulos"].append(i.split("\"")[1].split("\"")[0])
            ret["descs"].append(i.split("\"")[1].split("\"")[0])
            
            xmlURL = self.URL_DE_ANTENA3 + i.split("rel=\"/")[1].split("\"")[0]
            #print xmlURL
            streamXML = Descargar.getHtml(xmlURL)
            self.URL_DE_DESCARGA = self.__getUrlDescarga(streamXML)
            
            video["url_video"].append(self.URL_DE_DESCARGA + streamXML.split("<archivo><![CDATA[")[1].split("]")[0])
            video["url_img"] = self.URL_DE_ANTENA3+"clipping"+streamXML.split("<archivo><![CDATA[clipping")[1].split("]")[0]
            video["filename"].append(i.split("\"")[1].split("\"")[0] + '.mp4')
            video["partes"] = 1
            ret["videos"].append(video)
            
            #url2down.append(self.URL_DE_DESCARGA + streamXML.split("<archivo><![CDATA[")[1].split("]")[0])
            #ext = streamXML.split("<archivo><![CDATA[")[1].split("]")[0].split('.')[-1]
            #name.append(i.split("\"")[1].split("\"")[0] + '.' + ext)   
        
        return ret

    def normalMultiple(self, xmls):
        ret =   {
                "exito" : True,
                "num_videos" : 0,
                "mensaje"   : u"URLs obtenido correctamente",
                "videos":[],
                "titulos": [],
                "descs": []
                }
        cont = 0
        for xml in xmls:
            video = {
                    "url_video" : [],
                    "url_img"   : None,
                    "filename"  : [],
                    "tipo"      : "http",
                    "partes"    : 0,
                    "rtmpd_cmd" : None,
                    "menco_cmd" : None,
                    "url_publi" : None,
                    "otros"     : None,
                    "mensaje"   : None
                    }

            sxml = Descargar.get(xml)  
            url_desc = self.__getUrlDescarga(sxml)
            url_img = re.findall("<urlImg><!\[CDATA\[(.*)\]\]></urlImg>", sxml)[0]

            ret["num_videos"] += 1
            ret["titulos"].append(re.findall("<nombre><!\[CDATA\[(.*)\]\]></nombre>", sxml)[0])
            ret["descs"].append(re.findall("<descripcion><!\[CDATA\[(.*)\]\]></descripcion>", sxml)[0])
            
            video["url_video"].append(url_desc+re.findall("<archivo><!\[CDATA\[(.*\.mp4)\]\]></archivo>", sxml)[0])
            video["url_img"] = url_img+re.findall("<archivo><!\[CDATA\[(.*\.jpg)\]\]></archivo>", sxml)[0]
            print cont, ":", ret["titulos"][cont]
            video["filename"].append(Utiles.formatearNombre(ret["titulos"][cont]))
            video["partes"] = 1
            ret["videos"].append(video)

            cont += 1

        return ret
    
    def __modoF1(self, streamHTML):#TODO: ¡¡¡Acabar esta función para devolver todos los videos y sus partes!!!
        '''
           <param value="_urlData=http://www.antena3.com/gestorf1/swf/player_hitos/xml/data.xml&_image=http://www.antena3.com/gestorf1/pictures/361/361/malasia-portada_crop1.png&_id_list=1405&_promo1=http://www.smartadserver.com/call/pubx/15272/241149/4654/S/&_promo2=http://www.smartadserver.com/call/pubx/15272/241148/4654/S/" name="flashVars">
        '''
        streamHTML = Descargar.getHtmlUtf8(self.url)
        # Qué vídeo:
        streamVids = streamHTML.split("<ul class=\"a3_gp_visor_menu\">")[1].split("</ul>")[0].replace("\t", "")
        streamVids = streamVids.split("<li>")[1:]
        
        desc = None        
        try:
            desc = Utiles.recortar(streamHTML, "<meta property=\"og:description\" content=\"", "\"").strip()
        except:
            desc = None
        
        #self.debug(streamVids)
        ret =   {
                "exito" : True,
                "num_videos" : 0,
                "mensaje"   : u"URLs obtenido correctamente",
                "videos":[],
                "titulos": [],
                "descs": []
                }
        
        v = -1
        for i in streamVids: #todos los vídeos con todas sus partes
            video = {
                "url_video" : [],
                "url_img"   : None,
                "filename"  : [],
                "tipo"      : "http",
                "partes"    : 0,
                "rtmpd_cmd" : None,
                "menco_cmd" : None,
                "url_publi" : None,
                "otros"     : None,
                "mensaje"   : None
                }
            v+=1
            streamVid = streamVids[v]
            streamVidUrl = self.URL_DE_ANTENA3 + streamVid.split("href=\"")[1].split("\"")[0]
            self.debug(u"URL Video: " + streamVidUrl)
            streamHTML = Descargar.getHtml(streamVidUrl)
            
            #Partes
            id_list = streamHTML.split("_id_list=")[1].split("&")[0]
            listXMLurl = self.URL_DE_F1 + id_list + "_playlist.xml"
            self.debug(u"URL XML list: " + listXMLurl)
            listxml = Descargar.getHtml(listXMLurl)
            video["url_img"] = listxml.split("<picture>")[1].split("</picture>")[0].strip()
            listxml = listxml.split("<video>")[1:]
            #print listxml
            for b in listxml:
                video["partes"] += 1
                #video["mensaje"] = unicode(i.split(">")[1].split("<")[0].capitalize())
                endurl = b.split("<url>")[1].split("<")[0]
                #video["url_video"].append(endurl.replace(endurl.split("mp_")[0],"http://desprogresiva.antena3.com/"))
                video["url_video"].append(endurl.replace(endurl.split("mp_")[0],self.URL_DE_DESCARGA_LA_SEXTA))
                ext = "." + video["url_video"][-1].split(".")[-1]
                tit = b.split("<title>")[1].split("<")[0] + ext
                tit = Utiles.formatearNombre(tit)
                video["filename"].append(tit)
                
            ret["titulos"].append(unicode(i.split(">")[1].split("<")[0].capitalize()).encode('utf8'))
            ret["videos"].append(video)
            ret["num_videos"] += 1
            ret["descs"].append(unicode(desc).encode('utf8'))

        return ret


    def getInfo(self):
        '''
            Devuelve toda la información asociada a la URL recibida, de la siguiente forma:
            {
             "exito"     : bool,  <-- True (si se han obtenido videos)
             "num_video" : int,   <-- Número de vídeos obtenidos
             "mensaje"   : u"" ,  <-- Mensajes de la API (ej.: El vídeo no ha sido encontrado ["exito": False])
             "videos"    :  [{
                            "url_video" : [],   <-- Url de descarga de vídeo
                            "url_img"   : "",   <-- Url de la miniatura del video
                            "filename"  : [],   <-- Nombre de las partes para guardar en disco
                            "tipo"      : "",   <-- http, rtmp[e,..], mms, ...
                            "partes"    : int,  <-- Número de partes que tiene el vídeo
                            "rtmpd_cmd" : [],   <-- Comando rtmpdump (si tipo == rtmp) sino None
                            "menco_cmd" : [],   <-- Comando mencoder (Si tipo == rtmp) sino None
                            "url_publi" : "",   <-- Url del vídeo de publicidad asociado al vídeo
                            "otros"     : [],   <-- Lista donde se pueden pasar cosas opcionales
                            "mensaje"   : ""    <-- Mensajes de la API
                            }], <-- Debe ser una lista de tamaño "num_videos"
             "titulos"   : [u""], <-- Titulos de los videos
             "descs"     : [u""] <-- Descripción de cada vídeo
            }
            
            Los valores que no se rellenen, deberán devolver None.
            La clave "exito" es obligatoria, sino se puede encontrar el vídeo se puede devolver directamente:
            {
            "exito": False,
            "mensaje": "No se pudo descargar el video"  
            }
            
            "videos", "mesajes" y "descs" deben ser listas de cadenas (si no son None)
            "url_video", "filename", "rtmp_cmd", "menco_cmd" (de "videos") deben ser listas de cadenas (si no son None)
        '''
        img = None
        # print "[+] Procesando descarga"
        streamHTML = Descargar.getHtml(self.url)
        if self.url.find(".com/videos/") != -1: # Modo Salón
            try:
                img = self.URL_DE_ANTENA3 + Utiles.qe(streamHTML).split("player_capitulo.poster=\'/")[1].split("\'")[0]
            except:
                if streamHTML.find("<div class=\"premium\">") != -1: 
                    raise Error.GeneralPyspainTVsError(u"PyDownTV no acepta la descarga de contenidos premium de las cadenas.")
            url2down, name = self.__modoSalon(streamHTML)
        else: # Otro vídeos (No modo salón)
            self.log(u"[INFO] Vídeo normal (no Modo Salón)")
            # EN PRUEBAS (solo si hay varios vídeos...)! (23/04/2013) [RETROCOMPATIBLE]: #########
            xmls = re.findall("\.xml='(.*)'", streamHTML)
            if len(xmls) > 1:
                xmls = ["/".join(self.url.split("/")[:3])+i for i in xmls]
                return self.normalMultiple(xmls)

            #####################################################################################
            if streamHTML.find(".seoURL='") != -1: # Url directamente en HTML
                self.debug(u"Vídeo con SEO URL")
                img = self.URL_DE_ANTENA3 + streamHTML.split(".poster=\'/")[1].split("\'")[0]
                url2down, name = self.__modoNormalConURL(streamHTML)
            elif streamHTML.find("a3_gp_visor_player") != -1:
                self.log(u"[INFO] Vídeo de Fórmula 1")
                return self.__modoF1(streamHTML) # return directamente aquí (varios videos)
            else: # No está la url en el hmtl (buscar por varias partes)
                if streamHTML.find("<div class=\"visor\">") != -1: # Más de 1 parte # Quizas mejor "carrusel"?
                    return self.__modoNormalVariasPartes(streamHTML) # return directamente aquí (varios videos)
                    #url2down, name = self.__modoNormalVariasPartes(streamHTML)
                else: # Solo una parte
                    url2down, name = self.__modoNormalUnaParte(streamHTML)
        
        desc = None        
        try:
            desc = Utiles.recortar(streamHTML, "<meta property=\"og:description\" content=\"", "\"").strip()
        except:
            try:
                desc = Utiles.recortar(streamHTML, "<meta name=\"description\" content=\"", "\" />").strip()
            except:   
                desc = None
        
        #if type(url2down) == list:
        #    for i in url2down:
        #        if i.find("geobloqueo") != -1:
        #            self.log(u"[!!!] El vídeo \"" + i + "\" no se puedo descargar (geobloqueado)")
        #            url2down.remove(i)
        #            # TODO: Borrar también su nombre correspondiente
        #        
        #    # Comprobar si todas las partes están geobloqueadas (no quedan elementos en la lista):
        #    if len(url2down) == 0:
        #        raise Error.GeneralPyspainTVsError("Grupo Antena 3. Todo el contenido Geobloqueado.")
        #else:
        #    if url2down.find("geobloqueo") != -1:
        #        raise Error.GeneralPyspainTVsError("Grupo Antena 3. Todo el contenido Geobloqueado.")
        if type(name) == list:
            try:
                tit_vid = name[0].split(".")[0]
                tit_vid = tit_vid.replace("_" + tit_vid.split("_")[1], "")
            except:
                try:
                    tit_vid = Utiles.recortar(streamHTML, "<title>", "</title>").replace("ANTENA 3 TV", "").replace("-", "").strip()
                except:
                    tit_vid = "Vídeo de Grupo Antena 3"
            for i in name:
                b = Utiles.formatearNombre(i)
                name[name.index(i)] = b
        else:
            try:
                tit_vid = name.split(".")[0].replace("_" + name.split("_")[1], "")
                tit_vid = tit_vid.replace("_" + tit_vid.split("_")[1], "")
            except:
                try:
                    tit_vid = Utiles.recortar(streamHTML, "<title>", "</title>").replace("ANTENA 3 TV", "").replace("-", "").strip()
                except:
                    tit_vid = "Vídeo de Grupo Antena 3"
            name = Utiles.formatearNombre(name)
        
        #try:
        #    tit_vid = Utiles.recortar(streamHTML, "<title>", "</title>").replace("ANTENA 3 TV", "").replace("-", "").strip()
        #except:
        #    tit_vid = "Vídeo de Grupo Antena 3"
        tit_vid = tit_vid.replace("TV VIDEOS ONLINE", "").strip()
        
        return {"exito" : True,
                "num_videos" : 1,
                "mensaje"   : u"URL obtenido correctamente",
                "videos":[{
                        "url_video" : [url2down] if type(url2down) != list else url2down,
                        "url_img"   : img if img is not None else None,
                        "filename"  : [name] if type(name) != list else name,
                        "tipo"      : "http",
                        "partes"    : 1 if type(url2down) != list else len(url2down),
                        "rtmpd_cmd" : None,
                        "menco_cmd" : None,
                        "url_publi" : None,
                        "otros"     : None,
                        "mensaje"   : None
                        }],
                "titulos": [tit_vid] if tit_vid is not None else None,
                "descs": [desc] if desc is not None else None
                }

