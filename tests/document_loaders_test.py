import sys
import os

# 获取当前脚本的绝对路径
__current_script_path = os.path.abspath(__file__)
# 将项目根目录添加到sys.path
runtime_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__current_script_path)))
sys.path.append(runtime_root_dir)

if __name__ == "__main__":
    from deep_parser.core.document_loaders_helper import load_file_docs

    docs = load_file_docs("./conf/shenq.docx", "shenq.docx")

