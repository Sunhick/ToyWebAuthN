import subprocess

def compile_typescript():
    subprocess.run(["tsc", "--outDir", "static/js", "static/js/script.ts"])

if __name__ == "__main__":
    compile_typescript()
