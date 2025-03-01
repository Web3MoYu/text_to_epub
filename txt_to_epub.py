#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from ebooklib import epub
import re
import imghdr


def txt_to_epub(
    txt_path,
    epub_path=None,
    title=None,
    author="净无痕",
    language="zh-CN",
    chapter_pattern=r"^第.+章.*$",
    cover_image=None,
    paragraph_mode="smart",
    force_indent=True,
):
    """
    将TXT文件转换为EPUB格式

    参数:
        txt_path (str): TXT文件路径
        epub_path (str, 可选): 输出的EPUB文件路径，默认为TXT文件同目录下同名的.epub文件
        title (str, 可选): 电子书标题，默认为TXT文件名
        author (str, 可选): 作者名，默认为"MoYu"
        language (str, 可选): 语言代码，默认为中文"zh-CN"
        chapter_pattern (str, 可选): 识别章节的正则表达式，默认匹配"第X章"格式
        cover_image (str, 可选): 封面图片路径，默认为None
        paragraph_mode (str, 可选): 段落识别模式，可选值为"line"(每行一个段落)、"blank"(空行分隔段落)、"smart"(智能识别)
        force_indent (bool, 可选): 是否在HTML层面强制添加段落缩进，默认为True
    """

    # 如果未提供epub_path，则使用与txt文件同名的.epub文件路径
    if epub_path is None:
        epub_path = os.path.splitext(txt_path)[0] + ".epub"

    # 如果未提供标题，则使用TXT文件名作为标题
    if title is None:
        title = os.path.basename(os.path.splitext(txt_path)[0])

    # 创建EPUB书籍对象
    book = epub.EpubBook()

    # 设置元数据
    book.set_identifier(f"id-{title}")
    book.set_title(title)
    book.set_language(language)
    book.add_author(author)

    # 添加封面图片（如果提供）
    if cover_image and os.path.isfile(cover_image):
        try:
            # 检查是否为有效的图片文件
            img_type = imghdr.what(cover_image)
            if img_type in ["jpeg", "png", "gif"]:
                # 读取封面图片
                with open(cover_image, "rb") as img_file:
                    cover_content = img_file.read()

                # 确定MIME类型
                mime_type = f"image/{img_type}"
                if img_type == "jpg" or img_type == "jpeg":
                    mime_type = "image/jpeg"

                # 创建封面项目
                cover_img = epub.EpubItem(
                    uid="cover_image",
                    file_name=f"images/cover.{img_type}",
                    media_type=mime_type,
                    content=cover_content,
                )
                book.add_item(cover_img)

                # 设置为封面
                book.set_cover("images/cover." + img_type, cover_content)

                print(f"已添加封面图片: {cover_image}")
            else:
                print(
                    f"警告: 封面图片格式不支持 ({img_type})。支持的格式: jpeg, png, gif"
                )
        except Exception as e:
            print(f"添加封面图片时出错: {e}")
    elif cover_image:
        print(f"警告: 封面图片文件不存在: {cover_image}")

    # 增强的CSS样式，确保段落缩进在各种设备上正常显示
    style = """
    @namespace epub "http://www.idpf.org/2007/ops";
    body {
        font-family: "Noto Serif CJK SC", "Songti SC", SimSun, serif;
        line-height: 1.5;
        text-align: justify;
        padding: 0 1em;
    }
    h1, h2 {
        text-align: center;
        font-weight: bold;
        margin: 1em 0;
    }
    p {
        text-indent: 2em;              /* 标准缩进 */
        -webkit-text-indent: 2em;      /* Safari/Chrome 兼容 */
        -moz-text-indent: 2em;         /* Firefox 兼容 */
        -ms-text-indent: 2em;          /* IE 兼容 */
        margin: 0.5em 0;
        padding: 0;
    }
    """
    css_file = epub.EpubItem(
        uid="style_default",
        file_name="style/default.css",
        media_type="text/css",
        content=style,
    )
    book.add_item(css_file)

    # 读取TXT文件内容
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            # 尝试使用GBK编码读取
            with open(txt_path, "r", encoding="gbk") as f:
                content = f.read()
        except Exception as e:
            print(f"无法读取文件: {e}")
            sys.exit(1)

    # 按行分割内容
    lines = content.split("\n")

    # 识别章节
    chapter_regex = re.compile(chapter_pattern)
    chapters = []
    current_title = "前言"

    # 检查是否有缩进的函数，用于识别新段落
    def has_indent(line):
        """检查行是否以全角空格或多个空格开头（表示有缩进）"""
        if not line:
            return False
        # 检测全角空格（常用于中文排版）
        if line.startswith("　"):
            return True
        # 检测普通空格缩进（至少两个空格）
        if line.startswith("  ") or line.startswith("\t"):
            return True
        return False

    # 删除行首缩进
    def remove_indent(line):
        """删除行首的缩进空格，返回清理后的文本"""
        if not line:
            return ""
        # 删除全角空格
        line = line.lstrip("　")
        # 删除普通空格和制表符
        line = line.lstrip(" \t")
        return line

    # 处理段落格式的函数
    def process_paragraphs(text_lines, mode, add_indent=False):
        """根据指定模式处理段落"""
        paragraphs = []

        # 添加段落开头的缩进空格（如果启用）
        indent_str = "　　" if add_indent else ""  # 使用全角空格作为缩进

        if mode == "line":
            # 每行作为一个段落，但尊重原始缩进
            for line in text_lines:
                original_line = line
                line = line.strip()
                if not line:
                    continue

                # 如果原始行有缩进，表示这是一个新段落
                if has_indent(original_line):
                    # 保留段落格式但确保统一缩进
                    clean_text = remove_indent(original_line).strip()
                    paragraphs.append(f"<p>{indent_str}{clean_text}</p>")
                else:
                    # 没有缩进的行
                    paragraphs.append(f"<p>{indent_str}{line}</p>")

        elif mode == "blank":
            # 空行分隔段落
            current_para = []
            for line in text_lines:
                stripped_line = line.strip()

                # 如果是空行，则结束当前段落
                if not stripped_line:
                    if current_para:
                        paragraphs.append(f"<p>{indent_str}{''.join(current_para)}</p>")
                        current_para = []
                    continue

                # 检查是否有缩进（新段落的标志）
                if has_indent(line) and current_para:
                    # 结束前一个段落
                    paragraphs.append(f"<p>{indent_str}{''.join(current_para)}</p>")
                    current_para = []
                    # 开始新段落，移除缩进
                    current_para.append(remove_indent(line).strip())
                else:
                    # 正常添加到当前段落
                    if has_indent(line):
                        # 如果有缩进但是段落的第一行，移除缩进
                        current_para.append(remove_indent(line).strip())
                    else:
                        current_para.append(stripped_line)

            # 处理最后一个段落
            if current_para:
                paragraphs.append(f"<p>{indent_str}{''.join(current_para)}</p>")

        elif mode == "smart":
            # 智能识别：分析文本判断段落特征
            # 首先检查是否有明显的缩进格式
            has_indented_lines = any(
                has_indent(line) for line in text_lines if line.strip()
            )
            has_blank_lines = any(not line.strip() for line in text_lines)

            if has_indented_lines:
                # 文本使用缩进表示段落，每个带缩进的行是新段落的开始
                current_para = []
                for line in text_lines:
                    stripped_line = line.strip()
                    if not stripped_line:
                        # 跳过空行，但如果有未完成的段落则结束它
                        if current_para:
                            paragraphs.append(
                                f"<p>{indent_str}{''.join(current_para)}</p>"
                            )
                            current_para = []
                        continue

                    if has_indent(line):
                        # 有缩进，表示新段落开始
                        if current_para:
                            # 如果有未完成的段落，先结束它
                            paragraphs.append(
                                f"<p>{indent_str}{''.join(current_para)}</p>"
                            )
                            current_para = []
                        # 开始新段落，移除缩进
                        current_para.append(remove_indent(line).strip())
                    else:
                        # 没有缩进，继续当前段落
                        current_para.append(stripped_line)

                # 处理最后一个段落
                if current_para:
                    paragraphs.append(f"<p>{indent_str}{''.join(current_para)}</p>")

            elif has_blank_lines:
                # 使用空行作为段落分隔符
                return process_paragraphs(text_lines, "blank", add_indent)
            else:
                # 没有明显段落标记，基于标点符号和行特征智能识别
                current_para = []
                for line in text_lines:
                    line = line.strip()
                    if not line:
                        continue

                    # 判断一行是否可能是段落的结束
                    is_end_of_para = False
                    if line and line[-1] in "。！？.!?\"'」》)）":
                        is_end_of_para = True

                    current_para.append(line)

                    if is_end_of_para:
                        paragraphs.append(f"<p>{indent_str}{''.join(current_para)}</p>")
                        current_para = []

                # 处理最后一个段落
                if current_para:
                    paragraphs.append(f"<p>{indent_str}{''.join(current_para)}</p>")

        return paragraphs

    # 处理章节和段落
    chapter_lines = []

    for line in lines:
        # 不对行进行strip，保留原始格式以便识别缩进
        if not line.strip():
            chapter_lines.append("")  # 保留空行，用于段落识别
            continue

        # 检查是否是新章节开始
        match = chapter_regex.match(line.strip())
        if match:
            # 处理之前收集的章节内容
            if chapter_lines:
                chapter_content = process_paragraphs(
                    chapter_lines, paragraph_mode, force_indent
                )
                if chapter_content:
                    chapters.append((current_title, "\n".join(chapter_content)))

            # 开始新章节
            current_title = line.strip()
            chapter_lines = []
        else:
            chapter_lines.append(line)  # 保留原始行（包括空格）

    # 处理最后一个章节
    if chapter_lines:
        chapter_content = process_paragraphs(
            chapter_lines, paragraph_mode, force_indent
        )
        if chapter_content:
            chapters.append((current_title, "\n".join(chapter_content)))

    # 创建章节文件
    chapter_items = []
    for i, (chapter_title, chapter_content) in enumerate(chapters):
        chapter_id = f"chapter_{i+1}"
        chapter_file_name = f"chapter_{i+1}.xhtml"

        chapter = epub.EpubHtml(
            title=chapter_title, file_name=chapter_file_name, lang=language
        )

        chapter.content = f"""
        <html>
        <head>
            <title>{chapter_title}</title>
            <link rel="stylesheet" href="style/default.css" type="text/css" />
        </head>
        <body>
            <h2>{chapter_title}</h2>
            {chapter_content}
        </body>
        </html>
        """

        book.add_item(chapter)
        chapter_items.append(chapter)

    # 添加所有章节到主要索引
    book.toc = chapter_items

    # 添加默认NCX和导航文件
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # 定义阅读顺序
    spine = ["nav"] + chapter_items
    book.spine = spine

    # 创建EPUB文件
    epub.write_epub(epub_path, book)
    print(f"转换完成: {epub_path}")
    return epub_path


def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="将TXT文件转换为EPUB电子书")
    parser.add_argument("txt_file", help="要转换的TXT文件路径")
    parser.add_argument("-o", "--output", help="输出的EPUB文件路径")
    parser.add_argument("-t", "--title", help="电子书标题")
    parser.add_argument("-a", "--author", default="净无痕", help="作者名")
    parser.add_argument("-l", "--language", default="zh-CN", help="语言代码")
    parser.add_argument(
        "-c", "--chapter-pattern", default=r"^第.+章.*$", help="章节识别的正则表达式"
    )
    parser.add_argument(
        "-i", "--cover-image", help="封面图片路径（支持JPG、PNG、GIF格式）"
    )
    parser.add_argument(
        "-p",
        "--paragraph-mode",
        choices=["line", "blank", "smart"],
        default="smart",
        help="段落识别模式：line(每行一个段落)、blank(空行分隔段落)、smart(智能识别)",
    )
    parser.add_argument(
        "--no-indent",
        action="store_false",
        dest="force_indent",
        help="禁用强制段落缩进（默认启用）",
    )

    args = parser.parse_args()

    # 调用转换函数
    txt_to_epub(
        args.txt_file,
        args.output,
        args.title,
        args.author,
        args.language,
        args.chapter_pattern,
        args.cover_image,
        args.paragraph_mode,
        args.force_indent,
    )


if __name__ == "__main__":
    main()
