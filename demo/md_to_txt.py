# 读取本地文档
document_path = "../data/网易云音乐PRD.md"
with open(document_path, "r", encoding="utf-8") as file:
    document_content = file.read()

# 工作设置
piece_length_control = 1000  # 设置文本块的最大长度

# 分割文档
chunks = document_content.split("\n\n")  # 按双换行符分割文档
paragraphs = []
paragraph_num = -1
for chunk in chunks:
    if chunk.startswith("#"):  # 如果块以#开头，认为是新的段落
        paragraphs.append(chunk + "\n\n")
        paragraph_num += 1
    else:
        paragraphs[paragraph_num] += chunk + "\n\n"  # 否则，将块添加到当前段落
text_pieces = []
text_piece_num = 0
for paragraph in paragraphs:
    if len(text_pieces) == 0:  # 如果文本块列表为空，直接添加段落
        text_pieces.append(paragraph)
    else:
        if len(text_pieces[text_piece_num] + paragraph) > piece_length_control:  # 如果当前文本块加上段落超过长度限制
            text_pieces.append(paragraph)  # 添加新的文本块
            text_piece_num += 1
        else:
            text_pieces[text_piece_num] += paragraph  # 否则，将段落添加到当前文本块

# 打印分割后的文本
for text_piece in text_pieces:
    print("[Text Piece]: \n", text_piece, end="\n")
    print("------------------------以下开始进行推理------------------------")

