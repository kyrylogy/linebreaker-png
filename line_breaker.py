from textwrap import TextWrapper
from typing import List
import re


class VerticalWrapper(TextWrapper):
    break_characters = [".","!","?"]
    def __init__(self, width, height, *args, **kwargs):
        super(VerticalWrapper, self).__init__(*args, **kwargs)
        self.width = width
        self.height = height
    

    def _split(self, text: str) -> List[str]:
        """
        Split the text to wrap into indivisible chunks.  Chunks are
        not quite the same as words; see _wrap_chunks() for full
        details.  As an example, the text
          Look, goof-ball -- use the -b option!
        breaks into the following chunks:
          'Look,', ' ', 'goof-', 'ball', ' ', '--', ' ',
          'use', ' ', 'the', ' ', '-b', ' ', 'option!'
        if break_on_hyphens is True, or in:
          'Look,', ' ', 'goof-ball', ' ', '--', ' ',
          'use', ' ', 'the', ' ', '-b', ' ', option!'
        otherwise.
        """
        # Add space after punctuation
        text = re.sub(r'(?<=[.,!?:;])(?=[^\s])', r' ', text)
        if self.break_on_hyphens is True:
            chunks = self.wordsep_re.split(text)
        else:
            chunks = self.wordsep_simple_re.split(text)
        chunks = [c for c in chunks if c]
        return chunks


    def _wrap_chunks(self, chunks: List[str]) -> List[str]:
        """
        Wrap a sequence of text chunks and return a list of lines of
        length 'self.width' or less.  (If 'break_long_words' is false,
        some lines may be longer than this.)  Chunks correspond roughly
        to words and the whitespace between them: each chunk is
        indivisible (modulo 'break_long_words'), but a line break can
        come between any two chunks.  Chunks should not have internal
        whitespace; ie. a chunk is either all whitespace or a "word".
        Whitespace chunks will be removed from the beginning and end of
        lines, but apart from that whitespace is preserved.
        """
        blocks = []
        if self.width <= 0:
            raise ValueError("invalid width %r (must be > 0)" % self.width)
        if self.max_lines is not None:
            if self.max_lines > 1:
                indent = self.subsequent_indent
            else:
                indent = self.initial_indent
            if len(indent) + len(self.placeholder.lstrip()) > self.width:
                raise ValueError("placeholder too large for max width")

        chunks.reverse()
        # Complete/empty block loop
        while chunks:
            cur_block = []
            if len(cur_block) == 0:
                block_full = False
            # Complete/empty line loop
            while chunks:
                cur_line = []
                cur_len = 0
                if block_full:
                    break
                # Each word loop
                while chunks:
                    l = len(chunks[-1])
                    if chunks and len(chunks[-1]) > self.width:
                        self._handle_long_word(chunks, cur_line, cur_len, self.width)
                        cur_len = sum(map(len, cur_line))

                    if (cur_len + l <= self.width):
                        if any(c in chunks[-1] for c in self.break_characters) and len(cur_block) >= self.height-2: 
                            cur_line.append(chunks.pop())
                            cur_len += l
                            block_full = True
                            cur_block.append("".join(cur_line).strip())
                            break # start new line
                        cur_line.append(chunks.pop())
                        cur_len += l
                    else:
                        cur_block.append("".join(cur_line).strip())
                        break # start new line
                if block_full:
                    blocks.append(cur_block)
                    break
        cur_block.append("".join(cur_line))
        blocks.append(cur_block)
        return blocks

    def justify(self, lines, width):
        def _justify_single(line, width):
            gap_width, max_replace = divmod(width - len(line) + line.count(' '), line.count(' '))
            return line.replace(' ', ' ' * gap_width).replace(' ' * gap_width, ' ' * (gap_width + 1), max_replace)

        for i, line in enumerate(lines[:-1]):
            if len(line) <= width and line.count(' '):
                lines[i] = _justify_single(line, width).rstrip()
        return lines 


    def assemble(self, text: str) -> List[List[str]]:
        """
        Reformat the single paragraph in 'text' so there are
        'self.height' sized blocks of lines with 'self.width'
        maximum width on each line with punctuation as the
        breaking character of each block.
        """
        chunks = self._split_chunks(text)
        if self.fix_sentence_endings:
            self._fix_sentence_endings(chunks)
        lines = self._wrap_chunks(chunks)
        return lines


def format_blocks(blocks, line_breaks=4):
    paragraph = ""
    for block in blocks:
        for line in block:
            paragraph += line + "\n"
        paragraph += "\n" * line_breaks
    return paragraph
        

def create_paragraphs(lines, space_between_blocks, height):
    block = ""
    space_between_blocks = ("[]"+"\n") * space_between_blocks
    for i,l in enumerate(lines, 1):
        if i % height != 0:
            block = block + l + "\n"
        else:
            block += space_between_blocks
        
    return block