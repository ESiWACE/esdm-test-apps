# This file is part of the GGDML language extensions' source-to-source translator.
# The tool is intended to be used according to the GPL licence after the first
# version is published.
# This file works together with the GGDML extensions processor module.
# It is used to process the general-purpose-language.
# Nabeeh Jum'ah

import re
import os
class language:
    
    def __init__(self,DSL):
        self.storage_class_specifiers = ['typedef','extern','static','auto','register','inline']
        self.type_specifiers=['void','char','short','int','long','float','double','_Bool','_Complex','signed','unsigned']
        self.type_qualifiers=['const','restrict','volatile']
        self.keywords=self.storage_class_specifiers+self.type_specifiers+self.type_qualifiers+['for','while','do','sizeof','if','switch','case','return']
        self.currentPos = 0
        self.lComments=[]
        self.mComments=[]
        self.pragmas=[]
        self.DSL = DSL
        self.fileName = ''
        
    def readSource(self,filename):
        self.fileName = filename
        filevar = open(filename)
        self.srcCode = filevar.read()
        #preprocess
        self.includePaths = [os.path.dirname(os.path.abspath(filename))]+self.includePaths
        while True:
            m=re.search(r'//.*?$',self.srcCode,flags=re.M|re.S)
            if m==None:
                break
            self.lComments.append([m.start(), m.end(), self.srcCode[m.start():m.end()] ])
            self.srcCode = self.srcCode[:m.start()]+' '*(m.end()-m.start())+self.srcCode[m.end():]

        while True:
            m=re.search(r'/\*.*?\*/',self.srcCode,flags=re.M|re.S)
            if m==None:
                break
            self.mComments.append([m.start(), m.end(), self.srcCode[m.start():m.end()] ])
            self.srcCode = self.srcCode[:m.start()]+' '*(m.end()-m.start())+self.srcCode[m.end():]

        while True:
            m=re.search(r'^[ \t]*#.*?$',self.srcCode,flags=re.M|re.S)
            if m==None:
                break
            self.pragmas.append([m.start(), m.end(), self.srcCode[m.start():m.end()] ])
            self.srcCode = self.srcCode[:m.start()]+' '*(m.end()-m.start())+self.srcCode[m.end():]
            pText = m.group()
            m=re.search(r'#\s*include\s*\"(.+?)\"',pText,flags=re.M|re.S)
            if m!=None:
                nfn = m.group(1).strip()
                if os.path.exists(self.includePaths[0]+'/'+nfn):
                    self.handleIncludeFile(self.includePaths[0]+'/'+nfn)
            '''m=re.search(r'#\s*include\s*<(.+?)>',pText,flags=re.M|re.S)
            if m!=None:
                nfn = m.group(1).strip()
                for sp in self.includePaths:
                    if os.path.exists(sp+'/'+nfn):#postpone until ifdef switches are handled
                        #self.handleIncludeFile(sp+'/'+nfn)
                        break'''
                    
    def handleIncludeFile(self,filename):
        newDSLObj = self.DSL.__class__(self.DSL.confFileName)
        newDSLObj.readSource(filename)
        newDSLObj.parse()
        for i in newDSLObj.GPL.type_specifiers:
            found = False
            for j in self.type_specifiers:
                if i==j:
                    found=True
                    break
            if found==False:
                self.type_specifiers.append(i)
        t = newDSLObj.symbolTable
        t.update(self.DSL.symbolTable)
        self.DSL.symbolTable = t

    def reportError(self,errText):
        err = 'Error in ['
        if self.fileName!='':
            err = err + self.fileName
        else:
            err = err + 'external configuration code'
        el = self.errorLine()
        err = err + '] in line [' + str(el[0]) + '], ' + errText + ': ' + el[1]
        print err
        exit(1)
        
    def errorLine(self):
        ln = 1
        lb = 0
        for i in range(0,self.currentPos):
            if self.srcCode[i]=='\n':
                ln = ln+1
                lb = i
        le = 0
        for i in range(self.currentPos,len(self.srcCode)):
            if self.srcCode[i]=='\n':
                le = i
                break
        src = self.srcCode[lb:self.currentPos]+' <here> '+self.srcCode[self.currentPos:le]
        return [ln,src]

    def skipSpaces(self):
        mr = re.match('(\s*)', self.srcCode[self.currentPos:], re.S)
        if mr:
            self.currentPos = self.currentPos + mr.end(1)
            return mr.group(1)
        return None

   
    def checkType(self):
        for ty in self.type_specifiers:
            if self.checkSymbol(ty):
                return ty
        return None

    def checkID(self):
        revert = self.currentPos
        symb = self.checkSymbol('[a-zA-Z_][0-9a-zA-Z_]*')
        if symb==None:
            self.currentPos=revert
            return None
        for i in self.keywords:
            if i == symb:
                self.currentPos = revert
                return None
        return symb
        
        

    def checkSymbol(self,symbol):
        mr = re.match('('+symbol+')', self.srcCode[self.currentPos:], re.S)
        if mr:
            self.currentPos = self.currentPos + mr.end(1)
            return mr.group(1)
        return None
###########################################
    def declaration(self):
        self.dsl_declaration = False
        revert = self.currentPos
        ret=[self.currentPos,'declaration']
        
        self.skipSpaces()
        symb = self.declaration_specifiers()
        if symb==None:
            self.currentPos=revert
            return None
        ret.append(symb)
        
        revert = self.currentPos
        self.skipSpaces()
        symb = self.init_declarator_list()
        if symb==None:
            self.currentPos=revert
        else:
            ret.append(symb)

        self.skipSpaces()
        symb = self.checkSymbol(';')
        if symb==None:
            self.reportError('expected ;')
            return None

        if self.dsl_declaration == True:
            ret = self.DSL.translate_declaration(ret,'declaration')
        
        if ret[2][2]=='typedef':
            self.type_specifiers.append(ret[3][2][2][2][2])

        return ret

    def declaration_specifiers(self):
        revert = self.currentPos
        ret=[self.currentPos,'declaration_specifiers']
        
        while True:
            self.skipSpaces()
            symb = self.storage_class_specifier()
            if symb!=None:
                ret.append(symb)
                continue

            self.skipSpaces()
            symb = self.type_specifier()
            if symb!=None:
                ret.append(symb)
                continue

            self.skipSpaces()
            symb = self.type_qualifier()
            if symb!=None:
                ret.append(symb)
                continue
            break
        if len(ret)==2:
            return None
        return ret

    def init_declarator_list(self):
        revert = self.currentPos
        ret=[self.currentPos,'init_declarator_list']
        
        self.skipSpaces()
        symb = self.init_declarator()
        if symb!=None:
            ret.append(symb)
            while True:
                self.skipSpaces()
                symb = self.checkSymbol(',')
                if symb==None:
                    return ret
                self.skipSpaces()
                symb = self.init_declarator()
                if symb==None:
                    print 'init_declarator expected'#should return with error
                    break
                ret.append(symb)
        return None

    def init_declarator(self):
        revert = self.currentPos
        ret=[self.currentPos,'init_declarator']
        
        self.skipSpaces()
        symb = self.declarator()
        if symb==None:
            return None            
        ret.append(symb)
        
        self.skipSpaces()
        symb = self.checkSymbol('=')
        if symb==None:
            return ret
        
        self.skipSpaces()
        symb = self.initializer()
        if symb==None:
            print 'initializer expected'#error, revert
            return ret
        ret.append(symb)
        return ret
        
    def storage_class_specifier(self):
        for i in self.storage_class_specifiers:
            if self.checkSymbol(i)!=None:
                return i
        return None

    def type_specifier(self):
        self.skipSpaces()
        if self.DSL!=None:
            symb = self.DSL.type_specifier()
            if symb!=None:
                self.dsl_declaration = True
                return symb
        
        for i in self.type_specifiers:
            m = re.match('('+i+')[^0-9a-zA-Z_]', self.srcCode[self.currentPos:], re.S)
            if m:
                self.currentPos = self.currentPos + m.end(1)
                return i
            
        self.skipSpaces()
        symb = self.struct_or_union_specifier()
        if symb!=None:
            return symb

        symb = self.enum_specifier()
        if symb!=None:
            return symb
        
        return None

    def type_qualifier(self):
        for i in self.type_qualifiers:
            if self.checkSymbol(i)!=None:
                return i
        return None

    def struct_or_union_specifier(self):
        revert = self.currentPos
        ret=[self.currentPos,]
        
        self.skipSpaces()
        symb = self.checkSymbol('struct')
        if symb==None:
            symb = self.checkSymbol('union')
            if symb==None:
                return None
        ret.append(symb)

        self.skipSpaces()
        symb = self.checkID()
        if symb==None:
            symb = ''
        ret.append(symb)#add name or empty for non-named
        
        self.skipSpaces()
        symb = self.checkSymbol('\{')
        if symb==None:
            return ret
        
        self.skipSpaces()
        symb = self.struct_declaration_list()
        if symb!=None:
            ret.append(symb)

        self.skipSpaces()
        symb = self.checkSymbol('\}')
        if symb==None:
            self.reportError('expected } to end struct/union') 
        
        return ret

    def struct_declaration_list(self):
        revert = self.currentPos
        ret=[self.currentPos,'struct_declaration_list']
        
        while True:
            self.skipSpaces()
            symb = self.struct_declaration()
            if symb==None:
                break
            ret.append(symb)
        if len(ret)==2:
            return None
        return ret

    def struct_declaration(self):
        self.dsl_declaration = False
        revert = self.currentPos
        ret=[self.currentPos,'struct_declaration']
        
        self.skipSpaces()
        symb = self.specifier_qualifier_list()
        if symb==None:
            self.currentPos=revert
            return None
        ret.append(symb)
        
        self.skipSpaces()
        symb = self.struct_declarator_list()
        if symb==None:
            self.currentPos=revert
            return None
        ret.append(symb)

        self.skipSpaces()
        symb = self.checkSymbol(';')
        if symb==None:
            self.reportError('expected ;') 
            return None
        
        if self.dsl_declaration == True:
            ret = self.DSL.translate_declaration(ret,'struct_declaration')
        return ret

    def specifier_qualifier_list(self):
        revert = self.currentPos
        ret=[self.currentPos,'specifier_qualifier_list']
        
        while True:
            self.skipSpaces()
            symb = self.type_specifier()
            if symb!=None:
                ret.append(symb)
                continue

            self.skipSpaces()
            symb = self.type_qualifier()
            if symb!=None:
                ret.append(symb)
                continue
            break
        if len(ret)==2:
            return None
        return ret

    def struct_declarator_list(self):
        revert = self.currentPos
        ret=[self.currentPos,'struct_declarator_list']
        
        self.skipSpaces()
        symb = self.struct_declarator()
        if symb!=None:
            ret.append(symb)
            while True:
                self.skipSpaces()
                symb = self.checkSymbol(',')
                if symb==None:
                    return ret
                self.skipSpaces()
                symb = self.struct_declarator()
                if symb==None:
                    print 'init_declarator expected'#should return with error
                    break
                ret.append(symb)
        return None

    def struct_declarator(self):
        revert = self.currentPos
        ret=[self.currentPos,'struct_declarator']#needed?
        
        self.skipSpaces()
        symb = self.declarator()
        if symb!=None:
            ret.append(symb)
        
        self.skipSpaces()
        symb = self.checkSymbol(':')
        if symb!=None:
            self.skipSpaces()
            symb = self.constant_expression()
            if symb==None:
                self.reportError('value needed after colon(:)')
            ret.append(symb)
        
        if len(ret)==2:
            return None
        return ret

    def enum_specifier(self):
        revert = self.currentPos
        ret=[self.currentPos,'enum']
        
        self.skipSpaces()
        symb = self.checkSymbol('enum')
        if symb==None:
            return None

        self.skipSpaces()
        symb = self.checkID()
        if symb==None:
            symb = ''
        ret.append(symb)#add name or empty for non-named
        
        self.skipSpaces()
        symb = self.checkSymbol('\{')
        if symb==None:
            return ret
        
        self.skipSpaces()
        symb = self.enumerator_list()
        if symb==None:
            self.currentPos = revert
            self.reportError('enum should have a list of enumerators')
            return None
        ret.append(symb)

        self.skipSpaces()
        symb = self.checkSymbol('\}')
        if symb==None:
            self.reportError('expected } to end struct/union')
        
        return ret

    def enumerator_list(self):
        revert = self.currentPos
        ret=[self.currentPos,'enumerator_list']
        
        self.skipSpaces()
        symb = self.enumerator()
        if symb!=None:
            ret.append(symb)
            while True:
                self.skipSpaces()
                symb = self.checkSymbol(',')
                if symb==None:
                    return ret
                self.skipSpaces()
                symb = self.enumerator()
                if symb==None:
                    print 'init_declarator expected'#should return with error
                    break
                ret.append(symb)
        return None

    def enumerator(self):
        revert = self.currentPos
        ret=[self.currentPos,'enumerator']
        
        self.skipSpaces()
        symb = self.checkID()
        if symb==None:
            return None
        ret.append(symb)
        
        self.skipSpaces()
        symb = self.checkSymbol('=')
        if symb==None:
            return ret
        
        self.skipSpaces()
        symb = self.constant_expression()
        if symb==None:
            self.reportError('expected constant value after =')
        ret.append(symb)
        
        return ret

    def declarator(self):
        revert = self.currentPos
        ret=[self.currentPos,'declarator']
        
        self.skipSpaces()
        symb = self.pointer()
        if symb!=None:
            ret.append(symb)
        
        self.skipSpaces()
        symb = self.direct_declarator()
        if symb==None:
            self.currentPos = revert
            return None
        ret.append(symb)
        
        return ret

    def direct_declarator(self):
        revert = self.currentPos
        ret=[self.currentPos,'direct_declarator']
        
        self.skipSpaces()
        symb = self.checkID()
        if symb!=None:
            ret.append(symb)
        else:
            self.skipSpaces()
            symb = self.checkSymbol('\(')
            if symb==None:
                return None
            self.skipSpaces()
            symb = self.declarator()
            if symb==None:
                self.currentPos = revert
                return None
            ret.append(symb)
            self.skipSpaces()
            symb = self.checkSymbol('\)')
            if symb==None:
                self.currentPos = revert
                return None
            
        while True:
            self.skipSpaces()
            symb = self.checkSymbol('\[')
            if symb!=None:
                self.skipSpaces()
                symb = self.constant_expression()
                if symb!=None:
                    ret.append('[constant_expression]')
                    ret.append(symb)
                else:
                    ret.append('[]')
                self.skipSpaces()
                symb = self.checkSymbol('\]')
                if symb!=None:
                    continue
                else:
                    self.reportError('expected ]') 
                    return None
            else:
                self.skipSpaces()
                symb = self.checkSymbol('\(')
                if symb!=None:
                    self.skipSpaces()
                    symb = self.parameter_type_list()
                    if symb!=None:
                        ret.append('(parameter_type_list)')
                        ret.append(symb)
                    else:
                        self.skipSpaces()
                        symb = self.identifier_list()
                        if symb!=None:
                            ret.append('(identifier_list)')
                            ret.append(symb)
                        else:
                            ret.append('()')
                    self.skipSpaces()
                    symb = self.checkSymbol('\)')
                    if symb!=None:
                        continue
                    else:
                        self.reportError('expected )') 
                        return None
            break
        return ret
                    
    def pointer(self):
        revert = self.currentPos
        ret=[self.currentPos,'pointer']
        
        while True:
            self.skipSpaces()
            symb = self.checkSymbol('\*')
            if symb==None:
                break
            ret.append(symb)
            
            self.skipSpaces()
            symb = self.type_qualifier_list()
            if symb!=None:
                ret.append(symb)
        if len(ret)==2:
            return None
        return ret
        
    def type_qualifier_list(self):
        revert = self.currentPos
        ret=[]
        
        while True:
            self.skipSpaces()
            symb = self.type_qualifier()
            if symb==None:
                break
            ret.append(symb)
        if len(ret)==0:
            return None
        return ret

    def parameter_type_list(self):
        revert = self.currentPos
        ret=[self.currentPos,'parameter_type_list']
        
        self.skipSpaces()
        symb = self.parameter_list()
        if symb==None:
            return None
        ret.append(symb)
        
        self.skipSpaces()
        symb = self.checkSymbol(',')
        if symb!=None:
            self.skipSpaces()
            symb = self.checkSymbol('\.\.\.')
            if symb==None:
                self.reportError('expected parameter or (...)') 
                return None
            ret.append(symb)
        
        if len(ret)==2:
            return None
        return ret

    def parameter_list(self):
        revert = self.currentPos
        ret=[self.currentPos,'parameter_list']
        
        self.skipSpaces()
        symb = self.parameter_declaration()
        if symb!=None:
            ret.append(symb)
            while True:
                self.skipSpaces()
                revert = self.currentPos # var arg
                symb = self.checkSymbol(',')
                if symb==None:
                    return ret
                self.skipSpaces()
                symb = self.parameter_declaration()
                if symb==None:
                    self.currentPos = revert
                    return ret
                ret.append(symb)
        return None

    def parameter_declaration(self):
        revert = self.currentPos
        ret=[self.currentPos,'parameter_declaration']
        
        self.skipSpaces()
        symb = self.declaration_specifiers()
        if symb==None:
            return None
        ret.append(symb)
        
        self.skipSpaces()
        symb = self.declarator()
        if symb==None:
            symb = self.abstract_declarator()
        if symb!=None:
            ret.append(symb)
        return ret

    def identifier_list(self):
        revert = self.currentPos
        ret=[self.currentPos,'identifier_list']
        
        self.skipSpaces()
        symb = self.checkID()
        if symb!=None:
            ret.append(symb)
            while True:
                self.skipSpaces()
                symb = self.checkSymbol(',')
                if symb==None:
                    return ret
                self.skipSpaces()
                symb = self.checkID()
                if symb==None:
                    self.reportError('expected identifier') 
                    return None
                ret.append(symb)
        return None

    def type_name(self):
        revert = self.currentPos
        ret=[self.currentPos,'type_name']
        
        self.skipSpaces()
        symb = self.specifier_qualifier_list()
        if symb==None:
            return None
        ret.append(symb)
        
        self.skipSpaces()
        symb = self.abstract_declarator()
        if symb!=None:
            ret.append(symb)
        return ret

    def abstract_declarator(self):
        revert = self.currentPos
        ret=[self.currentPos,'abstract_declarator']
        
        self.skipSpaces()
        symb = self.pointer()
        if symb!=None:
            ret.append(symb)
        
        self.skipSpaces()
        symb = self.direct_abstract_declarator()
        if symb!=None:
            ret.append(symb)
            
        if len(ret)==2:
            return None
        return ret

    def direct_abstract_declarator(self):
        revert = self.currentPos
        ret=[self.currentPos,'direct_abstract_declarator']#??
        
        self.skipSpaces()
        symb = self.checkSymbol('\(')
        if symb!=None:
            self.skipSpaces()
            symb = self.abstract_declarator()
            if symb!=None:
                ret.append('(abstract_declarator)')
                ret.append(symb)
            else:
                symb = self.parameter_type_list()
                if symb!=None:
                    ret.append('(parameter_type_list)')
                    ret.append(symb)
                else:
                    ret.append('()')
            self.skipSpaces()
            symb = self.checkSymbol('\)')
            if symb==None:
                self.reportError('expected )') 
                return None
        else:
            symb = self.checkSymbol('\[')
            if symb==None:
                return None
            self.skipSpaces()
            symb = self.constant_expression()
            if symb!=None:
                ret.append('[constant_expression]')
                ret.append(symb)
            else:
                ret.append('[]')
            self.skipSpaces()
            symb = self.checkSymbol('\]')
            if symb==None:
                self.reportError('expected ]') 
                return None

        while True:
            self.skipSpaces()
            symb = self.checkSymbol('\[')
            if symb!=None:
                self.skipSpaces()
                symb = self.constant_expression()
                if symb!=None:
                    ret.append('[constant_expression]')
                    ret.append(symb)
                else:
                    ret.append('[]')
                self.skipSpaces()
                symb = self.checkSymbol('\]')
                if symb!=None:
                    continue
                else:
                    self.reportError('expected ]') 
                    return None
            else:
                self.skipSpaces()
                symb = self.checkSymbol('\(')
                if symb!=None:
                    self.skipSpaces()
                    symb = self.parameter_type_list()
                    if symb!=None:
                        ret.append('(parameter_type_list)')
                        ret.append(symb)
                    else:
                        ret.append('()')
                    self.skipSpaces()
                    symb = self.checkSymbol('\)')
                    if symb!=None:
                        continue
                    else:
                        self.reportError('expected )') 
                        return None
            break
        return ret

    def initializer(self):
        revert = self.currentPos
        ret=[self.currentPos,'initializer']
        
        self.skipSpaces()
        symb = self.assignment_expression()
        if symb!=None:
            ret.append(symb)
            return ret
        
        symb = self.checkSymbol('\{')
        if symb==None:
            return None
        
        self.skipSpaces()
        symb = self.initializer_list()
        if symb==None:
            return None
        ret.append(symb)

        self.skipSpaces()
        symb = self.checkSymbol(',')
        if symb!=None:
            ret.append(symb)

        self.skipSpaces()
        symb = self.checkSymbol('\}')
        if symb==None:
            self.reportError('expected }') 
            return None
        
        return ret

    def initializer_list(self):
        revert = self.currentPos
        ret=[self.currentPos,'initializer_list']
        
        self.skipSpaces()
        symb = self.initializer()
        if symb!=None:
            ret.append(symb)
            while True:
                revert = self.currentPos
                self.skipSpaces()
                revert = self.currentPos
                symb = self.checkSymbol(',')
                if symb==None:
                    return ret
                self.skipSpaces()
                symb = self.initializer()
                if symb==None:
                    self.currentPos = revert
                    return ret# there could be a ', }' ending instead of '}' only
                ret.append(symb)
        return None

    def statement(self):
        revert = self.currentPos
        ret=[self.currentPos,'statement']
        
        self.skipSpaces()
        if self.DSL!=None:
            symb = self.DSL.statement()
            if symb!=None:
                ret.append(symb)
                return ret

        self.skipSpaces()
        symb = self.labeled_statement()
        if symb!=None:
            ret.append(symb)
            return ret
        
        symb = self.compound_statement()
        if symb!=None:
            ret.append(symb)
            return ret

        symb = self.expression_statement()
        if symb!=None:
            ret.append(symb)
            return ret
        
        symb = self.selection_statement()
        if symb!=None:
            ret.append(symb)
            return ret

        symb = self.iteration_statement()
        if symb!=None:
            ret.append(symb)
            return ret

        symb = self.jump_statement()
        if symb!=None:
            ret.append(symb)
            return ret
        
        self.currentPos = revert
        return None

    def labeled_statement(self):
        revert = self.currentPos
        ret=[self.currentPos,'labeled_statement']#??
        
        self.skipSpaces()
        symb = self.checkSymbol('case')
        if symb!=None:
            ret.append(symb)
            
            self.skipSpaces()
            symb = self.constant_expression()
            if symb==None:
                self.reportError('case needes a constant expression') 
                return None
            ret.append(symb)
            
            self.skipSpaces()
            symb = self.checkSymbol(':')
            if symb==None:
                self.reportError('expected : in case statement') 
                return None

            self.skipSpaces()
            symb = self.statement()
            if symb==None:
                self.reportError('a statement expected in case statement') 
                return None
            ret.append(symb)

            return ret

        symb = self.checkSymbol('default')
        if symb!=None:
            ret.append(symb)
            
            self.skipSpaces()
            symb = self.checkSymbol(':')
            if symb==None:
                self.reportError('expected : in case statement') 
                return None

            self.skipSpaces()
            symb = self.statement()
            if symb==None:
                self.reportError('a statement expected in case statement') 
                return None
            ret.append(symb)

            return ret

        symb = self.checkID()
        if symb!=None:
            ret.append(symb)
            
            self.skipSpaces()
            symb = self.checkSymbol(':')
            if symb==None:
                self.currentPos= revert#revert as statement may be not a labeled, in case and default no need for this
                return None

            self.skipSpaces()
            symb = self.statement()
            if symb==None:
                self.reportError('a statement expected in after label') 
                return None
            ret.append(symb)

            return ret
        
        return None

    def compound_statement(self):
        revert = self.currentPos
        ret=[self.currentPos,'compound_statement']
        
        self.skipSpaces()
        symb = self.checkSymbol('\{')
        if symb==None:
            return None        
        
        while True:
            self.skipSpaces()
            symb = self.declaration()
            if symb!=None:
                ret.append(symb)
                continue

            self.skipSpaces()
            symb = self.statement()
            if symb!=None:
                ret.append(symb)
                continue
            break
            
        self.skipSpaces()
        symb = self.checkSymbol('\}')
        if symb==None:
            self.reportError('expected }') 
            self.currentPos= revert
            return None
        
        return ret

    def declaration_list(self):
        ret=[self.currentPos,'declaration_list'] # TODO: remove later
        
        while True:
            self.skipSpaces()
            symb = self.declaration()
            if symb==None:
                break
            ret.append(symb)
        if len(ret)==2: # TODO:take care if the node name taken away
            return None
        return ret

    def statement_list(self):
        ret=[self.currentPos,'statement_list'] # TODO: remove later
        
        while True:
            self.skipSpaces()
            symb = self.statement()
            if symb==None:
                break
            ret.append(symb)
        if len(ret)==2: # TODO:take care if the node name taken away
            return None
        return ret

    def expression_statement(self):
        revert = self.currentPos
        ret=[self.currentPos,'expression_statement'] # TODO: remove later
        
        self.skipSpaces()
        symb = self.expression()
        if symb!=None:
            ret.append(symb)

        symb = self.checkSymbol(';')
        if symb==None:
            self.currentPos= revert
            return None
        
        return ret

    def selection_statement(self):
        revert = self.currentPos
        ret=[self.currentPos,'selection_statement']#??
        
        self.skipSpaces()
        symb = self.checkSymbol('if')
        if symb!=None:
            ret.append(symb)
            
            self.skipSpaces()
            symb = self.checkSymbol('\(')
            if symb==None:
                self.reportError('expected ( after if') 
                self.currentPos= revert
                return None

            self.skipSpaces()
            symb = self.expression()
            if symb==None:
                self.reportError('expression needed in if() statement') 
                self.currentPos= revert
                return None
            ret.append(symb)
            
            self.skipSpaces()
            symb = self.checkSymbol('\)')
            if symb==None:
                self.reportError('expected ) after expression in if statement') 
                self.currentPos= revert
                return None

            self.skipSpaces()
            symb = self.statement()
            if symb==None:
                self.reportError('a statement expected in if().. statement') 
                return None
            ret.append(symb)

            self.skipSpaces()
            symb = self.checkSymbol('else')
            if symb==None:
                return ret

            self.skipSpaces()
            symb = self.statement()
            if symb==None:
                self.reportError('a statement expected after else in if statement') 
                return None
            ret.append(symb)
            return ret

        symb = self.checkSymbol('switch')
        if symb!=None:
            ret.append(symb)
            
            self.skipSpaces()
            symb = self.checkSymbol('\(')
            if symb==None:
                self.reportError('expected ( after switch') 
                self.currentPos= revert
                return None

            self.skipSpaces()
            symb = self.expression()
            if symb==None:
                self.reportError('expression needed in switch() statement')
                self.currentPos= revert
                return None
            ret.append(symb)
            
            self.skipSpaces()
            symb = self.checkSymbol('\)')
            if symb==None:
                self.reportError('expected ) after expression in switch statement') 
                self.currentPos= revert
                return None

            self.skipSpaces()
            symb = self.statement()
            if symb==None:
                self.reportError('a statement expected in switch().. statement') 
                return None
            ret.append(symb)
            return ret

    def iteration_statement(self):
        revert = self.currentPos
        ret=[self.currentPos,'iteration_statement']#??
        
        self.skipSpaces()
        symb = self.checkSymbol('while')
        if symb!=None:
            ret.append(symb)
            
            self.skipSpaces()
            symb = self.checkSymbol('\(')
            if symb==None:
                self.reportError('expected ( after while') 
                self.currentPos= revert
                return None

            self.skipSpaces()
            symb = self.expression()
            if symb==None:
                self.reportError('expression needed in while() statement') 
                self.currentPos= revert
                return None
            ret.append(symb)
            
            self.skipSpaces()
            symb = self.checkSymbol('\)')
            if symb==None:
                self.reportError('expected ) after expression in while statement') 
                self.currentPos= revert
                return None

            self.skipSpaces()
            symb = self.statement()
            if symb==None:
                self.reportError('a statement expected in while().. statement') 
                self.currentPos= revert
                return None
            ret.append(symb)
            return ret

        symb = self.checkSymbol('do')
        if symb!=None:
            ret.append(symb)
            
            self.skipSpaces()
            symb = self.statement()
            if symb==None:
                self.reportError('a statement expected in do statement') 
                self.currentPos= revert
                return None
            ret.append(symb)

            self.skipSpaces()
            symb = self.checkSymbol('while')
            if symb==None:
                self.reportError('expected while in do statement') 
                self.currentPos= revert
                return None

            self.skipSpaces()
            symb = self.checkSymbol('\(')
            if symb==None:
                self.reportError('expected ( after while in do statement') 
                self.currentPos= revert
                return None

            self.skipSpaces()
            symb = self.expression()
            if symb==None:
                self.reportError('expression needed in do .. while() statement') 
                self.currentPos= revert
                return None
            ret.append(symb)
            
            self.skipSpaces()
            symb = self.checkSymbol('\)')
            if symb==None:
                self.reportError('expected ) after expression in switch statement') 
                self.currentPos= revert
                return None

            self.skipSpaces()
            symb = self.checkSymbol(';')
            if symb==None:
                self.reportError('expected ; at the end of do .. while statement') 
                self.currentPos= revert
                return None

            return ret

        symb = self.checkSymbol('for')
        if symb!=None:
            ret.append(symb)
            
            self.skipSpaces()
            symb = self.checkSymbol('\(')
            if symb==None:
                self.reportError('expected ( after for') 
                self.currentPos= revert
                return None

            self.skipSpaces()
            symb = self.expression_statement()
            if symb==None:
                symb = self.declaration()#added later as part one of 'for' could be an expression and if not then a declaration stmt
                if symb==None:
                    self.reportError('expression or declaration statement needed in for statement') 
                    self.currentPos= revert
                    return None
            ret.append(symb)
            
            self.skipSpaces()
            symb = self.expression_statement()
            if symb==None:
                self.reportError('expression statement needed in for statement') 
                self.currentPos= revert
                return None
            ret.append(symb)

            self.skipSpaces()
            symb = self.expression()
            if symb!=None:
                ret.append(symb)

            self.skipSpaces()
            symb = self.checkSymbol('\)')
            if symb==None:
                self.reportError('expected ) in for statement') 
                self.currentPos= revert
                return None

            self.skipSpaces()
            symb = self.statement()
            if symb==None:
                self.reportError('a statement expected in for statement') 
                self.currentPos= revert
                return None
            ret.append(symb)
            return ret
        return None

    def jump_statement(self):
        revert = self.currentPos
        ret=[self.currentPos,'jump_statement']#??
        
        self.skipSpaces()
        symb = self.checkSymbol('goto')
        if symb!=None:
            ret.append(symb)
            
            self.skipSpaces()
            symb = self.checkID()
            if symb==None:
                self.reportError('expected identifier after goto') 
                self.currentPos= revert
                return None
            ret.append(symb)

            self.skipSpaces()
            symb = self.checkSymbol(';')
            if symb==None:
                self.reportError('expected ; after goto statement') 
                self.currentPos= revert
                return None
            return ret

        self.skipSpaces()
        symb = self.checkSymbol('continue')
        if symb!=None:
            ret.append(symb)
            
            self.skipSpaces()
            symb = self.checkSymbol(';')
            if symb==None:
                self.reportError('expected ; after continue statement') 
                self.currentPos= revert
                return None
            return ret

        self.skipSpaces()
        symb = self.checkSymbol('break')
        if symb!=None:
            ret.append(symb)
            
            self.skipSpaces()
            symb = self.checkSymbol(';')
            if symb==None:
                self.reportError('expected ; after break statement') 
                self.currentPos= revert
                return None
            return ret

        self.skipSpaces()
        symb = self.checkSymbol('return')
        if symb!=None:
            ret.append(symb)
            
            self.skipSpaces()
            symb = self.expression()
            if symb!=None:
                ret.append(symb)

            self.skipSpaces()
            symb = self.checkSymbol(';')
            if symb==None:
                self.reportError('expected ; after return statement') 
                self.currentPos= revert
                return None
            return ret
        return None

    def translation_unit(self):
        ret=[self.currentPos,'translation_unit']
        
        while True:
            self.skipSpaces()
            symb = self.external_declaration()
            if symb==None:
                break
            for i in self.DSL.TUs[0]:
                for j in i[2:]:
                    j[0]=symb[0]
                    ret.append(j)
            ret.append(symb)
            for i in self.DSL.TUs[1]:
                for j in i[2:]:
                    ret.append(j)
            #self.DSL.TUs=[[],[],[]]

        gl = []
        for i in self.DSL.TUs[2]+self.DSL.TUs[3]:
            for j in i[2:]:
                gl.append(j)

        ret = ret[0:2] + gl + ret[2:]
        if len(ret)==2:
            return None
        return ret

    def external_declaration(self):
        revert = self.currentPos
        ret=[self.currentPos,'external_declaration']
        
        self.skipSpaces()
        symb = self.function_definition()
        if symb!=None:
            ret.append(symb)
            return ret

        self.skipSpaces()
        symb = self.declaration()
        if symb!=None:
            ret.append(symb)
            return ret
        if len(self.srcCode)> self.currentPos:
            self.reportError('Unparsed code') 
        return None

    def function_definition(self):
        revert = self.currentPos
        ret=[self.currentPos,'function_definition']
        
        self.skipSpaces()
        symb = self.declaration_specifiers()
        if symb!=None:
            ret.append(symb)

        self.skipSpaces()
        symb = self.declarator()
        if symb==None:
            self.currentPos= revert
            return None
        ret.append(symb)

        self.skipSpaces()
        symb = self.declaration_list()
        if symb!=None:
            ret.append(symb)

        self.skipSpaces()
        symb = self.compound_statement()
        if symb==None:
            self.currentPos= revert
            return None
        ret.append(symb)
        return ret

    def constant_expression(self):
        revert = self.currentPos
        ret=[self.currentPos,'constant_expression']
        
        self.skipSpaces()
        symb = self.conditional_expression()
        if symb!=None:
            ret.append(symb)
            return ret
        
        self.currentPos = revert
        return None

    def expression(self):
        revert = self.currentPos
        ret=[self.currentPos,'expression']
        
        self.skipSpaces()
        symb = self.assignment_expression()
        if symb!=None:
            ret.append(symb)
            while True:
                self.skipSpaces()
                symb = self.checkSymbol(',')
                if symb==None:
                    return ret
                self.skipSpaces()
                symb = self.assignment_expression()
                if symb==None:
                    self.reportError('expected expression after ,') 
                    self.currentPos = revert
                    return None
                ret.append(symb)
        self.currentPos = revert
        return None

    def assignment_expression(self):
        revert = self.currentPos
        ret=[] ##
        
        self.skipSpaces()
        symb = self.conditional_expression()
        if symb==None:
            self.currentPos = revert
            return None            
        ret=symb

        self.skipSpaces()
        symb = self.checkSymbol('=|\*=|/=|%=|\+=|-=|<<=|>>=|&=|\^=|\|=')
        if symb==None:
            return ret
        
        self.currentPos = revert
        self.skipSpaces()
        symb = self.unary_expression()
        if symb==None:
            self.currentPos = revert#prevert
            return None
        ret = symb

        self.skipSpaces()
        symb = self.checkSymbol('=|\*=|/=|%=|\+=|-=|<<=|>>=|&=|\^=|\|=')
        if symb==None:
            self.currentPos = revert
            return ret
        ret = [symb,ret]
        
        self.skipSpaces()
        symb = self.assignment_expression()
        if symb==None:
            self.currentPos = revert
            return None            
        ret.append(symb)

        return ret

    def conditional_expression(self):
        revert = self.currentPos
        ret=['conditional_expression .?.:.'] ##
        
        self.skipSpaces()
        symb = self.logical_or_expression()
        if symb==None:
            self.currentPos = revert
            return None            
        ret = symb

        self.skipSpaces()
        symb = self.checkSymbol('\?')
        if symb==None:
            return ret
        ret = [symb,ret]

        self.skipSpaces()
        symb = self.expression()
        if symb==None:
            self.reportError('expression needed for ?: operator') 
            self.currentPos = revert
            return None            
        ret.append(symb)

        self.skipSpaces()
        symb = self.checkSymbol(':')
        if symb==None:
            self.reportError('(:) needed for ?: operator') 
            self.currentPos = revert
            return None

        self.skipSpaces()
        symb = self.conditional_expression()
        if symb==None:
            self.reportError('expression needed after colon in ?: operator') 
            self.currentPos = revert
            return None            
        ret.append(symb)            
        return ret

    def logical_or_expression(self):
        revert = self.currentPos
        ret=['logical_or_expression'] ##
        
        self.skipSpaces()
        symb = self.logical_and_expression()
        if symb==None:
            self.currentPos = revert
            return None            
        ret = symb

        while True:
            self.skipSpaces()
            symb = self.checkSymbol('\|\|')
            if symb==None:
                return ret
            ret = [symb,ret]#ret.append(symb)
            
            self.skipSpaces()
            symb = self.logical_and_expression()
            if symb==None:
                self.reportError('an expression expected after ||') 
                self.currentPos = revert
                return None
            ret.append(symb)
            
    def logical_and_expression(self):
        revert = self.currentPos
        ret=['logical_and_expression'] ##
        
        self.skipSpaces()
        symb = self.inclusive_or_expression()
        if symb==None:
            self.currentPos = revert
            return None            
        ret = symb

        while True:
            self.skipSpaces()
            symb = self.checkSymbol('&&')
            if symb==None:
                return ret
            ret = [symb,ret]#ret.append(symb)
            
            self.skipSpaces()
            symb = self.inclusive_or_expression()
            if symb==None:
                self.reportError('an expression expected after &&') 
                self.currentPos = revert
                return None
            ret.append(symb)

    def inclusive_or_expression(self):
        revert = self.currentPos
        ret=['inclusive_or_expression'] ##
        
        self.skipSpaces()
        symb = self.exclusive_or_expression()
        if symb==None:
            self.currentPos = revert
            return None            
        ret = symb

        while True:
            self.skipSpaces()
            symb=None
            if len(self.srcCode)>self.currentPos+1:
                if(self.srcCode[self.currentPos]=='|' and self.srcCode[self.currentPos+1]!='|' and self.srcCode[self.currentPos+1]!='='):
                    symb = '|'
                    self.currentPos = self.currentPos+1
            if symb==None:
                return ret
            ret = [symb,ret]#
            
            self.skipSpaces()
            symb = self.exclusive_or_expression()
            if symb==None:
                self.reportError('an expression expected after |') 
                self.currentPos = revert
                return None
            ret.append(symb)

    def exclusive_or_expression(self):
        revert = self.currentPos
        ret=['exclusive_or_expression'] ##
        
        self.skipSpaces()
        symb = self.and_expression()
        if symb==None:
            self.currentPos = revert
            return None            
        ret = symb

        while True:
            self.skipSpaces()
            symb = self.checkSymbol('\^')
            if symb==None:
                return ret
            if self.srcCode[self.currentPos]=='=':
                self.currentPos=self.currentPos-1
                return ret
            ret = [symb,ret]#ret.append(symb)
            
            self.skipSpaces()
            symb = self.and_expression()
            if symb==None:
                self.reportError('an expression expected after ^') 
                self.currentPos = revert
                return None
            ret.append(symb)

    def and_expression(self):
        revert = self.currentPos
        ret=['and_expression'] ##
        
        self.skipSpaces()
        symb = self.equality_expression()
        if symb==None:
            self.currentPos = revert
            return None            
        ret = symb

        while True:
            self.skipSpaces()
            symb=None
            if len(self.srcCode)>self.currentPos+1:
                if(self.srcCode[self.currentPos]=='&' and self.srcCode[self.currentPos+1]!='&' and self.srcCode[self.currentPos+1]!='='):
                    symb = '&'
                    self.currentPos = self.currentPos+1
            if symb==None:
                return ret
            ret = [symb,ret]##ret.append(symb)
            
            self.skipSpaces()
            symb = self.equality_expression()
            if symb==None:
                self.reportError('an expression expected after &') 
                self.currentPos = revert
                return None
            ret.append(symb)

    def equality_expression(self):
        revert = self.currentPos
        ret=['equality_expression'] ##
        
        self.skipSpaces()
        symb = self.relational_expression()
        if symb==None:
            self.currentPos = revert
            return None            
        ret = symb

        while True:
            self.skipSpaces()
            symb = self.checkSymbol('==|!=')#needed
            if symb==None:
                return ret
            ret = [symb,ret]#ret.append(symb)
            
            self.skipSpaces()
            symb = self.relational_expression()
            if symb==None:
                self.reportError('an expression expected after equaliy check operator') 
                self.currentPos = revert
                return None
            ret.append(symb)

    def relational_expression(self):
        revert = self.currentPos
        ret=['relational_expression'] ##
        
        self.skipSpaces()
        symb = self.shift_expression()
        if symb==None:
            self.currentPos = revert
            return None            
        ret = symb

        while True:
            self.skipSpaces()
            symb = self.checkSymbol('<=|>=')#needed
            if symb==None:
                symb = self.checkSymbol('<|>')#needed
                if symb==None:
                    return ret
            ret = [symb,ret]#ret.append(symb)
            
            self.skipSpaces()
            symb = self.shift_expression()
            if symb==None:
                self.reportError('an expression expected after relational operator') 
                self.currentPos = revert
                return None
            ret.append(symb)

    def shift_expression(self):
        revert = self.currentPos
        ret=['shift_expression'] ##
        
        self.skipSpaces()
        symb = self.additive_expression()
        if symb==None:
            self.currentPos = revert
            return None            
        ret = symb

        while True:
            self.skipSpaces()
            symb = self.checkSymbol('<<|>>')#needed
            if symb==None:
                return ret
            if self.srcCode[self.currentPos]=='=':
                self.currentPos=self.currentPos-2
                return ret
            ret = [symb,ret]#ret.append(symb)
            
            self.skipSpaces()
            symb = self.additive_expression()
            if symb==None:
                self.reportError('an expression expected after shift operator') 
                self.currentPos = revert
                return None
            ret.append(symb)

    def additive_expression(self):
        revert = self.currentPos
        ret=['additive_expression'] ##
        
        self.skipSpaces()
        symb = self.multiplicative_expression()
        if symb==None:
            self.currentPos = revert
            return None            
        ret = symb

        while True:
            self.skipSpaces()
            symb = self.checkSymbol('\+|-')#needed
            if symb==None:
                return ret
            if self.srcCode[self.currentPos]=='=':
                self.currentPos=self.currentPos-1
                return ret
            ret = [symb,ret]#ret.append(symb)
            
            self.skipSpaces()
            symb = self.multiplicative_expression()
            if symb==None:
                self.reportError('an expression expected after +/- operator') 
                self.currentPos = revert
                return None
            ret.append(symb)

    def multiplicative_expression(self):
        revert = self.currentPos
        ret=['multiplicative_expression'] ##
        
        self.skipSpaces()
        symb = self.cast_expression()
        if symb==None:
            self.currentPos = revert
            return None            
        ret = symb

        while True:
            self.skipSpaces()
            symb = self.checkSymbol('\*|/|%')#needed
            if symb==None:
                return ret
            if self.srcCode[self.currentPos]=='=':
                self.currentPos=self.currentPos-1
                return ret
            ret = [symb,ret]#ret.append(symb)
            
            self.skipSpaces()
            symb = self.cast_expression()
            if symb==None:
                self.reportError('an expression expected after *,/,% operator')
                self.currentPos = revert
                return None
            ret.append(symb)

    def cast_expression(self):
        revert = self.currentPos
        ret=['cast'] 
    
        if self.DSL!=None:
            symb = self.DSL.expression()
            if symb!=None:
                return symb
        self.currentPos = revert

        self.skipSpaces()
        symb = self.checkSymbol('\(')
        if symb==None:
            self.currentPos = revert
            self.skipSpaces()
            symb = self.unary_expression()
            if symb!=None:
                ret = symb
                return ret
            return None

        self.skipSpaces()
        symb = self.type_name()
        if symb==None:
            self.currentPos = revert
            self.skipSpaces()
            symb = self.unary_expression()
            if symb!=None:
                ret = symb
                return ret
            return None
        ret = [symb]

        self.skipSpaces()
        symb = self.checkSymbol('\)')
        if symb==None:
            self.currentPos = revert
            return None

        self.skipSpaces()
        symb = self.cast_expression()
        if symb==None:
            self.currentPos = revert
            return None
        ret.append(symb)
        return ret

    def unary_operator(self):
        self.skipSpaces()
        symb = self.checkSymbol('&|\*|\+|-|~|!')
        if symb==None:
            return None
        ret = symb
        return ret
        
    def unary_expression(self):
        revert = self.currentPos
        ret=['unary_expression'] 
        
        self.skipSpaces()
        symb = self.postfix_expression()
        if symb!=None:
            ret = symb
            return ret

        self.skipSpaces()
        symb = self.checkSymbol('\+\+|--')
        if symb!=None:
            ret.append(symb)
            self.skipSpaces()
            symb = self.unary_expression()
            if symb!=None:
                ret.append(symb)
                return ret
            self.currentPos = revert
            return None

        self.skipSpaces()
        symb = self.unary_operator()
        if symb!=None:
            ret.append(symb)
            self.skipSpaces()
            symb = self.cast_expression()
            if symb!=None:
                ret.append(symb)
                return ret
            self.currentPos = revert
            return None

        self.skipSpaces()
        symb = self.checkSymbol('sizeof')
        if symb!=None:
            ret.append(symb)
            self.skipSpaces()
            symb = self.checkSymbol('\(')
            if symb==None:
                self.currentPos = revert
                return None

            self.skipSpaces()
            symb = self.type_name()
            if symb==None:
                self.currentPos = revert
                return None
            ret.append(symb)

            self.skipSpaces()
            symb = self.checkSymbol('\)')
            if symb==None:
                self.currentPos = revert
                return None
            return ret

            self.skipSpaces()
            symb = self.unary_expression()
            if symb!=None:
                ret.append(symb)
                return ret
        
        self.currentPos = revert
        return None
    
    def argument_expression_list(self):
        revert = self.currentPos
        ret=[self.currentPos,'argument_expression_list']
        
        self.skipSpaces()
        symb = self.assignment_expression()
        if symb!=None:
            ret.append(symb)
            while True:
                self.skipSpaces()
                symb = self.checkSymbol(',')
                if symb==None:
                    return ret
                self.skipSpaces()
                symb = self.assignment_expression()
                if symb==None:
                    self.reportError('expected expression after ,') 
                    self.currentPos = revert
                    return None
                ret.append(symb)
        self.currentPos = revert
        return None
    
    def postfix_expression(self):
        revert = self.currentPos
        ret=[]
        
        self.skipSpaces()
        symb = self.primary_expression()
        if symb==None:
            self.currentPos = revert
            return None
        ret.append(symb)
                  
        while True:
            self.skipSpaces()
            symb = self.checkSymbol('\[')
            if symb!=None:
                self.skipSpaces()
                symb = self.expression()
                if symb==None:
                    self.reportError('expression expected after [') 
                    self.currentPos = revert
                    return None
                ret.append('[expression]')
                ret.append(symb)
                self.skipSpaces()
                symb = self.checkSymbol('\]')
                if symb!=None:
                    continue
                self.reportError('expected ]') 
                self.currentPos = revert
                return None

            symb = self.checkSymbol('\(')
            if symb!=None:
                self.skipSpaces()
                symb = self.argument_expression_list()
                if symb!=None:
                    ret.append('(argument_expression_list)')
                    ret.append(symb)
                else:
                    ret.append('()')
                self.skipSpaces()
                symb = self.checkSymbol('\)')
                if symb!=None:
                    continue
                #self.reportError('expected )') 
                self.currentPos = revert
                return None

            symb = self.checkSymbol('\.|->')
            if symb!=None:
                ret.append(symb)
                self.skipSpaces()
                symb = self.checkID()
                if symb!=None:
                    ret.append(symb)
                    continue
                self.reportError('expected member name') 
                self.currentPos = revert
                return None

            symb = self.checkSymbol('\+\+|--')
            if symb!=None:
                ret.append(symb)
                continue

            break
        return ret
    
    def primary_expression(self):
        revert = self.currentPos
        ret=['primary_expression']##
        
        self.skipSpaces()
        symb = self.checkID()
        if symb!=None:
            ret = symb
            return ret
            
        symb = self.checkSymbol('''([0-9]+[Ee][+-]?[0-9]+(f|F|l|L)?)|([0-9]*\.[0-9]+([Ee][+-]?[0-9]+)?(f|F|l|L)?)|([0-9]+\.[0-9]*([Ee][+-]?[0-9]+)?(f|F|l|L)?)''')
        if symb!=None:
            ret = symb
            return ret
            
        symb = self.checkSymbol('''(0[xX][a-fA-F0-9]+(u|U|l|L)*)|(0[0-9]+(u|U|l|L)*)|([0-9]+(u|U|l|L)*)|(L?'(\\.|[^\\'])+')''')
        if symb!=None:
            ret = symb
            return ret

        symb = self.checkSymbol('L?\"(\\.|[^\\"])*\"')
        if symb!=None:
            ret = symb
            return ret
        
        symb = self.checkSymbol('\(')
        if symb!=None:
            self.skipSpaces()
            symb = self.expression()
            if symb==None:
                self.currentPos = revert
                return None
            ret = symb
            self.skipSpaces()
            symb = self.checkSymbol('\)')
            if symb==None:
                self.reportError('expression started with paranthesis( should end with paranthesis)') 
            return ret
        self.currentPos = revert
        
        return None

class generator:
    
    def __init__(self):
        pass
    def declaration(self,node):
        if node[1]!='declaration':
            return None
        i = 2
        ret = ''
        
        symb = self.declaration_specifiers(node[i])
        if symb==None:
            print 'generator error: declaration with no declaration_specifiers'
            return None
        i = i + 1
        ret = ret + symb
        
        if len(node)>i:
            symb = self.init_declarator_list(node[i])
            if symb!=None:
                ret = ret + ' ' + symb

        ret = ret + ';'
        return ret

    def declaration_specifiers(self,node):
        if node[1]!='declaration_specifiers':
            return None
        ret = ''

        for i in node[2:]:
            if isinstance(i,list)==False:
                ret = ret + ' ' + i
            else:
                symb = self.struct_or_union_specifier(i)
                if symb!=None:
                    ret = ret + ' ' + symb
                    continue

                symb = self.enum_specifier(i)
                if symb!=None:
                    ret = ret  + ' ' + symb
                    continue
                print 'generator error: declaration_specifiers with unknown specifier'
                return None

        return ret[1:]

    def init_declarator_list(self,node):
        if node[1]!='init_declarator_list':
            return None
        ret = ''

        for i in node[2:]:
            symb = self.init_declarator(i)
            if symb!=None:
                ret = ret + ', ' + symb

        return ret[2:]

    def init_declarator(self,node):
        if node[1]!='init_declarator':
            return None
        i = 2
        
        symb = self.declarator(node[i])
        if symb==None:#no need
            print 'generator error: init_declarator with no declarator'
            return None
        i = i + 1
        ret = symb
        
        if len(node)>i:
            symb = self.initializer(node[i])
            if symb!=None:
                ret = ret + ' = ' + symb

        return ret
        
    def struct_or_union_specifier(self,node):
        if node[1]!='struct' and node[1]!= 'union':
            return None
        ret = node[1]+' '+node[2]
        
        if len(node)>3:
            symb = self.struct_declaration_list(node[3])
            if symb!=None:
                ret = ret + '{' + symb + '\n}'

        return ret

    def struct_declaration_list(self,node):
        if node[1]!='struct_declaration_list':
            return None
        
        ret = ''
        for i in node[2:]:
            symb = self.struct_declaration(i)
            ret = ret +'\n'+ symb
        return ret

    def struct_declaration(self,node):
        if node[1]!='struct_declaration':
            return None
        
        symb = self.specifier_qualifier_list(node[2])
        if symb==None:
            print 'generator error: struct_declaration without specifier_qualifier_list'
            return None
        ret = symb
        
        symb = self.struct_declarator_list(node[3])
        if symb==None:
            print 'generator error: struct_declaration without struct_declarator_list'
            return None
        ret = ret + ' ' + symb + ';'
        return ret

    def specifier_qualifier_list(self, node):
        if node[1]!='specifier_qualifier_list':
            return None
        ret = ''       
        for i in node[2:]:
            if isinstance(i,list)==False:
                ret = ret + ' ' + i
            else:
                symb = self.struct_or_union_specifier(i)
                if symb!=None:
                    ret = ret + ' ' + symb
                    continue

                symb = self.enum_specifier(i)
                if symb!=None:
                    ret = ret  + ' ' + symb
                    continue
                print 'generator error: declaration_specifiers with unknown specifier'
                return None

        return ret[1:]


    def struct_declarator_list(self,node):
        if node[1]!='struct_declarator_list':
            return None

        ret = ''
        for i in node[2:]:
            symb = self.struct_declarator(i)
            ret = ret + ' , ' + symb
        return ret[3:]

    def struct_declarator(self,node):
        if node[1]!='struct_declarator':
            return None
        
        ret = ''
        i = 2

        symb = self.declarator(node[i])
        if symb!=None:
            ret = ret + symb
            i = i + 1
        
        if len(node)>i:
            symb = self.constant_expression(node[i])
            if symb!=None:
                ret = ret + ':' + symb
        return ret

    def enum_specifier(self, node):
        if node[1]!='enum':
            return None
        
        ret = 'enum ' + node[2]
        
        if len(node)>3:
            symb = self.enumerator_list(node[3])
            ret = ret + '{' + symb + '}'
        
        return ret

    def enumerator_list(self, node):
        if node[1]!='enumerator_list':
            return None

        ret = ''
        for i in node[2:]:
            symb = self.enumerator(i)
            ret = ret + ' , ' + symb
        return ret[3:]
       
    def enumerator(self):
        if node[1]!='enumerator':
            return None
        
        ret = node[2]
        
        if len(node)>3:
            symb = self.constant_expression(node[3])
            ret = ret + ' = ' + symb
        
        return ret

    def declarator(self,node):
        if node[1]!='declarator':
            return None
        
        ret = ''
        i = 2
        if len(node)>3:
            symb = self.pointer(node[i])
            ret = ret + symb
            i = i + 1
        
        symb = self.direct_declarator(node[i])
        ret = ret + symb
        return ret

    def direct_declarator(self,node):
        if node[1]!='direct_declarator':
            return None
        
        ret = ''
        if isinstance(node[2],list)==False:
            ret = ret + node[2]
        else:
            symb = self.declarator()
            if symb==None:
                print 'generator error: direct_declarator with neither an identifer nor a (declarator)'
                return None
            ret = ret +'('+ symb+')'
            
        i = 3
        while True:
            if len(node)<=i:
                break
            if node[i]=='[]':
                ret = ret + '[]'
                i = i + 1
                continue
            elif node[i]=='[constant_expression]':
                symb = self.constant_expression(node[i+1])
                ret = ret + '[' + symb + ']'
                i = i + 2
                continue
            elif node[i]=='()':
                ret = ret + '()'
                i = i + 1
                continue
            elif node[i]=='(parameter_type_list)':
                symb = self.parameter_type_list(node[i+1])
                ret = ret + '(' + symb + ')'
                i = i + 2
                continue
            elif node[i]=='(identifier_list)':
                symb = self.identifier_list(node[i+1])
                ret = ret + '(' + symb + ')'
                i = i + 2
                continue
                
        return ret
    
    def pointer(self, node):
        if node[1]!='pointer':
            return None
        
        ret = ''
        for i in node[2:]:
            if isinstance(i,list):
                for j in i:
                    ret = ret + ' ' + j
            else:
                ret = ret + ' ' + i
        
        ret = ret + ' '
        return ret
        
    def parameter_type_list(self, node):
        if node[1]!='parameter_type_list':
            return None
        
        ret = self.parameter_list(node[2])
        if len(node)>3:
            ret = ret + ' , ...'
        return ret

    def parameter_list(self, node):
        if node[1]!='parameter_list':
            return None
        
        ret = ''
        for i in node[2:]:
            symb = self.parameter_declaration(i)
            if symb==None:
                print 'generator error: parameter list with a non parameter_declaration element'# no need in fact
            ret = ret + ' , ' + symb
        
        return ret[3:]

    def parameter_declaration(self, node):
        if node[1]!='parameter_declaration':
            return None
        
        symb = self.declaration_specifiers(node[2])
        if symb==None:
            print 'generator error: declaration with no declaration_specifiers'
            return None
        ret = symb
        
        if len(node)>3:
            symb = self.declarator(node[3])
            if symb==None:
                symb = self.abstract_declarator(node[3])
            if symb==None:
                print 'generator error: parameter_declaration should have a declarator or an abstract declarator'
            ret = ret + ' ' + symb

        return ret

    def identifier_list(self, node):
        if node[1]!='identifier_list':
            return None

        ret = ''
        for i in node[2:]:
            ret = ret + ' , ' + i
        return ret[3:]

    def type_name(self, node):
        if node[1]!='type_name':
            return None
        
        symb = self.specifier_qualifier_list(node[2])
        if symb==None:
            print 'generator error: type_name without specifier_qualifier_list'
            return None
        ret = symb
        
        if len(node)>3:
            symb = self.abstract_declarator(node[3])
            ret = ret + ' ' + symb
        return ret

    def abstract_declarator(self,node):
        if node[1]!='abstract_declarator':
            return None
        
        ret = ''
        i = 2

        symb = self.pointer(node[i])
        if symb!=None:
            ret = ret + symb
            i = i + 1
        
        if len(node)>i:
            symb = self.direct_abstract_declarator(node[i])
            if symb!=None:
                ret = ret + ' ' + symb
        return ret

    def direct_abstract_declarator(self, node):
        if node[1]!='direct_abstract_declarator':
            return None
        
        ret = ''
        i = 2
        while True:
            if len(node)<=i:
                break
            if node[i]=='[]':
                ret = ret + '[]'
                i = i + 1
                continue
            elif node[i]=='[constant_expression]':
                symb = self.constant_expression(node[i+1])
                ret = ret + '[' + symb + ']'
                i = i + 2
                continue
            elif node[i]=='()':
                ret = ret + '()'
                i = i + 1
                continue
            elif node[i]=='(parameter_type_list)':
                symb = self.parameter_type_list(node[i+1])
                ret = ret + '(' + symb + ')'
                i = i + 2
                continue
            elif node[i]=='(abstract_declarator)':
                symb = self.abstract_declarator(node[i+1])
                ret = ret + '(' + symb + ')'
                i = i + 2
                continue
                
        return ret

    def initializer(self, node):
        if node[1]!='initializer':
            return None
        
        ret = self.assignment_expression(node[2])
        if ret!=None:
            return ret
        
        ret = self.initializer_list(node[2])
        if ret==None:
            print 'generator error: initializer should contain an assignment_expression or an initializer_list'
            return None
        
        if len(node)>2:
            ret = '{' + ret + '}'
        
        return ret

    def initializer_list(self, node):
        if node[1]!='initializer_list':
            return None
        
        ret = ''
        for i in node[2:]:
            symb = self.initializer(i)
            if symb==None:
                print 'generator error: initializer_list with a non initializer element'# no need in fact
            ret = ret + ' , ' + symb
        
        return ret[3:]

    def statement(self, node):
        if node[1]!='statement':
            return None

        symb = self.labeled_statement(node[2])
        if symb!=None:
            return symb
        
        symb = self.compound_statement(node[2])
        if symb!=None:
            return symb

        symb = self.expression_statement(node[2])
        if symb!=None:
            return symb
        
        symb = self.selection_statement(node[2])
        if symb!=None:
            return symb

        symb = self.iteration_statement(node[2])
        if symb!=None:
            return symb

        symb = self.jump_statement(node[2])
        if symb!=None:
            return symb
        
        return 'None C statement'

    def labeled_statement(self, node):
        if node[1]!='labeled_statement':
            return None
        
        if node[2]=='case':
            symb = self.constant_expression(node[3])
            ret = 'case ' + symb + ' : '
            symb = self.statement(node[4])
            ret = ret + symb
            return ret

        if node[2]=='default': # not needed
            symb = self.statement(node[3])
            ret = 'default : ' + symb
            return ret

        symb = self.statement(node[3])
        ret = node[2] + ' : ' + symb
        return ret


    def compound_statement(self,node):
        if node[1]!='compound_statement':
            return None
        
        ret = '{'
        for i in node[2:]:
            symb = self.declaration(i)
            if symb!=None:
                ret = ret + '\n' + symb
                continue

            symb = self.statement(i)
            if symb!=None:
                ret = ret + '\n' + symb
                continue
            break
            
        ret = ret + '\n}'
        return ret

    def declaration_list(self,node):
        if node[1]!='declaration_list':
            return None
        
        ret = ''
        for i in node[2:]:
            symb = self.declaration(i)
            if symb==None:
                print 'generator error: declaration_list with a non declaration element'# no need in fact
            ret = ret + symb
        
        return ret

    def statement_list(self, node):
        if node[1]!='statement_list':
            return None
        
        ret = ''
        for i in node[2:]:
            symb = self.statement(i)
            if symb==None:
                print 'generator error: declaration_list with a non declaration element'# no need in fact
            ret = ret + symb
        
        return ret

    def expression_statement(self, node):
        if node[1]!='expression_statement':
            return None
        
        ret = ''
        if len(node)>2:
            symb = self.expression(node[2])
            if symb!=None:
                ret = symb
                
        ret = ret + ' ;'       
        return ret

    def selection_statement(self, node):
        if node[1]!='selection_statement':
            return None
        
        ret = ''
        if node[2]=='if': 
            symb = self.expression(node[3])
            ret = 'if ( ' + symb + ' ) '
            
            symb = self.statement(node[4])
            ret = ret + symb
            
            if len(node)<6:
                return ret
            
            symb = self.statement(node[5])
            ret = ret + ' else ' + symb
            return ret

        elif node[2]=='switch': 
            symb = self.expression(node[3])
            ret = 'switch ( ' + symb + ' ) '
            
            symb = self.statement(node[4])
            ret = ret + symb
            return ret

    def iteration_statement(self, node):
        if node[1]!='iteration_statement':
            return None
        
        ret = ''
        if node[2]=='while': 
            symb = self.expression(node[3])
            ret = 'while ( ' + symb + ' ) '
            
            symb = self.statement(node[4])
            ret = ret + symb            
            return ret

        elif node[2]=='do': 
            symb = self.statement(node[3])
            ret = 'do ' + symb + ' while ( '
            
            symb = self.expression(node[4])
            ret = ret + symb + ' );'
            return ret

        elif node[2]=='for': 
            symb = self.expression_statement(node[3])
            if symb==None:
                symb = self.declaration(node[3])
            ret = 'for(' + symb
            symb = self.expression_statement(node[4])
            ret = ret + symb
            i = 5
            if len(node)>6:
                symb = self.expression(node[i])
                ret = ret + symb
                i = i + 1
            symb = self.statement(node[i])
            ret = ret + ') ' + symb
            return ret

    def jump_statement(self, node):
        if node[1]!='jump_statement':
            return None
        
        ret = ''
        if node[2]=='goto': 
            return 'goto ' + node[3] + ';'

        elif node[2]=='continue': 
            return 'continue;'

        elif node[2]=='break': 
            return 'break;'

        elif node[2]=='return': 
            ret = 'return '
            if len(node)>3:
                symb = self.expression(node[3])
                ret = ret + symb
            ret = ret + ';'
            return ret

    def translation_unit(self,node):
        if node[1]!='translation_unit':
            return None
        ret=''
        for i in node[2:]:
            symb = self.external_declaration(i)
            if symb==None:
                return None
            ret = ret + '\n' + symb
        return ret

    def external_declaration(self,node):
        if node[1]!='external_declaration':
            return None

        ret=''
        
        symb = self.function_definition(node[2])
        if symb!=None:
            ret = symb
            return ret

        symb = self.declaration(node[2])
        if symb!=None:
            ret = symb
            return ret

        return None

    def function_definition(self,node):
        if node[1]!='function_definition':
            return None
        
        i = 2
        ret = ''
        
        symb = self.declaration_specifiers(node[i])
        if symb!=None:
            i = i + 1
            ret = ret + symb

        symb = self.declarator(node[i])
        if symb==None:
            print 'generator error: function definition with no declarator'
            return None
        i = i + 1
        ret = ret + ' ' + symb

        symb = self.declaration_list(node[i])
        if symb!=None:
            i = i + 1
            ret = ret + symb

        symb = self.compound_statement(node[i])
        if symb==None:
            print 'generator error: function definition with no body'
            return None
        ret = ret + '\n' + symb

        return ret

    def constant_expression(self,node):
        if node[1]!='constant_expression':
            return None

        return self.conditional_expression(node[2])

    def expression(self,node):
        if node[1]!='expression':
            return None
        ret = ''

        for i in node[2:]:
            symb = self.assignment_expression(i)
            ret = ret + ' , ' + symb

        return ret[2:]

    def assignment_expression(self,node):
        if isinstance(node[0],list)!=True:
            asgOps=['=','*=','/=','%=','+=','-=','<<=','>>=','&=','^=','|=']
            for i in asgOps:
                if i==node[0]:
                    symb = self.unary_expression(node[1])
                    ret = symb + ' ' + node[0]
                    symb = self.assignment_expression(node[2])
                    ret = ret + ' ' + symb
                    return ret
        return self.conditional_expression(node)

    def conditional_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='?':        
                symb = self.logical_or_expression(node[1])
                ret = symb + ' ? '
                symb = self.expression(node[2])
                ret = ret + symb + ' : '
                symb = self.conditional_expression(node[3])
                ret = ret + symb
                return ret
        return self.logical_or_expression(node)

    def logical_or_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='||':        
                symb = self.logical_or_expression(node[1])
                ret = symb + ' || '
                symb = self.logical_and_expression(node[2])
                ret = ret + symb
                return ret
        return self.logical_and_expression(node)
    
    def logical_and_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='&&':        
                symb = self.logical_and_expression(node[1])
                ret = symb + ' && '
                symb = self.inclusive_or_expression(node[2])
                ret = ret + symb
                return ret
        return self.inclusive_or_expression(node)
    
    def inclusive_or_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='|':
                symb = self.inclusive_or_expression(node[1])
                ret = symb + ' | '
                symb = self.exclusive_or_expression(node[2])
                ret = ret + symb
                return ret
        return self.exclusive_or_expression(node)
    
    def exclusive_or_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='^':
                symb = self.exclusive_or_expression(node[1])
                ret = symb + ' ^ '
                symb = self.and_expression(node[2])
                ret = ret + symb
                return ret
        return self.and_expression(node)

    def and_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='&':
                symb = self.and_expression(node[1])
                ret = symb + ' & '
                symb = self.equality_expression(node[2])
                ret = ret + symb
                return ret
        return self.equality_expression(node)

    def equality_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='==' or node[0]=='!=':
                symb = self.equality_expression(node[1])
                ret = symb + ' ' + node[0] + ' '
                symb = self.relational_expression(node[2])
                ret = ret + symb
                return ret
        return self.relational_expression(node)

    def relational_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='<' or node[0]=='>' or node[0]=='<=' or node[0]=='>=':
                symb = self.relational_expression(node[1])
                ret = symb + ' ' + node[0] + ' '
                symb = self.shift_expression(node[2])
                ret = ret + symb
                return ret
        return self.shift_expression(node)

    def shift_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='<<' or node[0]=='>>':
                symb = self.shift_expression(node[1])
                ret = symb + ' ' + node[0] + ' '
                symb = self.additive_expression(node[2])
                ret = ret + symb
                return ret
        return self.additive_expression(node)

    def additive_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='+' or node[0]=='-':
                symb = self.additive_expression(node[1])
                ret = symb + ' ' + node[0] + ' '
                symb = self.multiplicative_expression(node[2])
                ret = ret + symb
                return ret
        return self.multiplicative_expression(node)

    def multiplicative_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='*' or node[0]=='/' or node[0]=='%':
                symb = self.multiplicative_expression(node[1])
                ret = symb + ' ' + node[0] + ' '
                symb = self.cast_expression(node[2])
                ret = ret + symb
                return ret
        return self.cast_expression(node)

    def cast_expression(self,node):
        if isinstance(node[0],list)==True:
            symb = self.type_name(node[0])
            if symb!=None:
                ret = '(' + symb + ') '

                symb = self.cast_expression(node[1])
                ret = ret + symb
                return ret
        return self.unary_expression(node)

    def unary_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='unary_expression':
                if node[1]=='++' or node[1]=='--':
                    symb = self.unary_expression(node[2])
                    return node[1]+symb
                elif node[1]=='&' or node[1]=='*' or node[1]=='+' or node[1]=='-' or node[1]=='~' or node[1]=='!':
                    symb = self.cast_expression(node[2])
                    return node[1]+symb
                elif node[1]=='sizeof':
                    symb = self.type_name(node[2])
                    if symb == None:
                        symb = self.unary_expression(node[2])
                        return node[1]+symb
                    return node[1]+'('+symb+')'
       
        return self.postfix_expression(node)

    
    def argument_expression_list(self,node):
        if node[1]!='argument_expression_list':
            return None
        ret = ''

        for i in node[2:]:
            symb = self.assignment_expression(i)
            if symb!=None:
                ret = ret + ' , ' + symb

        return ret[2:]
    
    def postfix_expression(self,node):
        ret = self.primary_expression(node[0])
            
        i = 1
        while True:
            if len(node)<=i:
                break
            if node[i]=='++' or node[i]=='--':
                ret = ret + node[i]
                i = i + 1
                continue
            elif node[i]=='.' or node[i]=='->':
                ret = ret + node[i] + node[i+1]
                i = i + 2
                continue
            elif node[i]=='[expression]':
                symb = self.expression(node[i+1])
                ret = ret + '[' + symb + ']'
                i = i + 2
                continue
            elif node[i]=='()':
                ret = ret + '()'
                i = i + 1
                continue
            elif node[i]=='(argument_expression_list)':
                symb = self.argument_expression_list(node[i+1])
                ret = ret + '(' + symb + ')'
                i = i + 2
                continue
            else:#modification
                return None
                
        return ret
    
    def primary_expression(self,node):
        if isinstance(node,list)!=True:
            return node
        return '('+self.expression(node)+')'
        


class finalprocessor:
    
    def __init__(self):
        pass
    def finalOutput(self,dsl):
        code = self.translation_unit(dsl.ast)
        for i in dsl.GPL.pragmas+dsl.GPL.lComments+dsl.GPL.mComments:
            pos = 0
            while True:
                m=re.search(r' \$\#([-]?[0-9]+)\#\$ ',code[pos:],flags=re.M|re.S)
                if m==None:
                    code = code +'\n $#'+str(i[0])+'#$ '+i[2]+'\n'
                    break
                #print 'comment at ' + str(i[0]) +', group at'+ m.group(1)+', pos '+str(pos)
                if int(m.group(1))<i[0]:
                    pos = pos + m.end()
                    continue
                code = code[:pos+m.start()]+' $#'+str(i[0])+'#$ '+i[2]+'\n'+code[pos+m.start():]
                break
        code = re.sub(r' \$\#([-]?[0-9]+)\#\$ ','',code,flags=re.M|re.S)
        while True:
            m = re.search(r'__AddAnnotation\s*\(\s*"(.*?)"\s*\)\s*;',code,flags=re.M|re.S)
            if m==None:
                break
            code = code[:m.start()] +'#'+m.group(1)+ code[m.end():]
        return code

    def declaration(self,node):
        if node[1]!='declaration':
            return None
        i = 2
        ret = ''
        
        symb = self.declaration_specifiers(node[i])
        if symb==None:
            print 'generator error: declaration with no declaration_specifiers'
            return None
        i = i + 1
        ret = ret + symb
        
        if len(node)>i:
            symb = self.init_declarator_list(node[i])
            if symb!=None:
                ret = ret + ' ' + symb

        ret = ret + ';'
        return ' $#'+str(node[0])+'#$ '+ret

    def declaration_specifiers(self,node):
        if node[1]!='declaration_specifiers':
            return None
        ret = ''

        for i in node[2:]:
            if isinstance(i,list)==False:
                ret = ret + ' ' + i
            else:
                symb = self.struct_or_union_specifier(i)
                if symb!=None:
                    ret = ret + ' ' + symb
                    continue

                symb = self.enum_specifier(i)
                if symb!=None:
                    ret = ret  + ' ' + symb
                    continue
                print 'generator error: declaration_specifiers with unknown specifier'
                return None

        return ret[1:]

    def init_declarator_list(self,node):
        if node[1]!='init_declarator_list':
            return None
        ret = ''

        for i in node[2:]:
            symb = self.init_declarator(i)
            if symb!=None:
                ret = ret + ', ' + symb

        return ret[2:]

    def init_declarator(self,node):
        if node[1]!='init_declarator':
            return None
        i = 2
        
        symb = self.declarator(node[i])
        if symb==None:#no need
            print 'generator error: init_declarator with no declarator'
            return None
        i = i + 1
        ret = symb
        
        if len(node)>i:
            symb = self.initializer(node[i])
            if symb!=None:
                ret = ret + ' = ' + symb

        return ret
        
    def struct_or_union_specifier(self,node):
        if node[1]!='struct' and node[1]!= 'union':
            return None
        ret = node[1]+' '+node[2]
        
        if len(node)>3:
            symb = self.struct_declaration_list(node[3])
            if symb!=None:
                ret = ret + '{' + symb + '\n}'

        return ' $#'+str(node[0])+'#$ '+ret

    def struct_declaration_list(self,node):
        if node[1]!='struct_declaration_list':
            return None
        
        ret = ''
        for i in node[2:]:
            symb = self.struct_declaration(i)
            ret = ret +'\n'+ symb
        return ret

    def struct_declaration(self,node):
        if node[1]!='struct_declaration':
            return None
        
        symb = self.specifier_qualifier_list(node[2])
        if symb==None:
            print 'generator error: struct_declaration without specifier_qualifier_list'
            return None
        ret = symb
        
        symb = self.struct_declarator_list(node[3])
        if symb==None:
            print 'generator error: struct_declaration without struct_declarator_list'
            return None
        ret = ret + ' ' + symb + ';'
        return ret

    def specifier_qualifier_list(self, node):
        if node[1]!='specifier_qualifier_list':
            return None
        ret = ''       
        for i in node[2:]:
            if isinstance(i,list)==False:
                ret = ret + ' ' + i
            else:
                symb = self.struct_or_union_specifier(i)
                if symb!=None:
                    ret = ret + ' ' + symb
                    continue

                symb = self.enum_specifier(i)
                if symb!=None:
                    ret = ret  + ' ' + symb
                    continue
                print 'generator error: declaration_specifiers with unknown specifier'
                return None

        return ' $#'+str(node[0])+'#$ '+ret[1:]


    def struct_declarator_list(self,node):
        if node[1]!='struct_declarator_list':
            return None

        ret = ''
        for i in node[2:]:
            symb = self.struct_declarator(i)
            ret = ret + ' , ' + symb
        return ret[3:]

    def struct_declarator(self,node):
        if node[1]!='struct_declarator':
            return None
        
        ret = ''
        i = 2

        symb = self.declarator(node[i])
        if symb!=None:
            ret = ret + symb
            i = i + 1
        
        if len(node)>i:
            symb = self.constant_expression(node[i])
            if symb!=None:
                ret = ret + ':' + symb
        return ' $#'+str(node[0])+'#$ '+ret

    def enum_specifier(self, node):
        if node[1]!='enum':
            return None
        
        ret = 'enum ' + node[2]
        
        if len(node)>3:
            symb = self.enumerator_list(node[3])
            ret = ret + '{' + symb + '}'
            
        return ret

    def enumerator_list(self, node):
        if node[1]!='enumerator_list':
            return None

        ret = ''
        for i in node[2:]:
            symb = self.enumerator(i)
            ret = ret + ' , ' + symb
        return ret[3:]
       
    def enumerator(self, node):
        if node[1]!='enumerator':
            return None
        
        ret = node[2]
        
        if len(node)>3:
            symb = self.constant_expression(node[3])
            ret = ret + ' = ' + symb
        
        return ' $#'+str(node[0])+'#$ '+ret

    def declarator(self,node):
        if node[1]!='declarator':
            return None
        
        ret = ''
        i = 2
        if len(node)>3:
            symb = self.pointer(node[i])
            ret = ret + symb
            i = i + 1
        
        symb = self.direct_declarator(node[i])
        ret = ret + symb
        return ret

    def direct_declarator(self,node):
        if node[1]!='direct_declarator':
            return None
        
        ret = ''
        if isinstance(node[2],list)==False:
            ret = ret + node[2]
        else:
            symb = self.declarator(node[2])
            if symb==None:
                print 'generator error: direct_declarator with neither an identifer nor a (declarator)'
                return None
            ret = ret +'('+ symb+')'
            
        i = 3
        while True:
            if len(node)<=i:
                break
            if node[i]=='[]':
                ret = ret + '[]'
                i = i + 1
                continue
            elif node[i]=='[constant_expression]':
                symb = self.constant_expression(node[i+1])
                ret = ret + '[' + symb + ']'
                i = i + 2
                continue
            elif node[i]=='()':
                ret = ret + '()'
                i = i + 1
                continue
            elif node[i]=='(parameter_type_list)':
                symb = self.parameter_type_list(node[i+1])
                ret = ret + '(' + symb + ')'
                i = i + 2
                continue
            elif node[i]=='(identifier_list)':
                symb = self.identifier_list(node[i+1])
                ret = ret + '(' + symb + ')'
                i = i + 2
                continue
                
        return ' $#'+str(node[0])+'#$ '+ret
    
    def pointer(self, node):
        if node[1]!='pointer':
            return None
        
        ret = ''
        for i in node[2:]:
            if isinstance(i,list):
                for j in i:
                    ret = ret + ' ' + j
            else:
                ret = ret + ' ' + i
        
        ret = ret + ' '
        return ' $#'+str(node[0])+'#$ '+ret
        
    def parameter_type_list(self, node):
        if node[1]!='parameter_type_list':
            return None
        
        ret = self.parameter_list(node[2])
        if len(node)>3:
            ret = ret + ' , ...'
        return ret

    def parameter_list(self, node):
        if node[1]!='parameter_list':
            return None
        
        ret = ''
        for i in node[2:]:
            symb = self.parameter_declaration(i)
            if symb==None:
                print 'generator error: parameter list with a non parameter_declaration element'# no need in fact
            ret = ret + ' , ' + symb
        
        return ret[3:]

    def parameter_declaration(self, node):
        if node[1]!='parameter_declaration':
            return None
        
        symb = self.declaration_specifiers(node[2])
        if symb==None:
            print 'generator error: declaration with no declaration_specifiers'
            return None
        ret = symb
        
        if len(node)>3:
            symb = self.declarator(node[3])
            if symb==None:
                symb = self.abstract_declarator(node[3])
            if symb==None:
                print 'generator error: parameter_declaration should have a declarator or an abstract declarator'
            ret = ret + ' ' + symb

        return ' $#'+str(node[0])+'#$ '+ret

    def identifier_list(self, node):
        if node[1]!='identifier_list':
            return None

        ret = ''
        for i in node[2:]:
            ret = ret + ' , ' + i
        return ret[3:]

    def type_name(self, node):
        if node[1]!='type_name':
            return None
        
        symb = self.specifier_qualifier_list(node[2])
        if symb==None:
            print 'generator error: type_name without specifier_qualifier_list'
            return None
        ret = symb
        
        if len(node)>3:
            symb = self.abstract_declarator(node[3])
            ret = ret + ' ' + symb
        return ret

    def abstract_declarator(self,node):
        if node[1]!='abstract_declarator':
            return None
        
        ret = ''
        i = 2

        symb = self.pointer(node[i])
        if symb!=None:
            ret = ret + symb
            i = i + 1
        
        if len(node)>i:
            symb = self.direct_abstract_declarator(node[i])
            if symb!=None:
                ret = ret + ' ' + symb
        return ' $#'+str(node[0])+'#$ '+ret

    def direct_abstract_declarator(self, node):
        if node[1]!='direct_abstract_declarator':
            return None
        
        ret = ''
        i = 2
        while True:
            if len(node)<=i:
                break
            if node[i]=='[]':
                ret = ret + '[]'
                i = i + 1
                continue
            elif node[i]=='[constant_expression]':
                symb = self.constant_expression(node[i+1])
                ret = ret + '[' + symb + ']'
                i = i + 2
                continue
            elif node[i]=='()':
                ret = ret + '()'
                i = i + 1
                continue
            elif node[i]=='(parameter_type_list)':
                symb = self.parameter_type_list(node[i+1])
                ret = ret + '(' + symb + ')'
                i = i + 2
                continue
            elif node[i]=='(abstract_declarator)':
                symb = self.abstract_declarator(node[i+1])
                ret = ret + '(' + symb + ')'
                i = i + 2
                continue
                
        return ret

    def initializer(self, node):
        if node[1]!='initializer':
            return None
        
        ret = self.assignment_expression(node[2])
        if ret!=None:
            return ret
        
        ret = self.initializer_list(node[2])
        if ret==None:
            print 'generator error: initializer should contain an assignment_expression or an initializer_list'
            return None
        
        if len(node)>2:
            ret = '{' + ret + '}'
        
        return ' $#'+str(node[0])+'#$ '+ret

    def initializer_list(self, node):
        if node[1]!='initializer_list':
            return None
        
        ret = ''
        for i in node[2:]:
            symb = self.initializer(i)
            if symb==None:
                print 'generator error: initializer_list with a non initializer element'# no need in fact
            ret = ret + ' , ' + symb
        
        return ret[3:]

    def statement(self, node):
        if node[1]!='statement':
            return None

        symb = self.labeled_statement(node[2])
        if symb!=None:
            return ' $#'+str(node[0])+'#$ '+symb
        
        symb = self.compound_statement(node[2])
        if symb!=None:
            return ' $#'+str(node[0])+'#$ '+symb

        symb = self.expression_statement(node[2])
        if symb!=None:
            return ' $#'+str(node[0])+'#$ '+symb
        
        symb = self.selection_statement(node[2])
        if symb!=None:
            return ' $#'+str(node[0])+'#$ '+symb

        symb = self.iteration_statement(node[2])
        if symb!=None:
            return ' $#'+str(node[0])+'#$ '+symb

        symb = self.jump_statement(node[2])
        if symb!=None:
            return ' $#'+str(node[0])+'#$ '+symb
        
        return 'None C statement'

    def labeled_statement(self, node):
        if node[1]!='labeled_statement':
            return None
        
        if node[2]=='case':
            symb = self.constant_expression(node[3])
            ret = 'case ' + symb + ' : '
            symb = self.statement(node[4])
            ret = ret + symb
            return ret

        if node[2]=='default': # not needed
            symb = self.statement(node[3])
            ret = 'default : ' + symb
            return ret

        symb = self.statement(node[3])
        ret = node[2] + ' : ' + symb
        return ret


    def compound_statement(self,node):
        if node[1]!='compound_statement':
            return None
        
        ret = '{'
        for i in node[2:]:
            symb = self.declaration(i)
            if symb!=None:
                ret = ret + '\n' + symb
                continue

            symb = self.statement(i)
            if symb!=None:
                ret = ret + '\n' + symb
                continue
            break
            
        ret = ret + '\n}'
        return ret

    def declaration_list(self,node):
        if node[1]!='declaration_list':
            return None
        
        ret = ''
        for i in node[2:]:
            symb = self.declaration(i)
            if symb==None:
                print 'generator error: declaration_list with a non declaration element'# no need in fact
            ret = ret + symb
        
        return ret

    def statement_list(self, node):
        if node[1]!='statement_list':
            return None
        
        ret = ''
        for i in node[2:]:
            symb = self.statement(i)
            if symb==None:
                print 'generator error: declaration_list with a non declaration element'# no need in fact
            ret = ret + symb
        
        return ret

    def expression_statement(self, node):
        if node[1]!='expression_statement':
            return None
        
        ret = ''
        if len(node)>2:
            symb = self.expression(node[2])
            if symb!=None:
                ret = symb
                
        ret = ret + ' ;'       
        return ret

    def selection_statement(self, node):
        if node[1]!='selection_statement':
            return None
        
        ret = ''
        if node[2]=='if': 
            symb = self.expression(node[3])
            ret = 'if ( ' + symb + ' ) '
            
            symb = self.statement(node[4])
            ret = ret + symb
            
            if len(node)<6:
                return ret
            
            symb = self.statement(node[5])
            ret = ret + ' else ' + symb
            return ret

        elif node[2]=='switch': 
            symb = self.expression(node[3])
            ret = 'switch ( ' + symb + ' ) '
            
            symb = self.statement(node[4])
            ret = ret + symb
            return ret

    def iteration_statement(self, node):
        if node[1]!='iteration_statement':
            return None
        
        ret = ''
        if node[2]=='while': 
            symb = self.expression(node[3])
            ret = 'while ( ' + symb + ' ) '
            
            symb = self.statement(node[4])
            ret = ret + symb            
            return ret

        elif node[2]=='do': 
            symb = self.statement(node[3])
            ret = 'do ' + symb + ' while ( '
            
            symb = self.expression(node[4])
            ret = ret + symb + ' );'
            return ret

        elif node[2]=='for': 
            symb = self.expression_statement(node[3])
            if symb==None:
                symb = self.declaration(node[3])
            ret = 'for(' + symb
            symb = self.expression_statement(node[4])
            ret = ret + symb
            i = 5
            if len(node)>6:
                symb = self.expression(node[i])
                ret = ret + symb
                i = i + 1
            symb = self.statement(node[i])
            ret = ret + ') ' + symb
            return ret

    def jump_statement(self, node):
        if node[1]!='jump_statement':
            return None
        
        ret = ''
        if node[2]=='goto': 
            return 'goto ' + node[3] + ';'

        elif node[2]=='continue': 
            return 'continue;'

        elif node[2]=='break': 
            return 'break;'

        elif node[2]=='return': 
            ret = 'return '
            if len(node)>3:
                symb = self.expression(node[3])
                ret = ret + symb
            ret = ret + ';'
            return ret

    def translation_unit(self,node):
        if node[1]!='translation_unit':
            return None
        ret=''
        for i in node[2:]:
            symb = self.external_declaration(i)
            if symb==None:
                return None
            ret = ret + '\n' + symb
        return ' $#'+str(node[0])+'#$ '+ret

    def external_declaration(self,node):
        if node[1]!='external_declaration':
            return None

        ret=''
        
        symb = self.function_definition(node[2])
        if symb!=None:
            ret = symb
            return ' $#'+str(node[0])+'#$ '+ret

        symb = self.declaration(node[2])
        if symb!=None:
            ret = symb
            return ' $#'+str(node[0])+'#$ '+ret

        return None

    def function_definition(self,node):
        if node[1]!='function_definition':
            return None
        
        i = 2
        ret = ''
        
        symb = self.declaration_specifiers(node[i])
        if symb!=None:
            i = i + 1
            ret = ret + symb

        symb = self.declarator(node[i])
        if symb==None:
            print 'generator error: function definition with no declarator'
            return None
        i = i + 1
        ret = ret + ' ' + symb

        symb = self.declaration_list(node[i])
        if symb!=None:
            i = i + 1
            ret = ret + symb

        symb = self.compound_statement(node[i])
        if symb==None:
            print 'generator error: function definition with no body'
            return None
        ret = ret + '\n' + symb

        return ' $#'+str(node[0])+'#$ '+ret

    def constant_expression(self,node):
        if node[1]!='constant_expression':
            return None

        return ' $#'+str(node[0])+'#$ '+self.conditional_expression(node[2])

    def expression(self,node):
        if node[1]!='expression':
            return None
        ret = ''

        for i in node[2:]:
            symb = self.assignment_expression(i)
            ret = ret + ' , ' + symb

        return ' $#'+str(node[0])+'#$ '+ret[2:]

    def assignment_expression(self,node):
        if isinstance(node[0],list)!=True:
            asgOps=['=','*=','/=','%=','+=','-=','<<=','>>=','&=','^=','|=']
            for i in asgOps:
                if i==node[0]:
                    symb = self.unary_expression(node[1])
                    ret = symb + ' ' + node[0]
                    symb = self.assignment_expression(node[2])
                    ret = ret + ' ' + symb
                    return ret
        return self.conditional_expression(node)

    def conditional_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='?':        
                symb = self.logical_or_expression(node[1])
                ret = symb + ' ? '
                symb = self.expression(node[2])
                ret = ret + symb + ' : '
                symb = self.conditional_expression(node[3])
                ret = ret + symb
                return ret
        return self.logical_or_expression(node)

    def logical_or_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='||':        
                symb = self.logical_or_expression(node[1])
                ret = symb + ' || '
                symb = self.logical_and_expression(node[2])
                ret = ret + symb
                return ret
        return self.logical_and_expression(node)
    
    def logical_and_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='&&':        
                symb = self.logical_and_expression(node[1])
                ret = symb + ' && '
                symb = self.inclusive_or_expression(node[2])
                ret = ret + symb
                return ret
        return self.inclusive_or_expression(node)
    
    def inclusive_or_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='|':
                symb = self.inclusive_or_expression(node[1])
                ret = symb + ' | '
                symb = self.exclusive_or_expression(node[2])
                ret = ret + symb
                return ret
        return self.exclusive_or_expression(node)
    
    def exclusive_or_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='^':
                symb = self.exclusive_or_expression(node[1])
                ret = symb + ' ^ '
                symb = self.and_expression(node[2])
                ret = ret + symb
                return ret
        return self.and_expression(node)

    def and_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='&':
                symb = self.and_expression(node[1])
                ret = symb + ' & '
                symb = self.equality_expression(node[2])
                ret = ret + symb
                return ret
        return self.equality_expression(node)

    def equality_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='==' or node[0]=='!=':
                symb = self.equality_expression(node[1])
                ret = symb + ' ' + node[0] + ' '
                symb = self.relational_expression(node[2])
                ret = ret + symb
                return ret
        return self.relational_expression(node)

    def relational_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='<' or node[0]=='>' or node[0]=='<=' or node[0]=='>=':
                symb = self.relational_expression(node[1])
                ret = symb + ' ' + node[0] + ' '
                symb = self.shift_expression(node[2])
                ret = ret + symb
                return ret
        return self.shift_expression(node)

    def shift_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='<<' or node[0]=='>>':
                symb = self.shift_expression(node[1])
                ret = symb + ' ' + node[0] + ' '
                symb = self.additive_expression(node[2])
                ret = ret + symb
                return ret
        return self.additive_expression(node)

    def additive_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='+' or node[0]=='-':
                symb = self.additive_expression(node[1])
                ret = symb + ' ' + node[0] + ' '
                symb = self.multiplicative_expression(node[2])
                ret = ret + symb
                return ret
        return self.multiplicative_expression(node)

    def multiplicative_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='*' or node[0]=='/' or node[0]=='%':
                symb = self.multiplicative_expression(node[1])
                ret = symb + ' ' + node[0] + ' '
                symb = self.cast_expression(node[2])
                ret = ret + symb
                return ret
        return self.cast_expression(node)

    def cast_expression(self,node):
        if isinstance(node[0],list)==True:
            symb = self.type_name(node[0])
            if symb!=None:
                ret = '(' + symb + ') '

                symb = self.cast_expression(node[1])
                ret = ret + symb
                return ret
        return self.unary_expression(node)

    def unary_expression(self,node):
        if isinstance(node[0],list)!=True:
            if node[0]=='unary_expression':
                if node[1]=='++' or node[1]=='--':
                    symb = self.unary_expression(node[2])
                    return node[1]+symb
                elif node[1]=='&' or node[1]=='*' or node[1]=='+' or node[1]=='-' or node[1]=='~' or node[1]=='!':
                    symb = self.cast_expression(node[2])
                    return node[1]+symb
                elif node[1]=='sizeof':
                    symb = self.type_name(node[2])
                    if symb == None:
                        symb = self.unary_expression(node[2])
                        return node[1]+symb
                    return node[1]+'('+symb+')'
       
        return self.postfix_expression(node)

    
    def argument_expression_list(self,node):
        if node[1]!='argument_expression_list':
            return None
        ret = ''

        for i in node[2:]:
            symb = self.assignment_expression(i)
            if symb!=None:
                ret = ret + ' , ' + symb

        return ret[2:]
    
    def postfix_expression(self,node):
        ret = self.primary_expression(node[0])

        i = 1
        while True:
            if len(node)<=i:
                break
            if node[i]=='++' or node[i]=='--':
                ret = ret + node[i]
                i = i + 1
                continue
            elif node[i]=='.' or node[i]=='->':
                ret = ret + node[i] + node[i+1]
                i = i + 2
                continue
            elif node[i]=='[expression]':
                symb = self.expression(node[i+1])
                ret = ret + '[' + symb + ']'
                i = i + 2
                continue
            elif node[i]=='()':
                ret = ret + '()'
                i = i + 1
                continue
            elif node[i]=='(argument_expression_list)':
                symb = self.argument_expression_list(node[i+1])
                ret = ret + '(' + symb + ')'
                i = i + 2
                continue
            else:#modification
                return None
                
        return ret
    
    def primary_expression(self,node):
        if isinstance(node,list)!=True:
            return node
        return '('+self.expression(node)+')'
        


