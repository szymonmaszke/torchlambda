def compression_level(compression, level):
    def _wrong_parameters(minimum, maximum):
        print(
            "--level should be in range [{}, {}] for compression type {}".format(
                minimum, maximum, level
            )
        )
        exit(1)

    if compression == "DEFLATED":
        if not 0 <= level <= 9:
            _wrong_parameters(0, 9)
        return level
    if compression == "BZIP2":
        if not 1 <= level <= 9:
            _wrong_parameters(1, 9)
        return level

    return level
