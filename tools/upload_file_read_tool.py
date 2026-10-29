# 上传文件读取工具
from pathlib import Path
from typing import Annotated
from langchain_core.tools import tool
from api.monitor import monitor
from api.context import get_session_context
from utils.path_utils import resolve_path
import docx
import pypdf
import pandas as pd

# def read_file_content(filename: str, instruction: str = "提取全部内容") -> str:
#     """
#     读取指定文件的内容。支持 Markdown(.md)、Word(.docx)、PDF(.pdf) 和 Excel(.xlsx/.xls)。
#     对于 Excel 文件，会自动提供数据统计信息（head 和 describe）。

#     Args:
#         filename: 要读取的文件名或路径（支持 .md, .docx, .pdf, .xlsx, .xls）
#         instruction: 对提取内容的具体指令（例如：'提取摘要', '统计数据'）

@tool
def read_file_content(
        filename: Annotated[str, "要读取的文件名或路径（支持 .md, .docx, .pdf, .xlsx, .xls）"],
        instruction: Annotated[str, "对提取内容的具体指令（例如：'提取摘要', '统计数据'）"] = "提取全部内容"
) -> str:
    """
    读取指定文件的内容。支持 Markdown(.md)、Word(.docx)、PDF(.pdf) 和 Excel(.xlsx/.xls)。
    对于 Excel 文件，会自动提供数据统计信息（head 和 describe）。
    """
    # monitor.report_tool("文件内容读取工具", {"filename": filename, "instruction": instruction})

    # ====================== 1. Path 重构路径解析 ======================
    session_dir = get_session_context()
    file_path = Path(resolve_path(filename, session_dir))  # 转为Path对象

    # 检查文件是否存在（替代os.path.exists）
    if not file_path.exists():
        return f"错误：文件 '{filename}' 不存在 (解析路径: {file_path})。"

    # 获取后缀名（替代os.path.splitext，自动转小写）
    ext = file_path.suffix.lower()

    try:
        if ext in ['.md', '.txt']:
            # Path直接读取文本（替代open + os.path）
            return file_path.read_text(encoding='utf-8')

        elif ext == '.docx':
            doc = docx.Document(str(file_path))  # 转字符串传给docx
            full_text = [para.text for para in doc.paragraphs]
            return '\n'.join(full_text)

        elif ext == '.pdf':
            reader = pypdf.PdfReader(str(file_path))  # 转字符串传给pypdf
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
            return text

        elif ext in ['.xlsx', '.xls']:
            try:
                df = pd.read_excel(str(file_path))  # 转字符串传给pandas
            except Exception as e:
                return f"读取 Excel 失败: {str(e)}"

            result = [
                f"文件: {filename}",
                f"行数: {len(df)}, 列数: {len(df.columns)}",
                f"列名: {', '.join(df.columns.astype(str))}",
                "\n[前5行数据预览]:",
                df.head().to_string(index=False),
                "\n[统计描述]:",
                df.describe().to_string()
            ]
            return "\n".join(result)

        else:
            # 尝试作为纯文本读取
            try:
                return file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                return f"错误：不支持的文件格式 '{ext}'，且无法作为文本读取。"

    except Exception as e:
        return f"读取文件出错: {str(e)}"

# ====================== 测试入口（完全按你要求的格式） ======================
if __name__ == '__main__':
    # 1. 固定 session_dir（仅赋值，不Mock）
    def get_session_context():
        return "./test_session_123"

    # 2. 定义测试文件路径
    md_path = "sub_dir/测试文件.md"
    pdf_path = "sub_dir/测试文件.pdf"
    doc_path = "sub_dir/测试文件.docx"
    excel_path = "sub_dir/测试文件.xlsx"

    # 3. 测试调用（先测试MD文件，指令用默认）
    result = read_file_content.invoke({
        "filename": excel_path
    })
    print("===== 读取到文件结果 =====")
    print(result)
