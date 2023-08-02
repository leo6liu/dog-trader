from datetime import datetime
import os


def convert_time_to_minutes(time_string):
  """Converts a time string to minutes.

  Args:
    time_string: The time string in HH:MM format.

  Returns:
    The time in minutes.
  """

  time_struct = datetime.strptime(time_string, "%H:%M")
  minutes = time_struct.hour * 60 + time_struct.minute
  return minutes


def list_files_recursively(directory):
  """Lists all files under a directory recursively.

  Args:
    directory: The directory to list files from.

  Returns:
    A list of all files under the directory.
  """

  files = []
  for root, directories, filenames in os.walk(directory):
    for filename in filenames:
      files.append(os.path.join(root, filename))

  return files


def read_date_string(filename):
  """Reads the date string from a filename.

  Args:
    filename: The filename to read the date string from.

  Returns:
    The date string.
  """

  date_string = filename.split("_")[1]
  return date_string
