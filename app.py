# Settings
width = 65
height = 8
font_size = 54
block_size = 1
space_between_blocks = 6

# true/false
transparent = False
single_block = True
align = True
break_characters = [".", ",", ""]


def get_text(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = f.read()
        return data


if __name__ == "__main__":
    text_file = 'text.txt'
    from line_breaker import VerticalWrapper, format_blocks
    from create_image import *
    data = get_text(text_file)

    # lines = tokenize_sentences(data, width, align)
    paragraph = VerticalWrapper(width=width, height=height) 
    res = paragraph.assemble(data)
    [print(block) for block in res]

    # print(format_blocks(res, 3))
    # blocks = format_blocks(lines, space_between_blocks, height)
    # create_image(blocks, font_size, transparent, single_block, height, space_between_blocks)

