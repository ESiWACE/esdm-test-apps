# This file is part of the GGDML language extensions' source-to-source translator.
# The tool is intended to be used according to the GPL licence after the first
# version is published.
# This file works together with the general-purpose-language processor.
# It is used by the tool's main file to process the GGDML extensions and to handle domain decomposition.
# Nabeeh Jum'ah

import re
class DSL:
    def __init__(self,confFile):
        gplModule = __import__('C')
        self.confFileName = confFile
        self.language = getattr(gplModule, 'language')
        self.generator = getattr(gplModule, 'generator')
        self.finalprocessor = getattr(gplModule, 'finalprocessor')
        self.GPL = self.language(self)
        
        self.TUs=[[],[],[],[]]
        self.specifierList = []
        self.specifierSubs = []
        self.dataPointers = []
        self.variableStructure = ''
        self.symbolTable = {}
        self.allocationCases = []
        self.allocGlobalVars = []
        self.tAllocGlobalVars=0
        self.deallocationCases = []
        self.globalDomainBoundaries = []
        self.defaultDomainIndices = []
        self.indexOperators = []
        self.specialExpressions = []
        self.memoryLayouts = []
        self.recommendedAnnotations = {}
        self.numNodes = 1
        self.commLibInitCode = ''
        self.commFinCode = ''
        self.commNeededIncs = []
        self.commInitCode = ''
        self.commCode=[]
        self.commGlobals=[]
        self.tCommGlobals=0

        if confFile:
            f = open(confFile)
            confText = f.read()
            f.close()

            m=re.search(r'EXTERN\s*:\s*(.*?)$',confText,flags=re.M|re.S)
            if m!=None:
                externList = re.findall(r'[0-9a-zA-Z_]+', m.group(1))
                self.GPL.type_specifiers = self.GPL.type_specifiers + externList

            m=re.search(r'SPECIFIERS\s*:\s*(.*?)$',confText,flags=re.M|re.S)
            if m!=None:
                specifiersText = m.group(1)
                pos = 0
                while True:
                    m=re.search(r'\s*SPECIFIER\s*\((.*?)\)\s*',specifiersText[pos:],flags=re.M|re.S)
                    if m==None:
                        break
                    specifierText = m.group(1)
                    specifierList = re.findall(r'[0-9a-zA-Z_]+', specifierText)
                    self.specifierList.append(specifierList)
                    pos = pos + m.end()

            m=re.search(r'DECLARATIONS\s*:\s*(.*?)ENDDECLARATIONS',confText,flags=re.M|re.S)
            if m!=None:
                declarationsText = m.group(1)
                pos = 0
                while True:
                    m=re.search(r'\s*SUBSTITUTE\s+([0-9a-zA-Z_]+)\s+WITH\s+(.*?)$',declarationsText[pos:],flags=re.M|re.S)
                    if m==None:
                        break
                    subsList = [m.group(1),m.group(2)]
                    if re.match(r'NOTHING.*?',subsList[1],flags=re.M|re.S)!=None:
                        subsList[1] = ''
                    self.specifierSubs.append(subsList)
                    pos = pos + m.end()
                pos = 0
                while True:
                    m=re.search(r'\s*DATAPOINTER\s+([0-9a-zA-Z_]+)\s+(.*?)$',declarationsText[pos:],flags=re.M|re.S)
                    if m==None:
                        break
                    dpList = [m.group(1),m.group(2)]
                    self.dataPointers.append(dpList)
                    pos = pos + m.end()
                m=re.search(r'\s*VARIABLESTRUCTURE\s*:\s*(.*?)ENDVARIABLESTRUCTURE',declarationsText,flags=re.M|re.S)
                if m!=None:
                    self.variableStructure = m.group(1)

            m=re.search(r'ALLOCATIONS\s*:\s*(.*?)ENDALLOCATIONS',confText,flags=re.M|re.S)
            if m!=None:
                allocationsText = m.group(1)
                pos = 0
                while True:
                    m=re.search(r'\s*CASE\s*(.*?):\s*(.*?)ENDCASE',allocationsText[pos:],flags=re.M|re.S)
                    if m==None:
                        break
                    condList = re.findall(r'([0-9a-zA-Z_]+)\s*=\s*([0-9a-zA-Z_]+)', m.group(1))
                    self.allocationCases.append([condList,m.group(2)])
                    pos = pos + m.end()
                m=re.search(r'^\s*GLOBALVARS\s*:(.*?)ENDGLOBALVARS',allocationsText,flags=re.M|re.S)
                if m!=None:
                    globalVarsText = m.group(1)
                    pos = 0
                    while True:
                        m=re.search(r'^\s*(.*?;)$',globalVarsText[pos:],flags=re.M|re.S)
                        if m==None:
                            break
                        self.allocGlobalVars.append(m.group(1))
                        pos = pos + m.end()

            m=re.search(r'DEALLOCATIONS\s*:\s*(.*?)ENDDEALLOCATIONS',confText,flags=re.M|re.S)
            if m!=None:
                deallocationsText = m.group(1)
                pos = 0
                while True:
                    m=re.search(r'\s*CASE\s*(.*?):\s*(.*?)ENDCASE',deallocationsText[pos:],flags=re.M|re.S)
                    if m==None:
                        break
                    condList = re.findall(r'([0-9a-zA-Z_]+)\s*=\s*([0-9a-zA-Z_]+)', m.group(1))
                    self.deallocationCases.append([condList,m.group(2)])
                    pos = pos + m.end()

            m=re.search(r'GLOBALDOMAIN\s*:\s*(.*?)ENDGLOBALDOMAIN',confText,flags=re.M|re.S)
            if m!=None:
                globDomText = m.group(1)
                pos = 0
                while True:
                    m=re.search(r'\s*COMPONENT\s*\(\s*([0-9a-zA-Z_]+)\s*\)\s*:(.*?)ENDCOMPONENT',globDomText[pos:],flags=re.M|re.S)
                    if m==None:
                        break
                    component = [m.group(1),[]]
                    cmpText = m.group(2)
                    pos = pos + m.end()
                    
                    pos2 = 0
                    while True:
                        m=re.search(r'\s*RANGE\s*OF\s+(.*?)$',cmpText[pos2:],flags=re.M|re.S)
                        if m==None:
                            break
                        dimText = m.group(1)
                        dre = re.search(r'([0-9a-zA-Z_]+)\s*=\s*(.*?)\s+TO\s+(.*)', dimText)
                        if dre==None:
                            print 'Configuration error: Global domain boundaries configuration error: ' + dimText
                            exit()
                        component[1].append([dre.group(1),dre.group(2),dre.group(3)])
                        pos2 = pos2 + m.end()
                    self.globalDomainBoundaries.append(component)

                m=re.search(r'\s*DEFAULT\s*=\s*([0-9a-zA-Z_]+)(.*?)$',globDomText[pos:],flags=re.M|re.S)
                if m!=None:
                    self.defaultDomainIndices = [m.group(1)]
                    defIndText = m.group(2)
                    pos = 0
                    while True:
                        m=re.search(r'\s*\[(.*?)\]',defIndText[pos:],flags=re.M|re.S)
                        if m==None:
                            break
                        pos = pos + m.end()
                        self.defaultDomainIndices.append(re.findall(r'[a-zA-Z_][0-9a-zA-Z_]*', m.group(1)))

            m=re.search(r'INDEXOPERATORS\s*:\s*(.*?)ENDINDEXOPERATORS',confText,flags=re.M|re.S)
            if m!=None:
                indexOperatorText = m.group(1)
                pos = 0
                while True:
                    m=re.search(r'\s*([a-zA-Z_][0-9a-zA-Z_]+)\s*\(\s*([0-9a-zA-Z_]*)\s*\)\s*:\s*([a-zA-Z_][0-9a-zA-Z_]+)\s*=(.*?)$',indexOperatorText[pos:],flags=re.M|re.S)
                    if m==None:
                        break
                    self.indexOperators.append([m.group(1),m.group(2),m.group(3),m.group(4)])
                    pos = pos + m.end()

            m=re.search(r'SPECIALEXPRESSIONS\s*:\s*(.*?)ENDSPECIALEXPRESSIONS',confText,flags=re.M|re.S)
            if m!=None:
                specialExpressionText = m.group(1)
                pos=0
                while True:
                    m=re.search(r'TRANSLATE\s+(.*?)\s+TO\s+(.*?)$',specialExpressionText[pos:],flags=re.M|re.S)
                    if m==None:
                        break
                    self.specialExpressions.append([m.group(1),m.group(2)])
                    pos = pos + m.end()

            m=re.search(r'MEMORYLAYOUTS\s*:\s*(.*?)ENDMEMORYLAYOUTS',confText,flags=re.M|re.S)
            if m!=None:
                memLayoutsText = m.group(1)
                pos=0
                while True:
                    m=re.search(r'LAYOUT\s*\(\s*([0-9]+)\s*\)\s*:(.*?)ENDLAYOUT',memLayoutsText[pos:],flags=re.M|re.S)
                    if m==None:
                        break
                    layout = [int(m.group(1))]
                    layoutText = m.group(2)
                    pos = pos + m.end()
                    pos2 = 0
                    while True:
                        m=re.search(r'INDEX\s*=(.*?)$',layoutText[pos2:],flags=re.M|re.S)
                        if m==None:
                            break
                        layout.append(m.group(1))
                        pos2 = pos2 + m.end()
                    self.memoryLayouts.append(layout)

            m=re.search(r'ANNOTATIONS\s*:\s*(.*?)ENDANNOTATIONS',confText,flags=re.M|re.S)
            if m!=None:
                annotationsText = m.group(1)
                pos = 0
                while True:
                    m=re.search(r'\s*LEVEL\s+(-?[0-9]+)\s*:(.*?)$',annotationsText[pos:],flags=re.M|re.S)
                    if m==None:
                        break
                    self.recommendedAnnotations[m.group(1)] = m.group(2)
                    pos = pos + m.end()
                m=re.search(r'\s*(DEFAULT)\s*:(.*?)$',annotationsText,flags=re.M|re.S)
                if m!=None:
                    self.recommendedAnnotations[m.group(1)] = m.group(2)
                m=re.search(r'\s*(TIMESTEPS)\s*:(.*?)$',annotationsText,flags=re.M|re.S)
                if m!=None:
                    self.recommendedAnnotations[m.group(1)] = m.group(2)

            m=re.search(r'INCLUDEPATHS\s*:(.*?)ENDINCLUDEPATHS',confText,flags=re.M|re.S)
            if m!=None:
                incPathsText = m.group(1)
                includePaths=[]
                pos = 0
                while True:
                    m=re.search(r'\s+(.+?)$',incPathsText[pos:],flags=re.M|re.S)
                    if m==None:
                        break
                    includePaths.append(m.group(1))
                    pos = pos + m.end()
                self.GPL.includePaths = includePaths

            m=re.search(r'DOMAINDECOMPOSITION\s*:(.*?)ENDDOMAINDECOMPOSITION',confText,flags=re.M|re.S)
            if m!=None:
                domDecText = m.group(1)
                m=re.search(r'^\s*nodes\s*=\s*(.+?)$',domDecText,flags=re.M|re.S)
                if m!=None:
                    self.numNodes = m.group(1)
                m=re.search(r'^\s*processID\s*=\s*(.+?)$',domDecText,flags=re.M|re.S)
                if m!=None:
                    self.processID = m.group(1)
                m=re.search(r'^\s*INCLUDE\s*:\s*(.*?)$',domDecText,flags=re.M|re.S)
                if m!=None:
                    self.commNeededIncs = [False]+re.findall(r'(["<].+?[">])', m.group(1))
                m=re.search(r'INITIALIZATION\s*:(.*?)ENDINITIALIZATION',domDecText,flags=re.M|re.S)
                if m!=None:
                    self.commLibInitCode = m.group(1)
                m=re.search(r'FINALIZATION\s*:(.*?)ENDFINALIZATION',domDecText,flags=re.M|re.S)
                if m!=None:
                    self.commFinCode = m.group(1)

            for d in self.globalDomainBoundaries:
                gm='('+d[1][0][1]+')'
                gM='('+d[1][0][2]+')'
                ib='(('+gM+'-'+gm+'+('+self.numNodes+')-1)/'+self.numNodes+')'
                mb = '0'
                Mb = '(('+self.processID+'==('+gM+'-1)/'+ib+')&&('+gM+'%'+ib+')?'+gM+'%'+ib+':'+ib+')'
                localDomain=[[d[1][0][0],mb,Mb]]
                for dc in d[1][1:]:
                    localDomain.append(self.copyL(dc))
                d.append(localDomain)

            m=re.search(r'COMMUNICATION\s*:\s*(.*?)ENDCOMMUNICATION',confText,flags=re.M|re.S)
            if m!=None:
                commText = m.group(1)
                m=re.search(r'^\s*COMMGLOBALS\s*:(.*?)ENDCOMMGLOBALS',commText,flags=re.M|re.S)
                if m!=None:
                    commGlobalText = m.group(1)
                    pos = 0
                    while True:
                        m=re.search(r'^\s*(.*?;)$',commGlobalText[pos:],flags=re.M|re.S)
                        if m==None:
                            break
                        self.commGlobals.append(m.group(1))
                        pos = pos + m.end()
                m=re.search(r'^\s*COMMINITIALIZATION\s*:\s*(.*?)ENDCOMMINITIALIZATION',commText,flags=re.M|re.S)
                if m!=None:
                    self.commInitCode = m.group(1)
                m=re.search(r'^\s*COMMCODE\s*:\s*(.*?)ENDCOMMCODE',commText,flags=re.M|re.S)
                if m!=None:
                    commCode = m.group(1)
                    pos = 0
                    while True:
                        m=re.search(r'^\s*SECTION\s+\((.+?)\)\s+([0-9a-zA-Z_]+)\s+([0-9a-zA-Z_]+)\s*:\s*(.*?)ENDSECTION\s*$',commCode[pos:],flags=re.M|re.S)
                        if m==None:
                            break
                        self.commCode.append([m.group(1),m.group(2),m.group(3),m.group(4)])
                        pos = pos + m.end()
            '''pos=0
            while True:
                m=re.search(r'TYPE_EXTENSION\s+([a-zA-Z_][0-9a-zA-Z_]*)\s+=\s+([a-zA-Z_][0-9a-zA-Z_]*)(.*?)END\s*TYPE_EXTENSION',confText[pos:],flags=re.M|re.S)
                if m!=None:
                    extText = m.group(3)
                    lst=[m.group(2),True,[],[]]
                    extPos=0
                    while True:
                        im=re.search(r'NEEDS\s+(.*?)END\s*NEEDS',extText[extPos:],flags=re.M|re.S)
                        if im!=None:
                            jText = im.group(1)
                            jPos=0
                            jLst=[]
                            while True:
                                jm=re.search(r'EXTERN\s+([a-zA-Z_][0-9a-zA-Z_]*)\s+',jText[jPos:],flags=re.M|re.S)
                                if jm!=None:
                                    jLst.append(jm.group(1))
                                    jPos = jPos + jm.end()
                                    continue
                                break
                            lst[2].append(self.tmpParse(jText[jPos:],'translation_unit',jLst))
                            extPos = extPos + im.end()
                            continue
                        break                    
                    extPos=0
                    while True:
                        im=re.search(r'NEEDSX\s+(.*?)END\s*NEEDS',extText[extPos:],flags=re.M|re.S)
                        if im!=None:
                            jText = im.group(1)
                            jPos=0
                            jLst=[]
                            while True:
                                jm=re.search(r'EXTERN\s+([a-zA-Z_][0-9a-zA-Z_]*)\s+',jText[jPos:],flags=re.M|re.S)
                                if jm!=None:
                                    jLst.append(jm.group(1))
                                    jPos = jPos + jm.end()
                                    continue
                                break
                            lst[3].append(self.tmpParse(jText[jPos:],'translation_unit',jLst))
                            extPos = extPos + im.end()
                            continue
                        break                
                    self.typeExtensions[m.group(1)]=lst
                    self.GPL.type_specifiers.append(m.group(1))
                    self.GPL.keywords.append(m.group(1))
                    pos = pos + m.end()
                    continue
                break'''

        
    def tmpParse(self,code,node,ttLst):
        d= DSL(None)
        d.GPL.type_specifiers = d.GPL.type_specifiers+self.GPL.type_specifiers+ttLst
        d.GPL.keywords = d.GPL.keywords+self.GPL.keywords+ttLst
        d.GPL.srcCode = code
        tp= getattr(d.GPL, node)
        
        ret = self.processTmpParse(tp())
        if ret==None:
            print 'Invalide code provided for temporary parse:\n' + code[0:100] + '\n...\n...\n...'
        return ret
    
    def processTmpParse(self,ast):
        if isinstance(ast, list):
            ret = []
            for i in ast:
                ret.append(self.processTmpParse(i))
            return ret
        if isinstance(ast, int):
            return -1
        else:
            return ast
        

    def tmpGen(self,node,nodet):
        g= self.generator()
        tp= getattr(g, nodet)
        return tp(node)
        
    def readSource(self, fname):
        self.GPL.readSource(fname)
        
    def parse(self):
        self.ast = self.GPL.translation_unit()
        return self.ast
    
    def finalOutput(self):
        fp=self.finalprocessor()
        return fp.finalOutput(self)
        
    def type_specifier(self):
        for i in self.specifierList:
            for j in i[1:]:
                symb = self.GPL.checkSymbol(j)
                if symb!=None:
                    return j
        return None
    
    def translate_declaration(self,input,ttype):
        var_name = input [3][2][2][2][2]
        tmpTxt = self.tmpGen(input,ttype)

        var_atts = []#loc,dim,text,type
        for i in self.specifierList:
            found = False
            for j in i[1:]:
                m=re.search('\s+'+j+'\s+',tmpTxt,flags=re.M|re.S)
                if m!=None:
                    found = True
                    var_atts.append(j)
                    break
            if found==False:
                var_atts.append('')
        var_atts = [var_atts]
        
        dp=''
        for i in self.dataPointers:
            m=re.search('\s+'+i[0]+'\s+',tmpTxt,flags=re.M|re.S)
            if m!=None:
                dp=i[1]
                break
        for i in self.specifierSubs:
            tmpTxt = re.sub('\s+'+i[0]+'\s+',' '+i[1]+' ',tmpTxt,flags=re.M|re.S)
        
        var_atts.append(tmpTxt)#TODO?
        var_atts.append('')
        for i in self.GPL.type_specifiers:
            for j in input[2][2:]:
                if i==j:
                    var_atts[-1] = i
                    break
            if var_atts[-1] != '':
                break
        
        varStTxt = self.variableStructure
        varStTxt = re.sub('\$data_type',var_atts[-1],varStTxt,flags=re.M|re.S)
        tmpTxt = re.sub(var_atts[-1]+'\s+',varStTxt+'* ',tmpTxt,flags=re.M|re.S)
        
        wg=None
        for g in self.globalDomainBoundaries:
            found=True
            for s in var_atts[0]:
                m = re.search(s,g[0],flags=re.M|re.S)
                if m==None:
                    found=False
                    break
            if found:
                wg=g
                break
        var_atts.append(wg)
        var_atts.append(dp)

        self.symbolTable[var_name] = var_atts

        output = self.tmpParse(tmpTxt,ttype,[])
        return output
    
    def statement(self):

        symb = self.alloc_statement()
        if symb!=None:
            return symb

        symb = self.dealloc_statement()
        if symb!=None:
            return symb

        symb = self.foreach_statement()
        if symb!=None:
            return symb

        symb = self.timestep_statement()
        if symb!=None:
            return symb
        
        symb = self.comm_init_statement()
        if symb!=None:
            return symb
        
        symb = self.comm_lib_init_statement()
        if symb!=None:
            return symb

        symb = self.comm_lib_finalize_statement()
        if symb!=None:
            return symb

        return None

    def alloc_statement(self):
        revert = self.GPL.currentPos
        ret=[revert,'alloc_statement']
        
        self.GPL.skipSpaces()
        symb = self.GPL.checkSymbol('ALLOC ')
        if symb==None:
            self.GPL.currentPos = revert
            return None
        
        self.GPL.skipSpaces()
        symb = self.GPL.postfix_expression()
        if symb==None:
            self.GPL.currentPos = revert
            return None
        ret.append(symb)

        self.GPL.skipSpaces()
        symb = self.GPL.checkSymbol(';')
        if symb==None:
            self.GPL.currentPos= revert
            return None

        si=0
        while si<len(ret[2]):
            if ret[2][si]=='[expression]':
                break
            si = si+1
        si=si-1
        var_name = ret[2][si]
        if self.symbolTable.get(var_name) == None:
            self.GPL.reportError('Trying to allocate a non-declared grid-based variable '+var_name)
        data_type = self.symbolTable[var_name][2]
        
        newCode = ''
        for case in self.allocationCases:
            met=True
            for condition in case[0]:
                for i in range(0,len(self.specifierList)):
                    if condition[0]==self.specifierList[i][0]:
                        if condition[1]!=self.symbolTable[var_name][0][i]:
                            met=False
                            break
                if met==False:
                    break
            if met==False:
                continue
            else:
                newCode = case[1]
                break
        if newCode=='':
            return None
        
        var_name = self.tmpGen(ret[2],'postfix_expression')
        newCode = re.sub(r'\$var_name',var_name,newCode,flags=re.M|re.S)
        newCode = re.sub(r'\$data_type',data_type,newCode,flags=re.M|re.S)

        newAST = self.tmpParse(newCode,'statement',[])
        self.add_alloc_global_vars(False)
        return newAST[2]
    
    def add_alloc_global_vars(self,g):
        if self.tAllocGlobalVars==1:
            return
        if g:
            self.tAllocGlobalVars = 1
        else:
            self.tAllocGlobalVars = 2
        self.TUs[3]=[]
        for d in self.allocGlobalVars:
            if g:
                dt = d
            else:
                dt = 'extern '+d
            self.TUs[3].append( self.tmpParse(dt,'translation_unit',[]) )

    def dealloc_statement(self):
        revert = self.GPL.currentPos
        ret=[revert,'dealloc_statement']
        
        self.GPL.skipSpaces()
        symb = self.GPL.checkSymbol('DEALLOC ')
        if symb==None:
            self.GPL.currentPos = revert
            return None
        
        self.GPL.skipSpaces()
        symb = self.GPL.postfix_expression()
        if symb==None:
            self.GPL.currentPos = revert
            return None
        ret.append(symb)

        self.GPL.skipSpaces()
        symb = self.GPL.checkSymbol(';')
        if symb==None:
            self.GPL.currentPos= revert
            return None
        
        si=0
        while si<len(ret[2]):
            if ret[2][si]=='[expression]':
                break
            si = si+1
        si=si-1
        var_name = ret[2][si]
        if self.symbolTable.get(var_name) == None:
            self.GPL.reportError('Trying to deallocate a non-declared grid-based variable')
        data_type = self.symbolTable[var_name][2]
        
        newCode = ''
        for case in self.deallocationCases:
            met=True
            for condition in case[0]:
                for i in range(0,len(self.specifierList)):
                    if condition[0]==self.specifierList[i][0]:
                        if condition[1]!=self.symbolTable[var_name][0][i]:
                            met=False
                            break
                if met==False:
                    break
            if met==False:
                continue
            else:
                newCode = case[1]
                break
        if newCode=='':
            return None
        
        var_name = self.tmpGen(ret[2],'postfix_expression')
        newCode = re.sub(r'\$var_name',var_name,newCode,flags=re.M|re.S)
        newCode = re.sub(r'\$data_type',data_type,newCode,flags=re.M|re.S)

        newAST = self.tmpParse(newCode,'statement',[])

        return newAST[2]

    def foreach_statement(self):
        revert = self.GPL.currentPos
        ret=[revert,'foreach_statement']
        
        self.GPL.skipSpaces()
        symb = self.GPL.checkSymbol('for\s*each|FOR\s*EACH')
        if symb==None:
            self.GPL.currentPos = revert
            return None
        #ret.append(symb)
        
        self.GPL.skipSpaces()
        symb = self.GPL.checkID()
        if symb==None:
            self.GPL.currentPos = revert
            return None
        ret.append(symb)
        iteratorIndex = symb
        
        self.GPL.skipSpaces()
        symb = self.GPL.checkSymbol('in|IN')
        if symb==None:
            self.GPL.currentPos = revert
            return None
        
        procSrc = self.GPL.srcCode[:self.GPL.currentPos]
        m = re.search('(.*?)$',self.GPL.srcCode[self.GPL.currentPos:],flags=re.M|re.S)
        it1 = re.sub('\.\.','||',m.group(),flags=re.M|re.S)
        it2 = re.sub('{','[',it1,flags=re.M|re.S)
        it3 = re.sub('}',']',it2,flags=re.M|re.S)
        it4 = re.sub('\[\s*$','{\n',it3,flags=re.M|re.S)
        procSrc = procSrc + it4
        procSrc = procSrc + self.GPL.srcCode[self.GPL.currentPos+m.end(1):]
        self.GPL.srcCode = procSrc
        
        self.GPL.skipSpaces()
        symb = self.GPL.logical_or_expression()
        if symb==None:
            self.GPL.currentPos = revert
            return None
        ret.append(symb)

        self.GPL.skipSpaces()
        symb = self.GPL.statement()
        if symb==None:
            self.GPL.currentPos = revert
            return None
        ret.append(symb)
        
        domainBoundaries = self.parseDomainBoundaries(ret[3],iteratorIndex,revert)
        #indexSet=['i','j','k','l','m','n']
        self.addCommIncs()
        
        varList=[0]
        newstmt = self.translateSpecialExpressions(ret[4],iteratorIndex,domainBoundaries,revert)
        newstmt = self.translateIndices(newstmt,iteratorIndex,domainBoundaries,revert,varList)
        
        ncode = '{'
        
        exlst=[]
        for st in varList[1:]:
            if st[0]=='=':
                for var in st[2:]:
                    varname = var[0]
                    for ca in var[1:]:
                        for code in self.commCode:
                            if code[0]==ca and code[2]=='READ':
                                if self.symbolTable.get(varname) != None:
                                    dim = self.symbolTable[varname][0][1]
                                if dim==code[1]:
                                    added=False
                                    for ex in exlst:
                                        if ex[0]==varname and ex[1]==code[0]:
                                            added=True
                                    if added:
                                        continue
                                    adcode=re.sub('\$var_name',varname+self.symbolTable[varname][4],code[3],flags=re.M|re.S)
                                    ncode = ncode+adcode
                                    exlst.append([varname,code[0]])
                                    self.add_comm_globals(False)
        for st in varList[1:]:
            if st[0]=='?':
                for var in st[1:]:
                    varname = var[0]
                    for ca in var[1:]:
                        for code in self.commCode:
                            if code[0]==ca and code[2]=='READ':
                                if self.symbolTable.get(varname) != None:
                                    dim = self.symbolTable[varname][0][1]
                                if dim==code[1]:
                                    added=False
                                    for ex in exlst:
                                        if ex[0]==varname and ex[1]==code[0]:
                                            added=True
                                    if added:
                                        continue
                                    adcode=re.sub('\$var_name',varname+self.symbolTable[varname][4],code[3],flags=re.M|re.S)
                                    ncode = ncode+adcode
                                    exlst.append([varname,code[0]])
                                    self.add_comm_globals(False)
        
        for i in range(0,len(domainBoundaries)):
            if domainBoundaries[i][1]!=domainBoundaries[i][2]:
                if i==0:
                    mv='min_'+self.localDomain[0][0]
                    Mv='max_'+self.localDomain[0][0]
                    lm=self.localDomain[0][1]
                    llm=domainBoundaries[0][1]
                    lM=self.localDomain[0][2]
                    llM=domainBoundaries[0][2]
                    ib='((('+lM+')+'+self.numNodes+'-1)/'+self.numNodes+')'
                    ncode = ncode + 'size_t '+mv+'= '+self.processID+'==('+llm+')/'+ib+'?'+llm+'%'+ib+':0;'
                    ncode = ncode + 'size_t '+Mv+'= '+self.processID+'<('+llm+')/'+ib+'||'+self.processID+'>('+llM+'-1)/'+ib+'?0:' +self.processID+'==('+llM+'-1)/'+ib+'?'+llM+'%'+ib+'?'+llM+'%'+ib+':'+ib+':'+ib+';'
                    domainBoundaries[0][1]=mv
                    domainBoundaries[0][2]=Mv
                if self.recommendedAnnotations.get(str(i)) != None:
                    ncode = ncode + '__AddAnnotation("'+self.recommendedAnnotations[str(i)]+'");'
                elif self.recommendedAnnotations.get(str(i-len(domainBoundaries))) != None:
                    ncode = ncode + '__AddAnnotation("'+self.recommendedAnnotations[str(i-len(domainBoundaries))]+'");'
                elif self.recommendedAnnotations.get('DEFAULT') != None:
                    ncode = ncode + '__AddAnnotation("'+self.recommendedAnnotations['DEFAULT']+'");'
                ncode = ncode + 'for(size_t '+domainBoundaries[i][0]+'_index =('+domainBoundaries[i][1]+');'+domainBoundaries[i][0]+'_index <('+domainBoundaries[i][2]+');'+domainBoundaries[i][0]+'_index ++){'
            else:
                ncode = ncode + 'const size_t '+domainBoundaries[i][0]+'_index =('+domainBoundaries[i][1]+');{'
        ncode = ncode[:-1] + self.tmpGen(newstmt,'statement')
        for i in range(0,len(domainBoundaries)):
            ncode = ncode+'}'


        ncode = ncode[:-1]
        exlst=[]
        for st in varList[1:]:
            if st[0]=='=':
                if st[1]==[]:
                    continue
                varname = st[1][0]
                for ca in st[1][1:]:
                    for code in self.commCode:
                        if code[0]==ca and code[2]=='WRITE':
                            if self.symbolTable.get(varname) != None:
                                dim = self.symbolTable[varname][0][1]
                            if dim==code[1]:
                                added=False
                                for ex in exlst:
                                    if ex[0]==varname and ex[1]==code[0]:
                                        added=True
                                if added:
                                    continue
                                adcode=re.sub('\$var_name',varname+self.symbolTable[varname][4],code[3],flags=re.M|re.S)
                                ncode = ncode+adcode
                                exlst.append([varname,code[0]])
                                self.add_comm_globals(False)
        ncode = ncode+'}'

###########
        '''ncode = ncode[:-1]+'send(outer_region);recv(external_region);'
        for i in range(0,len(domainBoundaries)):
            if domainBoundaries[i][1]!=domainBoundaries[i][2]:
                if i==0:
                    mv='min_inner_'+self.localDomain[0][0]+'_region'
                    Mv='max_inner_'+self.localDomain[0][0]+'_region'
                    ncode = ncode + 'size_t '+mv+'= someformula;'
                    ncode = ncode + 'size_t '+Mv+'= someformula;'
                    domainBoundaries[0][1]=mv
                    domainBoundaries[0][2]=Mv
                if self.recommendedAnnotations.get(str(i)) != None:
                    ncode = ncode + '__AddAnnotation("'+self.recommendedAnnotations[str(i)]+'");'
                elif self.recommendedAnnotations.get(str(i-len(domainBoundaries))) != None:
                    ncode = ncode + '__AddAnnotation("'+self.recommendedAnnotations[str(i-len(domainBoundaries))]+'");'
                elif self.recommendedAnnotations.get('DEFAULT') != None:
                    ncode = ncode + '__AddAnnotation("'+self.recommendedAnnotations['DEFAULT']+'");'
                ncode = ncode + 'for(size_t '+domainBoundaries[i][0]+'_index =('+domainBoundaries[i][1]+');'+domainBoundaries[i][0]+'_index <('+domainBoundaries[i][2]+');'+domainBoundaries[i][0]+'_index ++){'
            else:
                ncode = ncode + 'const size_t '+domainBoundaries[i][0]+'_index =('+domainBoundaries[i][1]+');{'
        ncode = ncode[:-1] + self.tmpGen(ret[4],'statement')
        for i in range(0,len(domainBoundaries)):
            ncode = ncode+'}'


        ncode = ncode[:-1]+'wait_to_recv(external_region);'
        for i in range(0,len(domainBoundaries)):
            if domainBoundaries[i][1]!=domainBoundaries[i][2]:
                if i==0:
                    mv='min_outer_'+self.localDomain[0][0]+'_region'
                    Mv='max_outer_'+self.localDomain[0][0]+'_region'
                    ncode = ncode + 'size_t '+mv+'= someformula;'
                    ncode = ncode + 'size_t '+Mv+'= someformula;'
                    domainBoundaries[0][1]=mv
                    domainBoundaries[0][2]=Mv
                if self.recommendedAnnotations.get(str(i)) != None:
                    ncode = ncode + '__AddAnnotation("'+self.recommendedAnnotations[str(i)]+'");'
                elif self.recommendedAnnotations.get(str(i-len(domainBoundaries))) != None:
                    ncode = ncode + '__AddAnnotation("'+self.recommendedAnnotations[str(i-len(domainBoundaries))]+'");'
                elif self.recommendedAnnotations.get('DEFAULT') != None:
                    ncode = ncode + '__AddAnnotation("'+self.recommendedAnnotations['DEFAULT']+'");'
                ncode = ncode + 'for(size_t '+domainBoundaries[i][0]+'_index =('+domainBoundaries[i][1]+');'+domainBoundaries[i][0]+'_index <('+domainBoundaries[i][2]+');'+domainBoundaries[i][0]+'_index ++){'
            else:
                ncode = ncode + 'const size_t '+domainBoundaries[i][0]+'_index =('+domainBoundaries[i][1]+');{'
        ncode = ncode[:-1] + self.tmpGen(ret[4],'statement')
        for i in range(0,len(domainBoundaries)):
            ncode = ncode+'}'''

#####
        
        
        newast = self.tmpParse(ncode,'statement',[])
        ret = newast[2]
        return ret
    
    def copyL(self,l):
        if isinstance(l, list):
            ret = []
            for i in l:
                ret.append(self.copyL(i))
            return ret
        else:
            return l

    def parseDomainBoundaries(self,domainExpr,iteratorIndex,errLine):
        if len(domainExpr)>2:
            if domainExpr[1]=='[expression]':
                if domainExpr[2][2][0]=='||':
                    return [[domainExpr[0],self.tmpGen(domainExpr[2][2][1],'logical_or_expression'),self.tmpGen(domainExpr[2][2][2],'logical_or_expression')]]
                else:
                    return [[domainExpr[0],self.tmpGen(domainExpr[2][2][0],'logical_or_expression'),self.tmpGen(domainExpr[2][2][0],'logical_or_expression')]]
            elif domainExpr[0]=='*':
                return self.parseDomainBoundaries(domainExpr[1],iteratorIndex,errLine)+ self.parseDomainBoundaries(domainExpr[2],iteratorIndex,errLine)
            elif domainExpr[0]=='/':
                ret=[]
                for i in self.parseDomainBoundaries(domainExpr[1],iteratorIndex,errLine):
                    if i[0]!=domainExpr[2][0]:
                        ret.append(i)
                return ret
            elif domainExpr[0]=='|':
                ret=[]
                for i in self.parseDomainBoundaries(domainExpr[1],iteratorIndex,errLine):
                    if i[0]!=domainExpr[2][0]:
                        ret.append(i)
                    else:
                        ret=ret+self.parseDomainBoundaries(domainExpr[2],iteratorIndex,errLine)
                return ret                
        elif len(domainExpr)==1:
            for c in self.globalDomainBoundaries:
                if domainExpr[0]=='grid'+c[0]:
                    self.localDomain = self.copyL(c[1])
                    return self.copyL(c[1])
                elif domainExpr[0]=='grid':
                    for i in self.defaultDomainIndices[1:]:
                        if i[0]==c[0]:
                            for j in i[1:]:
                                if j==iteratorIndex:
                                    self.localDomain = self.copyL(c[1])
                                    return self.copyL(c[1])
            for c in self.globalDomainBoundaries:
                if domainExpr[0]=='grid':
                    if self.defaultDomainIndices[0]==c[0]:
                        self.localDomain = self.copyL(c[1])
                        return self.copyL(c[1])

        self.GPL.currentPos = errLine
        self.GPL.reportError('foreach statement: unexpected grid expression')
        exit(-1)
    
    def translateIndices(self,ast,iteratorIndex,domainBoundaries,errLine,varList):
        if isinstance(ast, list):
            assym=['=','*=','/=','%=','+=','-=','<<=','>>=','&=','^=','|=']#funcKerAn...
            if isinstance(ast[0], str):
                for s in assym:
                    if ast[0]==s:
                        ret = [ast[0]]
                        varList.append(['=',[]])
                        varList[0]=1
                        ret.append(self.translateIndices(ast[1],iteratorIndex,domainBoundaries,errLine,varList))
                        varList[0]=2
                        ret.append(self.translateIndices(ast[2],iteratorIndex,domainBoundaries,errLine,varList))
                        varList[0]=0
                        return ret#funcKerAn
            ret = []
            i = 0
            vla=False#funcKerAn
            while i < len(ast):
                if ast[i]=='[expression]':
                    si=0
                    while isinstance(ast[si], str):
                        si = si+1
                    if not vla:#funcKerAn...
                        if varList[0]==3:
                            varList[-1][-1].append(''.join(ast[:si-1]))
                        elif varList[0]==2:
                            varList[-1].append([''.join(ast[:si-1])])
                        elif varList[0]==1:
                            varList[-1][-1]=[''.join(ast[:si-1])]
                        elif varList[0]==0:
                            varList.append(['?',[''.join(ast[:si-1])]])
                        else:
                            print 'Tool Error'
                            exit(1)
                        vla=True#funcKerAn
                    if i == len(ast)-2:
                        if isinstance(ast[si-2], str):
                            if self.symbolTable.get(ast[si-2]) != None:
                                ret = ret+ re.split(' ',self.symbolTable[ast[si-2]][4])
                    rtl = len(ret)
                    ret = ret+self.translateIndex(ast[i+1][2],ast[si-2],iteratorIndex,domainBoundaries,errLine)
                    varListS = varList[0]#funcKerAn
                    varList[0]=3#funcKerAn
                    for j in range(rtl,len(ret)):
                        ret[j]=self.translateIndices(ret[j],iteratorIndex,domainBoundaries,errLine,varList)
                    i=i+2
                    varList[0]=varListS#funcKerAn
                else:
                    ret.append(self.translateIndices(ast[i],iteratorIndex,domainBoundaries,errLine,varList))
                    i=i+1
            return ret
        else:
            return ast
        
    def translateIndex(self,ast,varName,iteratorIndex,domainBoundaries,errLine):
        if ast[0]==iteratorIndex:
            if self.symbolTable.get(varName) != None:
                domainBoundaries = self.symbolTable[varName][3][1]
            else:
                self.GPL.currentPos = errLine
                self.GPL.reportError('The variable '+ varName +' is not declared with extended language')
            ret=[]
            for i in domainBoundaries:
                ret = ret+['[expression]',[-1, 'expression', [i[0]+'_index']]]
            if len(ast)>1:
                i = 1
                while i < len(ast):
                    if ast[i]=='.':
                        None
                    else:
                        for j in self.indexOperators:
                            if j[0]== ast[i]:
                                if j[1]=='' and ast[i+1]=='()':
                                    if j[2]=='RETURN':
                                        retList = re.findall(r'[a-zA-Z_][0-9a-zA-Z_]+', j[3])
                                        newRet = []
                                        k=0
                                        while k<len(domainBoundaries):
                                            for r in retList:
                                                if r==domainBoundaries[k][0]:
                                                    newRet.append(ret[2*k])
                                                    newRet.append(ret[2*k+1])
                                                    break
                                            k = k+1
                                        ret = newRet
                                    elif j[2]=='DROP':
                                        retList = re.findall(r'[a-zA-Z_][0-9a-zA-Z_]+', j[3])
                                        newRet = []
                                        k=0
                                        while k<len(domainBoundaries):
                                            found = False
                                            for r in retList:
                                                if r==domainBoundaries[k][0]:
                                                    found = True
                                                    break
                                            if found==False:
                                                newRet.append(ret[2*k])
                                                newRet.append(ret[2*k+1])
                                            k = k+1
                                        ret = newRet
                                    else:
                                        k=0
                                        while k<len(domainBoundaries):
                                            if j[2]==domainBoundaries[k][0]:
                                                break
                                            k = k+1
                                        if k==len(domainBoundaries):
                                            self.GPL.currentPos = errLine
                                            self.GPL.reportError('[CONFIGURATION problem] In configuration file: in\n'+j[0]+'('+j[1]+'):'+j[2]+'='+j[3]+'\nan invalid index '+ j[2]+' is referenced ')

                                        k = k*2+1
                                        newExpStr=j[3]
                                        subList = re.findall(r'\$[a-zA-Z_][0-9a-zA-Z_]+', newExpStr)
                                        for si in range(0,len(subList)):
                                            sk=0
                                            while sk<len(domainBoundaries):
                                                if subList[si][1:]==domainBoundaries[sk][0]:
                                                    break
                                                sk = sk+1
                                            if sk==len(domainBoundaries):
                                                if subList[si][1:]=='iteratorIndex':
                                                    subList[si]=[subList[si],iteratorIndex]
                                                else:
                                                    self.GPL.currentPos = errLine
                                                    self.GPL.reportError('[CONFIGURATION problem] In configuration file: in\n'+j[0]+'('+j[1]+'):'+j[2]+'='+j[3]+'\nan invalid index '+ subList[si]+' is referenced ')
                                            else:
                                                sk = sk*2+1
                                                subList[si]=[subList[si],'('+self.tmpGen(ret[sk][2],'logical_or_expression')+')']
                                        for si in subList:
                                            newExpStr = re.sub('\\'+si[0],si[1],newExpStr,flags=re.M|re.S)
                                        ret[k][2]=self.tmpParse(newExpStr,'logical_or_expression',[])
                                elif j[1]!='' and ast[i+1]=='(argument_expression_list)':
                                    if j[2]=='RETURN':
                                        retList = re.findall(r'[a-zA-Z_][0-9a-zA-Z_]+', j[3])
                                        newRet = []
                                        k=0
                                        while k<len(domainBoundaries):
                                            for r in retList:
                                                if r==domainBoundaries[k][0]:
                                                    newRet.append(ret[2*k])
                                                    newRet.append(ret[2*k+1])
                                                    break
                                            k = k+1
                                        ret = newRet
                                    elif j[2]=='DROP':
                                        retList = re.findall(r'[a-zA-Z_][0-9a-zA-Z_]+', j[3])
                                        newRet = []
                                        k=0
                                        while k<len(domainBoundaries):
                                            found = False
                                            for r in retList:
                                                if r==domainBoundaries[k][0]:
                                                    found = True
                                                    break
                                            if found==False:
                                                newRet.append(ret[2*k])
                                                newRet.append(ret[2*k+1])
                                            k = k+1
                                        ret = newRet
                                    else:
                                        k=0
                                        while k<len(domainBoundaries):
                                            if j[2]==domainBoundaries[k][0]:
                                                break
                                            k = k+1
                                        if k==len(domainBoundaries):
                                            self.GPL.currentPos = errLine
                                            self.GPL.reportError('[CONFIGURATION problem] In configuration file: in\n'+j[0]+'('+j[1]+'):'+j[2]+'='+j[3]+'\nan invalid index '+ j[2]+' is referenced ')
                                        k = k*2+1
                                        newExpStr=j[3]
                                        subList = re.findall(r'\$[a-zA-Z_][0-9a-zA-Z_]+', newExpStr)
                                        for si in range(0,len(subList)):
                                            sk=0
                                            while sk<len(domainBoundaries):
                                                if subList[si][1:]==domainBoundaries[sk][0]:
                                                    break
                                                sk = sk+1
                                            if sk==len(domainBoundaries):
                                                if subList[si][1:]=='iteratorIndex':
                                                    subList[si]=[subList[si],iteratorIndex]
                                                else:
                                                    self.GPL.currentPos = errLine
                                                    self.GPL.reportError('[CONFIGURATION problem] In configuration file, in\n'+j[0]+'('+j[1]+'):'+j[2]+'='+j[3]+'\nan invalid index '+ subList[si]+' is referenced ')
                                            else:
                                                sk = sk*2+1
                                                subList[si]=[subList[si],'('+self.tmpGen(ret[sk][2],'logical_or_expression')+')']
                                        for si in subList:
                                            newExpStr = re.sub('\\'+si[0],si[1],newExpStr,flags=re.M|re.S)
                                        subList = re.findall(r'\$[0-9]+', newExpStr)
                                        for arg in subList:
                                            if int(arg[1:])>len(ast[i+2])-3:#change later to choose among overloaded operators with various args
                                                self.GPL.currentPos = errLine
                                                self.GPL.reportError('[CONFIGURATION or SOURCE problem]The configuration file\n'+j[0]+'('+j[1]+'):'+j[2]+'='+j[3]+'\nreferences an argument not provided by the source code within the iterator\n')
                                            newExpStr = re.sub('\\'+arg,'('+self.tmpGen(ast[i+2][int(arg[1:])+2],'logical_or_expression')+')',newExpStr,flags=re.M|re.S)
                                        ret[k][2]=self.tmpParse(newExpStr,'logical_or_expression',[])
                    i = i+1
            for l in self.memoryLayouts:
                if 2*l[0]==len(ret):
                    newRet = []
                    for i in l[1:]:
                        newExpStr = i
                        subList = re.findall(r'\$[0-9]+', newExpStr)
                        for arg in subList:
                            if int(arg[1:])>=len(ret)/2:#change later to choose among overloaded operators with various args
                                self.GPL.currentPos = errLine
                                self.GPL.reportError('[CONFIGURATION problem]The configuration file\nINDEX'+j[0]+'('+j[1]+'):'+j[2]+'='+j[3]+'\nreferences an argument not provided by the source code within the iterator\n')
                            newExpStr = re.sub('\\'+arg,'('+self.tmpGen(ret[int(arg[1:])*2+1][2],'logical_or_expression')+')',newExpStr,flags=re.M|re.S)
                        newRet = newRet+['[expression]',[-1, 'expression', self.tmpParse(newExpStr,'logical_or_expression',[])]]
                    return newRet
            return ret
        return ['[expression]',[-1, 'expression',ast]]
    
    def translateSpecialExpressions(self,ast,iteratorIndex,domainBoundaries,errLine):
        for i in self.specialExpressions:
            skipExp = False
            oldCode = i[0]
            newCode = i[1]
            subList = re.findall(r'\$[a-zA-Z_][0-9a-zA-Z_]+', oldCode)
            for si in range(0,len(subList)):
                sk=0
                while sk<len(domainBoundaries):
                    if subList[si][1:]==domainBoundaries[sk][0]:
                        break
                    sk = sk+1
                if sk==len(domainBoundaries):
                    if subList[si][1:]=='iteratorIndex':
                        subList[si]=[subList[si],iteratorIndex]
                    else:
                        skipExp = True
                else:
                    subList[si]=[subList[si],subList[si][1:]+'_index']
                if skipExp:
                    break
            if skipExp:
                continue
            for si in subList:
                oldCode = re.sub('\\'+si[0],si[1],oldCode,flags=re.M|re.S)

            subList = re.findall(r'\$[a-zA-Z_][0-9a-zA-Z_]+', newCode)
            for si in range(0,len(subList)):
                sk=0
                while sk<len(domainBoundaries):
                    if subList[si][1:]==domainBoundaries[sk][0]:
                        break
                    sk = sk+1
                if sk==len(domainBoundaries):
                    if subList[si][1:]=='iteratorIndex':
                        subList[si]=[subList[si],iteratorIndex]
                    else:
                        skipExp = True
                else:
                    subList[si]=[subList[si],subList[si][1:]+'_index']
                if skipExp:
                    break
            if skipExp:
                continue
            for si in subList:
                newCode = re.sub('\\'+si[0],si[1],newCode,flags=re.M|re.S)

            ast=self.replace(ast,self.tmpParse(oldCode,'logical_or_expression',[]),self.tmpParse(newCode,'logical_or_expression',[]))
        return ast

    def replace(self,ast,oldnode,newnode):
        if isinstance(ast, list):
            ret = []
            for i in ast:
                ret.append(self.replace(i,oldnode,newnode))
            if cmp(ret,oldnode)==0:
                return newnode                
            return ret
        elif isinstance(ast, int):
            return -1
        else:
            return ast
    
    def timestep_statement(self):
        revert = self.GPL.currentPos
        
        self.GPL.skipSpaces()
        symb = self.GPL.checkSymbol('(TIME\s*STEP)|(time\s*step)\s*')
        if symb==None:
            self.GPL.currentPos = revert
            return None
        self.GPL.srcCode = self.GPL.srcCode[:revert]+' for'+self.GPL.srcCode[self.GPL.currentPos:]
        self.GPL.currentPos = revert
        tmpSt = self.GPL.iteration_statement()
        tmpStr = '{'
        if self.recommendedAnnotations.get('TIMESTEPS') != None:
            tmpStr = tmpStr + '__AddAnnotation("'+self.recommendedAnnotations['TIMESTEPS']+'");'
        tmpStr = tmpStr + self.tmpGen(tmpSt,'iteration_statement')
        tmpStr = tmpStr + '}'
        return self.tmpParse(tmpStr,'compound_statement',[])
        
    def comm_init_statement(self):
        revert = self.GPL.currentPos
        
        self.GPL.skipSpaces()
        symb = self.GPL.checkSymbol('INITCOMM\s*;')
        if symb==None:
            self.GPL.currentPos = revert
            return None
        self.add_comm_globals(True)
        self.add_alloc_global_vars(True)
        return self.tmpParse(self.commInitCode,'compound_statement',[])
    
    def add_comm_globals(self,g):
        if self.tCommGlobals==1:
            return
        if g:
            self.tCommGlobals = 1
        else:
            self.tCommGlobals = 2
        self.TUs[2]=[]
        for d in self.commGlobals:
            if g:
                dt = d
            else:
                dt = 'extern '+d
            self.TUs[2].append( self.tmpParse(dt,'translation_unit',[]) )

    def comm_lib_init_statement(self):
        revert = self.GPL.currentPos
        
        self.GPL.skipSpaces()
        symb = self.GPL.checkSymbol('INITCOMMLIB\s*;')
        if symb==None:
            self.GPL.currentPos = revert
            return None
        self.addCommIncs()
        return self.tmpParse(self.commLibInitCode,'compound_statement',[])

    def comm_lib_finalize_statement(self):
        revert = self.GPL.currentPos
        
        self.GPL.skipSpaces()
        symb = self.GPL.checkSymbol('FINCOMMLIB\s*;')
        if symb==None:
            self.GPL.currentPos = revert
            return None
        self.addCommIncs()
        return self.tmpParse(self.commFinCode,'compound_statement',[])

    def expression(self):
        revert = self.GPL.currentPos
        ret=[revert,'dsl_expression']
        
        self.GPL.skipSpaces()
        symb = self.GPL.checkSymbol('REDUCE\s*\(')
        if symb==None:
            self.GPL.currentPos = revert
            return None
        
        self.GPL.skipSpaces()
        redOperator = self.GPL.checkSymbol('[+*]')
        if redOperator==None:
            self.GPL.currentPos = revert
            return None

        self.GPL.skipSpaces()
        symb = self.GPL.checkSymbol(',')
        if symb==None:
            self.GPL.currentPos = revert
            return None

        self.GPL.skipSpaces()
        redIndex = self.GPL.checkID()
        if redIndex==None:
            self.GPL.currentPos = revert
            return None

        self.GPL.skipSpaces()
        symb = self.GPL.checkSymbol('=\s*{')
        if symb==None:
            self.GPL.currentPos= revert
            return None

        self.GPL.skipSpaces()
        lowerLim = self.GPL.checkSymbol('-?[0-9]+')#currently simple int values for the range of reduction operator
        if lowerLim==None:
            self.GPL.currentPos= revert
            return None

        self.GPL.skipSpaces()
        symb = self.GPL.checkSymbol('\.\.')
        if symb==None:
            self.GPL.currentPos= revert
            return None

        self.GPL.skipSpaces()
        higherLim = self.GPL.checkSymbol('-?[0-9]+')#currently simple int values for the range of reduction operator
        if higherLim==None:
            self.GPL.currentPos= revert
            return None

        self.GPL.skipSpaces()
        symb = self.GPL.checkSymbol('}\s*,')
        if symb==None:
            self.GPL.currentPos= revert
            return None
        
        self.GPL.skipSpaces()
        redExpression = self.GPL.logical_or_expression()
        if redExpression==None:
            self.GPL.currentPos= revert
            return None

        self.GPL.skipSpaces()
        symb = self.GPL.checkSymbol('\)')
        if symb==None:
            self.GPL.currentPos= revert
            return None
        
        expExpression = '('
        redExpressiont = '('+self.tmpGen(redExpression,'logical_or_expression')+')'
        for i in range(int(lowerLim),int(higherLim)):
            itExp = redExpressiont
            while True:
                m = re.search('[^0-9a-zA-Z_]('+redIndex+')[^0-9a-zA-Z_]',itExp,flags=re.M|re.S)
                if m==None:
                    break
                itExp = itExp[:m.start(1)]+str(i)+itExp[m.end(1):]
            expExpression = expExpression + itExp + redOperator
        itExp = redExpressiont
        while True:
            m = re.search('[^0-9a-zA-Z_]('+redIndex+')[^0-9a-zA-Z_]',itExp,flags=re.M|re.S)
            if m==None:
                break
            itExp = itExp[:m.start(1)]+higherLim+itExp[m.end(1):]
        expExpression = expExpression + itExp
        expExpression = expExpression + ')'
        
        return self.tmpParse(expExpression,'logical_or_expression',[])
    
    def addCommIncs(self):
        if self.commNeededIncs[0]==False:
            pos=0
            incLst=[]
            for inc in self.commNeededIncs[1:]:
                incLst.append([pos,pos,'#include '+inc])
                pos+=1
            self.GPL.pragmas[0][0]=pos
            self.GPL.pragmas=incLst+self.GPL.pragmas
            self.commNeededIncs[0]=True



class optimizer:
    def __init__(self):
        self.modules=[]
        self.optList=[]
        self.functionsDefined=[]
        
    def addModule(self,entry):
        self.modules.append(entry)
        
    def rInline(self,ast,st,modname):
        if isinstance(ast, list):
            if len(ast)>1:
                if isinstance(ast[1],str)==True:
                    if ast[1]=='expression':
                        self.rInline2(ast,st,[],modname)
            for i in range(0,len(ast)):
                self.rInline(ast[i],st+[i],modname)

    def rInline2(self,ast,pst,st,modname):
        if isinstance(ast, list):
            for i in range(0,len(ast)-1):
                if isinstance(ast[i],list)==False and isinstance(ast[i+1],list)==False:
                    if ast[i+1]=='(argument_expression_list)' or ast[i+1]=='()':
                        for j in self.functionsDefined:
                            if j[0]==ast[i]:
                                self.optList.append(['inline',pst,st,j[1],modname,j[2]])
                                break
            for i in range(0,len(ast)):
                self.rInline2(ast[i],pst,st+[i],modname)
    
    def listFunctionsDefined(self):
        self.functionsDefined=[]
        for f in self.modules:
            for i in range(2,len(f[1].ast)):
                if f[1].ast[i][2][1]=='function_definition':
                    if f[1].ast[i][2][2][1]=='declaration_specifiers':
                        self.functionsDefined.append([f[1].ast[i][2][3][2][2],[i,2],f[0]])
                    else:
                        self.functionsDefined.append([f[1].ast[i][2][2][2][2],[i,2],f[0]])
    
    def toLine(self, pos,dsl):
        count = 1
        for i in range(0,pos):
            if dsl.GPL.srcCode[i]=='\n':
                count = count+1
        return count
    
    def findPossibleOptimizations(self):
        self.listFunctionsDefined()
        self.optList=[]
        for f in self.modules:
            self.kPrep(f[1].ast)
        for f in self.modules:
            self.rInline(f[1].ast,[],f[0])
        for f in self.modules:
            self.rFuse(f[1].ast,[],f[0])
        ret = ''
        for i in range(0,len(self.optList)):
            if self.optList[i][0]=='inline':
                for j in self.modules:
                    if j[0]==self.optList[i][4]:
                        dsl = j[1]
                        break
                ret = ret + str(i)+': '
                tr = dsl.ast
                for j in self.optList[i][1]:
                    tr = tr[j]
                ret = ret + 'expression in['+self.optList[i][4]+'] line['+ str(self.toLine(tr[0],dsl))
                for j in self.optList[i][2]:
                    tr = tr[j]
                ret = ret + '] inline call [ '+ dsl.tmpGen(tr,'postfix_expression')
                ret = ret + ' ...]\n'
            elif self.optList[i][0]=='fusion':
                for j in self.modules:
                    if j[0]==self.optList[i][2]:
                        dsl = j[1]
                        break
                ret = ret + str(i)+': in file[' +self.optList[i][2]+ '] fusion loop:------>\n'
                tr = dsl.ast
                for j in self.optList[i][1][0][1]:
                    tr = tr[j]
                ret = ret + str(dsl.tmpGen(tr,'statement')) + '\n with loop:------>\n'
                tr = dsl.ast
                for j in self.optList[i][1][len(self.optList[i][1])-1][1]:
                    tr = tr[j]
                ret = ret + str(dsl.tmpGen(tr,'statement')) + '\n\n'
        return ret
    
    def applyOptimization(self,no):
        if self.optList[no][0]=='inline':
            for j in self.modules:
                if j[0]==self.optList[no][4]:
                    caller = j[1]
                if j[0]==self.optList[no][5]:
                    callee = j[1]
            self.applyInline(self.optList[no][1],self.optList[no][2],self.optList[no][3],caller,callee)
        elif self.optList[no][0]=='fusion':
            for j in self.modules:
                if j[0]==self.optList[no][2]:
                    dsl = j[1]
                    break
            self.applyFusion(self.optList[no][1],dsl)
            
    def applyInline(self,pst,st,fst,caller,callee):
        func = self.getNode(fst,callee)
        body = func[-1]
        parLst = []
        if func[2][1]=='declaration_specifiers':
            ddecl = func[3][-1]
        else:
            ddecl = func[2][-1]
        if ddecl[3]=='(parameter_type_list)':
            parLst = ddecl[4][2][2:]
        call = self.getNode(pst+st,caller)
        for i in range(0,len(parLst)):
            body = self.parReplace(body,parLst[i][3][-1][-1],caller.tmpParse('('+caller.tmpGen(call[2][i+2],'assignment_expression')+')','primary_expression',[]))
        retvartype=func[2][-1]
        proc=0
        retvarname=''
        if retvartype != 'void':#handle better TODO
            proc=1
            retvarname=ddecl[2]+'_IH_'
            retvardec = callee.tmpParse(retvartype+' '+retvarname+';','declaration',[])
            body = body[:2] + [retvardec] + body[2:]
        body = self.retReplace(body,ddecl[2]+'_IH_',callee)
        body.append(callee.tmpParse(ddecl[2]+'_IL_'+':;','statement',[]))
        caller.ast = self.addRet(caller.ast,retvarname,pst+st)
        tst = pst
        while True:
            stmt = self.getNode(tst,caller)
            if stmt[1]=='statement':
                break
            tst=tst[:-1]
        caller.ast = self.addBody(caller.ast,body,tst,proc)
        
    def getNode(self,st,dsl):
        tr = dsl.ast
        for i in st:
            tr = tr[i]
        return tr

    def parReplace(self,ast,oldnode,newnode):
        if isinstance(ast, list):
            ret = []
            if cmp(ast,oldnode)==0:
                return newnode
                
            for i in ast:
                ret.append(self.parReplace(i,oldnode,newnode))
            return ret
        elif isinstance(ast, str):
            if isinstance(oldnode,str):
                if ast==oldnode:
                    return newnode
            return ast
        else:
            return ast

    def retReplace(self,ast,retvarname,dsl):
        if isinstance(ast, list):
            ret = []
            if len(ast)>2:
                if isinstance(ast[1],str)==True:
                    if ast[1]=='jump_statement':
                        if ast[2]=='return':
                            if len(ast)>3:
                                return dsl.tmpParse('{'+retvarname+'='+dsl.tmpGen(ast[3],'expression')+'; goto '+retvarname[:-4]+'_IL_'+';}','compound_statement',[])                
                            else:
                                return dsl.tmpParse('goto '+retvarname[:-4]+'_IL_'+';','jump_statement',[])                
            for i in ast:
                ret.append(self.retReplace(i,retvarname,dsl))
            return ret
        else:
            return ast

    def addBody(self,ast,body,st,proc):
        if len(st)==1:
            if ast[1]=='compound_statement':
                return ast[:st[0]]+body[2:]+ast[st[0]+proc:]
            else:
                return ast[:st[0]]+[[-1,'statement',body]]+ast[st[0]+proc:]
        if isinstance(ast, list):
            ret = []
            for i in range(0,len(ast)):
                if i!=st[0]:
                    ret.append(ast[i])
                else:
                    ret.append(self.addBody(ast[i],body,st[1:],proc))
            return ret
        else:
            return ast

    def addRet(self,ast,retvarname,st):
        if len(st)==0:
            return [retvarname]
        if isinstance(ast, list):
            ret = []
            for i in range(0,len(ast)):
                if i!=st[0]:
                    ret.append(ast[i])
                else:
                    ret.append(self.addRet(ast[i],retvarname,st[1:]))
            return ret
        else:
            return ast

    def rFuse(self,ast,st,modname):
        if isinstance(ast, list):
            if len(ast)>3:
                if isinstance(ast[1],str)==True:
                    if ast[1]=='iteration_statement':
                        if ast[2]=='for':
                            self.rFuse2(st,modname)
            for i in range(0,len(ast)):
                self.rFuse(ast[i],st+[i],modname)

    def rFuse2(self,st,modname):
        for j in self.modules:
            if j[0]==modname:
                dsl = j[1]
                break
        cs= self.getNode(st[:-2],dsl)
        if len(cs)<2:
            return
        if isinstance(cs[1],str)!=True:
            return
        if cs[1]!='compound_statement':
            return
        for i in range(st[-2]+1,len(cs)):
            if cs[i][1]=='statement':
                if cs[i][2][1]=='iteration_statement':
                    if cmp(dsl.processTmpParse(self.getNode(st,dsl)[:-1]),dsl.processTmpParse(cs[i][2][:-1]))==0:
                        self.rFuse3(st,st[:-2]+[i,2],modname)

    def rFuse3(self,st1,st2,modname):
        tab=[]
        for j in self.modules:
            if j[0]==modname:
                dsl = j[1]
                break
        for i in range(st1[-2],st2[-2]+1):
            node = self.getNode(st1[:-2]+[i],dsl)
            if node[1]=='statement':
                rec = self.stmtAnalyse(node[2])
                if rec:
                    for ii in range(0,len(rec[2])):
                        jj=0
                        clen=len(rec[0])
                        while jj<clen:
                            if rec[2][ii]==rec[0][jj]:
                                del(rec[0][jj])
                                clen = clen - 1
                                continue
                            jj = jj + 1
                        jj=0
                        clen=len(rec[1])
                        while jj<clen:
                            if rec[2][ii]==rec[1][jj]:
                                del(rec[1][jj])
                                clen = clen - 1
                                continue
                            jj = jj + 1
                    del(rec[2])

            elif node[1]=='declaration':
                if len(node)>3:
                    rec = self.declAnalyse(node[3][2:])
            tab.append([0,st1[:-2]+[i]]+rec)
        #print tab
        for i in range(1,len(tab)-1):# TODO make sure to really enforce move policy
            mov=True
            for j in range(0,i):
                if tab[j][0]==-1 or tab[j][0]==2:
                    #tab[i][0]=-1
                    continue
                if self.movable(tab[i],tab[j]):
                    #tab[i][0]=-1
                    continue
                mov=False
                break
            if mov:
                if tab[i][0]==0:
                    tab[i][0]=-1
                elif tab[i][0]==1:#not needed if no multi-round check
                    tab[i][0]=2
                    
        for i in range(len(tab)-2,0,-1):# TODO make sure to really enforce move policy
            mov = True
            for j in range(i+1,len(tab)):
                if tab[j][0]==1 or tab[j][0]==2:# 2 may be not needed for single round checks
                    '''if tab[i][0]==-1:
                        tab[i][0]=2
                    else:#take care in multiround checks for old value 2
                        tab[i][0]=1'''
                    continue
                if self.movable(tab[i],tab[j]):
                    '''if tab[i][0]==-1:
                        tab[i][0]=2
                    else:#take care in multiround checks for old value 2
                        tab[i][0]=1'''
                    continue
                mov = False
                break
            if mov:
                if tab[i][0]==0:
                    tab[i][0]=1
                elif tab[i][0]==-1:
                    tab[i][0]=2
        fusable = True
        for i in tab[1:-1]:
            if i[0]==0:
                fusable=False
                break
        if fusable:
            self.optList.append(['fusion',tab,modname])                     
    
    def movable(self,s1,s2):
        for i in s1[2]:
            for j in s2[3]:
                if i==j:
                    #print i
                    #print s1[1][-1]
                    return False
        for i in s1[3]:
            for j in s2[2]:
                if i==j:
                    #print i
                    #print s1[1][-1]
                    return False
        if len(s1)>4:
            for i in s1[4]:
                for j in s2[2]+s2[3]:
                    if i==j:
                        #print i
                        #print s1[1][-1]
                        return False
        if len(s2)>4:
            for i in s2[4]:
                for j in s1[2]+s1[3]:
                    if i==j:
                        #print i
                        #print s2[1][-1]
                        return False
        return True

    def stmtAnalyse(self,ast):
        ret=[[],[],[]]
        if isinstance(ast, list):
            if isinstance(ast[0], str):
                assg = ['=','*=','/=','%=','+=','-=','<<=','>>=','&=','^=','|=',]
                for s in assg:
                    if ast[0]==s:
                        ret[0].append(ast[1][0])#extract from uniary, enhance,
                        ret[1] = ret[1] + self.travExp(ast[2])
            if len(ast)>2:#sample inc/dec pre
                if isinstance(ast[0], str) and isinstance(ast[1], str):
                    if ast[0]=='unary_expression' and (ast[1]=='++' or ast[1]=='--'):
                        ret[0].append(ast[2][0])#uniray enhance later
                        ret[1].append(ast[2][0])#uniray enhance later
            if len(ast)>1:
                if ast[1]=='declaration':
                    if len(ast)>3:
                        rec = self.declAnalyse(ast[3][2:])
                        if rec:
                            ret[0] = ret[0] + rec[0]
                            ret[1] = ret[1] + rec[1]
                            ret[2] = ret[2] + rec[2]
                        return ret

            for i in range(0,len(ast)):
                x=self.stmtAnalyse(ast[i])
                if x:
                    ret[0] = ret[0]+x[0]
                    ret[1] = ret[1]+x[1]
                    ret[2] = ret[2]+x[2]            
            return ret
        
    def travExp(self,ast):
        ret = []
        if isinstance(ast, list):
            if isinstance(ast[0], int):
                if len(ast)>1:
                    ast = ast[2:]
            for i in range(0,len(ast)):
                x=self.travExp(ast[i])
                if x:
                    ret = ret+x
        if isinstance(ast, str):#TODO handle variables in a more precice fashion
            m=re.match(r'[a-zA-Z_][0-9a-zA-Z_]*$',ast,flags=re.S)
            if m:
                ret.append(ast)
        return ret

    def declAnalyse(self,lst):
        ret=[[],[],[]]
        for i in lst:
            ret[2].append(i[2][2][2])
            if len(i)>3:
                ret[0].append(i[2][2][2])
                x = self.stmtAnalyse(i[3][2])
                if x:
                    ret[0] = ret[0]+x[0]
                    ret[1] = ret[1]+x[1]

        return ret
    
    def applyFusion(self,tab,dsl):
        dsl.ast=self.moveLoops(dsl.ast,tab[0][1],tab)

    def moveLoops(self,ast,st,tab):
        if len(st)==1:
            ret = ast[:tab[0][1][-1]]
            for i in range(1,len(tab)-1):
                if tab[i][0]==-1 or tab[i][0]==2:#may be handle 2 better later
                    ret.append(ast[tab[i][1][-1]])
            fstLoop = ast[tab[0][1][-1]]
            secLoop = ast[tab[len(tab)-1][1][-1]]
            fusedBlock = [-1, 'compound_statement']
            if fstLoop[2][-1][2][1] != 'compound_statement':
                fusedBlock.append(fstLoop[2][-1])
            else:
                for s in fstLoop[2][-1][2][2:]:
                    fusedBlock.append(s)
            if secLoop[2][-1][2][1] != 'compound_statement':
                fusedBlock.append(secLoop[2][-1])
            else:
                for s in secLoop[2][-1][2][2:]:
                    fusedBlock.append(s)
            fusedBlock = [-1, 'statement',fusedBlock]
            newLoop = fstLoop[0:2]
            newLoop.append(fstLoop[2][:-1])
            newLoop[2].append(fusedBlock)
            ret.append(newLoop)            
            for i in range(1,len(tab)-1):
                if tab[i][0]==1:
                    ret.append(ast[tab[i][1][-1]])
            ret = ret + ast[tab[len(tab)-1][1][-1]+1:]
            return ret
        if isinstance(ast, list):
            ret = []
            for i in range(0,len(ast)):
                if i!=st[0]:
                    ret.append(ast[i])
                else:
                    ret.append(self.moveLoops(ast[i],st[1:],tab))
            return ret
        else:
            return ast

    def kPrep(self,ast):
        if isinstance(ast, list):
            if len(ast)>2:
                if isinstance(ast[1],str)==True:
                    if ast[1]=='compound_statement':
                        rep = True
                        while rep:
                            for i in range(2,len(ast)):
                                res = self.kPrep2(ast[i])
                                if res:
                                    ast = ast[:i]+res+ast[i+1:]
                                    rep=True
                                    break
                                else:
                                    rep=False
            for i in range(0,len(ast)):
                ast[i]= self.kPrep(ast[i])
        return ast
        
    def kPrep2(self,ast):
        if isinstance(ast, list):
            if len(ast)>2:
                if isinstance(ast[1],str)==True:
                    if ast[1]=='statement':
                        if ast[2][1]=='compound_statement':
                            if ast[2][2][1]=='statement':
                                if ast[2][2][2][1]=='expression_statement':
                                    if ast[2][2][2][2][2][0]=='__AddAnnotation':
                                        if re.match(r'"\s*pragma\s*GGDML\s*kernel',ast[2][2][2][2][2][2][2][0],flags=re.M|re.S):
                                            return ast[2][3:]
        return None
