#!/usr/bin/python

import os
import cgi
import tempfile
#import string
import efp, efpXML, efpConfig, efpPathway
import re

form = cgi.FieldStorage(keep_blank_values=1)

error = 0
errorStrings = []
alertStrings = []
lowAlert = 0
sdAlert = 0

# Retrieve cgi inputs
pathway       = form.getvalue("pathWay")
dataSource    = form.getvalue("dataSource")
tissue        = form.getvalue("tissue")
tissue2       = form.getvalue("tissue2")
thresholdIn   = form.getvalue("threshold")
mode          = form.getvalue("modeInput")
useThreshold  = form.getvalue("override")
grey_low      = form.getvalue("modeMask_low")
grey_stddev   = form.getvalue("modeMask_stddev")

modes = ["Absolute", "Relative", "Compare"]

# for auto-custom angling - need to remove several commented out lines
#if not angle == "on":
testing_efp = open("output/testing_efpPathway.txt", "w")

pathways = efpXML.findXML("pathways")
#pathw1 = efpPathway.Pathway("Pathway1", "atgenexp_plus", "pathways/Pathway1_image.tga")
#pathw1.addGene("AT1G01050", "95,125,95,280,245,280,245,125","#FF6600")
#pathw1.addGene("AT2G02370", "530,130,530,285,690,285,690,130", "#F9F3B6")
#pathw1.addGene("AT2G26170", "320,400,320,555,475,555,475,400", "#64F3E7")

if useThreshold == "":
    useThreshold = None

# Try Entered Threshold; if fails or threshold not checked use default threshold
if useThreshold != None:
    try:
        threshold = float(thresholdIn) # Convert str to float
    except:
        # Threshold string was malformed
        error = 1
        errorStr = 'Invalid Threshold Value "%s"<br>' % thresholdIn
        errorStrings.append(errorStr)
        useThreshold = None
if useThreshold == None and thresholdIn == None:
    # assign a default value for first calls
    if mode == "Relative" or mode == "Compare":
        threshold = 2.0
    else:    #Absolute or none
        threshold = 500
    firstCall = 1
else:
    threshold = float(thresholdIn)
    firstCall = 0
    
img = None
imgMap = None

# Set Developmental_Map as default DataSource
if dataSource == None:
    dataSource = efpConfig.defaultDataSource

pwhandler = efpPathway.PathwaysHandler()

if pathway == None:
    # If no pathway is selected (99% of the time this means the user just arrived
    # at the page), just show them a color map
    pathway = pathways[0]
    imgFilename = "pathways/%s_image.png" % pathway
else:
    xmlName = "pathways/%s.xml" % pathway
    pwhandler.load(xmlName)

    view = pwhandler.pathways[0]

    if mode == 'Absolute':
        if useThreshold:
            (img,viewMaxSignal,sdAlert) = view.renderAbsolute(tissue, dataSource, threshold, grey_mask=grey_stddev)
        else:
            (img,viewMaxSignal,sdAlert) = view.renderAbsolute(tissue, dataSource, grey_mask=grey_stddev)
    else:
        if useThreshold:
            (img,viewMaxSignal,lowAlert) = view.renderRatio(mode, tissue, dataSource, tissue2, threshold=threshold, grey_mask=grey_low)
        else:
            (img,viewMaxSignal,lowAlert) = view.renderRatio(mode, tissue, dataSource, tissue2, grey_mask=grey_low)
    # alert the user that the scale has changed if no threshold is set
    if useThreshold == None and firstCall != 1:
        if viewMaxSignal > threshold:
            useThresholdFlag = "on"
            thresholdLevelSuggested = viewMaxSignal
            if mode == 'Relative':
                thresholdLevelSuggested = 4
            if mode == 'Compare':
                thresholdLevelSuggested = 4
            alertStr = "Note the maximum signal value has increased to %s from %s. Use the <a href='efpPathway.cgi?dataSource=%s&modeInput=%s&tissue=%s&override=%s&threshold=%s&modeMask_low=%s&modeMask_stddev=%s'>Signal Threshold option to keep it constant at %s</a>, or enter a value in the Signal Threshold box, such as <a href='efpPathway.cgi?dataSource=%s&modeInput=%s&tissue=%s&override=%s&threshold=%s&modeMask_low=%s&modeMask_stddev=%s'>%s</a>. The same colour scheme will then be applied across all views.<br>" % (viewMaxSignal, threshold, dataSource, mode, tissue, useThresholdFlag, threshold, grey_low, grey_stddev, threshold, dataSource, mode, tissue, useThresholdFlag, thresholdLevelSuggested, grey_low, grey_stddev, thresholdLevelSuggested)
            alertStrings.append(alertStr)
        elif viewMaxSignal < threshold:
            useThresholdFlag = "on"
            thresholdLevelSuggested = viewMaxSignal
            if mode == 'Relative':
                thresholdLevelSuggested = 4
            if mode == 'Compare':
                thresholdLevelSuggested = 4
            alertStr = "Note the maximum signal value has decreased to %s from %s. Use the <a href='efpPathway.cgi?dataSource=%s&modeInput=%s&tissue=%s&override=%s&threshold=%s&modeMask_low=%s&modeMask_stddev=%s'>Signal Threshold option to keep it constant at %s</a>, or enter a value in the Signal Threshold box, such as <a href='efpPathway.cgi?dataSource=%s&modeInput=%s&tissue=%s&override=%s&threshold=%s&modeMask_low=%s&modeMask_stddev=%s'>%s</a>. The same colour scheme will then be applied across all views.<br>" % (viewMaxSignal, threshold, dataSource, mode, tissue, useThresholdFlag, threshold, grey_low, grey_stddev, threshold, dataSource, mode, tissue, useThresholdFlag, thresholdLevelSuggested, grey_low, grey_stddev, thresholdLevelSuggested)
            alertStrings.append(alertStr)
        else:
            alertStr = ""
        threshold = viewMaxSignal
    elif useThreshold == None and firstCall == 1:
        threshold = viewMaxSignal

    # alert the user if SD filter or low filter should be activated
    if grey_stddev != "on" and sdAlert == 1 and mode == 'Absolute':
        grey_stddev_flag = "on"
        if useThreshold == None:
            useThreshold = ""
        alertStr = "Some samples exhibit high standard deviations for replicates. You can use <a href='efpPathway.cgi?dataSource=%s&modeInput=%s&tissue=%s&override=%s&threshold=%s&modeMask_low=%s&modeMask_stddev=%s'>standard deviation filtering</a> to mask those with a deviation greater than half their expression value.<br>" % (dataSource, mode, tissue, useThreshold, threshold, grey_low, grey_stddev_flag)
        alertStrings.append(alertStr)
    # alert the user if SD filter or low filter should be activated
    if grey_low != "on" and lowAlert == 1 and mode == 'Relative':
        grey_low_flag = "on"
        if useThreshold == None:
            useThreshold = ""
        alertStr = "Some sample ratios were calculated with low values that exhibit higher variation, potentially leading to ratios that are not a good reflection of the biology. You can <a href='efpPathway.cgi?dataSource=%s&modeInput=%s&tissue=%s&override=%s&threshold=%s&modeMask_low=%s&modeMask_stddev=%s'>low filter below 20 units</a> to mask these.<br>" % (dataSource, mode, tissue, useThreshold, threshold, grey_low_flag, grey_stddev)
        alertStrings.append(alertStr)

    # Otherwise, we render and display the option
    imgMap = view.getImageMap(mode, tissue, dataSource, useThreshold, threshold, grey_low, grey_stddev, tissue2)

    if img != None:
        imgFilename = view.drawImage(mode, viewMaxSignal, tissue, img)
        #Create a table of Expression Values and save it in a temporary file
        expTable = view.table
        tableFile = tempfile.mkstemp(suffix='.html', prefix='efp-', dir='output')
        os.system("chmod 644 " + tableFile[1])
        tf = open(tableFile[1], 'w')
        tf.write(expTable)
        tf.close()
        chartFile = tableFile[1].replace(".html", ".png")
        view.saveChart(chartFile, mode)
    # increase view counter
    
###-------------------------------------------------------HTML codes----------------------------------------------------------------------------------------------------------------------
print 'Content-Type: text/html\n'
print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">'
print '<html>'
print '<head>'
print '  <title>Arabidopsis eFP Pathway Browser</title>'
print '  <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">'
print '  <meta name="keywords" content="Arabidopsis, genomics, expression profiling, mRNA-seq, Affymetrix, microarray, protein-protein interactions, protein structure, polymorphism, subcellular localization, proteomics, poplar, rice, Medicago, barley, transcriptomics, proteomics, bioinformatics, data analysis, data visualization, AtGenExpress, PopGenExpress, cis-element prediction, coexpression analysis, Venn selection, molecular biology, genetic pathways">'
print '  <link rel="stylesheet" type="text/css" href="efp.css"/>'
print '  <link rel="stylesheet" type="text/css" href="domcollapse.css"/>'
print '  <script type="text/javascript" src="efp.js"></script>'
print '  <script type="text/javascript" src="efp_pathway.js"></script>'
print '  <script type="text/javascript" src="domcollapse.js"></script>'
print '</head>'

print '<body><form action="efpPathway.cgi" name="efpForm" method="POST">'
print '<table width="788" border="0" align="center" cellspacing="1" cellpadding="0">'
print '<tr><td>'
print '  <span style="float:right; top:0px; left:538px; width:250px; height:75px;">'
print '    <script type="text/javascript"><!--'
print '      google_ad_client = "pub-4138435367173950";'
print '      /* BAR 234x60, created 20-Nov-2009 */'
print '      google_ad_slot = "5308841066";'
print '      google_ad_width = 234;'
print '      google_ad_height = 60;'
print '    //-->'
print '    </script>'
print '    <script type="text/javascript" src="http://pagead2.googlesyndication.com/pagead/show_ads.js">'
print '    </script>'
print '  </span>'
print "<h1 style='vertical-align:middle;'><a href='http://bar.utoronto.ca'><img src='http://bar.utoronto.ca/bbc_logo_small.gif' alt='To the Bio-Analytic Resource Homepage' border=0 align=absmiddle></a>&nbsp;<img src='http://bar.utoronto.ca/bar_logo.gif' alt='The Bio-Analytic Resource' border=0 align=absmiddle>&nbsp;<img src='http://bar.utoronto.ca/efp/eFP_logo_large.png' align=absmiddle border=0>&nbsp;Arabidopsis eFP Browser<br><img src='http://bar.utoronto.ca/images/green_line.gif' width=98% alt='' height=6px border=0></h1>"

print '</td></tr>'
print '<tr><td align="middle">'
print '    <table>'
print '      <tr align = "center">'
print '      <th>Pathway</th>'
print '      <th>Data Source</th>'
print '      <th>Tissue/Condition</th>'
print '      <th style="white-space: nowrap;">Mode'
print '<input type="checkbox" name="modeMask_stddev" title="In Absolute Mode, check to mask samples that exhibit a standard deviation of more than 50 percent of the signal value" '
if grey_stddev == "on":
    print 'checked'
print ' value="on" />'
print '<input type="checkbox" name="modeMask_low" title="In Relative Mode, check to mask the use of low expression values in ratio calculations" '
if grey_low == "on":
    print 'checked'
print ' value="on" /></th>'
print '      <th id="t1">Signal Threshold<input type="checkbox" name="override" title="Check to enable threshold" onclick="checkboxClicked(this.form)" '
if useThreshold == "on":
    print 'checked'
print       ' value="on" />'
print '</th><th></th></tr>'
print '      <tr VALIGN="top"><td style="white-space: nowrap;">'

# Help Link
print '      <img src="http://bar.utoronto.ca/affydb/help.gif" border=0 align="top" alt="Click here for instructions in a new window" onClick="HelpWin = window.open(\'http://bar.utoronto.ca/affydb/BAR_instructions.html#efp\', \'HelpWindow\', \'width=600,height=300,scrollbars,resizable=yes\'); HelpWin.focus();">&nbsp;'

# Build drop down list of pathways
print '<select name="pathWay">'

for x in pathways:
    print '    <option value="%s"' % x
    # To preserve modes between form submits
    if pathway == x:
        print 'selected'
    print '>%s</option>' % x
print '      </select></td>'

tissuetext = "var tissues = new Object();\n"
tissuetext += "var tissue_colors = new Object();\n"
# Build drop down list of Data Sources
print '<td><select selected="Developmental_Map" name="dataSource" onchange="datasetSelected(this.options[this.selectedIndex].value);">'
for x in pwhandler.datasets.keys():
    print '    <option value="%s"' % x
    # To preserve modes between form submits
    if dataSource == x:
        print 'selected'
    print '>%s</option>' % x
    t = pwhandler.getTissues(x)
    tissuetext += "tissues['%s'] = ['" % x
    tissuetext += "', '".join(map(lambda k: k.name, t))
    tissuetext += "'];\n"
    tissuetext += "tissue_colors['%s'] = ['" % x
    tissuetext += "', '".join(map(lambda k: k.colorString, t))
    tissuetext += "'];\n"

print '      </select></td>'

# Build drop down list of Tissues/Conditions
print '<td width="300px"><select id="tissue" name="tissue" style="width:300px;overflow:hidden" onBlur="this.style.width=\'300px\';" onMouseDown="if(navigator.appName==\'Microsoft Internet Explorer\') {this.style.width=\'auto\';}" onChange="this.style.width=\'300px\';this.style.backgroundColor=this.options[this.selectedIndex].style.backgroundColor;this.style.color=suitColor(this.options[this.selectedIndex].style.backgroundColor);">'
print '</select><br>'
visible = "hidden"
if(mode == "Compare"):
    visible = "visible"
print '<select id="tissue2" name="tissue2" style="width:300px;overflow:hidden;visibility:%s" onBlur="this.style.width=\'300px\';" onMouseDown="if(navigator.appName==\'Microsoft Internet Explorer\') {this.style.width=\'auto\';}" onChange="this.style.width=\'300px\';this.style.backgroundColor=this.options[this.selectedIndex].style.backgroundColor;this.style.color=suitColor(this.options[this.selectedIndex].style.backgroundColor);">' % visible
print '</select>'
print '<script type="text/javascript">'
print tissuetext
print "datasetSelected('%s', '%s', '%s');\n</script>" % (dataSource, tissue, tissue2)

print '</td>'

# Build drop down list of modes
print '      <td><select selected="Absolute" name="modeInput" onChange="changeMode(this.form);toggleElementDisplay(\'tissue2\', this.options[this.selectedIndex].value==\'Compare\')">' 

# Preserve mode between form submits. If the user selected 'Compare' as his/her
# mode, when the page reloads, the list should still have 'Compare' selected.
for x in modes:
    print '    <option value="%s"' % x
    # To preserve modes between form submits
    if mode == x:
        print 'selected'
    print '>%s</option>' % x
print '      </select></td><td>'

print '      <input type="text" id="t0" name="threshold" value="%s" ' % threshold
if useThreshold == None: 
    print 'disabled'
print '      /></td>'
print '      <td><input type="submit" value="Go"/></td></tr>'
print '    </table>'
print '    </form>'
print '</tr></td>'
print '<tr><td>'

if error:
    print '    <ul>'
    for row in errorStrings:
        print '<li class="error">%s</li>' % row
    print '    </ul>'

if len(alertStrings) > 0:
    print '    <ul>'
    for row in alertStrings:
        print '<li>%s</li>' % row
    print '    </ul>'


###----------------------print the image-------------------------------------------------------------------------------------------------------------------------------------------------


# HN: May 14 2007 - mkstemp function in python 2.4 returns ABSOLUTE path to temp file. Therefore, need to split on "/" and return just the relative path    
imgFile = imgFilename;
temp_imgPath = imgFilename.split("/")
last_element = temp_imgPath[-1]
match = re.search('^efp', last_element) 
if match is not None:
    imgFile = 'output/%s'%(last_element)
print '  <img src="%s" border="0" ' % imgFile
if(imgMap != None):
    print 'usemap="#imgmap_%s">' % view.name
print '%s' % imgMap
print '</tr></td>'

if mode != None and not error:
    # Creates Button and Link to Page for Table of Expression Values
    print '<tr align="center"><td><br>'
    temp_tablePath = tableFile[1].split("/")
    tableFile_name = 'output/%s'%(temp_tablePath[-1])
    print '<input type="button" name="expressiontable" value="Click Here for Table of Expression Values" onclick="resizeIframe(\'ifr1\', ifr1);popup(\'table1\', \'fadein\', \'center\', 0, 1)">'
    print '&nbsp; &nbsp;'
    tableChart_name = tableFile_name.replace(".html", ".png")
    print '<input type="button" name="expressionchart" value="Click Here for Chart of Expression Values" onclick="popup(\'chart1\', \'fadein\', \'center\', 0, 1)">'
    print '</td></tr>'
    print '<script type="text/javascript" src="popup.js"></script>'
    print '<script type="text/javascript">'
    popup_content = '<span style="color:#000000"><b>For table download right click <a href="%s">here</a> and select "Save Link As ..."</b></span>' % tableFile_name
    popup_content += '<div class="closewin_text">'
    popup_content += '<a href="" onclick="popdown(\\\'table1\\\');return false;">'
    popup_content += '<span style="color:#000000">[Close]</span></a><br><br>'
    popup_content += '<a href="" onclick="switchPopup(\\\'table1\\\', \\\'chart1\\\');return false;">'
    popup_content += '<span style="color:#000000">[Switch to<br> Chart]</span></a></div>'
    popup_content += '<div class="chart"><iframe id="ifr1" name="ifr1" width=900 frameborder=0 src="%s">' % tableFile_name
    popup_content += 'Your browser doesn\\\'t support iframes. Please use link abvoe to open expression table</iframe></div>'
    popup_width = '1000';
    bg_color = '#FFFFFF';
    print "loadPopup(\'table1\',\'%s\',\'%s\',%s);" % (popup_content, bg_color, popup_width)
    popup_content = '<div class="closewin_text">'
    popup_content += '<a href="" onclick="popdown(\\\'chart1\\\');return false;">'
    popup_content += '<span style="color:#000000">[Close]</span></a><br><br>'
    popup_content += '<a href="" onclick="resizeIframe(\\\'ifr1\\\', ifr1);switchPopup(\\\'chart1\\\', \\\'table1\\\');return false;">'
    popup_content += '<span style="color:#000000">[Switch to<br>Table]</span></a><br><br>'
    popup_content += '<a href="" onclick="zoomElement(\\\'image1\\\', 0.1);return false;">'
    popup_content += '<span style="color:#000000">[Zoom +]</span></a><br>'
    popup_content += '<a href="" onclick="zoomElement(\\\'image1\\\', -0.1);return false;">'
    popup_content += '<span style="color:#000000">[Zoom -]</span></a><br>'
    popup_content += '<a href="" onclick="zoomElement(\\\'image1\\\', 0);return false;">'
    popup_content += '<span style="color:#000000">[Reset<br>zoom]</span></a></div>'
    popup_content += '<div class="chart"><img id="image1" height=580 src="%s"><br></div>' % tableChart_name
    print "loadPopup(\'chart1\',\'%s\',\'%s\',%s);" % (popup_content, bg_color, popup_width)
    print "</script>"
    print '<tr><td><img src="http://bar.utoronto.ca/bbclone/stats_image.php" title="" name="thumbnail" border="0" width="0px" height="0px"></tr></td>'
print '</table>'
print '</body>'
print '</html>'

