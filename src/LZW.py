# LZW compresssion function
def compress(data, max_bits):
    dictionary = {chr(i): i for i in range(256)}
    next_code = 256
    result = []
    w = ""

    max_size = 2 ** max_bits

    for c in data:
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            result.append(dictionary[w])
            if next_code < max_size:
                dictionary[wc] = next_code
                next_code += 1
            w = c

    if w:
        result.append(dictionary[w])

    return result

# LZW decompresssion function
def decompress(compressed, max_bits):
    dictionary = {i: chr(i) for i in range(256)}
    next_code = 256
    result = ""
    w = chr(compressed.pop(0))
    result += w

    max_size = 2 ** max_bits

    for k in compressed:
        if k in dictionary:
            entry = dictionary[k]
        elif k == next_code:
            entry = w + w[0]
        else:
            raise ValueError("Kompresi rusak atau tidak valid.")

        result += entry

        if next_code < max_size:
            dictionary[next_code] = w + entry[0]
            next_code += 1

        w = entry

    return result
