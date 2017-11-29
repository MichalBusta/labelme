'''
Created on Mar 24, 2014

@author: busta
'''

import os
import sys
import codecs
import cv2

def save_icdar_annotation(fileName, shapes):
    '''
    Saves the annotation in ICDAR 2013 format
    '''
    
    f = codecs.open(fileName, 'w', 'utf-8')
    for s in shapes:
        x = int(min(s['points'][0][0], s['points'][1][0], s['points'][2][0], s['points'][3][0]))
        y = int(min(s['points'][0][1], s['points'][1][1], s['points'][2][1], s['points'][3][1]))
        xm = int(max(s['points'][0][0], s['points'][1][0], s['points'][2][0], s['points'][3][0]))
        ym = int(max(s['points'][0][1], s['points'][1][1], s['points'][2][1], s['points'][3][1]))

        f.write(u'{0},{1},{2},{3},{4}\n'.format(x, y,  xm, ym, s['label']))
    f.close()
    
def save_mock_detection(filename, shapes, regions):
    
    mockDir = filename[:-4]
    if not os.path.exists(mockDir):
        os.mkdir(mockDir)
    baseName = os.path.basename(mockDir)
    desc_file = os.path.join(mockDir, baseName + '.txt')
    f = codecs.open(desc_file, 'w', 'utf-8')
    f.write(u'RECTANGLES:\n')
    indices = getIndicesERsInShapes(shapes, regions)
    idtoindex = {}
    for i in range(len(indices)):
        regId = indices[i]
        idtoindex[regId] = i
        imageName = '{0}.png'.format(regId)
        # Ensure region label is unicode
        if isinstance(regions[regId][0], str):
            regions[regId][0] = regions[regId][0].decode('utf-8')
        f.write(u'{0} {1} {2} {3} {4} {5}\n'.format(regions[regId][1], regions[regId][2], regions[regId][3],
                                                    regions[regId][4], imageName,
                                                    regions[regId][0]))
        img = regions[regId][5]
        imageName = '{1}/{0}.png'.format(regId, mockDir)
        cv2.imwrite(imageName, img)
    f.write(u'LINES:\n')
    for i in range(len(shapes)):
        poly = (shapes[i]['points'][0][0], shapes[i]['points'][0][1], shapes[i]['points'][1][0], shapes[i]['points'][1][1],
                  shapes[i]['points'][2][0], shapes[i]['points'][2][1], shapes[i]['points'][3][0], shapes[i]['points'][3][1])
        indices = []
        regs = getERsInPolygon(poly, regions, indices)
        delim = ""
        for j in range(len(indices)):
            regId = indices[j]
            if  regions[regId][7] == 2 or  regions[regId][7] == 1:
                f.write(u'{1}{0}'.format(idtoindex[regId], delim))
                delim = " "
        f.write('\n')
    

class ICDARAnnotation(object):
    '''
    classdocs
    '''
    
    def parse(self, splits, isDetection):
        
        x = int(float(splits[0]))
        y = int(float(splits[1]))
        width = int(float(splits[2]))
        height = int(float(splits[3]))
        text = '';
        for i in range(4, len(splits)): 
            text += splits[i]
        text = text.strip()
            
        if text[0] == '"' and text[-1] == '"':
            text = text[1:-1] 
        if isDetection:
            return (x, y, x + width, y + height, text)                
        return (x, y, width, height, text) 

    def __init__(self, fileName, isDetection = False):
        '''
        Constructor
        '''
        self.fileName = fileName
        
        file = open(fileName, "r")
        self.isValid = False
        delim = ','
        self.annotations = []
        for line in file:
          line = line.strip()  
          try:
              if line.startswith("TEXT_DET:"):
                  continue
              if line.startswith("TEXT_TRANS:"):
                  continue
              
              splits = line.split(delim)
              if len(splits) > 4:
                  annotation = splits
              else:
                  delim = ','
                  splits = line.split(delim)
                  annotation = self.parse(splits, isDetection)
                  
              self.annotations.append(annotation)
              self.isValid = True
          except:
              print("Unexpected error:{0}".format(sys.exc_info()[0]))
            
        file.close()
        
    def get_shapes(self):
        
        shapes = []
        for annotation in self.annotations: 
            points = []
            label = annotation[9]
            points.append((float(annotation[0]), float(annotation[1])))
            points.append((float(annotation[2]), float(annotation[3])))
            points.append((float(annotation[4]), float(annotation[5])))
            points.append((float(annotation[6]), float(annotation[7])))
            
            line_color = None
            fill_color = None
            
            shapes.append( (label, points, line_color, fill_color) )
            
        return shapes
