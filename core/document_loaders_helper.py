import importlib
import langchain.document_loaders
import json
from typing import List, Union, Dict
import chardet

from fuxi.utils.runtime_conf import get_log_verbose, logger
from deep_parser.core.config import LOADER_DICT, SUPPORTED_EXTS

import os
from pathlib import Path


# patch json.dumps to disable ensure_ascii
# def _new_json_dumps(obj, **kwargs):
#     kwargs["ensure_ascii"] = False
#     return _origin_json_dumps(obj, **kwargs)
#
#
# if json.dumps is not _new_json_dumps:
#     _origin_json_dumps = json.dumps
#     json.dumps = _new_json_dumps


class JSONLinesLoader(langchain.document_loaders.JSONLoader):
    '''
    行式 Json 加载器，要求文件扩展名为 .jsonl
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._json_lines = True


langchain.document_loaders.JSONLinesLoader = JSONLinesLoader


def get_loader_class(file_extension):
    for LoaderClass, extensions in LOADER_DICT.items():
        if file_extension in extensions:
            return LoaderClass


# 把一些向量化共用逻辑从KnowledgeFile抽取出来，等langchain支持内存文件的时候，可以将非磁盘文件向量化
def get_document_loaders(loader_name: str, file_path: str, loader_kwargs: Dict = None):
    '''
    根据loader_name和文件路径或内容返回文档加载器。
    '''
    loader_kwargs = loader_kwargs or {}
    try:
        if loader_name in ["RapidOCRPDFLoader", "RapidOCRLoader", "FilteredCSVLoader",
                           "RapidOCRDocLoader", "RapidOCRPPTLoader"]:
            document_loaders_module = importlib.import_module('deep_parser.document_loaders')
        else:
            document_loaders_module = importlib.import_module('langchain.document_loaders')
        DocumentLoader = getattr(document_loaders_module, loader_name)
    except Exception as e:
        msg = f"为文件{file_path}查找加载器{loader_name}时出错：{e}"
        logger.error(f'{e.__class__.__name__}: {msg}',
                     exc_info=e if get_log_verbose() else None)
        document_loaders_module = importlib.import_module('langchain.document_loaders')
        DocumentLoader = getattr(document_loaders_module, "UnstructuredFileLoader")

    if loader_name == "UnstructuredFileLoader":
        loader_kwargs.setdefault("autodetect_encoding", True)
    elif loader_name == "CSVLoader":
        if not loader_kwargs.get("encoding"):
            # 如果未指定 encoding，自动识别文件编码类型，避免langchain loader 加载文件报编码错误
            with open(file_path, 'rb') as struct_file:
                encode_detect = chardet.detect(struct_file.read())
            if encode_detect is None:
                encode_detect = {"encoding": "utf-8"}
            loader_kwargs["encoding"] = encode_detect["encoding"]
        ## TODO：支持更多的自定义CSV读取逻辑

    elif loader_name == "JSONLoader":
        loader_kwargs.setdefault("jq_schema", ".")
        loader_kwargs.setdefault("text_content", False)
    elif loader_name == "JSONLinesLoader":
        loader_kwargs.setdefault("jq_schema", ".")
        loader_kwargs.setdefault("text_content", False)

    loader = DocumentLoader(file_path, **loader_kwargs)
    print(f"-----------------------使用文档加载器：{loader_name}")
    return loader


def load_file_docs(
        filepath: str,
        filename: str,
        start_length: int = -1,
        loader_kwargs: Dict = {},
):
    """
    对应知识库目录中的文件，必须是磁盘上存在的才能进行向量化等操作。
    """
    filename = str(Path(filename).as_posix())
    ext = os.path.splitext(filename)[-1].lower()
    if ext not in SUPPORTED_EXTS:
        raise ValueError(f"暂未支持的文件格式 {ext} of {filename}")
    # filepath = filepath  # get_file_path(knowledge_base_name, filename)

    document_loader_name = get_loader_class(ext)

    logger.info(f"{document_loader_name} used for {filepath}")

    loader = get_document_loaders(loader_name=document_loader_name,
                                  file_path=filepath,
                                  loader_kwargs=loader_kwargs)
    docs = loader.load()

    return cut_docs(docs, start_length)


def cut_docs(
        docs: list,
        start_length: int = -1,
):
    """
    处理 start_length 位置，裁剪文档（实现分页效果）
    """

    target_docs = []
    if start_length >= 0:
        min_sta = start_length
        max_end = start_length + 30000
        t0 = 0
        t1 = 0
        not_start = True
        for doc in docs:
            doc_len = len(doc.page_content)
            t1 = t1 + doc_len
            if not_start:
                if t1 > min_sta:
                    start = min_sta - t0
                    if t1 > max_end:
                        doc.page_content = doc.page_content[start:max_end - t0]
                    else:
                        doc.page_content = doc.page_content[start:]

                    not_start = False
                    target_docs.append(doc)
            else:
                if t1 > max_end:
                    doc.page_content = doc.page_content[0:max_end - t0]
                    target_docs.append(doc)
                    break
                else:
                    target_docs.append(doc)

            t0 = t0 + doc_len
        docs = target_docs

        print(
            f"↓↓↓↓↓↓↓↓↓↓↓原始文档--------------------------------------start_length={start_length}--------------------")
        for doc in docs:
            print(len(doc.page_content))
            print(doc.page_content[:200] + "……………………" + doc.page_content[-200:])
            sl: int = len(doc.page_content)
            if sl > 200:
                el: int = sl - 200
                print(doc.page_content[:180] + "……………………" + doc.page_content[-el:])
            else:
                print(doc.page_content)
        print(
            f"↑↑↑↑↑↑↑↑↑↑↑原始文档--------------------------------------start_length={start_length}--------------------")
    return docs
