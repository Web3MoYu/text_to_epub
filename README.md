# TXT转EPUB工具

一个功能强大的Python脚本，用于将TXT文本文件转换为标准EPUB电子书格式。本工具能够智能识别段落、章节，添加封面图片，并生成美观的EPUB电子书。

## 功能特点

- **智能段落识别**：自动识别不同格式的段落（缩进式、空行分隔等）
- **章节自动识别**：默认识别中文小说常见的"第X章"格式章节
- **多种段落处理模式**：支持"line"、"blank"和"smart"三种段落识别模式
- **封面图片支持**：允许添加自定义封面图片（支持JPG、PNG、GIF格式）
- **强制缩进功能**：确保在所有阅读设备上正确显示段落缩进
- **编码自适应**：自动处理UTF-8和GBK编码的文本文件
- **完整元数据**：支持设置标题、作者、语言等电子书元数据
- **美观排版**：内置专为中文阅读优化的CSS样式

## 安装

### 前提条件

- Python 3.6 或更高版本
- pip (Python包管理器)

### 安装步骤

1. 克隆此仓库或下载代码：

```bash
git clone https://github.com/Web3MoYu/text_to_epub.git
cd txt-to-epub
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

最简单的用法，使用默认设置转换TXT文件：

```bash
python txt_to_epub.py 你的小说.txt
```

### 高级用法

使用更多选项来自定义生成的EPUB电子书：

```bash
python txt_to_epub.py 你的小说.txt -o 输出文件.epub -t "书名" -a "作者名" -l "zh-CN" -c "^第.+章.*$" -i 封面图片.jpg -p smart
```

### 命令行参数

| 参数 | 长选项 | 描述 | 默认值 |
|------|----------|-------------|---------|
| 位置参数 | | TXT文件路径 | 必须提供 |
| `-o` | `--output` | 输出的EPUB文件路径 | 与TXT同名的.epub文件 |
| `-t` | `--title` | 电子书标题 | TXT文件名 |
| `-a` | `--author` | 作者名 | "净无痕" |
| `-l` | `--language` | 语言代码 | "zh-CN" |
| `-c` | `--chapter-pattern` | 章节识别的正则表达式 | `^第.+章.*$` |
| `-i` | `--cover-image` | 封面图片路径 | 无 |
| `-p` | `--paragraph-mode` | 段落识别模式 | "smart" |
| | `--no-indent` | 禁用强制段落缩进 | 默认启用缩进 |

### 段落识别模式说明

- **line**：每行文本作为单独的段落处理
- **blank**：使用空行作为段落分隔符
- **smart**（默认）：智能识别段落格式，优先检查缩进格式，其次检查空行，最后使用标点符号判断

## 示例

### 转换带封面的小说

```bash
python txt_to_epub.py 绝世武神.txt -i cover.jpg -t "绝世武神" -a "净无痕"
```

### 使用空行分隔段落

```bash
python txt_to_epub.py 小说.txt -p blank
```

### 使用自定义章节识别模式

识别形如"Chapter 1"格式的章节：

```bash
python txt_to_epub.py 英文小说.txt -c "^Chapter [0-9]+"
```

## EPUB格式优势

- 可在绝大多数电子书阅读器和应用中使用
- 支持文本重排，适应不同屏幕大小
- 比PDF更适合在手机和电子墨水屏设备上阅读
- 支持书签、笔记、高亮等交互功能

## 贡献

欢迎通过Pull Request或Issue参与项目开发或提出建议。

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

## 致谢

- [EbookLib](https://github.com/aerkalov/ebooklib) 提供了EPUB处理核心功能
- 所有为这个项目提供反馈和建议的用户

## 作者

- **MoYu** - [GitHub个人资料链接](https://github.com/Web3MoYu)

---

希望这个工具能帮助您将喜爱的TXT小说转换为美观的EPUB电子书！如有问题请提交Issue。 