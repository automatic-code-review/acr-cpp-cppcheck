import hashlib
import os

import xmltodict


def review(config):
    rules = config['rules']
    path_source = config['path_source']

    output = "output.xml"
    path_size = len(path_source) + 1

    __run_cppcheck(path_source, output)

    with open(output, 'r') as arquivo:
        data = xmltodict.parse(arquivo.read())

    comments = []

    for error in data['results']['errors']['error']:
        id_error = error['@id']

        if id_error not in rules:
            continue

        msg_error = error['@msg']
        detail_error = error['@verbose']

        location_error = error['location']

        if isinstance(location_error, list):
            location_error = location_error[0]

        file_error = location_error['@file'][path_size:]
        line_error = location_error['@line']

        details = [
            f"Type: {id_error}<br>",
            f"<b>Message: {msg_error}</b><br>",
            f"<b>Detail: {detail_error}</b><br>",
            f"Arquivo: {file_error}",
            f"Linha: {line_error}",
        ]
        comment = "<br>".join(details)
        comments.append({
            'id': __generate_md5(comment),
            'comment': comment,
        })

    return comments


def __run_cppcheck(path_source, output):
    params = [
        f"cppcheck",
        f"-q",
        f"--language=c++",
        f"--enable=all",
        f"--suppress=unusedFunction",
        f"--xml",
        f"--output-file={output}",
        f"{path_source}"
    ]

    command = " ".join(params)
    os.system(command)


def __generate_md5(string):
    md5_hash = hashlib.md5()
    md5_hash.update(string.encode('utf-8'))
    return md5_hash.hexdigest()
