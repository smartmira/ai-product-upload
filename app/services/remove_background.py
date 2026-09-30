from rembg import remove


def remove_background(
    input_path,
    output_path
):

    if input_path == output_path:
        raise ValueError(
            "Input and output paths cannot be the same"
        )

    with open(input_path, "rb") as i:
        data = i.read()

    result = remove(data)

    with open(output_path, "wb") as o:
        o.write(result)

    return output_path