# This file is part of the GGDML language extensions' source-to-source translator.
# It processes a file or a project's directory that contains code written with
# extended language. It produces code that fits the target machine.
# The tool is intended to be used according to the GPL licence after the first
# version is published.
# This file works together with the GGDML extensions processor, and the general-
# purpose-language processor.
# Nabeeh Jum'ah

import re
import argparse
import os.path
import shutil

optimizer = None
def processSubDir(targetDir,baseDir,dir):
    for f in os.listdir(dir):
        absName = os.path.join(dir,f)
        rtb = os.path.relpath(absName,baseDir)
        print 'processing: ' + absName
        if os.path.isdir(absName):
            os.mkdir(os.path.join(targetDir,rtb))
            processSubDir(targetDir,baseDir,absName)
        elif os.path.isfile(absName):
            m=re.match(r'.*?((\.c)|(\.h))$',f,flags=re.S)
            if m:
                dsl=dslModule.DSL(args.sp)
                dsl.readSource(absName)
                dsl.parse()
                optimizer.addModule([absName,dsl,os.path.join(targetDir,rtb)])
            else:
                shutil.copy2(absName,os.path.join(targetDir,rtb))
        else:
            shutil.copy2(absName,os.path.join(targetDir,rtb))
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="source-to-source translation tool, translating DSL enriched code to pure host language")
    parser.add_argument("-dsl", help="the dsl to use")
    parser.add_argument("-sp", help="scientific programmer provided file")
    parser.add_argument("-o","--output", help="output file name")
    parser.add_argument("-ni","--nonInteractive", help="for non-interactive tool run",action="store_true")
    parser.add_argument("sourceFile", help="the source code file to translate")
    args=parser.parse_args()
    
    
    #load needed DSL, and handle options
    if args.dsl==None:
        print 'please provide the DSL module name'
        exit(1)
    if os.path.exists(args.dsl+'.py')!=True:
        print 'chosen DSL module does not exist, please provide a valid one'
        exit(1)

    if args.sp==None:
        print 'config file should be provided, provide by -sp option'
        exit(1)
    if os.path.exists(args.sp)!=True:
        print 'config file does not exist, please provide a valid one'
        exit(1)

    dslModule = __import__(args.dsl)

    #check if input file exists
    if os.path.isfile(args.sourceFile):
        dsl=dslModule.DSL(args.sp)
    
        #read source code file
        #and do preprocessing and process include files
        dsl.readSource(args.sourceFile)

        #parse
        dsl.parse()

        #to find and apply possible optimizations
        o=dslModule.optimizer(dsl)    


        #find/apply optimizations , write output code , or exit
        outputFileName = args.output
        if outputFileName==None:
            m=re.search(r'.dsl$',args.sourceFile)
            if m:
                outputFileName = re.sub(r'.dsl$','',args.sourceFile)
            else:
                outputFileName = args.sourceFile + '.new'

        if args.nonInteractive:
            #autotune
            f = open(outputFileName, 'w')
            f.write(dsl.finalOutput())
            f.close()
            exit(0)

        while True:
            choice =raw_input('Enter optimize, save, index, or exit: ')
            if choice=='exit':
                f = open(outputFileName, 'w')
                f.write(dsl.finalOutput())
                f.close()
                break

            elif choice=='index':
                choice =raw_input('choose 0-ijk 1-ikj 2-jik 3-jki 4-kij 5-kji: ')#change to read from dialect config files later
                choice = int(choice)
                #transform program
                continue

            elif choice=='save':
                f = open(outputFileName, 'w')
                f.write(dsl.finalOutput())
                f.close()
                continue

            elif choice=='optimize':
                print o.findPossibleOptimizations()
                choice =raw_input('Enter number of optimization to apply: ')
                choice = int(choice)
                if choice>=len(o.optList):
                    print 'invalid number, no such optimization in the list'
                    continue
                o.applyOptimization(choice)
                continue

            else:
                print 'invalid choice'

    elif os.path.isdir(args.sourceFile):
        rootDir = os.path.abspath(args.sourceFile)
        targetDir = os.path.join(os.path.dirname(rootDir),args.sp+'_target')
        os.mkdir(targetDir)
        optimizer=dslModule.optimizer()
        processSubDir(targetDir,rootDir,rootDir)
        while True:
            if args.nonInteractive==False:
                print optimizer.findPossibleOptimizations()
                choice =raw_input('Enter number of optimization to apply: ')
                choice = int(choice)
                if choice>=len(optimizer.optList):
                    print 'invalid number, no such optimization in the list'
                    break
                optimizer.applyOptimization(choice)
            else:
                break
        for f in optimizer.modules:
            of = open(f[2], 'w')
            of.write(f[1].finalOutput())
            of.close()

