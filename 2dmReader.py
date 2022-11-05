# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 20:05:30 2022

@author: Sharon
"""

import os
import time
import sys
import subprocess
import shlex
from struct import pack#,unpack
import numpy as np
import shapefile as shp
import pyarrow as pa
import pyarrow.compute as pc
from pyarrow.csv import read_csv,ReadOptions,ParseOptions,ConvertOptions#write_csv
import pyqtgraph as pg
import pyqtgraph.opengl as gl

TEMP = os.path.join(os.environ['TEMP'],'temp')
#SMS Mesh element Type only Linear Elements supported
elementTypes = ['E3T', 'E4Q']


# ----------------------------------------------------------------------------------------------------- #
# ---------------------------------------- Anlegen von Funktionen ------------------------------------- #
# ----------------------------------------------------------------------------------------------------- #

## Funktion fuer Konvertierung der 2dm-Nodes in Punkt-Shapefile

def cmdPrompt(cmd,out=None):
    '''
    Parameters
    ----------
    cmd : str
        findstr call for command prompt.

    Returns
    -------
    list
        The strings found in the file.

    '''
    if out == None:
        process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
        return process.stdout.readlines()
    else:
        with open(out,'w') as io:
            subprocess.run(shlex.split(cmd),stdout=io)

def readKnoten(infile):
    '''
    Parameters
    ----------
    infile : str
        file path of 2dm File.

    Returns
    -------
    c : np.array
        Node coordinates of the Model with Z values.

    '''
    cmdPrompt(f'findstr /b ND "{infile}"', out=TEMP)

    block = read_csv(TEMP,
                     read_options = ReadOptions(column_names=[b'0',b'1',b'2',b'3',b'4']),
                     parse_options =  ParseOptions(delimiter= ' '),
                     convert_options =  ConvertOptions(column_types={b'0':pa.string(),
                                 b'1':pa.uint32(),
                                 b'2':pa.float64(),
                                 b'3':pa.float64(),
                                 b'4':pa.float32()})
                     )
    os.remove(TEMP)

    nidx = block[1].to_numpy()
    idx = np.where(np.diff(nidx,prepend=0) != 1)[0]
    if len(idx) != 0:
        msg = '2dm Datei ist nicht renummeriert!'
        # print(msg)
        for i,ii in zip(nidx[idx-1],nidx[idx]):
            print(f'Node ID Gap: {i} - {ii}')
        sys.exit(msg)

    dtype = np.dtype([('xy','<d',(2,)),
                  ('z','<f',(1,))])
    c = np.zeros(len(block),dtype)
    c['xy'][:,0] = block[2].to_numpy()
    c['xy'][:,1] = block[3].to_numpy()
    c['z'][:,0] = block[4].to_numpy()
    return c

def readKuk(infile):
    '''
    Parameters
    ----------
    infile : str
        file path of 2dm File.

    Returns
    -------
    b : np.array
        Node IDs and vals of KUKs.

    '''
    blockBCN = cmdPrompt(f'findstr /r /c:"BC_VAL N .* 1 1 " "{infile}"')
    if blockBCN != []:
        blockBCN = [list(s.strip().split()[2:]) for s in blockBCN]
        blockBCN = np.array([[s[0],s[3]] for s in blockBCN],dtype= np.float64)
        dtype = np.dtype([('id','<i',(1,)), ('z','<f',(1,))])
        b = np.zeros(len(blockBCN),dtype)
        b['id'] = blockBCN[:,0:1]-1
        b['z'] = blockBCN[:,1:]
        return b
    return []

def readElements(infile):
    '''
    Parameters
    ----------
    card : str
        SMS 2dm Card Type: E3T,E4Q (Triangular or Quadrilateral)
        https://www.xmswiki.com/wiki/SMS:2D_Mesh_Files_*.2dm

    Returns
    -------
    TYPE
        vertices of the input element from the 2dm mesh.
    '''
    #SMS Mesh element Type only Linear Elements supported
    elementTypes = ['E3T', 'E4Q']
    e = {}

    column_types={b'0':pa.string(),
                b'1':pa.uint32(),
                b'2':pa.uint32(),
                b'3':pa.uint32(),
                b'4':pa.uint32(),
                b'5':pa.uint32(),
                b'6':pa.uint32()}

    for card in elementTypes:
        cmdPrompt(f'findstr /b {card} "{infile}"',out=TEMP)

        if os.path.getsize(TEMP) == 0:
            e[card] = None
        else:
            x=4
            types = column_types.copy()
            if card == 'E3T':
                del types[b'6']
                x=3

            block = read_csv(TEMP,
                             read_options = ReadOptions(column_names=list(types.keys())),
                             parse_options =  ParseOptions(delimiter= ' '),
                             convert_options =  ConvertOptions(column_types=types)
                             )

            dtype = np.dtype([('id',np.uint32,(1,)),
                              ('elem',np.uint32,(x,)),
                              ('mat',np.uint32,(1,))])
            ii = np.zeros(len(block),dtype)
            ii['id'][:,0] = block[1].to_numpy()
            ii['elem'][:,0] = block[2].to_numpy()
            ii['elem'][:,1] = block[3].to_numpy()
            ii['elem'][:,2] = block[4].to_numpy()
            if card == 'E4Q':
                ii['elem'][:,3] =  block[5].to_numpy()
            ii['elem'] -= 1
            ii['mat'][:,0] =  block[-1].to_numpy()
            e[card] = ii

        os.remove(TEMP)
    return e

def readElementsCP(infile,knoten):
    '''
    Parameters
    ----------
    card : str
        SMS 2dm Card Type: E3T,E4Q (Triangular or Quadrilateral)
        https://www.xmswiki.com/wiki/SMS:2D_Mesh_Files_*.2dm

    Returns
    -------
    TYPE
        center points of the input element from the 2dm mesh.
    '''
    #SMS Mesh element Type only Linear Elements supported
    elementTypes = ['E3T', 'E4Q']
    dtype = np.dtype([('id',np.uint32,(1,)),
                      ('typ',np.uint8,(1,)),
                      ('elem',np.uint32,(4,)),
                      ('cp','<d',(2,)),
                      ('mat',np.uint32,(1,))])
    iii = np.zeros(0,dtype)

    column_types={b'0':pa.string(),
                b'1':pa.uint32(),
                b'2':pa.uint32(),
                b'3':pa.uint32(),
                b'4':pa.uint32(),
                b'5':pa.uint32(),
                b'6':pa.uint32()}

    for card in elementTypes:
        cmdPrompt(f'findstr /b {card} "{infile}"',out=TEMP)

        if os.path.getsize(TEMP) != 0:
            types = column_types.copy()
            if card == 'E3T':
                del types[b'6']

            block = read_csv(TEMP,
                             read_options = ReadOptions(column_names=list(types.keys())),
                             parse_options =  ParseOptions(delimiter= ' '),
                             convert_options =  ConvertOptions(column_types=types)
                             )

            ii = np.zeros(len(block),dtype)
            ii['id'][:,0] =  block[1].to_numpy()
            ii['elem'][:,0] = block[2].to_numpy()-1
            ii['elem'][:,1] = block[3].to_numpy()-1
            ii['elem'][:,2] = block[4].to_numpy()-1
            if card == 'E4Q':
                ii['elem'][:,3] =  block[5].to_numpy()-1
                ii['typ'] = 1
                ii['cp'] = knoten['xy'][ii['elem']].mean(axis=1)
            else:
                ii['cp'] = knoten['xy'][ii['elem'][:,:3]].mean(axis=1)
            ii['mat'][:,0] =  block[-1].to_numpy()
            iii = np.append(iii,ii)
        os.remove(TEMP)
    return iii[np.argsort(iii['id'].ravel())]

def makeEdges(elements):
    kanten = []
    for card,ecard in elements.items():
        if ecard is not None:
            ecard = ecard['elem']
            ikanten = np.ones((len(ecard)*ecard.shape[1],2),dtype=np.uint32)
            for i in range(ecard.shape[1]):
                ikanten[i::ecard.shape[1]] = np.stack((ecard[:,i-1],ecard[:,i])).T
            kanten += [ikanten]
    kanten = np.vstack(kanten)
    kanten = np.sort(kanten) #sort so that col1 is the smaller than 2
    kanten = kanten[np.lexsort((kanten[:,1],kanten[:,0]))] # sort col 2 then col 1
    idx = np.all(np.diff(kanten,prepend=[[0,0]],axis=0) == 0,axis=1)
    return kanten[~idx]


def printdelta(t):
    delta = time.time()-t
    print('Time Taken(s): ',round(delta))
    return time.time()
# ----------------------------------------------------------------------------------------------------- #
# ----------------------------------------- Aufrufen der Funktionen ----------------------------------- #
# ----------------------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    startTime = time.time()
    # tasks = sys.argv[1]
    tInput2dm = os.path.abspath(sys.argv[1])
    # tInput2dm = mesh = r"C:\Projects\test\hydro_as-2d.2dm"#60MB
    # tInput2dm = mesh = r"C:\Projects\starkregen\hydro_as-2d.2dm" #1.4GB
    # shpno = os.path.abspath(sys.argv[3])
    
    c = readKnoten(tInput2dm)
    e = readElements(tInput2dm)
    
    print(f'Time Taken: {startTime-time.time()}')





