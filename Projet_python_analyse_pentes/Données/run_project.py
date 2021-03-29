#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on %(date)s : 13/01/2020 - 20/01/2020 - 22/01/2020

@author: %(username)s : @efize & @claverdure
"""

import numpy as np
from PIL import Image
from math import sqrt, atan, pi
import json 
import matplotlib.pyplot as plt


####### Transformations nécessaires et dictionnaire

def transformation_tiff_array():
    """ Cette fonction transforme une image .tif en tableau numpy array"""
    im = Image.open('La_Blanche.tif')
    im.show()
    ar = np.array(im)
    return ar
    

def enregistrer(tableau, nom):
    """Cette fonction permet d'enregistrer un tableau sous forme 
    d'image
    paramètre :
    tableau : tableau de couleur à transformer en image
    :tableautype: nd.array
    nom : nom du fichier enregistré
    :nomtype: string"""
    im = Image.fromarray(tableau) #converti le tableau en image
    im.save('Risque.tif')
        

####### Création de différents tableaux numpy : pente & aspects    

def carte_de_pente(tableau):
    """ Cette fonction calcule la pente sur la carte
    d'après la méthode de Horn
    paramètres : 
    tableau : image initiale transformée en matrice
    :tableautype: nd.array
    return : tableau de pente 
    :rtype: nd.array"""#pente est-ouest 
    array_pente = np.zeros((398,398))
    for i in range(398):
        for j in range(398):
            a = tableau[i-1][j-1]
            b = tableau[i-1][j]
            c = tableau[i-1][j+1]
            d = tableau[i][j-1]
            e = tableau[i][j]
            f = tableau[i][j+1]
            g = tableau[i+1][j-1]
            h = tableau[i+1][j]
            k = tableau[i+1][j+1]
            dz_dx = ((c+2*f+k)-(a+2*d+g))/(8*5) #pente est_ouest
            dz_dy = ((g+2*h+k)-(a+2*b+c))/(8*5) #pente nord_sud
            pente1 = sqrt((dz_dx)**2+(dz_dy)**2)
            pente = atan(pente1)*180/pi
            array_pente[i][j] = pente
    return array_pente

def carte_aspect(tableau):
    """Cette fonction calcule la carte d'aspect 
    d'après la méthode de Horn
    paramètres : 
    tableau : image initiale transformée en matrice
    :tableautype: nd.array
    return : tableau d'aspect en °
    :rtype: nd.array"""
    array_aspect = np.zeros((398,398))
    for i in range(398):
        for j in range(398):
            a = tableau[i-1][j-1]
            b = tableau[i-1][j]
            c = tableau[i-1][j+1]
            d = tableau[i][j-1]
            e = tableau[i][j]
            f = tableau[i][j+1]
            g = tableau[i+1][j-1]
            h = tableau[i+1][j]
            k = tableau[i+1][j+1]
            dz_dx = ((c+2*f+k)-(a+2*d+g))/(8*5) #pente est_ouest
            dz_dy = ((g+2*h+k)-(a+2*b+c))/(8*5) #pente nord_sud
            aspect = atan(dz_dx/dz_dy)
            if dz_dx < 0 :
                if dz_dy < 0 :
                    array_aspect[i][j]=180-(aspect*180/pi)
                else :
                    array_aspect[i][j]=-(aspect*180/pi)
            else : 
                if dz_dy < 0 :
                    array_aspect[i][j]=180-(aspect*180/pi)
                else :
                    array_aspect[i][j]=360-(aspect*180/pi)
    return array_aspect

########## Création de cartes
    

def colorer(tableau):
    image = np.zeros((400,400,3), dtype=np.uint8)
    with open('colors.json', "r") as read_file :
        data = json.load(read_file)
    for i in range(398):
        for j in range(398):
            if abs(tableau[i][j]) <= 30 : 
                image[i+1][j+1] = data["colors"][0]["color"]
            elif abs(tableau[i][j]) > 30 and abs(tableau[i][j]) <= 35 :
                image[i+1][j+1] = data["colors"][1]["color"]
            elif abs(tableau[i][j]) > 35 and abs(tableau[i][j]) <= 40 :
                image[i+1][j+1] = data["colors"][2]["color"]
            elif abs(tableau[i][j]) > 40 and abs(tableau[i][j]) <= 45 :
                image[i+1][j+1] = data["colors"][3]["color"]
            else : 
                image[i+1][j+1] = data["colors"][4]["color"]
    return image
                
        
    
def risque(pente, aspect):
    """ Cette fonction permet de colorer en bleu foncées les pentes 
    orientées vers le Nord-Est et supérieures à 35°. Pour cela on utilise
    l'aspect et la pente. 
    paramètres : 
    pente : tableau des pentes
    :pentetype: nd.array
    aspect : tableau des aspects
    :aspecttype: nd.array
    return : tableau uint8 coloré
    :rtype: nd.array uint8"""
    tableau = np.zeros((400,400,3), dtype=np.uint8)
    for i in range(398):
        for j in range(398): 
            if pente[i][j]>35 :
                if (aspect[i][j]<90) or (aspect[i][j]>290) :
                    tableau[i+1][j+1]=[0,51,102] #bleu foncé
                else :
                    tableau[i+1][j+1] =[116,208,241] #bleu clair
            else : 
                tableau[i+1][j+1]=[255,255,255]
    return tableau


        
def calcul_pixel_itinéraire():
    """ Cette fonction permet de caluler les pixels que l'on trouve
    sur le trajet et sur le terrain. On utilise pour ça le modèle
    numérique de terrain
    paramètres : 
    return : pixels
    :rtype: liste """
    chemin = []
    coin = [970700.0000000000, 6425000.0000000000]
    with open('route.geojson') as json_file:
        coordonnees = json.load(json_file)
    trajet = coordonnees['features'][0]['geometry']['coordinates']
    for i in range(len(trajet)): 
        trajet2 = (trajet[i][0]-coin[0])/5
        trajet3 = -(trajet[i][1]-coin[1])/5 
        #les directions sont inversées en (N,E) de (S,E) vecteurs origines sont inversés 
        chemin.append([trajet2,trajet3])
    return chemin


def altitude_terrain(chemin, tableau):
    """ Cette fonction renvoie la pente calculer en chaque point du terrain 
    se trouvant sur le trajet. On utilise la méthode d'interpolation jointe
    par mail.
    paramètres : 
    chemin : point du trajet
    :chemintype: tuple(float,float)
    tableau : tableau des altitudes
    :tableautype: nd.array
    return : liste de pente 
    :rtype: liste"""
    altitude_chemin = []
    for i in range(len(chemin)):
        x = chemin[i][0]
        y = chemin[i][1]
        #on cherche les 4 pixels entourant notre point
        x1 = int(chemin[i][0])
        x2 = int(chemin[i][0])+1
        y1 = int(chemin[i][1])
        y2 = int(chemin[i][1])+1
        #on fait ensuite l'interpolation de l'altitude à ce point précis
        h1 = tableau[x1,y1]
        h2 = tableau[x1,y2]
        h3 = tableau[x2,y1]
        h4 = tableau[x2,y2]
        altitude1 = (y1-y)*h1+(1-(y1-y))*h2
        altitude2 = (y2-y)*h3+(1-(y2-y))*h4
        altitude = (x1-x)*altitude1 + (1-(x1-x))*altitude2
        altitude_chemin.append(altitude)
        
        
    #Mise en place du graphe 

    plt.plot(altitude_chemin)
    plt.xlabel('numero point')
    plt.ylabel('altitude (m)')
    plt.suptitle('evolution altitude le long du chemin')
    plt.show()
    
    
    return altitude_chemin
            

    
def pente_itinéraire(chemin, altitude_chemin):
    """ Cette fonction calcule la pente entre 2 points de l'itinéraire
    paramètres : 
    chemin : points du trajet
    :chemintype: liste(float)
    altitude_chemin : altitude précise des points du chemin
    :altitude type: liste"""
    #pente = dénivelé / longueur parcourue
    pente_chemin = []
    for j in range(len(chemin)-1):
        distance = sqrt((chemin[j+1][0]-chemin[j][0])**2+(chemin[j+1][1]-chemin[j][1])**2)*5
        denivele = abs(altitude_chemin[j+1] - altitude_chemin[j])
        pente = abs(atan(denivele/distance))*180/pi
        pente_chemin.append(pente)
        
        
    #Mise en place du graphe 
    
    plt.plot(pente_chemin)
    plt.xlabel('numero point')
    plt.ylabel('pente (degres)')
    plt.suptitle('evolution pente le long du chemin')
    plt.show()
    
    
    
    return pente_chemin

def densification_chemin (chemin): 
    """ Cette fonction permet de densifier le nuage de points d'altitudes 
    de notre chemin pour avoir un trace plus precis
    paramètres : chemin
    return : chemin_2
    :rtype: liste """
    chemin_2 = []
    for i in range (len(chemin)-1):
        x0 = chemin[i][0]
        x1 = chemin[i+1][0]
        y0 = chemin[i][1]
        y1 = chemin[i+1][1]
        dist = sqrt((x1-x0)**2 + (y1 - y0)**2)
        if dist <= 1 :
            chemin_2 += [[x1 , y1]]
        else:
            n = int(dist)
            dx = (x1 - x0)/(n+1)
            dy = (y1 - y0)/(n+1)
            for i in range (n):
                xi = x0 + i*dx
                yi = y0 + i*dy
                chemin_2 += [[xi , yi]]
            chemin_2 += [[x1 , y1]]
    return chemin_2
    



if __name__ == "__main__":
    
    tableau = transformation_tiff_array()
    
    pente = carte_de_pente(tableau)
    
    aspect = carte_aspect(tableau)
    
    hypsometrique = colorer(pente)
    
    risque = risque(pente, aspect)
    
    enregistrer(risque, 'risque.tif')
    
    chemin = calcul_pixel_itinéraire()
    
    chemin_densif = densification_chemin(chemin)
    
    altitude_chemin = altitude_terrain(chemin_densif, tableau)
    
    pente_chemin = pente_itinéraire(chemin_densif, altitude_chemin)
    
    
    
    
