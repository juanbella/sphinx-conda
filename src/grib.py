#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import datetime
import pygrib
import time
import os

import pandas as pd


def write_csv(csv_read, csv_write, date_from, date_to):
    """
    Escribe los datos de un csv de una fecha dada en otro fichero csv
    :param csv_read: fichero con los datos a leer
    :param csv_write: fichero en el que escribir los datos
    :param date_from: fecha a partir de la cual escribir los datos.
                        None -> A partir de la primera fecha posible
    :param date_to: fecha hasta la que escribir los datos
                        None -> Hasta la última fecha posible
    """
    csv_reader = csv.reader(csv_read, delimiter=',', quotechar='|')
    csv_writer = csv.writer(csv_write, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

    next(csv_reader)  # Nos saltamos la cabecera del fichero

    for row in csv_reader:
        date = datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        if date_from != None and date_to != None \
                and (date.day < date_from.day or date.day > date_to.day):
            continue
        elif date_from == None and date_to != None \
                and date.day > date_to.day:
            continue
        elif date_from != None and date_to == None \
                and date.day < date_from.day:
            continue
        csv_writer.writerow(row)


def concat_csv(date_from=None, date_to=None, output_file=None, *inputfiles):
    """
    Concatena los ficheros pasados como argumento en función del rango
    de fechas pasadas como argumento
    :param date_from: fecha a partir de la cual escribir los datos.
                        None -> A partir de la primera fecha posible
    :param date_to: fecha hasta la que escribir los datos
                        None -> Hasta la última fecha posible
    :param output_file: nombre del fichero en el que guardar los
                        datos concatenados
    :param inputfiles: lista de los nombres de los ficheros a concatenar

    """
    # csv_file_1 = open('/media/sf_Compartida/ficheros_grib/csv/csv_IICCAN00i3_ECMWF.20170916', 'r')
    # csv_file_2 = open('/media/sf_Compartida/ficheros_grib/csv/csv_IICCAN00i3_ECMWF.20170917', 'r')
    # csv_file_3 = open('/media/sf_Compartida/ficheros_grib/csv/csv_IICCAN00i3_ECMWF.20170918', 'r')
    csv_file_output = open('/media/sf_Compartida/ficheros_grib/csv/output', 'w', newline='')

    # csv_file_output  = open(output_file, 'w', newline='')
    csv_writer = csv.writer(csv_file_output, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(["date", "forecast_date", "variable coords", "value"])

    date_from = datetime.datetime(year=2017, month=9, day=19, hour=0, minute=0, second=0)
    date_to = datetime.datetime(year=2017, month=9, day=19, hour=0, minute=0, second=0)

    for file in inputfiles:
        f = open(file, 'r')
        write_csv(f, csv_file_output, date_from, date_to)
        f.close()

    csv_file_output.close()
    return


def grib_to_csv(grib_file=None, csv_filename=None, days=None):
    """
    Introduce los datos de un fichero grib en un fichero csv

    Los datos de la medición se introducen en un fichero csv organizado
    por la fecha de la toma de datos, fecha de la predicción, nombre
    de la variable y coordenadas de dónde se ha tomado y valor.

    :param grib_file: nombre del fichero del que tomar los datos
    :param csv_filename: nombre del fichero en el que volcar los datos
    :param days: número de días a incluir en el diccionario
                            None -> todos los días (valor por defecto)
                            0 -> Día de la toma de datos
                            1 -> Día de la toma de datos más un día

    """
    # grib = pygrib.open(grib_file)
    # grib = pygrib.open('../grib/IICCAN00t3_ECMWF.20170906')
    grib = pygrib.open('/media/sf_Compartida/ficheros_grib/IICCAN00i3_ECMWF.20170918')
    # csv_file = open(csv_filename, 'w', newline='')
    # csv_file = open('../csv/' + grib.name[-25:], 'w', newline='')
    csv_file = open('/media/sf_Compartida/ficheros_grib/csv/csv_' + grib.name[-25:], 'w', newline='')
    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(["date", "forecast_date", "variable coords", "value"])

    dates = []
    for grb in grib:
        if not grb.analDate in dates:  # obtención de las fechas de toma de datos
            dates.append(grb.analDate)

    dicc = {}
    for date in dates:
        # comproboación del rango de datos a incluir en el fichero
        if days != None:
            time_max = date + datetime.timedelta(days=days)

        dicc[date] = {}
        data = grib.select(analDate=date)

        for grb in data:
            time = date + datetime.timedelta(hours=grb['endStep'])
            if days != None and time.day > time_max.day:
                continue

            values = grb.values
            lat, lon = grb.latlons()
            variable_name = grb['name']

            if not time in dicc[date]:
                dicc[date][time] = {}

            for i in range(lat.shape[0]):
                for j in range(lat.shape[1]):
                    coords = lat[i][j], lon[i][j]
                    key = variable_name + str(coords)
                    csv_writer.writerow([time] + [date] + [key] + [values[i][j]])

    csv_file.close()
    return


def crear_matriz_datos(days=0, inputfiles=None):
    """
    Concatena los ficheros pasados como argumento para crear una matriz
    de datos

    A partir de los fichesros pasados, crea una matriz de datos en la
    que las fechas de generacion y predicción tiene una diferencia de
    los días pasados como argumento

    :param days: Número de días entre las fechas de generación y predicción
    :param inputfiles: lista con la ruta a los ficheros a concatenar
    :return: dataframe con los datos obtenidos
    """

    matriz = pd.DataFrame()

    for file in inputfiles:
        df = pd.read_pickle(file)
        criterion = df.index.map(
            lambda x: x.day == df.loc[x, 'generation date'].day + days)
        df = df[criterion == True]
        matriz = pd.concat([matriz, df])

    matriz.to_pickle('/media/sf_Compartida/ficheros_grib/semana/pickle/output_matrix')
    return matriz


def actualizar_matriz_datos(matriz_datos, inputfiles):
    """
    Actualiza la matriz de datos con los registros correspondientes de
    los ficheros pasados

    Concatena los registros de los dataframes pasados como argumento a
    la matriz de datos. Únicamente se escogen los que tienen el mismo
    rango fecha de predicción/fecha de generación

    :param matriz_datos: ruta al fichero pickle que contiene la matriz
                            de datos
    :param inputfiles: lista con la ruta a los ficheros pickle que
                            introducir en la matriz de datos
    :return: matriz de datos actualizada
    """
    matriz = pd.read_pickle(matriz_datos)

    days = matriz.index[0].day - matriz['generation date'][0].day

    for file in inputfiles:
        df = pd.read_pickle(file)
        criterion = df.index.map(
            lambda x: x.day == df.loc[x, 'generation date'].day + days)
        df = df[criterion == True]
        # comprobar que no esta ya en el dataframe
        matriz = pd.concat([matriz, df])

    matriz.to_pickle(matriz_datos)
    return matriz


def grib_to_dicc(grib, days=None):
    """
    Introduce los datos de un fichero grib en un diccionario

    Los datos de la medición se introducen en un diccionario ordenado
    por la fecha de la toma de datos, fecha de la predicción y nombre
    de la variable y coordenadas de dónde se ha tomado.

    :param grib: objeto grib que contiene los datos del fichero
    :param days: número de días a incluir en el diccionario
                            None -> todos los días (valor por defecto)
                            0 -> Día de la toma de datos
                            1 -> Día de la toma de datos más un día
    :return: diccionario con los datos
    """

    dates = []
    for grb in grib:
        if not grb.analDate in dates:  # obtención de las fechas de toma de datos
            dates.append(grb.analDate)

    dicc = {}
    for date in dates:
        # comproboación del rango de datos a incluir en el diccionario
        if days != None:
            time_max = date + datetime.timedelta(days=days)

        dicc[date] = {}
        data = grib.select(analDate=date)

        for grb in data:

            #Comprobamos que no nos salimos del rango de fechas a incluir
            time = date + datetime.timedelta(hours=grb['P1'])
            if days != None and time.day > time_max.day:
                continue

            values = grb.values
            lat, lon = grb.latlons()
            variable_name = grb['name']

            if not time in dicc[date]:
                dicc[date][time] = {}

            #obtenemos las coordenadas y valores de las mismas
            #y las introducimos ene l diccionaro
            for i in range(lat.shape[0]):
                for j in range(lat.shape[1]):
                    coords = lat[i][j], lon[i][j]
                    key = variable_name + str(coords)
                    dicc[date][time][key] = values[i][j]
    return dicc


def grib_to_df(grib_file=None, days=None):
    """
    Introduce los datos de un fichero grib en un dataframe

    Los datos de la medición se introducen en un dataframe con la fecha
    de la predicción como índice.

    :param grib_file: nombre del fichero del que tomar los datos
    :param days: número de días a incluir en el diccionario
                            None -> todos los días (valor por defecto)
                            0 -> Día de la toma de datos
                            1 -> Día de la toma de datos más un día
    :return: lista con los dataframes creados    """

    grib = pygrib.open(grib_file)
    # grib = pygrib.open("../grib/TLsTxcTOsoSYmtRzKDl0e75I4HAjqDApvbc.grb")
    # grib = pygrib.open('../grib/test_20170301.grib')
    # grib = pygrib.open('../grib/Historicoprueba2.grib')
    # grib = pygrib.open('../grib/IICPEN00t3_ECMWF.20170918')

    dicc = grib_to_dicc(grib, days)

    dataframes = []
    for date in dicc:
        # file_name = '../txt/dataframe_' \
        #             + str(grib.name[-22:-15] + '_' + grib.name[-8:]) \
        #             + '.txt'
        # file = open(file_name, 'w')
        df = pd.DataFrame.from_dict(dicc[date], orient='index')
        df.index.name = 'prediction date'
        df.insert(0, 'generation date', date)

        df.to_pickle('../pickle/' + grib.name[-25:])
        # df.to_pickle('/media/sf_Compartida/ficheros_grib/semana/pickle/' + grib.name[-25:])
        # file.write(str(df))
        # file.close()
        dataframes.append(df)

    grib.close()

    return dataframes


if __name__ == '__main__':
    start_time = time.time()

    # grib_to_df(days=None)
    # grib_to_csv(forcasted_day=None)
    # concat_csv()
    # csv_file_1 = '/media/sf_Compartida/ficheros_grib/csv/csv_IICCAN00i3_ECMWF.20170916'
    # csv_file_2 = '/media/sf_Compartida/ficheros_grib/csv/csv_IICCAN00i3_ECMWF.20170917'
    # csv_file_3 = '/media/sf_Compartida/ficheros_grib/csv/csv_IICCAN00i3_ECMWF.20170918'
    #
    # concat_csv(None, None, None, csv_file_1, csv_file_2, csv_file_3)
    # crear_matriz_datos(0,'../pickle/IICPEN00t3_ECMWF.20170916','../pickle/IICPEN00t3_ECMWF.20170917','../pickle/IICPEN00t3_ECMWF.20170918')


    for entry in os.scandir("../grib"):
        if entry.name.startswith("IIC"):
            grib_to_df(entry.path,None)

    # ficheros = []
    # for entry in os.scandir("/media/sf_Compartida/ficheros_grib/semana/pickle"):
    #     if entry.name.startswith("IICPEN00t3"):
    #         ficheros.append(entry.path)
    #
    # crear_matriz_datos(1,ficheros)

    # actualizar_matriz_datos('/media/sf_Compartida/ficheros_grib/semana/pickle/output_matrix',
    #                         ['/media/sf_Compartida/ficheros_grib/semana/pickle/IICPEN00t3_ECMWF.20170927'])

    print("--- %s seconds ---" % (time.time() - start_time))
