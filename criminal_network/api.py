from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os
import shutil
import subprocess


app = FastAPI(
    title="Criminal Network Analysis API"
)


# =====================================================
# FOLDERS
# =====================================================

RAW_DATA = "raw_data"
OUTPUT = "output"


os.makedirs(RAW_DATA, exist_ok=True)
os.makedirs(OUTPUT, exist_ok=True)


# =====================================================
# HOME
# =====================================================

@app.get("/")
def home():

    return {
        "status": "Backend running",
        "service": "Criminal Network Analysis"
    }


# =====================================================
# ANALYZE CASE
# =====================================================

@app.post("/analyze")
async def analyze_case(
    files: list[UploadFile] = File(...)
):

    try:

        saved_files = []


        # =============================================
        # 1. SAVE RAW FILES
        # =============================================

        for file in files:

            file_path = os.path.join(
                RAW_DATA,
                file.filename
            )

            with open(
                file_path,
                "wb"
            ) as buffer:

                shutil.copyfileobj(
                    file.file,
                    buffer
                )

            saved_files.append(file.filename)


        # =============================================
        # 2. IMPORT DATA INTO NEO4J
        # =============================================

        # Change these script names if yours are different.

        subprocess.run(
            [
                "python",
                "scripts/import_cdr.py"
            ],
            check=True,
            shell=True
        )


        subprocess.run(
            [
                "python",
                "scripts/import_transactions.py"
            ],
            check=True,
            shell=True
        )


        # =============================================
        # 3. NETWORK ANALYSIS
        # =============================================

        subprocess.run(
            [
                "python",
                "scripts/analyze_network.py"
            ],
            check=True,
            shell=True
        )


        # =============================================
        # 4. QWEN / FINAL ANALYSIS
        # =============================================

        subprocess.run(
            [
                "python",
                "scripts/final_analysis.py"
            ],
            check=True,
            shell=True
        )


        # =============================================
        # 5. READ FINAL REPORT
        # =============================================

        report_path = os.path.join(
            OUTPUT,
            "final_report.txt"
        )


        report = ""


        if os.path.exists(report_path):

            with open(
                report_path,
                "r",
                encoding="utf-8"
            ) as file:

                report = file.read()


        # =============================================
        # 6. RETURN RESULT TO FRONTEND
        # =============================================

        return JSONResponse({

            "status": "success",

            "message": "Case analysis completed",

            "files": saved_files,

            "report": report,

            "graph": "Neo4j updated successfully"

        })


    except subprocess.CalledProcessError as error:

        return JSONResponse(

            status_code=500,

            content={

                "status": "error",

                "message":
                "Backend processing failed",

                "details": str(error)

            }

        )


    except Exception as error:

        return JSONResponse(

            status_code=500,

            content={

                "status": "error",

                "message": str(error)

            }

        )