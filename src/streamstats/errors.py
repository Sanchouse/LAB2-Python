class StreamStatsError(ValueError):
    pass


class ErrorOrWarningLevelError(TypeError):
    pass


class IncorrectDateError(StreamStatsError):
    pass


class DifferentTypesError(StreamStatsError):
    pass


class UnsupportedFormatError(StreamStatsError):
    pass


class InvalidTimestampError(StreamStatsError):
    pass


class IncorrectDataError(StreamStatsError):
    pass


class UnicodeError(StreamStatsError):
    pass


def validation(type_of_error:str, *args) -> None:
    """Raise an error if something wrong"""
    if type_of_error == "UNICODE ERROR":
        raise UnicodeError(f"Unicode of file '{args[0]}' is not utf-8")
    if type_of_error == "INCORRECT TIME":
        raise IncorrectDateError("Does not conform to the ISO 8601 format.")
    elif type_of_error == "FUTURE":
        raise IncorrectDateError("Impossible date and time.")
    elif type_of_error == "INCORRECT LEVEL":
        raise IncorrectDataError(f"Incorrect type of level: {args[0]}")
    elif type_of_error == "EMPTY ROW":
        raise IncorrectDataError(f"row №{args[0]} cannot be empty.")
    elif type_of_error == "EMPTY SOURCE":
        raise IncorrectDataError(f"The source in file '{args[1]}' in row {args[0]} cannot be empty.")
    elif type_of_error == "MISSING VALUE":
        raise IncorrectDataError(f"The column '{args[0]}' in row cannot be missing.")
    elif type_of_error == "DIFFERENT TYPES":
        raise DifferentTypesError(f"The types of input files '{args[1]}' do not match the written ones '{args[0]}'.")
    elif type_of_error == "INCORRECT FIELDS":
        raise IncorrectDataError("An incorrect name for one of the required columns, or their absence, or the presence of unnecessary columns.")
    elif type_of_error == "INCORRECT READ":
        raise IncorrectDataError(f"Incorrect/missing key or incorrect/missing value in the JSON file '{args[0]}'.")
    elif type_of_error == "MISSING FILE":
        raise StreamStatsError(f"There is no such file {args[0]}.")
    elif type_of_error == "UNKNOWN TYPE":
        raise UnsupportedFormatError(f"{args[0]} files are not supported.")
    elif type_of_error == "ERROR":
        raise ErrorOrWarningLevelError(f"File {args[0]} [{args[2]}] has ERROR in row {args[1]}.")
    elif type_of_error == "CRITICAL":
        raise ErrorOrWarningLevelError(f"File {args[0]} [{args[2]}] has CRITICAL in row {args[1]}.")