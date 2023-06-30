import hashlib
import os

import xmltodict


def review(config):
    rules = config['rules']
    path_source = config['path_source']

    if not __has_cpp_files(path_source):
        print('acr-cpp-cppcheck não possui arquivo .cpp, ignorando verificação')
        return []

    output = "output.xml"
    path_size = len(path_source) + 1

    __run_cppcheck(path_source, output)

    with open(output, 'r') as arquivo:
        data = xmltodict.parse(arquivo.read())

    comments = []

    errors = data['results']['errors']['error']

    if not isinstance(errors, list):
        errors = [errors]

    for error in errors:
        id_error = error['@id']

        if id_error not in rules:
            continue

        msg_error = error['@msg']
        detail_error = error['@verbose']

        if 'location' not in error:
            continue

        location_error = error['location']

        if isinstance(location_error, list):
            end_line = None
            start_line = None

            for location_error_current in location_error:
                current_line = location_error_current['@line']

                if end_line is None or end_line < current_line:
                    end_line = current_line

                if start_line is None or start_line > current_line:
                    start_line = current_line

            file_error = location_error[0]['@file'][path_size:]

        else:
            start_line = location_error['@line']
            end_line = start_line
            file_error = location_error['@file'][path_size:]

        details = [
            f"Type: {id_error}<br>",
            f"<b>Message: {msg_error}</b><br>",
            f"<b>Detail: {detail_error}</b><br>",
            f"Arquivo: {file_error}",
            f"Linha: {start_line} até {end_line}",
        ]
        comment = "<br>".join(details)
        comments.append({
            'id': __generate_md5(comment),
            'comment': comment,
            "position": {
                'language': 'c++',
                'path': file_error,
                'startInLine': int(start_line),
                'endInLine': int(end_line)
            }
        })

    return comments


def __has_cpp_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".cpp"):
                return True

    return False


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
