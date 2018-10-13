def extract(text, start_keyword, end_keyword, start_offset, end_offset):
    start = text.find(start_keyword) + start_offset
    end = len(text)
    if end_keyword is not None:
        end = text.find(end_keyword, start) + end_offset
    if start != start_offset - 1 and end != end_offset - 1:
        return text[start:end]
    else:
        return None