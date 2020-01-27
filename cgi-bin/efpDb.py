#!/usr/bin/python
#
# Module for retrieving gene expression data from the Department
# of Botany's Atgenexpress database

import MySQLdb
import re
import sys
import efpConfig
import efp

testing_efp = open("output/testing_efpDb.txt", "w")

class Gene:
    def __init__(self, id, database):
        self.conn = None
        self.connOrtho = None
        self.annotation = None
        self.alias = None
        self.geneId = None
        self.probesetId = None
        self.ncbiId = None
        self.database = database
        self.lookup = None
        self.webservice_gene = None
	self.andquery = ""
        self.queryGene = None
	#if efpConfig.species != "POP" and id != None:
           #id = re.sub("(\.\d)$", "", id) # reduce splice variants (remove .n)
	#else:
	#   self.andquery = "AND t1.pgi LIKE 'POP" + "%"
	#   self.andquery = self.andquery + '%' + "\'"
        self.retrieveGeneData(id, self.andquery)
        if(self.geneId == None):
            self.ncbiToGeneId(id)
            self.retrieveGeneData(self.geneId, self.andquery)
        # Modification for eFP Brachy
        if (self.geneId == None):
            if (re.search(r'\.1$', id, re.I)):
                id = re.sub(r'\.1$', '.2', id)
                self.retrieveGeneData(id, self.andquery)

    
    def getGeneId(self):
        #primaryGene = re.sub("a","A", primaryGene)
        #primaryGene = re.sub("T","t", primaryGene)
        #primaryGene = re.sub("G","g", primaryGene)
        #primaryGene = re.sub("C","c", primaryGene)
        #primaryGene = re.sub("M","m", primaryGene)
        return self.geneId

    
    def getProbeSetId(self):
        #primaryGene = re.sub("A","a", primaryGene)
        #primaryGene = re.sub("T","t", primaryGene)
        
        return self.probesetId
    
    def getNcbiId(self):
        return self.ncbiId
    
    def setQueryGene(self, queryGene):
        self.queryGene = queryGene
    
    '''
    # name: retrieveGeneData
    # desc: Retrieves the probeset ID that corresponds to the given gene ID
    '''
    def retrieveGeneData(self, id, andquery):
    	    
	if(id == None):
            return
        if(efpConfig.DB_ANNO == None or efpConfig.DB_LOOKUP_TABLE == None or efpConfig.LOOKUP[self.database] == "0"): # annotations db not defined
            self.retrieveLookupGeneData(id)
            return

        if(self.conn == None):
            self.connect(efpConfig.DB_ANNO)
        
        cursor = self.conn.cursor()
	testing_efp.write("SELECT t1.%s, t1.%s FROM %s t1 WHERE (t1.%s=%%s or t1.%s=%%s) AND t1.date=(SELECT MAX(t2.date) FROM %s t2) %s\n"%(efpConfig.DB_LOOKUP_GENEID_COL, efpConfig.DB_LOOKUP_ARABIDOPSIS_COL, efpConfig.DB_LOOKUP_TABLE, efpConfig.DB_LOOKUP_ARABIDOPSIS_COL, efpConfig.DB_LOOKUP_GENEID_COL, efpConfig.DB_LOOKUP_TABLE, andquery))
	testing_efp.write("id = %s\n"%id)
	select_cmd = "SELECT t1.%s, t1.%s FROM %s t1 WHERE (t1.%s=%%s or t1.%s=%%s) AND t1.date=(SELECT MAX(t2.date) FROM %s t2) %s" % \
                     (efpConfig.DB_LOOKUP_GENEID_COL, efpConfig.DB_LOOKUP_ARABIDOPSIS_COL, efpConfig.DB_LOOKUP_TABLE, efpConfig.DB_LOOKUP_ARABIDOPSIS_COL, efpConfig.DB_LOOKUP_GENEID_COL, efpConfig.DB_LOOKUP_TABLE, andquery)
        cursor.execute(select_cmd,(id, id))
	row = cursor.fetchall()
        cursor.close()
        self.conn = None
        if len(row) > 0:
            self.geneId = row[0][0]
            self.probesetId = row[0][1]
        return

    '''
    # name: retrieveLookupGeneData
    # desc: Checks whether a gene exists when no lookup is available e.g. RNA-seq Data
    '''
    def retrieveLookupGeneData(self, id):
        
        if(id == None):
            return
    
        if(self.conn == None):
            self.connect(self.database)
        
        matching_gene = id.partition("_")
	matching_gene = matching_gene[0] 
        cursor = self.conn.cursor()
        cursor.execute("SELECT data_probeset_id FROM sample_data WHERE data_probeset_id LIKE %s", (matching_gene + '%',))
        row = cursor.fetchall()
        cursor.close()
        self.conn = None

        if len(row) > 0:
            self.geneId = id
            self.probesetId = id
                    
        return

        

    '''
    # name: ncbiToGeneId
    # desc: Returns the AGI corresponding to the NCBI gi accession
    # notes: NCBI gi accession comes from NCBI Linkout. Need to check whether NCBI gi accession is a NCBI GeneID or NCBI RefSeq.
    '''
    def ncbiToGeneId(self, ncbi_gi):
	if (ncbi_gi == None):
            return None
        if(efpConfig.DB_ANNO == None or efpConfig.DB_NCBI_GENE_TABLE == None): # ncbi lookup db not defined
            return None
        if(self.conn == None):
            self.connect(efpConfig.DB_ANNO)
        
        cursor = self.conn.cursor()
        
        select_cmd = "SELECT t1.%s FROM %s t1 WHERE t1.geneid=%%s or t1.protid=%%s" % (efpConfig.DB_NCBI_GENEID_COL, efpConfig.DB_NCBI_ID_TABLE)
        cursor.execute(select_cmd,(ncbi_gi, ncbi_gi))
        row = cursor.fetchall()
        cursor.close()
        if len(row) != 0:
            self.geneId = row[0][0]
            self.ncbiId = ncbi_gi
        return

    def getLookup(self):
        
        if(self.database == "maize_rice_comparison"):
            if(self.conn == None):
                self.connect(efpConfig.DB_ANNO)
            cursor = self.conn.cursor()
            MaizeConvert3 = re.match("GRMZM2G[0-9]{6}_T[0-9]{1,2}", self.geneId)
            MaizeConvert4 = re.match("^AC[0-9]{6}\.[0-9]{1}_FGT[0-9]{3}$", self.geneId)
	    
            if MaizeConvert3 is not None:
                self.geneId = re.sub("_T[0-9]{1,2}", "", self.geneId)
                
            if MaizeConvert4 is not None:
                self.geneId = (self.geneId).replace("FGT", "FG")
            
            select_cmd = "SELECT rice_id FROM %s WHERE %s=%%s AND date = (SELECT MAX(date) FROM %s)" % (efpConfig.DB_ORTHO_LOOKUP_TABLE, efpConfig.DB_ORTHO_GENEID_COL, efpConfig.DB_ORTHO_LOOKUP_TABLE)
            cursor.execute(select_cmd, (self.geneId,))
            result = cursor.fetchone()
            if result != None:
                self.lookup = result[0]
                
                cursor.close()
            return self.lookup
        if(self.database == "rice_maize_comparison"):
            if(self.conn == None):
                self.connect(efpConfig.DB_ANNO)
            cursor = self.conn.cursor()
            
            select_cmd = "SELECT maize_id FROM %s WHERE %s=%%s AND date = (SELECT MAX(date) FROM %s)" % (efpConfig.DB_ORTHO_LOOKUP_TABLE, efpConfig.DB_ORTHO_GENEID_COL, efpConfig.DB_ORTHO_LOOKUP_TABLE)
            cursor.execute(select_cmd, (self.geneId,))
            result = cursor.fetchone()
            if result != None:
                self.lookup = result[0]
                
                cursor.close()
            return self.lookup


    def getAnnotation(self):
        if(efpConfig.DB_ANNO == None or efpConfig.DB_ANNO_TABLE == None): # annotations db not defined
            return None
        if(self.annotation == None):
            if(self.conn == None):
                self.connect(efpConfig.DB_ANNO)
            

            # Return the annotation and alias for a given geneId
            cursor = self.conn.cursor()
            MaizeConvert1 = re.match("^GRMZM2G[0-9]{6}$", self.geneId)
            MaizeConvert2 = re.match("^AC[0-9]{6}\.[0-9]{1}_FG[0-9]{3}$", self.geneId)
            MaizeSp1 = "_T01"
            if MaizeConvert1 is not None:
                self.geneId = self.geneId + MaizeSp1
            if MaizeConvert2 is not None:
                self.geneId = self.geneId.replace("FG", "FGT")
            select_cmd = "SELECT annotation FROM %s WHERE %s=%%s AND date = (SELECT MAX(date) FROM %s)" % (efpConfig.DB_ANNO_TABLE, efpConfig.DB_ANNO_GENEID_COL, efpConfig.DB_ANNO_TABLE)
            cursor.execute(select_cmd, (self.geneId,))
            result = cursor.fetchone()
            if result != None:
                self.annotation = result[0]
                cursor.close()
                
                splitter = re.compile('__')
                items = splitter.split(self.annotation)
                splitter = re.compile('_')
                aliases = splitter.split(items[0])
                if len(items) == 1:
                    aliases[0] = ''
                self.alias = aliases[0]
        return self.annotation
    
    def getSequence(self):
        if(efpConfig.DB_ORTHO == None): # annotations db not defined
            return None
        if(self.connOrtho == None):
            self.connectOrthoDB()   
        cursor = self.connOrtho.cursor()
        select_cmd = "SELECT sequence FROM %s WHERE gene = %%s" % (efpConfig.spec_names[efpConfig.species].lower(),)
        cursor.execute(select_cmd, (self.getGeneId(),))
        seq = cursor.fetchone()
        if (seq == None):
            return None
        return seq[0]
    
    def getOrthologs(self, spec1, spec2):
        if(efpConfig.DB_ORTHO == None): # annotations db not defined
            return None
        if(self.connOrtho == None):
            self.connectOrthoDB()   
        cursor = self.connOrtho.cursor()
        
        scc_probesets = {}
        scc_genes = {}
        align_probesets = {}

        #selecting queries from the orthologs db for spec2 GENE IDs
        select_cmd = "SELECT t2.Gene_A, t3.sequence, t2.SCC_Value, t2.Probeset_A FROM orthologs_scc t2 LEFT JOIN %s t3 ON t3.gene = t2.Gene_A WHERE t2.Probeset_B = %%s AND t2.Genome_A = %%s AND t2.Genome_B = %%s" % (efpConfig.spec_names[spec2].lower(),) + \
                     " UNION SELECT t2.Gene_B, t3.sequence, t2.SCC_Value, t2.Probeset_B FROM orthologs_scc t2 LEFT JOIN %s t3 ON t3.gene = t2.Gene_A WHERE t2.Probeset_A = %%s AND t2.Genome_B = %%s AND t2.Genome_A = %%s" % (efpConfig.spec_names[spec2].lower(),)
        cursor.execute(select_cmd, (self.getProbeSetId(), spec2, spec1, self.getProbeSetId(), spec2, spec1))
        rows = cursor.fetchall()
        
        for row in rows:
            gene = row[0]
            gene = efpConfig.spec_names[spec2]+ '_' + gene
            seq = row[1]
            if(seq != None):
                align_probesets[gene] = seq
            scc = row[2]
            probeset = [row[3]]
            scc_genes[row[3]] = row[0]
            if scc in scc_probesets:
                scc_probesets[scc].extend(probeset)
            else:
                scc_probesets[scc] = list()
                scc_probesets[scc].extend(probeset)
        cursor.close()
        return scc_genes, scc_probesets, align_probesets
    
    def getAlias(self):
        if(self.alias == None):
            self.getAnnotation()
        return self.alias
    
    def connect (self, db_name):
        try:
            self.conn = MySQLdb.connect (host = efpConfig.DB_HOST, user = efpConfig.DB_USER, passwd = efpConfig.DB_PASSWD, db = db_name)
        except MySQLdb.Error, e:
            print >> sys.stderr, "Error %d: %s" % (e.args[0], e.args[1])

    def connectOrthoDB (self):
        try:
            self.connOrtho = MySQLdb.connect (host = efpConfig.DB_HOST, user = efpConfig.DB_USER, passwd = efpConfig.DB_PASSWD, db = efpConfig.DB_ORTHO)
        except MySQLdb.Error, e:
            print >> sys.stderr, "Error %d: %s" % (e.args[0], e.args[1])


class Gene_ATX (Gene):
    def __init__(self, id):
        Gene.__init__(self, id, "atTax")
        self.geneId = self.checkGene(id)
        
    '''
    # name: checkGene
    # desc: Searchs for At-TAX geneId    
    '''
    def checkGene(self, gene):
        if(gene == None):
            return None
        gene = re.sub("t", "T", gene)
        gene = re.sub("g", "G", gene)
        file = open('%s/geneid.txt' % efpConfig.dataDir)
        if gene+'\n' not in file:
            file.close()
            return None
        else:
            file.close()
            return gene
