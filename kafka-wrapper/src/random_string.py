def create_string_from_bytes(size_in_bytes):
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    generated_string = ""
    while len(generated_string.encode('utf-8')) < size_in_bytes:
        generated_string += characters
    generated_string = generated_string[:size_in_bytes]
    return generated_string
