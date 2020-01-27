'''
Created on May 31, 2010
@author: Robert Breit

Module with classes for genetic pathways
'''
import math
import glob
import os
import tempfile

import efpConfig
import efp, efpXML, efpDb

import PIL.Image

# use Python-lxml 
import lxml.sax
from lxml import etree
from xml.sax.handler import ContentHandler

#import pdb
#pdb.set_trace()
#from xml.sax import saxutils
#from xml.sax import make_parser
#from xml.sax.handler import feature_namespaces

testing_serv = open("output/testing_efpPathway.txt", "w")

filecounter = 75

class Pathway(efp.View):
    chartSpaceperChar = 0.07
    def __init__(self, name, db, img, datasets={}):
        efp.View.__init__(self, name, db, "", img)
        self.genes = []
        self.conn = None
        self.tissue = ""
        self.datasets = datasets
        self.group = None
        
    def setName(self, name):
        self.name = name

    def setDb(self, db):
        self.database = db

    def setGroup(self, group):
        self.group = group

    def setImage(self, img):
        self.colorMap = PIL.Image.open(img)
    
    def addGene(self, gene):
        self.genes.append(gene)
    
    def getGenes(self):
        return self.genes
    
    def getDatasets(self):
        return self.datasets.keys()

    def getDataset(self, datasetName=""):
        if((datasetName == "") or (datasetName not in self.datasets)):
            return None
        return self.datasets[datasetName]

    def createGene(self, gene, dataset):
        view = self.datasets[dataset]
        return view.createGene(gene)

    def getDatabase(self, dataset):
         view = self.datasets[dataset]
         #testing_serv.write("dataset name = %s\tdatabase name = %s\n"%(dataset,view.getDatabase()))
         return view.getDatabase()

    def getTissue(self, dataset, tissueName):
        view = self.datasets[dataset]
        tissues = []
        for group in view.groups:
            for tissue in group.tissues:
                if(tissue.name == tissueName):
                    return (tissue, group)

    def getPathwayMaxSignal(self, tissue, ratio):
        viewMaxSignal = 0.0
        for gene in self.genes:
            (signal,stddev) = tissue.getMeanSignal(gene)
            if ratio:
                control = self.group.getControlSignal(gene)
                if control == 0:
                    signal = 0
                else:
                    if signal != 0:
                        signal = abs(math.log(signal/control)/math.log(2))
            #assign the max signal for legend
            if signal > viewMaxSignal:
                viewMaxSignal = signal
        
        viewMaxSignal = math.floor(viewMaxSignal*100)/100
        return viewMaxSignal

    def renderAbsolute(self, tissueName, dataSource, threshold=0.0, grey_mask=False):
        outImage = self.colorMap.copy()
        (tissue, self.group) = self.getTissue(dataSource, tissueName)
        
        # Minimum color threshold for max is 10, giving us [0, 10] on the
        # color legend
        MIN_THRESHOLD = 10
        maxSignal = self.getPathwayMaxSignal(tissue, False)
        maxGreater = False
        
        if threshold >= MIN_THRESHOLD:
            max = threshold
            if maxSignal > threshold:
                maxGreater = True
        else:
            # If the user doesn't give us a reasonable value for threshold,
            # use the maximum signal from Atgenexp for this gene
            max = maxSignal
        n = 1
        sdAlert = 0
        self.startTable(False, False)
        for gene in self.genes:
            # If for some reason this gene object doesn't have a color key
            # assigned (malformed XML data?), skip it
            if gene.colorKey == (0, 0, 0):
                continue
            
            (signal,stddev) = tissue.getMeanSignal(gene)
            intensity = int(math.floor(signal * 255.0 / max))
            
            # Grey out expression levels with high standard deviations
            if signal != 0 and stddev/signal > 0.5 and grey_mask == 'on':
                color = (221, 221, 221)  # CCCCCC
            # Otherwise, colour appropriately
            else:
                color = (255, 255 - intensity, 0)
            # Add to developing Table of Expression Values
            self.appendTable(gene, signal, n, False, stddev, None, None, gene.colorKey)
            # pass an alert back to the user otherwise
            if signal != 0 and stddev/signal > 0.5 and grey_mask != 'on':
                sdAlert = 1
            
            # Perform fast color replacement
            outImage.replaceFill(self.colorMap, gene.colorKey, color)

            n += 1

        # Complete Table of Expression Values
        self.endTable()
        self.renderLegend(outImage, "Absolute", max, 0, lessThan=False, greaterThan=maxGreater)
        return (outImage,maxSignal,sdAlert)
        
        # renderAbsolute

    def renderRatio(self, mode, tissueName, dataSource, tissueName2, threshold=0.0, grey_mask=False):
        
        outImage = self.colorMap.copy()
        (tissue, group) = self.getTissue(dataSource, tissueName)
        self.group = group
        
        # Minimum color threshold for median is 0.6, giving us [-0.6, 0.6] on
        # the color legend ~ 1.5-Fold
        MIN_THRESHOLD = 0.6
        maxSignal = self.getPathwayMaxSignal(tissue, True)
        if(mode == 'Compare'):
            (tissue2, group2) = self.getTissue(dataSource, tissueName2)
            self.group = group2
            maxSignal2 = self.getPathwayMaxSignal(tissue2, True)
            maxSignal = max(maxSignal, maxSignal2)
        maxGreater = False
        
        if threshold >= MIN_THRESHOLD:
            maxThres = threshold
            if maxSignal > threshold:
                maxGreater = True
        else:
            # If the user doesn't give us a reasonable value for threshold,
            # use the maximum signal from Atgenexp for this gene
            maxThres = maxSignal
        intensity = 0
        median = 0.0
        log2 = math.log(2)
        
        n = 1
        lowAlert = 0
        if(mode == 'Compare'):
            self.startTable(True, False)
        else:
            self.startTable(True, True)
        for gene in self.genes:
            control = self.group.getControlSignal(gene)
            # If for some reason this tissue object doesn't have a color key
            # assigned (malformed XML data?), skip it
            if gene.colorKey == (0, 0, 0):
                continue
            
            (signal,stddev) = tissue.getMeanSignal(gene)
            if (signal == 0 or control == 0):
                ratioLog2 = 0
            else:
                ratioLog2  = math.log(signal / control) / log2
            ratio2Log2 = 0
            if(mode == 'Compare'):
                control2 = group2.getControlSignal(gene)
                (signal2,stddev2) = tissue2.getMeanSignal(gene)
                if (signal2 != 0 and control2 != 0):
                    ratio2Log2  = math.log(signal2 / control2) / log2
            if((ratioLog2 - ratio2Log2) == 0):
                intensity = 0
            else:
                intensity = int(math.floor(255 * (ratioLog2-ratio2Log2) / maxThres))
                intensity = efp.clamp(intensity, -255, 255)
            
            # Grey out low expression levels
            if mode == 'Relative' and signal <= 20 and grey_mask == 'on':
                color = (221, 221, 221)  # CCCCCC
            # Otherwise, colour appropriately
            elif intensity > 0:
                color = (255, 255 - intensity, 0)
            else:
                color = (255 + intensity, 255 + intensity, - intensity)
            # Add to developing Table of Expression Values
            if(mode == 'Compare'):
                self.appendTable(gene, ratioLog2-ratio2Log2, n, True, None, None, None, gene.colorKey)
            else:
                self.appendTable(gene, ratioLog2, n, True, None, signal, control, gene.colorKey)
                
            
            # Alert the user if low filter turned off
            if signal <= 20 and grey_mask != 'on':
                lowAlert = 1
            
            outImage.replaceFill(self.colorMap, gene.colorKey, color)
            n += 1

        # Complete Table of Expression Values
        self.endTable()

        self.renderLegend(outImage, "Log2 Ratio", maxThres, -maxThres, lessThan=maxGreater, greaterThan=maxGreater, isRelative=True)            
        return (outImage,maxSignal,lowAlert)
        # renderRatio


    def drawImage(self, mode, viewMaxSignal, tissue, img):
        # save generated image in output file.
        # First clean up output folder if necessary
        global filecounter

        files = glob.glob("output/*")
        if len(files) > filecounter:
            os.system("rm -f output/*")
        # Create a named temporary file with global read permissions
        outfile = tempfile.mkstemp(suffix='.png', prefix='efp-', dir='output')
        os.system("chmod 644 " + outfile[1])

        # Draw the AGI in the top left corner
        draw = PIL.ImageDraw.Draw(img)

        # draw a red box around button links to heatmaps if the searched gene is contained in the heatmap
        for extra in self.extras:
            # extra.button is true when a red box should be drawn, ie. when the searched gene is in the heatmap list
            if not extra.button == False:
                # split the coords into a list and cast to integers
                strCoords = extra.coords.split(',')
                coords = []
                for coord in strCoords:
                    coords.append(int(coord))
                # draw the box using the coords list
                draw.polygon(coords, outline=(255,0,0))

        img.save(outfile[1])
        imgFilename = outfile[1]
        filecounter += 1
        
        return imgFilename

    def getImageMap(self, mode, tissueName, datasource, useT, threshold, grey_low, grey_stddev, tissueName2=None):
        out = '<map name="imgmap_%s">'%self.name
        if useT == None:
            useT = ""
        for extra in self.extras:
            if extra.parameters == True:
                out += '<area shape="polygon" coords="%s" title="%s" href="%s&modeInput=%s&tissue=%s&tissue2=%s&override=%s&threshold=%s&modeMask_low=%s&modeMask_stddev=%s">\n' % (extra.coords, extra.name, extra.link, mode, tissueName, tissueName2, useT, threshold, grey_low, grey_stddev)
            else:
                out += '<area shape="polygon" coords="%s" title="%s" href="%s">\n' % (extra.coords, extra.name, extra.link)
        
        (tissue, self.group) = self.getTissue(datasource, tissueName)
        if(mode == "Compare" and tissueName2 != None):
            (tissue2, group2) = self.getTissue(datasource, tissueName2)
        for gene in self.genes:
            control = self.group.getControlSignal(gene)
            (signal,stddev) = tissue.getMeanSignal(gene)
            if mode == "Absolute":
                sigFloor = math.floor(signal*100)
                sigString = "Level: %s, SD: %s" % (sigFloor/100,stddev)
            else:
                if signal != 0:
                    signal = math.log(signal / control) / math.log(2)
                if (mode == "Compare"  and tissueName2 != None):
                    control2 = group2.getControlSignal(gene)
                    (value2,stddev2) = tissue2.getMeanSignal(gene)
                    signal2 = math.log(value2 / control2) / math.log(2)
                    signal =  signal - signal2
                sigFloor = math.floor(signal*100) / 100
                fold = math.floor(math.pow(2, signal)*100) / 100
                sigString = "Log2 Value: %s, Fold-Change: %s" % (sigFloor, fold)
            for coords in gene.coords:
                if gene.parameters == True:
                    out += '<area shape="polygon" coords="%s" title="%s\n | %s | \n%s" href="%s?dataSource=%s&modeInput=%s&primaryGene=%s&override=%s&threshold=%s&modeMask_low=%s&modeMask_stddev=%s">\n' % (coords, gene.getGeneId(), sigString, gene.getAnnotation(), gene.url, datasource, mode, gene.getGeneId(), useT, threshold, grey_low, grey_stddev) 
                else:
                    out += '<area shape="polygon" coords="%s" title="%s\n | %s | \n%s" href="%s">\n' % (coords, gene.getGeneId(), sigString, gene.getAnnotation(), gene.url) 
        return out

    def startTable(self, ratio, relative):
        self.table += '<style type=text/css>\n'
        # Background Colour of the Rows Alternates
        self.table += 'tr.r0 {background-color:#FFFFDD}\n'
        self.table += 'tr.r1 {background-color:#FFFFFF}\n'
        self.table += 'tr.rt {background-color:#FFFF99}\n'
        self.table += 'tr.rg {background-color:#DDDDDD}\n'
        self.table += 'td {font-family:arial;font-size:8pt;}\n'
        self.table += '</style>\n'
        self.table += '<table cellspacing=0 border=1 cellpadding=2 align=center>\n'
        # Column Headings
        self.table += '<tr class=rt><td><B>#</B></td><td><B>Gene</B></td>'
        if (relative == True):
            self.table += '<td><B>Sample signal</B></td><td><B>Control signal</B></td>'
        if (ratio == True):
            self.table += '<td><B>Log2 Ratio</B></td><td><B>Fold-Change</B></td>'
        else:
            self.table += '<td><B>Expression Level</B></td><td><B>Standard Deviation</B></td>'
        self.table += '<td></td><td><B>Links</B></td></tr>\n'


class PathwaysHandler(ContentHandler):
    def __init__(self):
        self.pathways = []
        self.datasets = {}
        datasets = efpXML.findXML(efpConfig.dataDir)
        for x in datasets:
            spec = efp.Specimen()
            xmlName = "%s/%s.xml" % (efpConfig.dataDir, x)
            spec.load(xmlName)
            views = spec.getViews()
            self.datasets[x] = views[views.keys()[0]]

    def getDatasets(self):
        return self.datasets

    def getTissues(self, dataset=""):
        if((dataset == "") or (dataset not in self.datasets)):
            return []
        view = self.datasets[dataset]
        tissues = []
        for group in view.groups:
            #for tissue in group.tissues:
            tissues.extend(group.tissues)
        return tissues

    def startElementNS(self, dict,  qname, attrs):
	uri, name = dict
        if name == 'pathway':
            self.currentPathway = Pathway(attrs.getValueByQName('name'), attrs.getValueByQName('db'), 'pathways/' + attrs.getValueByQName('img'), self.datasets)

        if name == 'coords':
            graph = (attrs.getValueByQName('graphX'), attrs.getValueByQName('graphY'))
            legend = (int(attrs.getValueByQName('legendX')), int(attrs.getValueByQName('legendY')))
            self.currentPathway.addGraphCoords(graph)
            self.currentPathway.addLegendCoords(legend)

        if name == 'extra':
            e = efp.Extra(attrs.getValueByQName('name'), attrs.getValueByQName('link'), attrs.getValueByQName("parameters"), attrs.getValueByQName('coords'), attrs.get('check'), attrs.get('checkColumn'))
            self.currentPathway.addExtra(e)
        
        if name == 'gene':
            g = self.currentPathway.createGene(attrs.getValueByQName('name'), attrs.getValueByQName('colorKey'), attrs.getValueByQName('parameters'))
            self.currentGene = g
        
        if name == 'link':
            url = attrs.getValueByQName('url')
            self.currentGene.addURL(url)
        
        if name == 'area':
            coords = attrs.getValueByQName('coords')
            self.currentGene.addCoords(coords)
        
    def endElementNS(self, qname, name):
        if name == 'pathway':
            self.pathways.append(self.currentPathway)
        
        if name == 'gene':
            self.currentPathway.addGene(self.currentGene)

    def load(self, file):
        # Create a parser
        #parser = make_parser()
        #parser.setFeature(feature_namespaces, 0)
        # Create the handler
        #parser.setContentHandler(self)
       	handler = PathwaysHandler(self) 
        # Parse the file
        #parser.parse(file)
	tree = etree.parse(file)
	lxml.sax.saxify(tree, handler)

class Gene(efpDb.Gene, efp.Tissue):
    def __init__(self, id, colorKey, parameters=None, coords=None):
        efpDb.Gene.__init__(self, id)
        efp.Tissue.__init__(self, id, colorKey)
        if parameters == "Yes":
            self.parameters = True
        else:
            self.parameters = False
        if(coords != None):
            self.addCoords(coords)


