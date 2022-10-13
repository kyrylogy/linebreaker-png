# Settings
width = 65
height = 8
font_size = 48
line_breaks = 2

# true/false
transparent = False
single_block = False 




# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
def get_text(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = f.read()
        return data


if __name__ == "__main__":
    text_file = 'text.txt'
    from line_breaker import VerticalWrapper
    from create_image import *
    data = get_text(text_file)

    paragraph = VerticalWrapper(width=width, height=height) 
    blocks = paragraph.assemble(data)
    create_image(blocks, font_size, transparent, single_block)

