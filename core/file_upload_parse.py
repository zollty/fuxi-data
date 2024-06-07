from fastapi import Body, File, Form, UploadFile
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import json
import datetime, decimal
from fuxi.utils.runtime_conf import get_temp_dir
from fuxi.utils.thread_helper import run_in_thread_pool
from fuxi.utils.api_base import (BaseResponse, ListResponse)
from deep_parser.core.document_loaders_helper import load_file_docs, cut_docs
from deep_parser.document_loaders import *


def parse_files_in_thread(
        files: List[UploadFile],
        dir: str,
        start_length: int = -1,
        special_loader: str = None,
):
    """
    通过多线程将上传的文件保存到对应目录内。
    生成器返回保存结果：[success or error, filename, msg, docs]
    """

    def parse_file(file: UploadFile):
        """
        保存单个文件。
        """
        filename = file.filename
        try:
            file_path = os.path.join(dir, filename)
            file_content = file.file.read()  # 读取上传文件的内容
            if not os.path.isdir(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            with open(file_path, "wb") as f:
                f.write(file_content)

            print(f"do load_file_docs--------------------------file_path: {file_path}")
            if special_loader:
                docs = []
                if special_loader == "rapid_ocr_pdf":
                    loader = RapidOCRPDFLoader(file_path=file_path)
                    docs = loader.load()

                docs = cut_docs(docs, start_length)
            else:
                docs = load_file_docs(
                    file_path,
                    filename=filename,
                    start_length=start_length
                )
            print(f"load_file_docs--------------------------ret: {docs}")
            return True, filename, f"成功上传文件 {filename}", docs
        except Exception as e:
            msg = f"{filename} 文件上传失败，报错信息为: {e}"
            return False, filename, msg, []

    params = [{"file": file} for file in files]
    for result in run_in_thread_pool(parse_file, params=params):
        yield result

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            print("MyEncoder-datetime.datetime")
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        if isinstance(obj, int):
            return int(obj)
        elif isinstance(obj, float):
            return float(obj)
        # elif isinstance(obj, array):
        #    return obj.tolist()
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        else:
            return super(MyEncoder, self).default(obj)

def parse_docs_inner(
        files: List[UploadFile] = File(..., description="上传文件，支持多文件"),
        start_size: int = Form(0, description="解析开始的字符位置"),
        special_loader: str = None,
) -> BaseResponse:
    failed_files = []
    file_docs = []
    path, id0 = get_temp_dir()
    print(f"--------------------------update file, save dir: {id0}")
    rt_success = False
    for success, file, msg, documents in parse_files_in_thread(files=files,
                                                               dir=path,
                                                               start_length=start_size,
                                                               special_loader=special_loader):
        if success:
            file_docs.append(
                {"name": file, "docs": [{"page_content": x.page_content, "metadata": x.metadata} for x in documents]})
            print(f"{file}--------------------------parse file success: ")
            print(file_docs)
            rt_success = True
        else:
            failed_files.append({file: msg})
            print(f"{file}--------------------------parse file failed: ")
            print(msg)
    if rt_success:  # json.dumps(, ensure_ascii=False)
        # strdata = json.dumps({"id": id0, "files": file_docs, "failed_files": failed_files}, cls=MyEncoder, ensure_ascii=False)
        # return JSONResponse(strdata, status_code=200)
        return BaseResponse(code=200, msg="文件解析成功", data={"id": id0, "files": file_docs, "failed_files": failed_files})
    #return JSONResponse({"id": id0, "failed_files": failed_files}, status_code=500)
    return BaseResponse(code=500, msg="解析文件失败", data={"id": id0, "failed_files": failed_files})


def parse_docs(
        files: List[UploadFile] = File(..., description="上传文件，支持多文件"),
        start_size: int = Form(0, description="解析开始的字符位置"),
) -> BaseResponse:
    return parse_docs_inner(files, start_size)


def parse_docs_rapid_ocr_pdf(
        files: List[UploadFile] = File(..., description="上传文件，支持多文件"),
        start_size: int = Form(0, description="解析开始的字符位置"),
) -> BaseResponse:
    return parse_docs_inner(files, start_size, "rapid_ocr_pdf")
