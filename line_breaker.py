from textwrap import TextWrapper
from typing import List
import re


class VerticalWrapper(TextWrapper):
    break_characters = [".",",","!","?"]
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
        lines = []
        if self.width <= 0:
            raise ValueError("invalid width %r (must be > 0)" % self.width)
        if self.max_lines is not None:
            if self.max_lines > 1:
                indent = self.subsequent_indent
            else:
                indent = self.initial_indent
            if len(indent) + len(self.placeholder.lstrip()) > self.width:
                raise ValueError("placeholder too large for max width")

        # Arrange in reverse order so items can be efficiently popped
        # from a stack of chucks.
        chunks.reverse()

        while chunks:
            # Start the list of chunks that will make up the current line.
            # cur_len is just the length of all the chunks in cur_line.
            cur_line = []
            cur_len = 0

            if lines:
                indent = self.subsequent_indent
            else:
                indent = self.initial_indent

            # Maximum width for this line.
            width = self.width - len(indent)

            # First chunk on line is whitespace -- drop it, unless this
            # is the very beginning of the text (ie. no lines started yet).
            if self.drop_whitespace and chunks[-1].strip() == '' and lines:
                del chunks[-1]

            while chunks:
                l = len(chunks[-1])
                cur_height = (len(lines) + 1) % self.height
                if cur_height == 1:
                    block_full = False
                if not block_full:
                    # Add to current line
                    if (cur_len + l <= width):
                        cur_line.append(chunks.pop())
                        cur_len += l
                        # End current paragraph
                        if any(c in cur_line[-1] for c in self.break_characters) and cur_height >= self.height-2: 
                            block_full=True
                            break
                    # Nope, this line is full.
                    else:
                        break
                # Block is completed.
                else:
                    break

            # The current line is full, and the next chunk is too big to
            # fit on *any* line (not just this one).
            if chunks and len(chunks[-1]) > width:
                self._handle_long_word(chunks, cur_line, cur_len, width)
                cur_len = sum(map(len, cur_line))

            # If the last chunk on this line is all whitespace, drop it.
            # if self.drop_whitespace and cur_line and cur_line[-1].strip() == '':
                cur_len -= len(cur_line[-1])
                del cur_line[-1]



            if (self.max_lines is None or
                len(lines) + 1 < self.max_lines or
                (not chunks or
                    self.drop_whitespace and
                    len(chunks) == 1 and
                    not chunks[0].strip()) and cur_len <= width):
                # Convert current line back to a string and store it in
                # list of all lines (return value).
                lines.append(indent + ''.join(cur_line))
            else:
                while cur_line:
                    if (cur_line[-1].strip() and
                        cur_len + len(self.placeholder) <= width):
                        cur_line.append(self.placeholder)
                        lines.append(indent + ''.join(cur_line))
                        break
                    cur_len -= len(cur_line[-1])
                    del cur_line[-1]
                else:
                    if lines:
                        prev_line = lines[-1].rstrip()
                        if (len(prev_line) + len(self.placeholder) <=
                                self.width):
                            lines[-1] = prev_line + self.placeholder
                            break
                    lines.append(indent + self.placeholder.lstrip())
                break
            # print(f"[*] -> {cur_line}")
        lines = list(filter(None, lines))
        return lines


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
        blocks = []
        block = []
        for i, line in enumerate(lines, 1):
            if i % self.height != 0:
                block.append(line)
            else:
                blocks.append(block)
                block = []
        return blocks


def format_blocks(blocks, line_breaks):
    paragraph = ""
    for block in blocks:
        for line in block:
            paragraph += line + "\n"
        paragraph += "\n\r" * line_breaks
    return paragraph
        

# def tokenize_sentences(text, width, align=False):
#     # sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
#     # fixed_text = " ".join(sent_detector.tokenize(text.strip()))
#     lines = wrap(text, width, break_long_words=False, fix_sentence_endings=True, replace_whitespace=False)
#     if align:
#         lines = justify(lines, width)
#     return lines


def create_paragraphs(lines, space_between_blocks, height):
    block = ""
    space_between_blocks = ("[]"+"\n") * space_between_blocks
    for i,l in enumerate(lines, 1):
        if i % height != 0:
            block = block + l + "\n"
        else:
            block += space_between_blocks
        
    return block