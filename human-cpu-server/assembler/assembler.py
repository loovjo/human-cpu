from sys import argv

from parser import tokenize, cleanup
from instructions import read_instlist
from compile_ctx import CompileCtx

if __name__ == "__main__":
    if len(argv) == 2:
        inpath = argv[1]
        outpath = "a.out"
    elif len(argv) == 3:
        inpath = argv[1]
        outpath = argv[2]
    else:
        print("python3 assembler.py <input> [output]")
        exit()

    with open(inpath, "r") as f:
        content = f.read()

    tokens = tokenize(content)
    tokens = cleanup(tokens)

    instlist = read_instlist(tokens)

    compile_ctx = CompileCtx()
    for inst in instlist:
        inst.compile_to_bytes(compile_ctx)

    result = compile_ctx.postproc()

    with open(outpath, "wb") as out:
        out.write(result)
