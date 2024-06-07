import sys
import os

# 获取当前脚本的绝对路径
__current_script_path = os.path.abspath(__file__)
# 将项目根目录添加到sys.path
runtime_root_dir = os.path.dirname(os.path.dirname(__current_script_path))
sys.path.append(runtime_root_dir)

from fastapi import FastAPI, Body, Request, File, Form, UploadFile
from starlette.responses import RedirectResponse
from fuxi.utils.api_base import (BaseResponse, ListResponse)


async def document():
    return RedirectResponse(url="/docs")

def mount_app_routes(app: FastAPI):
    from deep_parser.core.file_upload_parse import parse_docs, parse_docs_rapid_ocr_pdf

    app.get("/",
            response_model=BaseResponse,
            summary="swagger 文档")(document)

    app.post("/deep_parser/normal_v1",
             tags=["DeepParser"],
             summary="文档解析的默认方法（支持各种格式，v1版本）"
             )(parse_docs)

    app.post("/deep_parser/rapid_ocr_pdf",
             tags=["DeepParser"],
             summary="使用Rapidocr，pyMuPDF，cv2等技术解析PDF文档"
             )(parse_docs_rapid_ocr_pdf)


if __name__ == "__main__":
    import argparse
    from fuxi.utils.fastapi_tool import create_app, run_api

    title = "FenghouAI DeepParser API Server"
    parser = argparse.ArgumentParser(prog='fenghou-ai',
                                     description=title)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8112)
    parser.add_argument("--ssl_keyfile", type=str)
    parser.add_argument("--ssl_certfile", type=str)
    # 初始化消息
    args = parser.parse_args()
    args_dict = vars(args)

    app = create_app([mount_app_routes], version="1.0.0", title=title)

    run_api(app,
            host=args.host,
            port=args.port,
            ssl_keyfile=args.ssl_keyfile,
            ssl_certfile=args.ssl_certfile,
            )
